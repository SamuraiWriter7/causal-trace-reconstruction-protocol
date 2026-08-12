#!/usr/bin/env python3

from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]

SCHEMA_DIR = ROOT / "schemas"
PASS_DIR = ROOT / "examples" / "pass"
FAIL_DIR = ROOT / "examples" / "fail"

VERSION = "0.3.0"

SCHEMA_FILES = {
    "causal-observation": "causal-observation.schema.json",
    "forward-trace": "forward-trace.schema.json",
    "backward-trace": "backward-trace.schema.json",
    "causal-reconstruction": "causal-reconstruction.schema.json",
    "temporal-precedence-assessment": (
        "temporal-precedence-assessment.schema.json"
    ),
    "hypothesis-comparison": "hypothesis-comparison.schema.json",
    "causal-validation": "causal-validation.schema.json",
}

TemporalResult = Literal[
    "satisfied",
    "unresolved",
    "violated",
]


# ---------------------------------------------------------------------------
# Loading and schema validation
# ---------------------------------------------------------------------------


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise ValueError(
            f"{path}: root must be an object"
        )

    return data


def format_schema_error(error: Any) -> str:
    if error.absolute_path:
        location = ".".join(
            str(part)
            for part in error.absolute_path
        )
    else:
        location = "<root>"

    return f"{location}: {error.message}"


def load_validators() -> dict[
    str,
    Draft202012Validator,
]:
    validators: dict[
        str,
        Draft202012Validator,
    ] = {}

    for record_type, filename in SCHEMA_FILES.items():
        schema_path = SCHEMA_DIR / filename
        schema = load_json(schema_path)

        Draft202012Validator.check_schema(
            schema
        )

        validators[record_type] = (
            Draft202012Validator(
                schema,
                format_checker=FormatChecker(),
            )
        )

    return validators


def schema_errors(
    document: dict[str, Any],
    validators: dict[
        str,
        Draft202012Validator,
    ],
) -> list[str]:

    record_type = document.get(
        "record_type"
    )

    if record_type not in validators:
        return [
            f"unknown record_type: "
            f"{record_type!r}"
        ]

    validator = validators[record_type]

    errors = sorted(
        validator.iter_errors(document),
        key=lambda error: [
            str(part)
            for part in error.absolute_path
        ],
    )

    return [
        format_schema_error(error)
        for error in errors
    ]


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------


def document_id(
    document: dict[str, Any],
) -> str | None:

    record_type = document.get(
        "record_type"
    )

    key_by_type = {
        "causal-observation":
            "observation_id",
        "forward-trace":
            "trace_id",
        "backward-trace":
            "trace_id",
        "causal-reconstruction":
            "reconstruction_id",
        "temporal-precedence-assessment":
            "assessment_id",
        "hypothesis-comparison":
            "comparison_id",
        "causal-validation":
            "validation_id",
    }

    key = key_by_type.get(
        record_type
    )

    if key is None:
        return None

    value = document.get(key)

    if isinstance(value, str):
        return value

    return None


def build_registry(
    documents: list[
        dict[str, Any]
    ],
) -> dict[
    str,
    dict[
        str,
        dict[str, Any],
    ],
]:

    registry: dict[
        str,
        dict[
            str,
            dict[str, Any],
        ],
    ] = {}

    for document in documents:
        record_type = document.get(
            "record_type"
        )
        identifier = document_id(
            document
        )

        if not isinstance(
            record_type,
            str,
        ):
            continue

        if identifier is None:
            continue

        registry.setdefault(
            record_type,
            {},
        )[identifier] = document

    return registry


def evidence_ids_for_observation(
    observation: dict[str, Any],
) -> set[str]:

    result: set[str] = set()

    for evidence in observation.get(
        "evidence",
        [],
    ):
        evidence_id = evidence.get(
            "evidence_id"
        )

        if isinstance(
            evidence_id,
            str,
        ):
            result.add(
                evidence_id
            )

    return result


def reconstruction_hypotheses(
    reconstruction: dict[str, Any],
) -> dict[
    str,
    dict[str, Any],
]:

    result: dict[
        str,
        dict[str, Any],
    ] = {}

    for hypothesis in (
        reconstruction.get(
            "candidate_hypotheses",
            [],
        )
    ):
        hypothesis_id = (
            hypothesis.get(
                "hypothesis_id"
            )
        )

        if isinstance(
            hypothesis_id,
            str,
        ):
            result[hypothesis_id] = (
                hypothesis
            )

    return result


def trace_step_ids(
    trace_ids: list[str],
    traces: dict[
        str,
        dict[str, Any],
    ],
) -> set[str]:

    result: set[str] = set()

    for trace_id in trace_ids:
        trace = traces.get(
            trace_id
        )

        if trace is None:
            continue

        for step in trace.get(
            "steps",
            [],
        ):
            step_id = step.get(
                "step_id"
            )

            if isinstance(
                step_id,
                str,
            ):
                result.add(
                    step_id
                )

    return result


# ---------------------------------------------------------------------------
# Temporal helpers
# ---------------------------------------------------------------------------


def parse_datetime(
    value: str,
) -> datetime:

    normalized = value

    if value.endswith("Z"):
        normalized = (
            value[:-1]
            + "+00:00"
        )

    parsed = datetime.fromisoformat(
        normalized
    )

    if parsed.tzinfo is None:
        raise ValueError(
            "date-time must include "
            "a timezone offset"
        )

    return parsed.astimezone(
        timezone.utc
    )


def timing_bounds(
    timing: dict[str, Any],
) -> tuple[
    datetime,
    datetime,
] | None:

    kind = timing.get(
        "kind"
    )

    if kind == "unknown":
        return None

    if kind == "exact":
        at = parse_datetime(
            timing["at"]
        )

        return (
            at,
            at,
        )

    if kind == "interval":
        earliest = parse_datetime(
            timing["earliest_at"]
        )

        latest = parse_datetime(
            timing["latest_at"]
        )

        if earliest > latest:
            raise ValueError(
                "earliest_at must not "
                "be later than latest_at"
            )

        return (
            earliest,
            latest,
        )

    raise ValueError(
        f"unknown timing kind: "
        f"{kind!r}"
    )


def evaluate_ordering(
    relation: str,
    cause_bounds: tuple[
        datetime,
        datetime,
    ],
    effect_bounds: tuple[
        datetime,
        datetime,
    ],
) -> TemporalResult:

    (
        cause_earliest,
        cause_latest,
    ) = cause_bounds

    (
        effect_earliest,
        effect_latest,
    ) = effect_bounds

    if relation == "strict-before":

        if (
            cause_latest
            < effect_earliest
        ):
            return "satisfied"

        if (
            cause_earliest
            >= effect_latest
        ):
            return "violated"

        return "unresolved"

    if relation == "before-or-equal":

        if (
            cause_latest
            <= effect_earliest
        ):
            return "satisfied"

        if (
            cause_earliest
            > effect_latest
        ):
            return "violated"

        return "unresolved"

    raise ValueError(
        "unknown precedence relation: "
        f"{relation!r}"
    )


def evaluate_causal_window(
    cause_bounds: tuple[
        datetime,
        datetime,
    ],
    effect_bounds: tuple[
        datetime,
        datetime,
    ],
    causal_window: dict[str, Any],
) -> TemporalResult:

    (
        cause_earliest,
        cause_latest,
    ) = cause_bounds

    (
        effect_earliest,
        effect_latest,
    ) = effect_bounds

    min_allowed = float(
        causal_window[
            "min_lag_seconds"
        ]
    )

    max_allowed = float(
        causal_window[
            "max_lag_seconds"
        ]
    )

    if min_allowed > max_allowed:
        raise ValueError(
            "causal_window "
            "min_lag_seconds must not "
            "exceed max_lag_seconds"
        )

    lag_min = (
        effect_earliest
        - cause_latest
    ).total_seconds()

    lag_max = (
        effect_latest
        - cause_earliest
    ).total_seconds()

    if (
        lag_max < min_allowed
        or lag_min > max_allowed
    ):
        return "violated"

    if (
        lag_min >= min_allowed
        and lag_max <= max_allowed
    ):
        return "satisfied"

    return "unresolved"


def evaluate_precedence_constraint(
    constraint: dict[str, Any],
    events_by_id: dict[
        str,
        dict[str, Any],
    ],
) -> tuple[
    TemporalResult,
    str | None,
]:

    constraint_id = (
        constraint.get(
            "constraint_id"
        )
    )

    cause_event_id = (
        constraint.get(
            "cause_event_id"
        )
    )

    effect_event_id = (
        constraint.get(
            "effect_event_id"
        )
    )

    cause_event = events_by_id.get(
        cause_event_id
    )

    effect_event = events_by_id.get(
        effect_event_id
    )

    if cause_event is None:
        return (
            "unresolved",
            (
                f"{constraint_id}: "
                "unknown cause_event_id "
                f"{cause_event_id!r}"
            ),
        )

    if effect_event is None:
        return (
            "unresolved",
            (
                f"{constraint_id}: "
                "unknown effect_event_id "
                f"{effect_event_id!r}"
            ),
        )

    try:
        cause_bounds = timing_bounds(
            cause_event.get(
                "timing",
                {},
            )
        )

        effect_bounds = timing_bounds(
            effect_event.get(
                "timing",
                {},
            )
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ) as exc:

        return (
            "unresolved",
            (
                f"{constraint_id}: "
                f"invalid timing: {exc}"
            ),
        )

    if (
        cause_bounds is None
        or effect_bounds is None
    ):
        return (
            "unresolved",
            None,
        )

    try:
        ordering_result = (
            evaluate_ordering(
                constraint.get(
                    "relation"
                ),
                cause_bounds,
                effect_bounds,
            )
        )

    except ValueError as exc:
        return (
            "unresolved",
            f"{constraint_id}: {exc}",
        )

    if (
        ordering_result
        == "violated"
    ):
        return (
            "violated",
            None,
        )

    causal_window = (
        constraint.get(
            "causal_window"
        )
    )

    if causal_window is None:
        return (
            ordering_result,
            None,
        )

    try:
        window_result = (
            evaluate_causal_window(
                cause_bounds,
                effect_bounds,
                causal_window,
            )
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ) as exc:

        return (
            "unresolved",
            (
                f"{constraint_id}: "
                "invalid causal_window: "
                f"{exc}"
            ),
        )

    if (
        window_result
        == "violated"
    ):
        return (
            "violated",
            None,
        )

    if (
        ordering_result
        == "satisfied"
        and window_result
        == "satisfied"
    ):
        return (
            "satisfied",
            None,
        )

    return (
        "unresolved",
        None,
    )


def expected_temporal_status(
    results: dict[
        str,
        TemporalResult,
    ],
) -> str:

    satisfied_count = sum(
        result == "satisfied"
        for result
        in results.values()
    )

    unresolved_count = sum(
        result == "unresolved"
        for result
        in results.values()
    )

    violated_count = sum(
        result == "violated"
        for result
        in results.values()
    )

    if violated_count > 0:
        return "violated"

    if (
        unresolved_count > 0
        and satisfied_count > 0
    ):
        return "partially-ordered"

    if unresolved_count > 0:
        return (
            "insufficient-temporal-evidence"
        )

    return "consistent"


# ---------------------------------------------------------------------------
# Semantic validation
# ---------------------------------------------------------------------------


def semantic_errors(
    document: dict[str, Any],
    registry: dict[
        str,
        dict[
            str,
            dict[str, Any],
        ],
    ],
) -> list[str]:

    errors: list[str] = []

    if (
        document.get(
            "schema_version"
        )
        != VERSION
    ):
        errors.append(
            "schema_version must be "
            f"{VERSION!r}"
        )

    record_type = document.get(
        "record_type"
    )

    observations = registry.get(
        "causal-observation",
        {},
    )

    forward_traces = registry.get(
        "forward-trace",
        {},
    )

    backward_traces = registry.get(
        "backward-trace",
        {},
    )

    reconstructions = registry.get(
        "causal-reconstruction",
        {},
    )

    temporal_assessments = (
        registry.get(
            "temporal-precedence-assessment",
            {},
        )
    )

    comparisons = registry.get(
        "hypothesis-comparison",
        {},
    )

    # -----------------------------------------------------------------------
    # causal-observation
    # -----------------------------------------------------------------------

    if (
        record_type
        == "causal-observation"
    ):

        evidence_ids = [
            evidence.get(
                "evidence_id"
            )
            for evidence
            in document.get(
                "evidence",
                [],
            )
        ]

        if (
            len(evidence_ids)
            != len(set(evidence_ids))
        ):
            errors.append(
                "evidence_id values "
                "must be unique"
            )

    # -----------------------------------------------------------------------
    # forward-trace / backward-trace
    # -----------------------------------------------------------------------

    elif record_type in {
        "forward-trace",
        "backward-trace",
    }:

        observation_id = (
            document.get(
                "observation_id"
            )
        )

        observation = (
            observations.get(
                observation_id
            )
        )

        if observation is None:
            errors.append(
                "unknown observation_id: "
                f"{observation_id!r}"
            )

            return errors

        known_evidence = (
            evidence_ids_for_observation(
                observation
            )
        )

        step_ids = [
            step.get("step_id")
            for step
            in document.get(
                "steps",
                [],
            )
        ]

        if (
            len(step_ids)
            != len(set(step_ids))
        ):
            errors.append(
                "step_id values "
                "must be unique"
            )

        for step in document.get(
            "steps",
            [],
        ):
            step_id = step.get(
                "step_id"
            )

            for evidence_ref in (
                step.get(
                    "evidence_refs",
                    [],
                )
            ):
                if (
                    evidence_ref
                    not in known_evidence
                ):
                    errors.append(
                        f"{step_id}: "
                        "unknown evidence_ref "
                        f"{evidence_ref!r}"
                    )

    # -----------------------------------------------------------------------
    # causal-reconstruction
    # -----------------------------------------------------------------------

    elif (
        record_type
        == "causal-reconstruction"
    ):

        observation_id = (
            document.get(
                "observation_id"
            )
        )

        observation = (
            observations.get(
                observation_id
            )
        )

        if observation is None:
            errors.append(
                "unknown observation_id: "
                f"{observation_id!r}"
            )

        forward_ids = document.get(
            "forward_trace_ids",
            [],
        )

        backward_ids = document.get(
            "backward_trace_ids",
            [],
        )

        for trace_id in forward_ids:
            trace = forward_traces.get(
                trace_id
            )

            if trace is None:
                errors.append(
                    "unknown "
                    "forward_trace_id: "
                    f"{trace_id!r}"
                )
                continue

            if (
                trace.get(
                    "observation_id"
                )
                != observation_id
            ):
                errors.append(
                    "forward trace "
                    f"{trace_id!r} "
                    "belongs to a "
                    "different observation"
                )

        for trace_id in backward_ids:
            trace = backward_traces.get(
                trace_id
            )

            if trace is None:
                errors.append(
                    "unknown "
                    "backward_trace_id: "
                    f"{trace_id!r}"
                )
                continue

            if (
                trace.get(
                    "observation_id"
                )
                != observation_id
            ):
                errors.append(
                    "backward trace "
                    f"{trace_id!r} "
                    "belongs to a "
                    "different observation"
                )

        forward_step_ids = (
            trace_step_ids(
                forward_ids,
                forward_traces,
            )
        )

        backward_step_ids = (
            trace_step_ids(
                backward_ids,
                backward_traces,
            )
        )

        all_step_ids = (
            forward_step_ids
            | backward_step_ids
        )

        hypothesis_ids: list[str] = []

        known_evidence: set[str] = set()

        if observation is not None:
            known_evidence = (
                evidence_ids_for_observation(
                    observation
                )
            )

        for hypothesis in (
            document.get(
                "candidate_hypotheses",
                [],
            )
        ):

            hypothesis_id = (
                hypothesis.get(
                    "hypothesis_id"
                )
            )

            if isinstance(
                hypothesis_id,
                str,
            ):
                hypothesis_ids.append(
                    hypothesis_id
                )

            for evidence_ref in (
                hypothesis.get(
                    "evidence_refs",
                    [],
                )
            ):
                if (
                    evidence_ref
                    not in known_evidence
                ):
                    errors.append(
                        f"{hypothesis_id}: "
                        "unknown evidence_ref "
                        f"{evidence_ref!r}"
                    )

            contradiction_ids = [
                contradiction.get(
                    "contradiction_id"
                )
                for contradiction
                in hypothesis.get(
                    "contradictions",
                    [],
                )
            ]

            if (
                len(contradiction_ids)
                != len(
                    set(
                        contradiction_ids
                    )
                )
            ):
                errors.append(
                    f"{hypothesis_id}: "
                    "contradiction_id "
                    "values must be unique"
                )

            for contradiction in (
                hypothesis.get(
                    "contradictions",
                    [],
                )
            ):

                for evidence_ref in (
                    contradiction.get(
                        "evidence_refs",
                        [],
                    )
                ):
                    if (
                        evidence_ref
                        not in known_evidence
                    ):
                        errors.append(
                            f"{hypothesis_id}: "
                            "contradiction "
                            "references unknown "
                            "evidence "
                            f"{evidence_ref!r}"
                        )

            meeting_point_ids = [
                meeting_point.get(
                    "meeting_point_id"
                )
                for meeting_point
                in hypothesis.get(
                    "meeting_points",
                    [],
                )
            ]

            if (
                len(meeting_point_ids)
                != len(
                    set(
                        meeting_point_ids
                    )
                )
            ):
                errors.append(
                    f"{hypothesis_id}: "
                    "meeting_point_id "
                    "values must be unique"
                )

            for meeting_point in (
                hypothesis.get(
                    "meeting_points",
                    [],
                )
            ):

                forward_step_id = (
                    meeting_point.get(
                        "forward_step_id"
                    )
                )

                backward_step_id = (
                    meeting_point.get(
                        "backward_step_id"
                    )
                )

                if (
                    forward_step_id
                    not in forward_step_ids
                ):
                    errors.append(
                        f"{hypothesis_id}: "
                        "unknown "
                        "forward_step_id "
                        f"{forward_step_id!r}"
                    )

                if (
                    backward_step_id
                    not in backward_step_ids
                ):
                    errors.append(
                        f"{hypothesis_id}: "
                        "unknown "
                        "backward_step_id "
                        f"{backward_step_id!r}"
                    )

            segment_ids = [
                segment.get(
                    "segment_id"
                )
                for segment
                in hypothesis.get(
                    "candidate_path",
                    [],
                )
            ]

            if (
                len(segment_ids)
                != len(
                    set(
                        segment_ids
                    )
                )
            ):
                errors.append(
                    f"{hypothesis_id}: "
                    "segment_id values "
                    "must be unique"
                )

            for segment in (
                hypothesis.get(
                    "candidate_path",
                    [],
                )
            ):

                for step_ref in (
                    segment.get(
                        "basis_step_refs",
                        [],
                    )
                ):
                    if (
                        step_ref
                        not in all_step_ids
                    ):
                        errors.append(
                            f"{hypothesis_id}: "
                            "path references "
                            "unknown step "
                            f"{step_ref!r}"
                        )

        if (
            len(hypothesis_ids)
            != len(
                set(hypothesis_ids)
            )
        ):
            errors.append(
                "candidate hypothesis_id "
                "values must be unique"
            )

        active_hypotheses = [
            hypothesis
            for hypothesis
            in document.get(
                "candidate_hypotheses",
                [],
            )
            if (
                hypothesis.get(
                    "status"
                )
                == "active"
            )
        ]

        status = document.get(
            "reconstruction_status"
        )

        if status == "no-convergence":

            if active_hypotheses:
                errors.append(
                    "no-convergence "
                    "reconstruction must not "
                    "contain active hypotheses"
                )

        else:

            if not active_hypotheses:
                errors.append(
                    f"{status} "
                    "reconstruction requires "
                    "at least one active "
                    "hypothesis"
                )

        if (
            status == "ambiguous"
            and len(
                active_hypotheses
            ) < 2
        ):
            errors.append(
                "ambiguous reconstruction "
                "requires at least two "
                "active hypotheses"
            )

        if status == "converged":

            if not any(
                hypothesis.get(
                    "meeting_points"
                )
                for hypothesis
                in active_hypotheses
            ):
                errors.append(
                    "converged reconstruction "
                    "requires at least one "
                    "active hypothesis with "
                    "a meeting point"
                )

    # -----------------------------------------------------------------------
    # temporal-precedence-assessment
    # -----------------------------------------------------------------------

    elif (
        record_type
        == "temporal-precedence-assessment"
    ):

        reconstruction_id = (
            document.get(
                "reconstruction_id"
            )
        )

        reconstruction = (
            reconstructions.get(
                reconstruction_id
            )
        )

        if reconstruction is None:
            errors.append(
                "unknown reconstruction_id: "
                f"{reconstruction_id!r}"
            )

            return errors

        hypotheses = (
            reconstruction_hypotheses(
                reconstruction
            )
        )

        hypothesis_id = (
            document.get(
                "hypothesis_id"
            )
        )

        if (
            hypothesis_id
            not in hypotheses
        ):
            errors.append(
                "unknown hypothesis_id: "
                f"{hypothesis_id!r}"
            )

        observation_id = (
            reconstruction.get(
                "observation_id"
            )
        )

        observation = (
            observations.get(
                observation_id
            )
        )

        known_evidence: set[str] = set()

        if observation is None:
            errors.append(
                "reconstruction references "
                "unknown observation_id: "
                f"{observation_id!r}"
            )

        else:
            known_evidence = (
                evidence_ids_for_observation(
                    observation
                )
            )

        events = document.get(
            "events",
            [],
        )

        event_ids = [
            event.get(
                "event_id"
            )
            for event
            in events
        ]

        if (
            len(event_ids)
            != len(
                set(event_ids)
            )
        ):
            errors.append(
                "temporal event_id "
                "values must be unique"
            )

        events_by_id = {
            event.get(
                "event_id"
            ): event
            for event
            in events
            if isinstance(
                event.get(
                    "event_id"
                ),
                str,
            )
        }

        for event in events:

            event_id = event.get(
                "event_id"
            )

            try:
                timing_bounds(
                    event.get(
                        "timing",
                        {},
                    )
                )

            except (
                KeyError,
                TypeError,
                ValueError,
            ) as exc:
                errors.append(
                    f"{event_id}: "
                    "invalid timing: "
                    f"{exc}"
                )

            for evidence_ref in (
                event.get(
                    "evidence_refs",
                    [],
                )
            ):
                if (
                    evidence_ref
                    not in known_evidence
                ):
                    errors.append(
                        f"{event_id}: "
                        "unknown evidence_ref "
                        f"{evidence_ref!r}"
                    )

        constraints = document.get(
            "precedence_constraints",
            [],
        )

        constraint_ids = [
            constraint.get(
                "constraint_id"
            )
            for constraint
            in constraints
        ]

        if (
            len(constraint_ids)
            != len(
                set(
                    constraint_ids
                )
            )
        ):
            errors.append(
                "constraint_id values "
                "must be unique"
            )

        results: dict[
            str,
            TemporalResult,
        ] = {}

        for constraint in constraints:

            constraint_id = (
                constraint.get(
                    "constraint_id"
                )
            )

            if not isinstance(
                constraint_id,
                str,
            ):
                continue

            (
                result,
                diagnostic,
            ) = (
                evaluate_precedence_constraint(
                    constraint,
                    events_by_id,
                )
            )

            results[
                constraint_id
            ] = result

            if diagnostic is not None:
                errors.append(
                    diagnostic
                )

            if result == "violated":
                errors.append(
                    f"{constraint_id}: "
                    "temporal precedence "
                    "is violated"
                )

        declared_violations = (
            document.get(
                "violations",
                [],
            )
        )

        violation_ids = [
            violation.get(
                "violation_id"
            )
            for violation
            in declared_violations
        ]

        if (
            len(violation_ids)
            != len(
                set(violation_ids)
            )
        ):
            errors.append(
                "violation_id values "
                "must be unique"
            )

        declared_violated_constraint_ids: (
            list[str]
        ) = []

        for violation in (
            declared_violations
        ):

            constraint_id = (
                violation.get(
                    "constraint_id"
                )
            )

            declared_violated_constraint_ids.append(
                constraint_id
            )

            if (
                constraint_id
                not in results
            ):
                errors.append(
                    "violation references "
                    "unknown constraint_id "
                    f"{constraint_id!r}"
                )

            for evidence_ref in (
                violation.get(
                    "evidence_refs",
                    [],
                )
            ):
                if (
                    evidence_ref
                    not in known_evidence
                ):
                    errors.append(
                        f"{violation.get('violation_id')}: "
                        "unknown evidence_ref "
                        f"{evidence_ref!r}"
                    )

        if (
            len(
                declared_violated_constraint_ids
            )
            != len(
                set(
                    declared_violated_constraint_ids
                )
            )
        ):
            errors.append(
                "each violated constraint "
                "may appear only once "
                "in violations"
            )

        expected_violated = {
            constraint_id
            for (
                constraint_id,
                result,
            )
            in results.items()
            if result == "violated"
        }

        declared_violated = set(
            declared_violated_constraint_ids
        )

        missing_violation_records = (
            expected_violated
            - declared_violated
        )

        unexpected_violation_records = (
            declared_violated
            - expected_violated
        )

        for constraint_id in sorted(
            missing_violation_records
        ):
            errors.append(
                f"{constraint_id}: "
                "violated constraint "
                "requires a violation record"
            )

        for constraint_id in sorted(
            unexpected_violation_records
        ):
            errors.append(
                f"{constraint_id}: "
                "violation record exists "
                "but constraint is not "
                "violated"
            )

        declared_unresolved_list = (
            document.get(
                "unresolved_constraints",
                [],
            )
        )

        declared_unresolved = set(
            declared_unresolved_list
        )

        if (
            len(
                declared_unresolved_list
            )
            != len(
                declared_unresolved
            )
        ):
            errors.append(
                "unresolved_constraints "
                "values must be unique"
            )

        unknown_unresolved = (
            declared_unresolved
            - set(results)
        )

        for constraint_id in sorted(
            unknown_unresolved
        ):
            errors.append(
                "unresolved_constraints "
                "references unknown "
                "constraint_id "
                f"{constraint_id!r}"
            )

        expected_unresolved = {
            constraint_id
            for (
                constraint_id,
                result,
            )
            in results.items()
            if result == "unresolved"
        }

        for constraint_id in sorted(
            expected_unresolved
            - declared_unresolved
        ):
            errors.append(
                f"{constraint_id}: "
                "unresolved constraint "
                "must be listed in "
                "unresolved_constraints"
            )

        for constraint_id in sorted(
            declared_unresolved
            - expected_unresolved
        ):
            if constraint_id in results:
                errors.append(
                    f"{constraint_id}: "
                    "listed as unresolved "
                    "but computed result is "
                    f"{results[constraint_id]!r}"
                )

        expected_status = (
            expected_temporal_status(
                results
            )
        )

        declared_status = (
            document.get(
                "assessment_status"
            )
        )

        if (
            declared_status
            != expected_status
        ):
            errors.append(
                "assessment_status "
                f"{declared_status!r} "
                "does not match computed "
                "temporal state "
                f"{expected_status!r}"
            )

    # -----------------------------------------------------------------------
    # hypothesis-comparison
    # -----------------------------------------------------------------------

    elif (
        record_type
        == "hypothesis-comparison"
    ):

        reconstruction_id = (
            document.get(
                "reconstruction_id"
            )
        )

        reconstruction = (
            reconstructions.get(
                reconstruction_id
            )
        )

        if reconstruction is None:
            errors.append(
                "unknown reconstruction_id: "
                f"{reconstruction_id!r}"
            )

            return errors

        hypotheses = (
            reconstruction_hypotheses(
                reconstruction
            )
        )

        active_ids = {
            hypothesis_id
            for (
                hypothesis_id,
                hypothesis,
            )
            in hypotheses.items()
            if (
                hypothesis.get(
                    "status"
                )
                == "active"
            )
        }

        entries = document.get(
            "entries",
            [],
        )

        compared_ids = [
            entry.get(
                "hypothesis_id"
            )
            for entry
            in entries
        ]

        if (
            len(compared_ids)
            != len(
                set(compared_ids)
            )
        ):
            errors.append(
                "comparison hypothesis_id "
                "values must be unique"
            )

        unknown_ids = (
            set(compared_ids)
            - set(hypotheses)
        )

        for hypothesis_id in sorted(
            unknown_ids
        ):
            errors.append(
                "comparison references "
                "unknown hypothesis "
                f"{hypothesis_id!r}"
            )

        if (
            set(compared_ids)
            != active_ids
        ):
            errors.append(
                "comparison must include "
                "every active hypothesis "
                "exactly once"
            )

        temporal_ids: list[str] = []

        for entry in entries:

            hypothesis_id = (
                entry.get(
                    "hypothesis_id"
                )
            )

            temporal_assessment_id = (
                entry.get(
                    "temporal_assessment_id"
                )
            )

            if isinstance(
                temporal_assessment_id,
                str,
            ):
                temporal_ids.append(
                    temporal_assessment_id
                )

            assessment = (
                temporal_assessments.get(
                    temporal_assessment_id
                )
            )

            if assessment is None:
                errors.append(
                    f"{hypothesis_id}: "
                    "unknown "
                    "temporal_assessment_id "
                    f"{temporal_assessment_id!r}"
                )
                continue

            if (
                assessment.get(
                    "reconstruction_id"
                )
                != reconstruction_id
            ):
                errors.append(
                    f"{hypothesis_id}: "
                    "temporal assessment "
                    "belongs to a different "
                    "reconstruction"
                )

            if (
                assessment.get(
                    "hypothesis_id"
                )
                != hypothesis_id
            ):
                errors.append(
                    f"{hypothesis_id}: "
                    "temporal assessment "
                    "belongs to hypothesis "
                    f"{assessment.get('hypothesis_id')!r}"
                )

        if (
            len(temporal_ids)
            != len(
                set(temporal_ids)
            )
        ):
            errors.append(
                "comparison "
                "temporal_assessment_id "
                "values must be unique"
            )

        ranks = [
            entry.get("rank")
            for entry
            in entries
        ]

        expected_ranks = list(
            range(
                1,
                len(entries) + 1,
            )
        )

        if (
            sorted(ranks)
            != expected_ranks
        ):
            errors.append(
                "comparison ranks must "
                "form the sequence "
                f"{expected_ranks}"
            )

        ranked_entries = sorted(
            entries,
            key=lambda entry: (
                entry.get(
                    "rank",
                    0,
                )
            ),
        )

        scores = [
            entry.get(
                "final_score"
            )
            for entry
            in ranked_entries
        ]

        if any(
            scores[index]
            < scores[index + 1]
            for index
            in range(
                len(scores) - 1
            )
        ):
            errors.append(
                "final_score must not "
                "increase as rank decreases"
            )

        margin = document.get(
            "selection_margin"
        )

        expected_margin: (
            float | None
        )

        if len(ranked_entries) >= 2:
            expected_margin = (
                ranked_entries[0][
                    "final_score"
                ]
                - ranked_entries[1][
                    "final_score"
                ]
            )

        else:
            expected_margin = None

        if expected_margin is None:

            if margin is not None:
                errors.append(
                    "selection_margin "
                    "must be null when "
                    "only one hypothesis "
                    "is compared"
                )

        else:

            if (
                margin is None
                or not math.isclose(
                    margin,
                    expected_margin,
                    rel_tol=1e-9,
                    abs_tol=1e-9,
                )
            ):
                errors.append(
                    "selection_margin "
                    "must equal the "
                    "difference between "
                    "rank 1 and rank 2 "
                    "final_score"
                )

        decision = document.get(
            "decision",
            {},
        )

        decision_status = (
            decision.get(
                "status"
            )
        )

        tie_threshold = (
            document.get(
                "tie_threshold"
            )
        )

        if (
            decision_status
            == "selected"
        ):

            selected_id = (
                decision.get(
                    "selected_hypothesis_id"
                )
            )

            if (
                selected_id
                not in compared_ids
            ):
                errors.append(
                    "selected_hypothesis_id "
                    "must reference a "
                    "compared hypothesis"
                )

            if ranked_entries:

                top_id = (
                    ranked_entries[0].get(
                        "hypothesis_id"
                    )
                )

                if (
                    selected_id
                    != top_id
                ):
                    errors.append(
                        "selected_hypothesis_id "
                        "must be the rank 1 "
                        "hypothesis"
                    )

            if (
                expected_margin
                is not None
                and expected_margin
                < tie_threshold
            ):
                errors.append(
                    "selected decision "
                    "is invalid because "
                    "the selection margin "
                    "is below tie_threshold"
                )

            selected_entry = next(
                (
                    entry
                    for entry
                    in entries
                    if (
                        entry.get(
                            "hypothesis_id"
                        )
                        == selected_id
                    )
                ),
                None,
            )

            if (
                selected_entry
                is not None
            ):
                assessment = (
                    temporal_assessments.get(
                        selected_entry.get(
                            "temporal_assessment_id"
                        )
                    )
                )

                if (
                    assessment
                    is not None
                    and assessment.get(
                        "assessment_status"
                    )
                    == "violated"
                ):
                    errors.append(
                        "selected hypothesis "
                        "must not have a "
                        "violated temporal "
                        "assessment"
                    )

        elif (
            decision_status
            == "ambiguous"
        ):

            if (
                len(ranked_entries)
                < 2
            ):
                errors.append(
                    "ambiguous decision "
                    "requires at least "
                    "two hypotheses"
                )

            elif (
                expected_margin
                is not None
                and expected_margin
                >= tie_threshold
            ):
                errors.append(
                    "ambiguous decision "
                    "is invalid because "
                    "the selection margin "
                    "is not below "
                    "tie_threshold"
                )

    # -----------------------------------------------------------------------
    # causal-validation
    # -----------------------------------------------------------------------

    elif (
        record_type
        == "causal-validation"
    ):

        reconstruction_id = (
            document.get(
                "reconstruction_id"
            )
        )

        reconstruction = (
            reconstructions.get(
                reconstruction_id
            )
        )

        if reconstruction is None:
            errors.append(
                "unknown reconstruction_id: "
                f"{reconstruction_id!r}"
            )

            return errors

        hypotheses = (
            reconstruction_hypotheses(
                reconstruction
            )
        )

        hypothesis_id = (
            document.get(
                "hypothesis_id"
            )
        )

        if (
            hypothesis_id
            not in hypotheses
        ):
            errors.append(
                "unknown hypothesis_id: "
                f"{hypothesis_id!r}"
            )

        observation_id = (
            reconstruction.get(
                "observation_id"
            )
        )

        observation = (
            observations.get(
                observation_id
            )
        )

        known_evidence: set[str] = set()

        if observation is None:
            errors.append(
                "reconstruction references "
                "unknown observation_id: "
                f"{observation_id!r}"
            )

        else:
            known_evidence = (
                evidence_ids_for_observation(
                    observation
                )
            )

        evidence_check_ids = [
            check.get(
                "check_id"
            )
            for check
            in document.get(
                "evidence_checks",
                [],
            )
        ]

        if (
            len(evidence_check_ids)
            != len(
                set(
                    evidence_check_ids
                )
            )
        ):
            errors.append(
                "evidence check_id "
                "values must be unique"
            )

        for evidence_check in (
            document.get(
                "evidence_checks",
                [],
            )
        ):

            evidence_ref = (
                evidence_check.get(
                    "evidence_ref"
                )
            )

            if (
                evidence_ref
                not in known_evidence
            ):
                errors.append(
                    f"{evidence_check.get('check_id')}: "
                    "unknown evidence_ref "
                    f"{evidence_ref!r}"
                )

        counterfactual_ids = [
            test.get(
                "test_id"
            )
            for test
            in document.get(
                "counterfactual_tests",
                [],
            )
        ]

        if (
            len(counterfactual_ids)
            != len(
                set(counterfactual_ids)
            )
        ):
            errors.append(
                "counterfactual test_id "
                "values must be unique"
            )

        for competing_id in (
            document.get(
                "competing_hypothesis_refs",
                [],
            )
        ):

            if (
                competing_id
                not in hypotheses
            ):
                errors.append(
                    "unknown competing "
                    "hypothesis "
                    f"{competing_id!r}"
                )

            if (
                competing_id
                == hypothesis_id
            ):
                errors.append(
                    "a hypothesis cannot "
                    "compete with itself"
                )

        temporal_assessment_id = (
            document.get(
                "temporal_assessment_id"
            )
        )

        temporal_assessment = (
            temporal_assessments.get(
                temporal_assessment_id
            )
        )

        if (
            temporal_assessment
            is None
        ):
            errors.append(
                "unknown "
                "temporal_assessment_id: "
                f"{temporal_assessment_id!r}"
            )

        else:

            if (
                temporal_assessment.get(
                    "reconstruction_id"
                )
                != reconstruction_id
            ):
                errors.append(
                    "temporal assessment "
                    "belongs to a different "
                    "reconstruction"
                )

            if (
                temporal_assessment.get(
                    "hypothesis_id"
                )
                != hypothesis_id
            ):
                errors.append(
                    "temporal assessment "
                    "belongs to a different "
                    "hypothesis"
                )

        comparison_id = document.get(
            "comparison_id"
        )

        if comparison_id is not None:

            comparison = (
                comparisons.get(
                    comparison_id
                )
            )

            if comparison is None:
                errors.append(
                    "unknown comparison_id: "
                    f"{comparison_id!r}"
                )

            elif (
                comparison.get(
                    "reconstruction_id"
                )
                != reconstruction_id
            ):
                errors.append(
                    "comparison belongs "
                    "to a different "
                    "reconstruction"
                )

        conclusion = document.get(
            "conclusion",
            {},
        )

        if (
            conclusion.get(
                "status"
            )
            == "supported"
        ):

            supporting_evidence = any(
                check.get(
                    "assessment"
                )
                == "supports"
                for check
                in document.get(
                    "evidence_checks",
                    [],
                )
            )

            if not supporting_evidence:
                errors.append(
                    "supported conclusion "
                    "requires at least one "
                    "supporting evidence check"
                )

            tests = document.get(
                "counterfactual_tests",
                [],
            )

            if not tests:
                errors.append(
                    "supported conclusion "
                    "requires at least one "
                    "counterfactual test"
                )

            elif not any(
                test.get(
                    "supports_hypothesis"
                )
                is True
                for test
                in tests
            ):
                errors.append(
                    "supported conclusion "
                    "requires at least one "
                    "supporting "
                    "counterfactual test"
                )

            if (
                temporal_assessment
                is None
                or temporal_assessment.get(
                    "assessment_status"
                )
                != "consistent"
            ):
                errors.append(
                    "supported conclusion "
                    "requires temporal "
                    "assessment status "
                    "'consistent'"
                )

    return errors


# ---------------------------------------------------------------------------
# Example validation runner
# ---------------------------------------------------------------------------


def validate_pass_examples(
    validators: dict[
        str,
        Draft202012Validator,
    ],
) -> tuple[
    list[dict[str, Any]],
    bool,
]:

    documents: list[
        dict[str, Any]
    ] = []

    success = True

    print(
        "\n[pass examples]\n"
    )

    paths = sorted(
        PASS_DIR.glob(
            "*.yaml"
        )
    )

    for path in paths:

        print(
            f"- "
            f"{path.relative_to(ROOT)}"
        )

        try:
            document = load_yaml(
                path
            )

        except Exception as exc:
            print(
                f"  [load-error] {exc}"
            )

            success = False
            continue

        errors = schema_errors(
            document,
            validators,
        )

        if errors:

            print(
                "  [schema-error]"
            )

            for error in errors:
                print(
                    f"    - {error}"
                )

            success = False
            continue

        print(
            "  [schema-ok]"
        )

        documents.append(
            document
        )

    registry = build_registry(
        documents
    )

    for document in documents:

        identifier = document_id(
            document
        )

        errors = semantic_errors(
            document,
            registry,
        )

        if errors:

            print(
                "  [semantic-error] "
                f"{identifier}"
            )

            for error in errors:
                print(
                    f"    - {error}"
                )

            success = False

        else:

            print(
                "  [semantic-ok] "
                f"{identifier}"
            )

    return (
        documents,
        success,
    )


def validate_fail_examples(
    validators: dict[
        str,
        Draft202012Validator,
    ],
    pass_documents: list[
        dict[str, Any]
    ],
) -> bool:

    success = True

    pass_registry = build_registry(
        pass_documents
    )

    print(
        "\n[fail examples]\n"
    )

    paths = sorted(
        FAIL_DIR.glob(
            "*.yaml"
        )
    )

    for path in paths:

        print(
            f"- "
            f"{path.relative_to(ROOT)}"
        )

        try:
            document = load_yaml(
                path
            )

        except Exception as exc:

            print(
                "  [expected-failure] "
                f"load-error: {exc}"
            )

            continue

        errors = schema_errors(
            document,
            validators,
        )

        if errors:

            print(
                "  "
                "[expected-schema-failure]"
            )

            for error in errors:
                print(
                    f"    - {error}"
                )

            continue

        semantic = semantic_errors(
            document,
            pass_registry,
        )

        if semantic:

            print(
                "  "
                "[expected-semantic-failure]"
            )

            for error in semantic:
                print(
                    f"    - {error}"
                )

            continue

        print(
            "  [unexpected-pass]"
        )

        success = False

    return success


def main() -> int:

    print(
        "=== Causal Trace "
        "Reconstruction Protocol "
        "v0.3 Validation ==="
    )

    try:
        validators = (
            load_validators()
        )

    except Exception as exc:

        print(
            "[fatal] failed to "
            "load schemas: "
            f"{exc}"
        )

        return 1

    for (
        record_type,
        filename,
    ) in SCHEMA_FILES.items():

        print(
            f"schema "
            f"[{record_type}]: "
            f"schemas/{filename}"
        )

    (
        pass_documents,
        pass_ok,
    ) = validate_pass_examples(
        validators
    )

    fail_ok = (
        validate_fail_examples(
            validators,
            pass_documents,
        )
    )

    if (
        pass_ok
        and fail_ok
    ):

        print(
            "\n[validation-ok]"
        )

        return 0

    print(
        "\n[validation-failed]"
    )

    return 1


if __name__ == "__main__":
    sys.exit(
        main()
    )
