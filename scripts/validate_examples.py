#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]

SCHEMA_DIR = ROOT / "schemas"
PASS_DIR = ROOT / "examples" / "pass"
FAIL_DIR = ROOT / "examples" / "fail"

VERSION = "0.1.0"

SCHEMA_FILES = {
    "causal-observation": "causal-observation.schema.json",
    "forward-trace": "forward-trace.schema.json",
    "backward-trace": "backward-trace.schema.json",
    "causal-reconstruction": "causal-reconstruction.schema.json",
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

        if not isinstance(record_type, str) or identifier is None:
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

    if record_type in {"forward-trace", "backward-trace"}:
        observation_id = document.get("observation_id")
        observation = observations.get(observation_id)

        if observation is None:
            errors.append(
                f"unknown observation_id: {observation_id!r}"
            )
        else:
            known_evidence = evidence_ids_for_observation(observation)

            for step in document.get("steps", []):
                for evidence_ref in step.get("evidence_refs", []):
                    if evidence_ref not in known_evidence:
                        errors.append(
                            f"{step.get('step_id')}: "
                            f"unknown evidence_ref {evidence_ref!r}"
                        )

    elif record_type == "causal-reconstruction":
        observation_id = document.get("observation_id")
        forward_trace_id = document.get("forward_trace_id")
        backward_trace_id = document.get("backward_trace_id")

        if observation_id not in observations:
            errors.append(
                f"unknown observation_id: {observation_id!r}"
            )

        forward_trace = forward_traces.get(forward_trace_id)
        backward_trace = backward_traces.get(backward_trace_id)

        if forward_trace is None:
            errors.append(
                f"unknown forward_trace_id: {forward_trace_id!r}"
            )

        if backward_trace is None:
            errors.append(
                f"unknown backward_trace_id: {backward_trace_id!r}"
            )

        if (
            forward_trace is not None
            and forward_trace.get("observation_id") != observation_id
        ):
            errors.append(
                "forward trace observation_id does not match reconstruction"
            )

        if (
            backward_trace is not None
            and backward_trace.get("observation_id") != observation_id
        ):
            errors.append(
                "backward trace observation_id does not match reconstruction"
            )

        forward_step_ids = set()
        backward_step_ids = set()

        if forward_trace is not None:
            forward_step_ids = {
                step.get("step_id")
                for step in forward_trace.get("steps", [])
            }

        if backward_trace is not None:
            backward_step_ids = {
                step.get("step_id")
                for step in backward_trace.get("steps", [])
            }

        for meeting_point in document.get("meeting_points", []):
            forward_step_id = meeting_point.get("forward_step_id")
            backward_step_id = meeting_point.get("backward_step_id")

            if forward_step_id not in forward_step_ids:
                errors.append(
                    f"{meeting_point.get('meeting_point_id')}: "
                    f"unknown forward_step_id {forward_step_id!r}"
                )

            if backward_step_id not in backward_step_ids:
                errors.append(
                    f"{meeting_point.get('meeting_point_id')}: "
                    f"unknown backward_step_id {backward_step_id!r}"
                )

        if (
            document.get("reconstruction_status") == "converged"
            and not document.get("meeting_points")
        ):
            errors.append(
                "converged reconstruction requires at least one meeting point"
            )

    elif record_type == "causal-validation":
        reconstruction_id = document.get("reconstruction_id")

        if reconstruction_id not in reconstructions:
            errors.append(
                f"unknown reconstruction_id: {reconstruction_id!r}"
            )

        conclusion = document.get("conclusion", {})

        if conclusion.get("status") == "supported":
            tests = document.get("counterfactual_tests", [])

            if not tests:
                errors.append(
                    "supported conclusion requires at least one "
                    "counterfactual test"
                )
            elif not any(
                test.get("supports_hypothesis") is True
                for test in tests
            ):
                errors.append(
                    "supported conclusion requires at least one "
                    "supporting counterfactual test"
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

        errors = schema_errors(document, validators)

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
        errors = semantic_errors(document, registry)

        if errors:
            print(f"  [semantic-error] {identifier}")
            for error in errors:
                print(f"    - {error}")
            success = False
        else:
            print(f"  [semantic-ok] {identifier}")

    return documents, success


def validate_fail_examples(
    validators: dict[str, Draft202012Validator],
    pass_documents: list[dict[str, Any]],
) -> bool:
    success = True
    pass_registry = build_registry(pass_documents)

    print("\n[fail examples]\n")

    paths = sorted(FAIL_DIR.glob("*.yaml"))

    for path in paths:
        print(f"- {path.relative_to(ROOT)}")

        try:
            document = load_yaml(path)
        except Exception as exc:
            print(f"  [expected-failure] load-error: {exc}")
            continue

        errors = schema_errors(document, validators)

        if errors:
            print("  [expected-schema-failure]")
            for error in errors:
                print(f"    - {error}")
            continue

        semantic = semantic_errors(document, pass_registry)

        if semantic:
            print("  [expected-semantic-failure]")
            for error in semantic:
                print(f"    - {error}")
            continue

        print("  [unexpected-pass]")
        success = False

    return success


def main() -> int:
    print(
        "=== Causal Trace Reconstruction Protocol "
        "v0.1 Validation ==="
    )

    try:
        validators = load_validators()
    except Exception as exc:
        print(f"[fatal] failed to load schemas: {exc}")
        return 1

    for record_type, filename in SCHEMA_FILES.items():
        print(f"schema [{record_type}]: schemas/{filename}")

    pass_documents, pass_ok = validate_pass_examples(validators)

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
