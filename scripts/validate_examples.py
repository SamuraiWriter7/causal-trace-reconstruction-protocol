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

VERSION = "0.5.0"

SCHEMA_FILES = {
    "causal-observation": "causal-observation.schema.json",
    "forward-trace": "forward-trace.schema.json",
    "backward-trace": "backward-trace.schema.json",
    "causal-reconstruction": "causal-reconstruction.schema.json",
    "temporal-precedence-assessment": (
        "temporal-precedence-assessment.schema.json"
    ),
    "hypothesis-comparison": "hypothesis-comparison.schema.json",
    "counterfactual-branch": "counterfactual-branch.schema.json",
    "causal-necessity-sufficiency-assessment": (
        "causal-necessity-sufficiency-assessment.schema.json"
    ),
    "causal-validation": "causal-validation.schema.json",
    "ctrp-conformance-assessment": (
        "ctrp-conformance-assessment.schema.json"
    ),
    "causal-reconstruction-receipt": (
        "causal-reconstruction-receipt.schema.json"
    ),
}

TemporalResult = Literal[
    "satisfied",
    "unresolved",
    "violated",
]


STAGE_TO_RECORD_TYPE = {
    "observation": "causal-observation",
    "forward-trace": "forward-trace",
    "backward-trace": "backward-trace",
    "reconstruction": "causal-reconstruction",
    "temporal-assessment": "temporal-precedence-assessment",
    "hypothesis-comparison": "hypothesis-comparison",
    "counterfactual-branching": "counterfactual-branch",
    "necessity-sufficiency": (
        "causal-necessity-sufficiency-assessment"
    ),
    "causal-validation": "causal-validation",
}


CORE_REQUIRED_STAGES = {
    "observation",
    "forward-trace",
    "backward-trace",
    "reconstruction",
    "temporal-assessment",
    "causal-validation",
}


SUPPORTED_REQUIRED_STAGES = CORE_REQUIRED_STAGES.union(
    {
        "hypothesis-comparison",
        "counterfactual-branching",
        "necessity-sufficiency",
    }
)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_json(path: Path) -> dict[str, Any]:
    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        data = json.load(handle)

    if not isinstance(
        data,
        dict,
    ):
        raise ValueError(
            f"{path}: JSON root must be an object"
        )

    return data


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        data = yaml.safe_load(handle)

    if not isinstance(
        data,
        dict,
    ):
        raise ValueError(
            f"{path}: YAML root must be an object"
        )

    return data


# ---------------------------------------------------------------------------
# JSON Schema
# ---------------------------------------------------------------------------


def format_schema_error(
    error: Any,
) -> str:

    if error.absolute_path:
        location = ".".join(
            str(part)
            for part
            in error.absolute_path
        )
    else:
        location = "<root>"

    return (
        f"{location}: "
        f"{error.message}"
    )


def load_validators() -> dict[
    str,
    Draft202012Validator,
]:

    validators: dict[
        str,
        Draft202012Validator,
    ] = {}

    for (
        record_type,
        filename,
    ) in SCHEMA_FILES.items():

        schema_path = (
            SCHEMA_DIR
            / filename
        )

        schema = load_json(
            schema_path
        )

        Draft202012Validator.check_schema(
            schema
        )

        validators[
            record_type
        ] = Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
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
            "unknown record_type: "
            f"{record_type!r}"
        ]

    validator = validators[
        record_type
    ]

    errors = sorted(
        validator.iter_errors(
            document
        ),
        key=lambda error: [
            str(part)
            for part
            in error.absolute_path
        ],
    )

    return [
        format_schema_error(
            error
        )
        for error
        in errors
    ]


# ---------------------------------------------------------------------------
# Registry
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
        "counterfactual-branch":
            "branch_id",
        "causal-necessity-sufficiency-assessment":
            "assessment_id",
        "causal-validation":
            "validation_id",
        "ctrp-conformance-assessment":
            "conformance_id",
        "causal-reconstruction-receipt":
            "receipt_id",
    }

    key = key_by_type.get(
        record_type
    )

    if key is None:
        return None

    value = document.get(
        key
    )

    if isinstance(
        value,
        str,
    ):
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


def lookup_record(
    registry: dict[
        str,
        dict[
            str,
            dict[str, Any],
        ],
    ],
    record_type: str,
    identifier: str | None,
) -> dict[str, Any] | None:

    if identifier is None:
        return None

    return registry.get(
        record_type,
        {},
    ).get(
        identifier
    )


def reference_exists(
    registry: dict[
        str,
        dict[
            str,
            dict[str, Any],
        ],
    ],
    identifier: str,
) -> bool:

    for records in registry.values():
        if identifier in records:
            return True

    return False


# ---------------------------------------------------------------------------
# General helpers
# ---------------------------------------------------------------------------


def has_duplicates(
    values: list[Any],
) -> bool:

    return (
        len(values)
        != len(set(values))
    )


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

    for hypothesis in reconstruction.get(
        "candidate_hypotheses",
        [],
    ):

        hypothesis_id = hypothesis.get(
            "hypothesis_id"
        )

        if isinstance(
            hypothesis_id,
            str,
        ):
            result[
                hypothesis_id
            ] = hypothesis

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

    if value.endswith(
        "Z"
    ):
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
            timing[
                "earliest_at"
            ]
        )

        latest = parse_datetime(
            timing[
                "latest_at"
            ]
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
        "unknown timing kind: "
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

    if (
        relation
        == "before-or-equal"
    ):

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

    if (
        min_allowed
        > max_allowed
    ):
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

    constraint_id = constraint.get(
        "constraint_id"
    )

    cause_event_id = constraint.get(
        "cause_event_id"
    )

    effect_event_id = constraint.get(
        "effect_event_id"
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

    causal_window = constraint.get(
        "causal_window"
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
        satisfied_count > 0
        and unresolved_count > 0
    ):
        return "partially-ordered"

    if unresolved_count > 0:
        return (
            "insufficient-temporal-evidence"
        )

    return "consistent"


# ---------------------------------------------------------------------------
# Counterfactual / role helpers
# ---------------------------------------------------------------------------


def branch_supports_role(
    branch: dict[str, Any],
    expected_test_type: str,
) -> bool:

    return (
        branch.get(
            "test_type"
        )
        == expected_test_type
        and branch.get(
            "branch_status"
        )
        == "completed"
        and branch.get(
            "branch_conclusion",
            {},
        ).get(
            "assessment"
        )
        == "supports-hypothesis"
    )


def expected_causal_role(
    necessity_status: str | None,
    sufficiency_status: str | None,
) -> str:

    if (
        necessity_status
        == "supported"
        and sufficiency_status
        == "supported"
    ):
        return (
            "necessary-and-sufficient"
        )

    if (
        necessity_status
        == "supported"
        and sufficiency_status
        == "not-supported"
    ):
        return "necessary-only"

    if (
        necessity_status
        == "not-supported"
        and sufficiency_status
        == "supported"
    ):
        return "sufficient-only"

    if (
        necessity_status
        == "not-supported"
        and sufficiency_status
        == "not-supported"
    ):
        return "neither-supported"

    return "undetermined"


# ---------------------------------------------------------------------------
# Conformance helpers
# ---------------------------------------------------------------------------


def stage_reference_valid(
    stage: str,
    identifier: str,
    reconstruction: dict[str, Any],
    hypothesis_id: str,
    validation_id: str,
    registry: dict[
        str,
        dict[
            str,
            dict[str, Any],
        ],
    ],
) -> bool:

    expected_type = (
        STAGE_TO_RECORD_TYPE.get(
            stage
        )
    )

    if expected_type is None:
        return False

    record = lookup_record(
        registry,
        expected_type,
        identifier,
    )

    if record is None:
        return False

    reconstruction_id = reconstruction.get(
        "reconstruction_id"
    )

    if stage == "observation":
        return (
            identifier
            == reconstruction.get(
                "observation_id"
            )
        )

    if stage == "forward-trace":
        return (
            identifier
            in reconstruction.get(
                "forward_trace_ids",
                [],
            )
        )

    if stage == "backward-trace":
        return (
            identifier
            in reconstruction.get(
                "backward_trace_ids",
                [],
            )
        )

    if stage == "reconstruction":
        return (
            identifier
            == reconstruction_id
        )

    if stage == "causal-validation":
        return (
            identifier
            == validation_id
        )

    if record.get(
        "reconstruction_id"
    ) != reconstruction_id:
        return False

    if stage in {
        "temporal-assessment",
        "counterfactual-branching",
        "necessity-sufficiency",
    }:
        return (
            record.get(
                "hypothesis_id"
            )
            == hypothesis_id
        )

    return True


def expected_bypass_statuses(
    reconstruction: dict[str, Any],
    validation: dict[str, Any],
    temporal_assessments: dict[
        str,
        dict[str, Any],
    ],
    counterfactual_branches: dict[
        str,
        dict[str, Any],
    ],
    role_assessments: dict[
        str,
        dict[str, Any],
    ],
) -> dict[str, str]:

    result: dict[
        str,
        str,
    ] = {}

    result[
        "CTRP-BYPASS-001"
    ] = (
        "passed"
        if reconstruction
        else "failed"
    )

    supported = (
        validation.get(
            "conclusion",
            {},
        ).get(
            "status"
        )
        == "supported"
    )

    temporal_id = validation.get(
        "temporal_assessment_id"
    )

    if supported:
        result[
            "CTRP-BYPASS-002"
        ] = (
            "passed"
            if temporal_id
            in temporal_assessments
            else "failed"
        )
    else:
        result[
            "CTRP-BYPASS-002"
        ] = "not-applicable"

    branch_refs = validation.get(
        "counterfactual_branch_refs",
        [],
    )

    if supported:
        result[
            "CTRP-BYPASS-003"
        ] = (
            "passed"
            if (
                branch_refs
                and all(
                    ref
                    in counterfactual_branches
                    for ref
                    in branch_refs
                )
            )
            else "failed"
        )
    else:
        result[
            "CTRP-BYPASS-003"
        ] = "not-applicable"

    role_id = validation.get(
        "necessity_sufficiency_assessment_id"
    )

    if supported:
        result[
            "CTRP-BYPASS-004"
        ] = (
            "passed"
            if role_id
            in role_assessments
            else "failed"
        )
    else:
        result[
            "CTRP-BYPASS-004"
        ] = "not-applicable"

    result[
        "CTRP-BYPASS-006"
    ] = (
        "passed"
        if reconstruction.get(
            "claim_level"
        )
        == "hypothesis"
        else "failed"
    )

    return result


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

    temporal_assessments = registry.get(
        "temporal-precedence-assessment",
        {},
    )

    comparisons = registry.get(
        "hypothesis-comparison",
        {},
    )

    counterfactual_branches = registry.get(
        "counterfactual-branch",
        {},
    )

    role_assessments = registry.get(
        "causal-necessity-sufficiency-assessment",
        {},
    )

    validations = registry.get(
        "causal-validation",
        {},
    )

    conformances = registry.get(
        "ctrp-conformance-assessment",
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

        if has_duplicates(
            evidence_ids
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

        observation_id = document.get(
            "observation_id"
        )

        observation = observations.get(
            observation_id
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
            step.get(
                "step_id"
            )
            for step
            in document.get(
                "steps",
                [],
            )
        ]

        if has_duplicates(
            step_ids
        ):
            errors.append(
                "step_id values must be unique"
            )

        for step in document.get(
            "steps",
            [],
        ):

            step_id = step.get(
                "step_id"
            )

            for evidence_ref in step.get(
                "evidence_refs",
                [],
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

        observation_id = document.get(
            "observation_id"
        )

        observation = observations.get(
            observation_id
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
                    "unknown forward_trace_id: "
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
                    f"forward trace "
                    f"{trace_id!r} belongs "
                    "to a different observation"
                )

        for trace_id in backward_ids:

            trace = backward_traces.get(
                trace_id
            )

            if trace is None:
                errors.append(
                    "unknown backward_trace_id: "
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
                    f"backward trace "
                    f"{trace_id!r} belongs "
                    "to a different observation"
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

        known_evidence: set[str] = set()

        if observation is not None:
            known_evidence = (
                evidence_ids_for_observation(
                    observation
                )
            )

        hypothesis_ids: list[str] = []

        for hypothesis in document.get(
            "candidate_hypotheses",
            [],
        ):

            hypothesis_id = hypothesis.get(
                "hypothesis_id"
            )

            if isinstance(
                hypothesis_id,
                str,
            ):
                hypothesis_ids.append(
                    hypothesis_id
                )

            for evidence_ref in hypothesis.get(
                "evidence_refs",
                [],
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

            if has_duplicates(
                contradiction_ids
            ):
                errors.append(
                    f"{hypothesis_id}: "
                    "contradiction_id values "
                    "must be unique"
                )

            for contradiction in hypothesis.get(
                "contradictions",
                [],
            ):

                for evidence_ref in contradiction.get(
                    "evidence_refs",
                    [],
                ):

                    if (
                        evidence_ref
                        not in known_evidence
                    ):
                        errors.append(
                            f"{hypothesis_id}: "
                            "contradiction references "
                            "unknown evidence "
                            f"{evidence_ref!r}"
                        )

            meeting_point_ids = [
                meeting.get(
                    "meeting_point_id"
                )
                for meeting
                in hypothesis.get(
                    "meeting_points",
                    [],
                )
            ]

            if has_duplicates(
                meeting_point_ids
            ):
                errors.append(
                    f"{hypothesis_id}: "
                    "meeting_point_id values "
                    "must be unique"
                )

            for meeting in hypothesis.get(
                "meeting_points",
                [],
            ):

                forward_step_id = meeting.get(
                    "forward_step_id"
                )

                backward_step_id = meeting.get(
                    "backward_step_id"
                )

                if (
                    forward_step_id
                    not in forward_step_ids
                ):
                    errors.append(
                        f"{hypothesis_id}: "
                        "unknown forward_step_id "
                        f"{forward_step_id!r}"
                    )

                if (
                    backward_step_id
                    not in backward_step_ids
                ):
                    errors.append(
                        f"{hypothesis_id}: "
                        "unknown backward_step_id "
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

            if has_duplicates(
                segment_ids
            ):
                errors.append(
                    f"{hypothesis_id}: "
                    "segment_id values "
                    "must be unique"
                )

            for segment in hypothesis.get(
                "candidate_path",
                [],
            ):

                for step_ref in segment.get(
                    "basis_step_refs",
                    [],
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

        if has_duplicates(
            hypothesis_ids
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

        if (
            status
            == "no-convergence"
        ):

            if active_hypotheses:
                errors.append(
                    "no-convergence reconstruction "
                    "must not contain active "
                    "hypotheses"
                )

        else:

            if not active_hypotheses:
                errors.append(
                    f"{status} reconstruction "
                    "requires at least one "
                    "active hypothesis"
                )

        if (
            status
            == "ambiguous"
            and len(
                active_hypotheses
            ) < 2
        ):
            errors.append(
                "ambiguous reconstruction "
                "requires at least two "
                "active hypotheses"
            )

        if (
            status
            == "converged"
            and not any(
                hypothesis.get(
                    "meeting_points"
                )
                for hypothesis
                in active_hypotheses
            )
        ):
            errors.append(
                "converged reconstruction "
                "requires at least one active "
                "hypothesis with a meeting point"
            )

    # -----------------------------------------------------------------------
    # temporal-precedence-assessment
    # -----------------------------------------------------------------------

    elif (
        record_type
        == "temporal-precedence-assessment"
    ):

        reconstruction_id = document.get(
            "reconstruction_id"
        )

        reconstruction = reconstructions.get(
            reconstruction_id
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

        hypothesis_id = document.get(
            "hypothesis_id"
        )

        if (
            hypothesis_id
            not in hypotheses
        ):
            errors.append(
                "unknown hypothesis_id: "
                f"{hypothesis_id!r}"
            )

        observation_id = reconstruction.get(
            "observation_id"
        )

        observation = observations.get(
            observation_id
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

        if has_duplicates(
            event_ids
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

            for evidence_ref in event.get(
                "evidence_refs",
                [],
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

        if has_duplicates(
            constraint_ids
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

            constraint_id = constraint.get(
                "constraint_id"
            )

            if not isinstance(
                constraint_id,
                str,
            ):
                continue

            (
                result,
                diagnostic,
            ) = evaluate_precedence_constraint(
                constraint,
                events_by_id,
            )

            results[
                constraint_id
            ] = result

            if diagnostic is not None:
                errors.append(
                    diagnostic
                )

            if (
                result
                == "violated"
            ):
                errors.append(
                    f"{constraint_id}: "
                    "temporal precedence "
                    "is violated"
                )

        declared_violations = document.get(
            "violations",
            [],
        )

        violation_ids = [
            violation.get(
                "violation_id"
            )
            for violation
            in declared_violations
        ]

        if has_duplicates(
            violation_ids
        ):
            errors.append(
                "violation_id values "
                "must be unique"
            )

        declared_violated = {
            violation.get(
                "constraint_id"
            )
            for violation
            in declared_violations
        }

        expected_violated = {
            constraint_id
            for (
                constraint_id,
                result,
            )
            in results.items()
            if result == "violated"
        }

        for violation in declared_violations:

            violation_id = violation.get(
                "violation_id"
            )

            constraint_id = violation.get(
                "constraint_id"
            )

            if (
                constraint_id
                not in results
            ):
                errors.append(
                    f"{violation_id}: "
                    "unknown constraint_id "
                    f"{constraint_id!r}"
                )

            for evidence_ref in violation.get(
                "evidence_refs",
                [],
            ):

                if (
                    evidence_ref
                    not in known_evidence
                ):
                    errors.append(
                        f"{violation_id}: "
                        "unknown evidence_ref "
                        f"{evidence_ref!r}"
                    )

        for constraint_id in sorted(
            expected_violated
            - declared_violated
        ):
            errors.append(
                f"{constraint_id}: "
                "violated constraint requires "
                "a violation record"
            )

        for constraint_id in sorted(
            declared_violated
            - expected_violated
        ):
            errors.append(
                f"{constraint_id}: "
                "violation record exists but "
                "constraint is not violated"
            )

        declared_unresolved_list = document.get(
            "unresolved_constraints",
            [],
        )

        if has_duplicates(
            declared_unresolved_list
        ):
            errors.append(
                "unresolved_constraints "
                "values must be unique"
            )

        declared_unresolved = set(
            declared_unresolved_list
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
                "unresolved constraint must "
                "be listed in "
                "unresolved_constraints"
            )

        for constraint_id in sorted(
            declared_unresolved
            - expected_unresolved
        ):

            if constraint_id in results:
                errors.append(
                    f"{constraint_id}: "
                    "listed as unresolved but "
                    "computed result is "
                    f"{results[constraint_id]!r}"
                )

            else:
                errors.append(
                    "unresolved_constraints "
                    "references unknown "
                    "constraint_id "
                    f"{constraint_id!r}"
                )

        expected_status = (
            expected_temporal_status(
                results
            )
        )

        declared_status = document.get(
            "assessment_status"
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

        reconstruction_id = document.get(
            "reconstruction_id"
        )

        reconstruction = reconstructions.get(
            reconstruction_id
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

        if has_duplicates(
            compared_ids
        ):
            errors.append(
                "comparison hypothesis_id "
                "values must be unique"
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

            hypothesis_id = entry.get(
                "hypothesis_id"
            )

            if (
                hypothesis_id
                not in hypotheses
            ):
                errors.append(
                    "comparison references "
                    "unknown hypothesis "
                    f"{hypothesis_id!r}"
                )

            temporal_id = entry.get(
                "temporal_assessment_id"
            )

            if isinstance(
                temporal_id,
                str,
            ):
                temporal_ids.append(
                    temporal_id
                )

            assessment = (
                temporal_assessments.get(
                    temporal_id
                )
            )

            if assessment is None:
                errors.append(
                    f"{hypothesis_id}: "
                    "unknown "
                    "temporal_assessment_id "
                    f"{temporal_id!r}"
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
                    "belongs to a different "
                    "hypothesis"
                )

        if has_duplicates(
            temporal_ids
        ):
            errors.append(
                "comparison "
                "temporal_assessment_id "
                "values must be unique"
            )

        ranks = [
            entry.get(
                "rank"
            )
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
            key=lambda entry: entry.get(
                "rank",
                0,
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

        expected_margin: float | None

        if (
            len(ranked_entries)
            >= 2
        ):
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

        margin = document.get(
            "selection_margin"
        )

        if expected_margin is None:

            if margin is not None:
                errors.append(
                    "selection_margin must "
                    "be null when only one "
                    "hypothesis is compared"
                )

        elif (
            margin is None
            or not math.isclose(
                margin,
                expected_margin,
                rel_tol=1e-9,
                abs_tol=1e-9,
            )
        ):
            errors.append(
                "selection_margin must equal "
                "the difference between "
                "rank 1 and rank 2 "
                "final_score"
            )

        decision = document.get(
            "decision",
            {},
        )

        decision_status = decision.get(
            "status"
        )

        tie_threshold = document.get(
            "tie_threshold"
        )

        if (
            decision_status
            == "selected"
        ):

            selected_id = decision.get(
                "selected_hypothesis_id"
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

                top_id = ranked_entries[
                    0
                ].get(
                    "hypothesis_id"
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
                expected_margin is not None
                and expected_margin
                < tie_threshold
            ):
                errors.append(
                    "selected decision is "
                    "invalid because the "
                    "selection margin is below "
                    "tie_threshold"
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

            if selected_entry is not None:

                temporal_id = (
                    selected_entry.get(
                        "temporal_assessment_id"
                    )
                )

                assessment = (
                    temporal_assessments.get(
                        temporal_id
                    )
                )

                if (
                    assessment is not None
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
                expected_margin is not None
                and expected_margin
                >= tie_threshold
            ):
                errors.append(
                    "ambiguous decision is "
                    "invalid because the "
                    "selection margin is not "
                    "below tie_threshold"
                )

    # -----------------------------------------------------------------------
    # counterfactual-branch
    # -----------------------------------------------------------------------

    elif (
        record_type
        == "counterfactual-branch"
    ):

        reconstruction_id = document.get(
            "reconstruction_id"
        )

        reconstruction = reconstructions.get(
            reconstruction_id
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

        hypothesis_id = document.get(
            "hypothesis_id"
        )

        if (
            hypothesis_id
            not in hypotheses
        ):
            errors.append(
                "unknown hypothesis_id: "
                f"{hypothesis_id!r}"
            )

        temporal_id = document.get(
            "temporal_assessment_id"
        )

        temporal = (
            temporal_assessments.get(
                temporal_id
            )
        )

        if temporal is None:
            errors.append(
                "unknown "
                "temporal_assessment_id: "
                f"{temporal_id!r}"
            )

        else:

            if (
                temporal.get(
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
                temporal.get(
                    "hypothesis_id"
                )
                != hypothesis_id
            ):
                errors.append(
                    "temporal assessment "
                    "belongs to a different "
                    "hypothesis"
                )

        observation = observations.get(
            reconstruction.get(
                "observation_id"
            )
        )

        known_evidence: set[str] = set()

        if observation is not None:
            known_evidence = (
                evidence_ids_for_observation(
                    observation
                )
            )

        step_ids = [
            step.get(
                "step_id"
            )
            for step
            in document.get(
                "branch_steps",
                [],
            )
        ]

        if has_duplicates(
            step_ids
        ):
            errors.append(
                "counterfactual branch "
                "step_id values must "
                "be unique"
            )

        for step in document.get(
            "branch_steps",
            [],
        ):

            step_id = step.get(
                "step_id"
            )

            for evidence_ref in step.get(
                "evidence_refs",
                [],
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

        test_type = document.get(
            "test_type"
        )

        intervention_mode = document.get(
            "intervention",
            {},
        ).get(
            "mode"
        )

        if (
            test_type
            == "necessity"
            and intervention_mode
            not in {
                "suppress",
                "replace",
            }
        ):
            errors.append(
                "necessity branch must "
                "suppress or replace the "
                "candidate cause"
            )

        if (
            test_type
            == "sufficiency"
            and intervention_mode
            != "force"
        ):
            errors.append(
                "sufficiency branch must "
                "force the candidate cause"
            )

        branch_status = document.get(
            "branch_status"
        )

        outcome_occurrence = document.get(
            "counterfactual_outcome",
            {},
        ).get(
            "occurrence"
        )

        assessment = document.get(
            "branch_conclusion",
            {},
        ).get(
            "assessment"
        )

        if (
            branch_status
            == "completed"
            and outcome_occurrence
            == "unknown"
        ):
            errors.append(
                "completed counterfactual "
                "branch must not have an "
                "unknown counterfactual "
                "outcome"
            )

        if (
            branch_status
            == "completed"
            and assessment
            == "supports-hypothesis"
        ):

            if (
                test_type
                == "necessity"
                and outcome_occurrence
                != "not-occurred"
            ):
                errors.append(
                    "supporting necessity "
                    "branch requires the "
                    "counterfactual outcome "
                    "not to occur"
                )

            if (
                test_type
                == "sufficiency"
                and outcome_occurrence
                != "occurred"
            ):
                errors.append(
                    "supporting sufficiency "
                    "branch requires the "
                    "counterfactual outcome "
                    "to occur"
                )

    # -----------------------------------------------------------------------
    # causal-necessity-sufficiency-assessment
    # -----------------------------------------------------------------------

    elif (
        record_type
        == "causal-necessity-sufficiency-assessment"
    ):

        reconstruction_id = document.get(
            "reconstruction_id"
        )

        reconstruction = reconstructions.get(
            reconstruction_id
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

        hypothesis_id = document.get(
            "hypothesis_id"
        )

        if (
            hypothesis_id
            not in hypotheses
        ):
            errors.append(
                "unknown hypothesis_id: "
                f"{hypothesis_id!r}"
            )

        role_specs = (
            (
                "necessity",
                "necessity",
            ),
            (
                "sufficiency",
                "sufficiency",
            ),
        )

        for (
            field_name,
            expected_test_type,
        ) in role_specs:

            role_data = document.get(
                field_name,
                {},
            )

            role_status = role_data.get(
                "status"
            )

            branch_refs = role_data.get(
                "branch_refs",
                [],
            )

            if (
                role_status
                == "not-tested"
                and branch_refs
            ):
                errors.append(
                    f"{field_name} status "
                    "'not-tested' must not "
                    "contain branch_refs"
                )

            resolved: list[
                dict[str, Any]
            ] = []

            for branch_ref in branch_refs:

                branch = (
                    counterfactual_branches.get(
                        branch_ref
                    )
                )

                if branch is None:
                    errors.append(
                        f"{field_name}: "
                        "unknown branch_ref "
                        f"{branch_ref!r}"
                    )
                    continue

                resolved.append(
                    branch
                )

                if (
                    branch.get(
                        "reconstruction_id"
                    )
                    != reconstruction_id
                ):
                    errors.append(
                        f"{field_name}: "
                        f"branch {branch_ref!r} "
                        "belongs to a different "
                        "reconstruction"
                    )

                if (
                    branch.get(
                        "hypothesis_id"
                    )
                    != hypothesis_id
                ):
                    errors.append(
                        f"{field_name}: "
                        f"branch {branch_ref!r} "
                        "belongs to a different "
                        "hypothesis"
                    )

                if (
                    branch.get(
                        "test_type"
                    )
                    != expected_test_type
                ):
                    errors.append(
                        f"{field_name}: "
                        f"branch {branch_ref!r} "
                        "has incompatible "
                        "test_type "
                        f"{branch.get('test_type')!r}"
                    )

            if (
                role_status
                == "supported"
            ):

                if not branch_refs:
                    errors.append(
                        f"{field_name} status "
                        "'supported' requires "
                        "at least one branch_ref"
                    )

                elif not any(
                    branch_supports_role(
                        branch,
                        expected_test_type,
                    )
                    for branch
                    in resolved
                ):
                    errors.append(
                        f"{field_name} status "
                        "'supported' requires "
                        "at least one completed "
                        "supporting "
                        "counterfactual branch"
                    )

        necessity_status = document.get(
            "necessity",
            {},
        ).get(
            "status"
        )

        sufficiency_status = document.get(
            "sufficiency",
            {},
        ).get(
            "status"
        )

        expected_role = (
            expected_causal_role(
                necessity_status,
                sufficiency_status,
            )
        )

        declared_role = document.get(
            "causal_role"
        )

        if (
            declared_role
            != expected_role
        ):
            errors.append(
                "causal_role "
                f"{declared_role!r} "
                "is inconsistent with "
                "necessity/sufficiency "
                "statuses; expected "
                f"{expected_role!r}"
            )

    # -----------------------------------------------------------------------
    # causal-validation
    # -----------------------------------------------------------------------

    elif (
        record_type
        == "causal-validation"
    ):

        reconstruction_id = document.get(
            "reconstruction_id"
        )

        reconstruction = reconstructions.get(
            reconstruction_id
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

        hypothesis_id = document.get(
            "hypothesis_id"
        )

        if (
            hypothesis_id
            not in hypotheses
        ):
            errors.append(
                "unknown hypothesis_id: "
                f"{hypothesis_id!r}"
            )

        observation = observations.get(
            reconstruction.get(
                "observation_id"
            )
        )

        known_evidence: set[str] = set()

        if observation is not None:
            known_evidence = (
                evidence_ids_for_observation(
                    observation
                )
            )

        check_ids = [
            check.get(
                "check_id"
            )
            for check
            in document.get(
                "evidence_checks",
                [],
            )
        ]

        if has_duplicates(
            check_ids
        ):
            errors.append(
                "evidence check_id "
                "values must be unique"
            )

        for check in document.get(
            "evidence_checks",
            [],
        ):

            evidence_ref = check.get(
                "evidence_ref"
            )

            if (
                evidence_ref
                not in known_evidence
            ):
                errors.append(
                    f"{check.get('check_id')}: "
                    "unknown evidence_ref "
                    f"{evidence_ref!r}"
                )

        for competing_id in document.get(
            "competing_hypothesis_refs",
            [],
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

        temporal_id = document.get(
            "temporal_assessment_id"
        )

        temporal = (
            temporal_assessments.get(
                temporal_id
            )
        )

        if temporal is None:
            errors.append(
                "unknown "
                "temporal_assessment_id: "
                f"{temporal_id!r}"
            )

        else:

            if (
                temporal.get(
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
                temporal.get(
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

            comparison = comparisons.get(
                comparison_id
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
                    "comparison belongs to "
                    "a different reconstruction"
                )

        branch_refs = document.get(
            "counterfactual_branch_refs",
            [],
        )

        resolved_branches: list[
            dict[str, Any]
        ] = []

        for branch_ref in branch_refs:

            branch = (
                counterfactual_branches.get(
                    branch_ref
                )
            )

            if branch is None:
                errors.append(
                    "unknown "
                    "counterfactual_branch_ref: "
                    f"{branch_ref!r}"
                )
                continue

            resolved_branches.append(
                branch
            )

            if (
                branch.get(
                    "reconstruction_id"
                )
                != reconstruction_id
            ):
                errors.append(
                    "counterfactual branch "
                    f"{branch_ref!r} "
                    "belongs to a different "
                    "reconstruction"
                )

            if (
                branch.get(
                    "hypothesis_id"
                )
                != hypothesis_id
            ):
                errors.append(
                    "counterfactual branch "
                    f"{branch_ref!r} "
                    "belongs to a different "
                    "hypothesis"
                )

        role_id = document.get(
            "necessity_sufficiency_assessment_id"
        )

        role_assessment = (
            role_assessments.get(
                role_id
            )
        )

        if role_assessment is None:
            errors.append(
                "unknown "
                "necessity_sufficiency_assessment_id: "
                f"{role_id!r}"
            )

        else:

            if (
                role_assessment.get(
                    "reconstruction_id"
                )
                != reconstruction_id
            ):
                errors.append(
                    "necessity/sufficiency "
                    "assessment belongs to "
                    "a different reconstruction"
                )

            if (
                role_assessment.get(
                    "hypothesis_id"
                )
                != hypothesis_id
            ):
                errors.append(
                    "necessity/sufficiency "
                    "assessment belongs to "
                    "a different hypothesis"
                )

        conclusion_status = document.get(
            "conclusion",
            {},
        ).get(
            "status"
        )

        if (
            conclusion_status
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

            if (
                temporal is None
                or temporal.get(
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

            if not branch_refs:
                errors.append(
                    "supported conclusion "
                    "requires at least one "
                    "counterfactual branch"
                )

            elif not any(
                branch.get(
                    "branch_status"
                )
                == "completed"
                and branch.get(
                    "branch_conclusion",
                    {},
                ).get(
                    "assessment"
                )
                == "supports-hypothesis"
                for branch
                in resolved_branches
            ):
                errors.append(
                    "supported conclusion "
                    "requires at least one "
                    "completed supporting "
                    "counterfactual branch"
                )

            if role_assessment is None:
                errors.append(
                    "supported conclusion "
                    "requires a valid "
                    "necessity/sufficiency "
                    "assessment"
                )

            else:

                necessity_status = (
                    role_assessment.get(
                        "necessity",
                        {},
                    ).get(
                        "status"
                    )
                )

                sufficiency_status = (
                    role_assessment.get(
                        "sufficiency",
                        {},
                    ).get(
                        "status"
                    )
                )

                if (
                    necessity_status
                    != "supported"
                    and sufficiency_status
                    != "supported"
                ):
                    errors.append(
                        "supported conclusion "
                        "requires necessity or "
                        "sufficiency to be "
                        "supported"
                    )

    # -----------------------------------------------------------------------
    # ctrp-conformance-assessment
    # -----------------------------------------------------------------------

    elif (
        record_type
        == "ctrp-conformance-assessment"
    ):

        reconstruction_id = document.get(
            "reconstruction_id"
        )

        hypothesis_id = document.get(
            "hypothesis_id"
        )

        validation_id = document.get(
            "validation_id"
        )

        reconstruction = reconstructions.get(
            reconstruction_id
        )

        validation = validations.get(
            validation_id
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

        if (
            hypothesis_id
            not in hypotheses
        ):
            errors.append(
                "unknown hypothesis_id: "
                f"{hypothesis_id!r}"
            )

        if validation is None:
            errors.append(
                "unknown validation_id: "
                f"{validation_id!r}"
            )

            return errors

        if (
            validation.get(
                "reconstruction_id"
            )
            != reconstruction_id
        ):
            errors.append(
                "validation belongs to a "
                "different reconstruction"
            )

        if (
            validation.get(
                "hypothesis_id"
            )
            != hypothesis_id
        ):
            errors.append(
                "validation belongs to a "
                "different hypothesis"
            )

        stage_checks = document.get(
            "required_stage_checks",
            [],
        )

        stages = [
            check.get(
                "stage"
            )
            for check
            in stage_checks
        ]

        if has_duplicates(
            stages
        ):
            errors.append(
                "required stage checks "
                "must contain each stage "
                "at most once"
            )

        stage_map = {
            check.get(
                "stage"
            ): check
            for check
            in stage_checks
        }

        validation_status = validation.get(
            "conclusion",
            {},
        ).get(
            "status"
        )

        required_stages = set(
            CORE_REQUIRED_STAGES
        )

        if (
            validation_status
            == "supported"
        ):
            required_stages = set(
                SUPPORTED_REQUIRED_STAGES
            )

        broken_refs: set[str] = set()
        checked_ref_count = 0

        for stage, check in stage_map.items():

            status = check.get(
                "status"
            )

            refs = check.get(
                "record_refs",
                [],
            )

            checked_ref_count += len(
                refs
            )

            if (
                status == "present"
                and not refs
            ):
                errors.append(
                    f"stage {stage!r} "
                    "is present but contains "
                    "no record_refs"
                )

            if (
                status
                in {
                    "missing",
                    "not-required",
                }
                and refs
            ):
                errors.append(
                    f"stage {stage!r} "
                    f"with status {status!r} "
                    "must not contain "
                    "record_refs"
                )

            for ref in refs:

                if not reference_exists(
                    registry,
                    ref,
                ):
                    broken_refs.add(
                        ref
                    )
                    continue

                if not stage_reference_valid(
                    stage,
                    ref,
                    reconstruction,
                    hypothesis_id,
                    validation_id,
                    registry,
                ):
                    broken_refs.add(
                        ref
                    )

        for stage in sorted(
            required_stages
        ):

            check = stage_map.get(
                stage
            )

            if check is None:
                errors.append(
                    "required stage check "
                    f"{stage!r} is missing"
                )
                continue

            if (
                check.get(
                    "status"
                )
                != "present"
            ):
                errors.append(
                    f"required stage {stage!r} "
                    "must have status "
                    "'present'"
                )

        bypass_checks = document.get(
            "bypass_checks",
            [],
        )

        rule_ids = [
            check.get(
                "rule_id"
            )
            for check
            in bypass_checks
        ]

        if has_duplicates(
            rule_ids
        ):
            errors.append(
                "bypass rule_id values "
                "must be unique"
            )

        expected_bypass = (
            expected_bypass_statuses(
                reconstruction,
                validation,
                temporal_assessments,
                counterfactual_branches,
                role_assessments,
            )
        )

        declared_bypass = {
            check.get(
                "rule_id"
            ): check.get(
                "status"
            )
            for check
            in bypass_checks
        }

        for (
            rule_id,
            expected_status,
        ) in expected_bypass.items():

            if rule_id not in declared_bypass:
                errors.append(
                    "required bypass check "
                    f"{rule_id!r} is missing"
                )

                continue

            if (
                declared_bypass[
                    rule_id
                ]
                != expected_status
            ):
                errors.append(
                    f"{rule_id}: "
                    "declared status "
                    f"{declared_bypass[rule_id]!r} "
                    "does not match computed "
                    f"status {expected_status!r}"
                )

        reference_integrity = document.get(
            "reference_integrity",
            {},
        )

        declared_checked_refs = (
            reference_integrity.get(
                "checked_refs"
            )
        )

        declared_broken_refs = set(
            reference_integrity.get(
                "broken_refs",
                [],
            )
        )

        declared_ref_status = (
            reference_integrity.get(
                "status"
            )
        )

        if (
            declared_checked_refs
            != checked_ref_count
        ):
            errors.append(
                "reference_integrity."
                "checked_refs must equal "
                "the number of stage "
                "record_refs checked"
            )

        if (
            declared_broken_refs
            != broken_refs
        ):
            errors.append(
                "reference_integrity."
                "broken_refs does not match "
                "computed broken references"
            )

        expected_ref_status = (
            "valid"
            if not broken_refs
            else "invalid"
        )

        if (
            declared_ref_status
            != expected_ref_status
        ):
            errors.append(
                "reference_integrity.status "
                f"{declared_ref_status!r} "
                "does not match computed "
                f"status "
                f"{expected_ref_status!r}"
            )

        has_invalid_stage = any(
            check.get(
                "status"
            )
            == "invalid"
            for check
            in stage_checks
        )

        has_failed_bypass = any(
            status == "failed"
            for status
            in expected_bypass.values()
        )

        missing_required_stage = any(
            (
                stage not in stage_map
                or stage_map[
                    stage
                ].get(
                    "status"
                )
                != "present"
            )
            for stage
            in required_stages
        )

        if (
            has_invalid_stage
            or has_failed_bypass
            or broken_refs
        ):
            expected_conformance = (
                "non-conformant"
            )

        elif missing_required_stage:
            expected_conformance = (
                "incomplete"
            )

        else:
            expected_conformance = (
                "conformant"
            )

        declared_conformance = document.get(
            "conformance_status"
        )

        if (
            declared_conformance
            != expected_conformance
        ):
            errors.append(
                "conformance_status "
                f"{declared_conformance!r} "
                "does not match computed "
                "status "
                f"{expected_conformance!r}"
            )

        blocking_issues = document.get(
            "blocking_issues",
            [],
        )

        if (
            declared_conformance
            == "conformant"
            and blocking_issues
        ):
            errors.append(
                "conformant assessment "
                "must not contain "
                "blocking_issues"
            )

    # -----------------------------------------------------------------------
    # causal-reconstruction-receipt
    # -----------------------------------------------------------------------

    elif (
        record_type
        == "causal-reconstruction-receipt"
    ):

        reconstruction_id = document.get(
            "reconstruction_id"
        )

        hypothesis_id = document.get(
            "hypothesis_id"
        )

        validation_id = document.get(
            "validation_id"
        )

        conformance_id = document.get(
            "conformance_id"
        )

        reconstruction = reconstructions.get(
            reconstruction_id
        )

        validation = validations.get(
            validation_id
        )

        conformance = conformances.get(
            conformance_id
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

        if (
            hypothesis_id
            not in hypotheses
        ):
            errors.append(
                "unknown hypothesis_id: "
                f"{hypothesis_id!r}"
            )

        if validation is None:
            errors.append(
                "unknown validation_id: "
                f"{validation_id!r}"
            )

            return errors

        if conformance is None:
            errors.append(
                "unknown conformance_id: "
                f"{conformance_id!r}"
            )

            return errors

        if (
            validation.get(
                "reconstruction_id"
            )
            != reconstruction_id
        ):
            errors.append(
                "receipt validation belongs "
                "to a different reconstruction"
            )

        if (
            validation.get(
                "hypothesis_id"
            )
            != hypothesis_id
        ):
            errors.append(
                "receipt validation belongs "
                "to a different hypothesis"
            )

        if (
            conformance.get(
                "reconstruction_id"
            )
            != reconstruction_id
        ):
            errors.append(
                "receipt conformance "
                "assessment belongs to a "
                "different reconstruction"
            )

        if (
            conformance.get(
                "hypothesis_id"
            )
            != hypothesis_id
        ):
            errors.append(
                "receipt conformance "
                "assessment belongs to a "
                "different hypothesis"
            )

        if (
            conformance.get(
                "validation_id"
            )
            != validation_id
        ):
            errors.append(
                "receipt conformance "
                "assessment references a "
                "different validation"
            )

        validation_status = validation.get(
            "conclusion",
            {},
        ).get(
            "status"
        )

        final_status = document.get(
            "final_status"
        )

        if (
            final_status
            != validation_status
        ):
            errors.append(
                "receipt final_status must "
                "match causal validation "
                "conclusion status"
            )

        if (
            final_status
            == "supported"
            and conformance.get(
                "conformance_status"
            )
            != "conformant"
        ):
            errors.append(
                "supported receipt requires "
                "conformance_status "
                "'conformant'"
            )

        role_id = validation.get(
            "necessity_sufficiency_assessment_id"
        )

        role_assessment = (
            role_assessments.get(
                role_id
            )
        )

        if role_assessment is None:
            errors.append(
                "receipt cannot resolve "
                "necessity/sufficiency "
                "assessment from validation"
            )

        else:

            expected_role = (
                role_assessment.get(
                    "causal_role"
                )
            )

            declared_role = document.get(
                "causal_role"
            )

            if (
                declared_role
                != expected_role
            ):
                errors.append(
                    "receipt causal_role "
                    f"{declared_role!r} "
                    "does not match "
                    "necessity/sufficiency "
                    "assessment role "
                    f"{expected_role!r}"
                )

        trace_refs = document.get(
            "trace_refs",
            [],
        )

        allowed_trace_refs = set(
            reconstruction.get(
                "forward_trace_ids",
                [],
            )
        ).union(
            reconstruction.get(
                "backward_trace_ids",
                [],
            )
        ).union(
            validation.get(
                "counterfactual_branch_refs",
                [],
            )
        )

        for trace_ref in trace_refs:

            if (
                trace_ref
                not in allowed_trace_refs
            ):
                errors.append(
                    "receipt trace_ref "
                    f"{trace_ref!r} "
                    "is not part of the "
                    "validated causal path"
                )

            if not reference_exists(
                registry,
                trace_ref,
            ):
                errors.append(
                    "receipt trace_ref "
                    f"{trace_ref!r} "
                    "does not resolve"
                )

        assessment_refs = document.get(
            "assessment_refs",
            [],
        )

        required_assessment_refs = {
            validation_id,
            conformance_id,
            validation.get(
                "temporal_assessment_id"
            ),
            validation.get(
                "necessity_sufficiency_assessment_id"
            ),
        }

        comparison_id = validation.get(
            "comparison_id"
        )

        if comparison_id is not None:
            required_assessment_refs.add(
                comparison_id
            )

        required_assessment_refs.discard(
            None
        )

        missing_assessment_refs = (
            required_assessment_refs
            - set(
                assessment_refs
            )
        )

        for missing_ref in sorted(
            missing_assessment_refs
        ):
            errors.append(
                "receipt assessment_refs "
                "is missing required "
                f"reference {missing_ref!r}"
            )

        for assessment_ref in assessment_refs:

            if not reference_exists(
                registry,
                assessment_ref,
            ):
                errors.append(
                    "receipt assessment_ref "
                    f"{assessment_ref!r} "
                    "does not resolve"
                )

    return errors


# ---------------------------------------------------------------------------
# Pass examples
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
                f"  [semantic-error] "
                f"{identifier}"
            )

            for error in errors:
                print(
                    f"    - {error}"
                )

            success = False

        else:

            print(
                f"  [semantic-ok] "
                f"{identifier}"
            )

    return (
        documents,
        success,
    )


# ---------------------------------------------------------------------------
# Fail examples
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:

    print(
        "=== Causal Trace Reconstruction Protocol "
        "v0.5 Validation ==="
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
