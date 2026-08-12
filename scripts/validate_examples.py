#!/usr/bin/env python3

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]

SCHEMA_DIR = ROOT / "schemas"
PASS_DIR = ROOT / "examples" / "pass"
FAIL_DIR = ROOT / "examples" / "fail"

VERSION = "0.2.0"

SCHEMA_FILES = {
    "causal-observation": "causal-observation.schema.json",
    "forward-trace": "forward-trace.schema.json",
    "backward-trace": "backward-trace.schema.json",
    "causal-reconstruction": "causal-reconstruction.schema.json",
    "hypothesis-comparison": "hypothesis-comparison.schema.json",
    "causal-validation": "causal-validation.schema.json",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be an object")

    return data


def format_schema_error(error: Any) -> str:
    if error.absolute_path:
        location = ".".join(str(part) for part in error.absolute_path)
    else:
        location = "<root>"

    return f"{location}: {error.message}"


def load_validators() -> dict[str, Draft202012Validator]:
    validators: dict[str, Draft202012Validator] = {}

    for record_type, filename in SCHEMA_FILES.items():
        schema_path = SCHEMA_DIR / filename
        schema = load_json(schema_path)

        Draft202012Validator.check_schema(schema)

        validators[record_type] = Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        )

    return validators


def schema_errors(
    document: dict[str, Any],
    validators: dict[str, Draft202012Validator],
) -> list[str]:

    record_type = document.get("record_type")

    if record_type not in validators:
        return [f"unknown record_type: {record_type!r}"]

    validator = validators[record_type]

    errors = sorted(
        validator.iter_errors(document),
        key=lambda error: list(error.absolute_path),
    )

    return [format_schema_error(error) for error in errors]


def document_id(document: dict[str, Any]) -> str | None:
    record_type = document.get("record_type")

    key_by_type = {
        "causal-observation": "observation_id",
        "forward-trace": "trace_id",
        "backward-trace": "trace_id",
        "causal-reconstruction": "reconstruction_id",
        "hypothesis-comparison": "comparison_id",
        "causal-validation": "validation_id",
    }

    key = key_by_type.get(record_type)

    if key is None:
        return None

    value = document.get(key)

    if isinstance(value, str):
        return value

    return None


def build_registry(
    documents: list[dict[str, Any]],
) -> dict[str, dict[str, dict[str, Any]]]:

    registry: dict[str, dict[str, dict[str, Any]]] = {}

    for document in documents:
        record_type = document.get("record_type")
        identifier = document_id(document)

        if not isinstance(record_type, str):
            continue

        if identifier is None:
            continue

        registry.setdefault(record_type, {})[identifier] = document

    return registry


def evidence_ids_for_observation(
    observation: dict[str, Any],
) -> set[str]:

    result: set[str] = set()

    for evidence in observation.get("evidence", []):
        evidence_id = evidence.get("evidence_id")

        if isinstance(evidence_id, str):
            result.add(evidence_id)

    return result


def reconstruction_hypotheses(
    reconstruction: dict[str, Any],
) -> dict[str, dict[str, Any]]:

    result: dict[str, dict[str, Any]] = {}

    for hypothesis in reconstruction.get("candidate_hypotheses", []):
        hypothesis_id = hypothesis.get("hypothesis_id")

        if isinstance(hypothesis_id, str):
            result[hypothesis_id] = hypothesis

    return result


def trace_step_ids(
    trace_ids: list[str],
    traces: dict[str, dict[str, Any]],
) -> set[str]:

    result: set[str] = set()

    for trace_id in trace_ids:
        trace = traces.get(trace_id)

        if trace is None:
            continue

        for step in trace.get("steps", []):
            step_id = step.get("step_id")

            if isinstance(step_id, str):
                result.add(step_id)

    return result


def semantic_errors(
    document: dict[str, Any],
    registry: dict[str, dict[str, dict[str, Any]]],
) -> list[str]:

    errors: list[str] = []

    if document.get("schema_version") != VERSION:
        errors.append(
            f"schema_version must be {VERSION!r}"
        )

    record_type = document.get("record_type")

    observations = registry.get("causal-observation", {})
    forward_traces = registry.get("forward-trace", {})
    backward_traces = registry.get("backward-trace", {})
    reconstructions = registry.get("causal-reconstruction", {})
    comparisons = registry.get("hypothesis-comparison", {})

    if record_type in {"forward-trace", "backward-trace"}:

        observation_id = document.get("observation_id")
        observation = observations.get(observation_id)

        if observation is None:
            errors.append(
                f"unknown observation_id: {observation_id!r}"
            )
            return errors

        known_evidence = evidence_ids_for_observation(observation)

        for step in document.get("steps", []):
            step_id = step.get("step_id")

            for evidence_ref in step.get("evidence_refs", []):
                if evidence_ref not in known_evidence:
                    errors.append(
                        f"{step_id}: unknown evidence_ref "
                        f"{evidence_ref!r}"
                    )

    elif record_type == "causal-reconstruction":

        observation_id = document.get("observation_id")
        observation = observations.get(observation_id)

        if observation is None:
            errors.append(
                f"unknown observation_id: {observation_id!r}"
            )

        forward_ids = document.get("forward_trace_ids", [])
        backward_ids = document.get("backward_trace_ids", [])

        for trace_id in forward_ids:
            trace = forward_traces.get(trace_id)

            if trace is None:
                errors.append(
                    f"unknown forward_trace_id: {trace_id!r}"
                )
                continue

            if trace.get("observation_id") != observation_id:
                errors.append(
                    f"forward trace {trace_id!r} belongs to a "
                    "different observation"
                )

        for trace_id in backward_ids:
            trace = backward_traces.get(trace_id)

            if trace is None:
                errors.append(
                    f"unknown backward_trace_id: {trace_id!r}"
                )
                continue

            if trace.get("observation_id") != observation_id:
                errors.append(
                    f"backward trace {trace_id!r} belongs to a "
                    "different observation"
                )

        forward_step_ids = trace_step_ids(
            forward_ids,
            forward_traces,
        )

        backward_step_ids = trace_step_ids(
            backward_ids,
            backward_traces,
        )

        all_step_ids = forward_step_ids | backward_step_ids

        hypothesis_ids: list[str] = []

        known_evidence: set[str] = set()

        if observation is not None:
            known_evidence = evidence_ids_for_observation(
                observation
            )

        for hypothesis in document.get(
            "candidate_hypotheses",
            [],
        ):
            hypothesis_id = hypothesis.get("hypothesis_id")

            if isinstance(hypothesis_id, str):
                hypothesis_ids.append(hypothesis_id)

            for evidence_ref in hypothesis.get(
                "evidence_refs",
                [],
            ):
                if evidence_ref not in known_evidence:
                    errors.append(
                        f"{hypothesis_id}: unknown evidence_ref "
                        f"{evidence_ref!r}"
                    )

            for contradiction in hypothesis.get(
                "contradictions",
                [],
            ):
                for evidence_ref in contradiction.get(
                    "evidence_refs",
                    [],
                ):
                    if evidence_ref not in known_evidence:
                        errors.append(
                            f"{hypothesis_id}: contradiction "
                            f"references unknown evidence "
                            f"{evidence_ref!r}"
                        )

            for meeting_point in hypothesis.get(
                "meeting_points",
                [],
            ):

                forward_step_id = meeting_point.get(
                    "forward_step_id"
                )

                backward_step_id = meeting_point.get(
                    "backward_step_id"
                )

                if forward_step_id not in forward_step_ids:
                    errors.append(
                        f"{hypothesis_id}: unknown "
                        f"forward_step_id "
                        f"{forward_step_id!r}"
                    )

                if backward_step_id not in backward_step_ids:
                    errors.append(
                        f"{hypothesis_id}: unknown "
                        f"backward_step_id "
                        f"{backward_step_id!r}"
                    )

            for segment in hypothesis.get(
                "candidate_path",
                [],
            ):
                for step_ref in segment.get(
                    "basis_step_refs",
                    [],
                ):
                    if step_ref not in all_step_ids:
                        errors.append(
                            f"{hypothesis_id}: path references "
                            f"unknown step {step_ref!r}"
                        )

        if len(hypothesis_ids) != len(set(hypothesis_ids)):
            errors.append(
                "candidate hypothesis_id values must be unique"
            )

        active_hypotheses = [
            hypothesis
            for hypothesis in document.get(
                "candidate_hypotheses",
                [],
            )
            if hypothesis.get("status") == "active"
        ]

        status = document.get("reconstruction_status")

        if status == "no-convergence":
            if active_hypotheses:
                errors.append(
                    "no-convergence reconstruction must not "
                    "contain active hypotheses"
                )

        else:
            if not active_hypotheses:
                errors.append(
                    f"{status} reconstruction requires at least "
                    "one active hypothesis"
                )

        if status == "ambiguous":
            if len(active_hypotheses) < 2:
                errors.append(
                    "ambiguous reconstruction requires at least "
                    "two active hypotheses"
                )

        if status == "converged":
            if not any(
                hypothesis.get("meeting_points")
                for hypothesis in active_hypotheses
            ):
                errors.append(
                    "converged reconstruction requires at least "
                    "one active hypothesis with a meeting point"
                )

    elif record_type == "hypothesis-comparison":

        reconstruction_id = document.get("reconstruction_id")
        reconstruction = reconstructions.get(reconstruction_id)

        if reconstruction is None:
            errors.append(
                f"unknown reconstruction_id: "
                f"{reconstruction_id!r}"
            )
            return errors

        hypotheses = reconstruction_hypotheses(
            reconstruction
        )

        active_ids = {
            hypothesis_id
            for hypothesis_id, hypothesis in hypotheses.items()
            if hypothesis.get("status") == "active"
        }

        entries = document.get("entries", [])

        compared_ids = [
            entry.get("hypothesis_id")
            for entry in entries
        ]

        if len(compared_ids) != len(set(compared_ids)):
            errors.append(
                "comparison hypothesis_id values must be unique"
            )

        unknown_ids = set(compared_ids) - set(hypotheses)

        for hypothesis_id in sorted(unknown_ids):
            errors.append(
                f"comparison references unknown hypothesis "
                f"{hypothesis_id!r}"
            )

        if set(compared_ids) != active_ids:
            errors.append(
                "comparison must include every active hypothesis "
                "exactly once"
            )

        ranks = [
            entry.get("rank")
            for entry in entries
        ]

        expected_ranks = list(
            range(1, len(entries) + 1)
        )

        if sorted(ranks) != expected_ranks:
            errors.append(
                "comparison ranks must form the sequence "
                f"{expected_ranks}"
            )

        ranked_entries = sorted(
            entries,
            key=lambda entry: entry.get("rank", 0),
        )

        scores = [
            entry.get("final_score")
            for entry in ranked_entries
        ]

        if any(
            scores[index] < scores[index + 1]
            for index in range(len(scores) - 1)
        ):
            errors.append(
                "final_score must not increase as rank decreases"
            )

        margin = document.get("selection_margin")

        expected_margin: float | None

        if len(ranked_entries) >= 2:
            expected_margin = (
                ranked_entries[0]["final_score"]
                - ranked_entries[1]["final_score"]
            )
        else:
            expected_margin = None

        if expected_margin is None:
            if margin is not None:
                errors.append(
                    "selection_margin must be null when only "
                    "one hypothesis is compared"
                )
        else:
            if margin is None or not math.isclose(
                margin,
                expected_margin,
                rel_tol=1e-9,
                abs_tol=1e-9,
            ):
                errors.append(
                    "selection_margin must equal the difference "
                    "between rank 1 and rank 2 final_score"
                )

        decision = document.get("decision", {})
        decision_status = decision.get("status")
        tie_threshold = document.get("tie_threshold")

        if decision_status == "selected":

            selected_id = decision.get(
                "selected_hypothesis_id"
            )

            if selected_id not in compared_ids:
                errors.append(
                    "selected_hypothesis_id must reference a "
                    "compared hypothesis"
                )

            if ranked_entries:
                top_id = ranked_entries[0].get(
                    "hypothesis_id"
                )

                if selected_id != top_id:
                    errors.append(
                        "selected_hypothesis_id must be the "
                        "rank 1 hypothesis"
                    )

            if (
                expected_margin is not None
                and expected_margin < tie_threshold
            ):
                errors.append(
                    "selected decision is invalid because the "
                    "selection margin is below tie_threshold"
                )

        elif decision_status == "ambiguous":

            if len(ranked_entries) < 2:
                errors.append(
                    "ambiguous decision requires at least "
                    "two hypotheses"
                )

            elif expected_margin is not None:
                if expected_margin >= tie_threshold:
                    errors.append(
                        "ambiguous decision is invalid because "
                        "the selection margin is not below "
                        "tie_threshold"
                    )

    elif record_type == "causal-validation":

        reconstruction_id = document.get("reconstruction_id")
        reconstruction = reconstructions.get(reconstruction_id)

        if reconstruction is None:
            errors.append(
                f"unknown reconstruction_id: "
                f"{reconstruction_id!r}"
            )
            return errors

        hypotheses = reconstruction_hypotheses(
            reconstruction
        )

        hypothesis_id = document.get("hypothesis_id")

        if hypothesis_id not in hypotheses:
            errors.append(
                f"unknown hypothesis_id: {hypothesis_id!r}"
            )

        for competing_id in document.get(
            "competing_hypothesis_refs",
            [],
        ):
            if competing_id not in hypotheses:
                errors.append(
                    f"unknown competing hypothesis "
                    f"{competing_id!r}"
                )

            if competing_id == hypothesis_id:
                errors.append(
                    "a hypothesis cannot compete with itself"
                )

        comparison_id = document.get("comparison_id")

        if comparison_id is not None:

            comparison = comparisons.get(comparison_id)

            if comparison is None:
                errors.append(
                    f"unknown comparison_id: "
                    f"{comparison_id!r}"
                )

            elif (
                comparison.get("reconstruction_id")
                != reconstruction_id
            ):
                errors.append(
                    "comparison belongs to a different "
                    "reconstruction"
                )

        conclusion = document.get("conclusion", {})

        if conclusion.get("status") == "supported":

            tests = document.get(
                "counterfactual_tests",
                [],
            )

            if not tests:
                errors.append(
                    "supported conclusion requires at least "
                    "one counterfactual test"
                )

            elif not any(
                test.get("supports_hypothesis") is True
                for test in tests
            ):
                errors.append(
                    "supported conclusion requires at least "
                    "one supporting counterfactual test"
                )

    return errors


def validate_pass_examples(
    validators: dict[str, Draft202012Validator],
) -> tuple[list[dict[str, Any]], bool]:

    documents: list[dict[str, Any]] = []
    success = True

    print("\n[pass examples]\n")

    paths = sorted(PASS_DIR.glob("*.yaml"))

    for path in paths:
        print(f"- {path.relative_to(ROOT)}")

        try:
            document = load_yaml(path)
        except Exception as exc:
            print(f"  [load-error] {exc}")
            success = False
            continue

        errors = schema_errors(
            document,
            validators,
        )

        if errors:
            print("  [schema-error]")

            for error in errors:
                print(f"    - {error}")

            success = False
            continue

        print("  [schema-ok]")
        documents.append(document)

    registry = build_registry(documents)

    for document in documents:

        identifier = document_id(document)

        errors = semantic_errors(
            document,
            registry,
        )

        if errors:
            print(
                f"  [semantic-error] {identifier}"
            )

            for error in errors:
                print(f"    - {error}")

            success = False

        else:
            print(
                f"  [semantic-ok] {identifier}"
            )

    return documents, success


def validate_fail_examples(
    validators: dict[str, Draft202012Validator],
    pass_documents: list[dict[str, Any]],
) -> bool:

    success = True

    pass_registry = build_registry(
        pass_documents
    )

    print("\n[fail examples]\n")

    paths = sorted(FAIL_DIR.glob("*.yaml"))

    for path in paths:

        print(f"- {path.relative_to(ROOT)}")

        try:
            document = load_yaml(path)

        except Exception as exc:

            print(
                f"  [expected-failure] "
                f"load-error: {exc}"
            )

            continue

        errors = schema_errors(
            document,
            validators,
        )

        if errors:

            print(
                "  [expected-schema-failure]"
            )

            for error in errors:
                print(f"    - {error}")

            continue

        semantic = semantic_errors(
            document,
            pass_registry,
        )

        if semantic:

            print(
                "  [expected-semantic-failure]"
            )

            for error in semantic:
                print(f"    - {error}")

            continue

        print("  [unexpected-pass]")
        success = False

    return success


def main() -> int:

    print(
        "=== Causal Trace Reconstruction Protocol "
        "v0.2 Validation ==="
    )

    try:
        validators = load_validators()

    except Exception as exc:

        print(
            f"[fatal] failed to load schemas: {exc}"
        )

        return 1

    for record_type, filename in SCHEMA_FILES.items():

        print(
            f"schema [{record_type}]: "
            f"schemas/{filename}"
        )

    pass_documents, pass_ok = (
        validate_pass_examples(
            validators
        )
    )

    fail_ok = validate_fail_examples(
        validators,
        pass_documents,
    )

    if pass_ok and fail_ok:

        print("\n[validation-ok]")
        return 0

    print("\n[validation-failed]")
    return 1


if __name__ == "__main__":
    sys.exit(main())
