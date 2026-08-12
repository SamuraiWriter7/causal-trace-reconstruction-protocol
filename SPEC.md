# Causal Trace Reconstruction Protocol Specification

**Protocol:** Causal Trace Reconstruction Protocol  
**Abbreviation:** CTRP  
**Version:** `0.5.0`  
**Status:** Minimum Complete Specification  
**Schema Dialect:** JSON Schema Draft 2020-12

---

## 1. Purpose

The Causal Trace Reconstruction Protocol (CTRP) defines a structured method for reconstructing, comparing, temporally evaluating, counterfactually testing, validating, auditing, and issuing receipts for incomplete causal reasoning paths.

CTRP is designed for situations where a system observes:

```text
Cause
  ↓
  ?
  ?
  ↓
Outcome
```

but does not possess a complete causal trace connecting the two.

The protocol provides explicit records for:

1. observation,
2. forward causal inference,
3. backward causal inference,
4. causal reconstruction,
5. temporal precedence evaluation,
6. competing hypothesis comparison,
7. counterfactual branching,
8. necessity and sufficiency assessment,
9. causal validation,
10. end-to-end workflow conformance,
11. final reconstruction receipt.

CTRP MUST preserve uncertainty.

CTRP MUST NOT silently convert reconstructed causal explanations into proven causal facts.

The foundational distinction is:

```text
Schema Validity
≠
Semantic Validity
≠
Workflow Conformance
≠
Proven Causality
```

---

# 2. Normative Language

The keywords:

- **MUST**
- **MUST NOT**
- **SHOULD**
- **SHOULD NOT**
- **MAY**

are normative requirements.

`MUST` and `MUST NOT` define mandatory protocol behavior.

`SHOULD` and `SHOULD NOT` define recommended behavior that may be overridden only with explicit justification.

`MAY` defines optional behavior.

---

# 3. Protocol Scope

CTRP specifies the structure and validation of reconstructed causal traces.

CTRP does not define:

- universal scientific proof,
- legal proof standards,
- ownership rights,
- economic settlement,
- royalty calculation,
- payment infrastructure,
- identity systems,
- cryptographic signature formats,
- model-training requirements.

CTRP MAY be embedded inside larger provenance, governance, audit, attribution, settlement, or royalty systems.

Example:

```text
Origin
  ↓
Trace
  ↓
Causal Reconstruction
  ↓
Audit
  ↓
Attribution
  ↓
Settlement
  ↓
Royalty
```

CTRP governs the causal reconstruction portion of such a pipeline.

---

# 4. Core Safety Principle

All causal reconstruction outputs MUST preserve the distinction between:

```text
Observed Fact
Inferred State
Candidate Hypothesis
Counterfactual Result
Validated Hypothesis
Proven Causality
```

A CTRP-compliant implementation MUST NOT treat these states as interchangeable.

The following statements are normative:

```text
Reconstruction ≠ Proof
Temporal Consistency ≠ Proof
Hypothesis Selection ≠ Proof
Counterfactual Support ≠ Proof
Necessity/Sufficiency Support ≠ Universal Law
Workflow Conformance ≠ Proof
Receipt Issuance ≠ Proof
```

Where `claim_level` is defined by a CTRP record, the value MUST remain:

```yaml
claim_level: hypothesis
```

unless a future protocol version explicitly defines another claim class.

---

# 5. Protocol Lifecycle

The complete CTRP v0.5 lifecycle is:

```text
Causal Observation
        ↓
 ┌──────┴──────┐
 ↓             ↓
Forward      Backward
Trace         Trace
 ↓             ↓
 └──────┬──────┘
        ↓
Causal Reconstruction
        ↓
Temporal Precedence Assessment
        ↓
Hypothesis Comparison
        ↓
Counterfactual Branching
        ↓
Necessity / Sufficiency Assessment
        ↓
Causal Validation
        ↓
CTRP Conformance Assessment
        ↓
Causal Reconstruction Receipt
```

The protocol stages are logically separated.

An implementation MAY generate records concurrently where dependencies allow, but MUST preserve the required reference relationships.

---

# 6. Record Types

CTRP v0.5 defines eleven primary record types:

```text
causal-observation
forward-trace
backward-trace
causal-reconstruction
temporal-precedence-assessment
hypothesis-comparison
counterfactual-branch
causal-necessity-sufficiency-assessment
causal-validation
ctrp-conformance-assessment
causal-reconstruction-receipt
```

Each record MUST:

- conform to its JSON Schema,
- declare `schema_version`,
- declare `record_type`,
- contain the identifier required by its schema,
- satisfy applicable semantic validation rules.

---

# 7. Versioning

All CTRP v0.5 records MUST declare:

```yaml
schema_version: "0.5.0"
```

Schemas MUST use a corresponding protocol identifier ending in:

```text
:0.5.0
```

A v0.5 semantic validator MUST NOT silently treat earlier schema versions as v0.5 records.

A migration process MAY convert older records, but the resulting migrated record MUST explicitly declare the new version.

---

# 8. Causal Observation

## 8.1 Purpose

`causal-observation` defines the observed causal context from which reconstruction begins.

It provides the authoritative evidence namespace for downstream trace records.

Conceptually:

```text
Observed Initial State
        ↓
Unknown Mechanism
        ↓
Observed Outcome
```

---

## 8.2 Identifier

A causal observation MUST contain:

```text
observation_id
```

The identifier MUST be unique within the validation scope.

---

## 8.3 Evidence

Evidence entries MUST contain unique `evidence_id` values within the observation.

Downstream records referencing evidence MUST reference evidence belonging to the appropriate source observation.

An implementation MUST reject unknown evidence references.

Evidence SHOULD distinguish observed data from inferred conclusions where the schema permits.

---

# 9. Forward Trace

## 9.1 Purpose

`forward-trace` represents cause-forward inference.

It asks:

> Given the known or proposed initiating condition, what downstream causal states are expected?

Conceptually:

```text
Cause
 ↓
State A
 ↓
State B
 ↓
Outcome
```

---

## 9.2 Observation Binding

Every forward trace MUST reference an existing:

```text
observation_id
```

The referenced observation defines the evidence namespace used by the trace.

---

## 9.3 Steps

Each forward trace step MUST have a unique `step_id` within the trace.

Evidence references in forward steps MUST resolve to evidence belonging to the referenced observation.

Forward traces MUST NOT reference evidence from unrelated observations unless a future extension explicitly defines cross-observation evidence binding.

---

# 10. Backward Trace

## 10.1 Purpose

`backward-trace` represents outcome-backward inference.

It asks:

> What prior states would be required or plausible for the observed outcome to occur?

Conceptually:

```text
Cause?
 ↑
Prior State?
 ↑
Required State?
 ↑
Observed Outcome
```

---

## 10.2 Observation Binding

Every backward trace MUST reference an existing causal observation.

---

## 10.3 Steps

Each backward step MUST have a unique `step_id`.

Evidence references MUST resolve to evidence belonging to the corresponding observation.

Backward inference MUST remain explicitly distinguishable from direct observation.

---

# 11. Causal Reconstruction

## 11.1 Purpose

`causal-reconstruction` reconciles forward and backward traces into one or more candidate causal hypotheses.

The reconstruction stage is the protocol's meet-in-the-middle layer.

```text
Forward Reasoning
       ↓
Possible State
       ↓
   Meeting Point
       ↑
Possible State
       ↑
Backward Reasoning
```

---

## 11.2 Trace References

A reconstruction MAY reference multiple:

```text
forward_trace_ids
backward_trace_ids
```

Every referenced forward and backward trace MUST exist.

Every referenced trace MUST belong to the same source observation as the reconstruction.

---

## 11.3 Candidate Hypotheses

A reconstruction MAY contain multiple candidate hypotheses.

Each candidate hypothesis MUST have a unique:

```text
hypothesis_id
```

within the reconstruction.

A hypothesis MAY contain:

- statement,
- meeting points,
- candidate causal path,
- evidence references,
- contradictions,
- unresolved gaps,
- confidence,
- status.

---

## 11.4 Evidence Integrity

Every evidence reference used by a candidate hypothesis MUST resolve to evidence from the reconstruction's source observation.

Contradiction evidence MUST obey the same requirement.

---

## 11.5 Meeting Points

Meeting points reconcile forward and backward reasoning.

A meeting point MUST reference valid forward and backward trace steps.

A meeting point MUST NOT reference unknown step identifiers.

A meeting point indicates structural convergence.

It does not establish causal proof.

---

## 11.6 Candidate Path

Candidate path segments MUST contain unique segment identifiers where defined.

Any `basis_step_refs` MUST resolve to known steps belonging to the forward or backward traces attached to the reconstruction.

---

## 11.7 Reconstruction Status

Permitted reconstruction states include:

```text
converged
partial
ambiguous
no-convergence
```

### `converged`

A converged reconstruction MUST contain at least one active hypothesis.

At least one active hypothesis SHOULD contain a meeting point.

The reference validator requires such a meeting point.

### `partial`

A partial reconstruction MUST contain at least one active hypothesis but MAY retain unresolved causal gaps.

### `ambiguous`

An ambiguous reconstruction MUST contain at least two active hypotheses.

### `no-convergence`

A `no-convergence` reconstruction MUST NOT contain active hypotheses.

---

## 11.8 Claim Level

Where the reconstruction schema defines a claim level, it MUST remain hypothesis-level.

A reconstruction MUST NOT declare the causal explanation proven merely because forward and backward traces converge.

---

# 12. Temporal Precedence Assessment

## 12.1 Purpose

`temporal-precedence-assessment` evaluates whether the candidate causal path is temporally possible.

The central requirement is:

> A cause cannot explain an effect if the required causal event occurs after the effect.

---

## 12.2 Hypothesis Binding

Every temporal assessment MUST reference:

```text
reconstruction_id
hypothesis_id
```

The hypothesis MUST exist within the referenced reconstruction.

---

## 12.3 Event Timing

Supported timing representations include:

```text
exact
interval
unknown
```

### Exact

```yaml
timing:
  kind: exact
  at: "2026-08-12T00:00:00Z"
```

### Interval

```yaml
timing:
  kind: interval
  earliest_at: "2026-08-12T00:00:00Z"
  latest_at: "2026-08-12T00:00:03Z"
```

The earliest value MUST NOT be later than the latest value.

### Unknown

```yaml
timing:
  kind: unknown
  rationale: Reliable timing evidence is unavailable.
```

Unknown timing MUST remain unresolved.

It MUST NOT be converted into an exact time by semantic validation.

---

# 13. Temporal Relations

CTRP v0.5 supports:

```text
strict-before
before-or-equal
```

For a cause interval:

```text
[cause_earliest, cause_latest]
```

and an effect interval:

```text
[effect_earliest, effect_latest]
```

the reference validator evaluates `strict-before` as follows.

### Satisfied

```text
cause_latest < effect_earliest
```

### Violated

```text
cause_earliest >= effect_latest
```

### Unresolved

All remaining overlap cases.

For `before-or-equal`:

### Satisfied

```text
cause_latest <= effect_earliest
```

### Violated

```text
cause_earliest > effect_latest
```

Otherwise:

```text
unresolved
```

---

# 14. Causal Windows

A precedence constraint MAY define:

```text
min_lag_seconds
max_lag_seconds
```

The minimum lag MUST NOT exceed the maximum lag.

The possible causal lag interval is:

```text
lag_min = effect_earliest - cause_latest
lag_max = effect_latest - cause_earliest
```

If the possible lag interval does not overlap the allowed causal window, the constraint MUST be treated as violated.

If the possible lag is fully contained within the window, it MAY be treated as satisfied.

Partial overlap MUST remain unresolved.

---

# 15. Temporal Assessment Status

Allowed temporal states include:

```text
consistent
partially-ordered
violated
insufficient-temporal-evidence
```

The reference semantic validator derives these states.

### `violated`

At least one precedence constraint is violated.

### `partially-ordered`

At least one constraint is satisfied, at least one remains unresolved, and none is violated.

### `insufficient-temporal-evidence`

No violation exists, but temporal evidence is insufficient to resolve the required ordering.

### `consistent`

All evaluated constraints are satisfied and none remain unresolved.

Declared assessment status MUST match the computed temporal state.

---

# 16. Temporal Violations

Every computed violated constraint MUST have a corresponding violation record where the schema requires violation tracking.

A violation record MUST NOT claim a constraint is violated if the validator computes that it is not.

Unresolved constraint identifiers MUST match the computed unresolved constraints.

---

# 17. Hypothesis Comparison

## 17.1 Purpose

`hypothesis-comparison` compares active candidate causal hypotheses.

CTRP does not assume that a single explanation must always win.

---

## 17.2 Coverage

Every active hypothesis in the referenced reconstruction MUST be included exactly once in the comparison.

Rejected or inactive hypotheses MAY be excluded according to implementation policy.

---

## 17.3 Comparison Factors

CTRP v0.5 comparison entries may include:

```text
path_coherence
evidence_support
temporal_consistency
contradiction_penalty
gap_penalty
final_score
rank
rationale
```

Each comparison entry MUST reference the relevant:

```text
temporal_assessment_id
```

The referenced temporal assessment MUST belong to the same reconstruction and hypothesis.

---

# 18. Comparison Ranking

Ranks MUST form a complete sequence:

```text
1, 2, ..., N
```

Final scores MUST NOT increase as rank decreases.

For two or more hypotheses:

```text
selection_margin
=
rank_1.final_score - rank_2.final_score
```

The declared margin MUST match the computed value within implementation tolerance.

---

# 19. Hypothesis Decision

Allowed decision states include:

```text
selected
ambiguous
insufficient-evidence
all-rejected
```

---

## 19.1 Selected

A `selected` decision MUST reference the rank-1 hypothesis.

A selected hypothesis MUST NOT possess a temporal assessment whose status is:

```text
violated
```

If the selection margin is below `tie_threshold`, the implementation MUST NOT select a winner.

---

## 19.2 Ambiguous

`ambiguous` requires at least two compared hypotheses.

If:

```text
selection_margin >= tie_threshold
```

then an ambiguous declaration is semantically invalid under the reference rules.

This prevents false ambiguity.

---

# 20. Counterfactual Branch

## 20.1 Purpose

`counterfactual-branch` represents an alternate causal world produced by intervention.

The branch MUST preserve:

- what was changed,
- which state was targeted,
- how the branch evolved,
- what assumptions were introduced,
- what evidence or simulation supported transitions,
- what outcome occurred or did not occur.

---

# 21. Counterfactual Test Types

Supported test types include:

```text
necessity
sufficiency
alternative-mechanism
```

---

## 21.1 Necessity

A necessity branch asks:

> If the candidate cause were removed or replaced, would the outcome disappear?

Conceptually:

```text
¬Cause
  ↓
Counterfactual Trace
  ↓
¬Effect ?
```

A necessity branch MUST use an intervention compatible with removing the proposed cause.

Under the reference validator:

```text
mode = suppress
or
mode = replace
```

is required.

A necessity branch using:

```text
mode = force
```

is semantically invalid.

---

## 21.2 Sufficiency

A sufficiency branch asks:

> If the candidate cause were forced into existence, would the outcome occur?

Conceptually:

```text
Cause
 ↓
Counterfactual Trace
 ↓
Effect ?
```

A sufficiency branch MUST use:

```text
mode = force
```

under the reference semantic rules.

---

# 22. Counterfactual Branch Completion

A branch whose:

```text
branch_status = completed
```

MUST NOT declare:

```text
counterfactual_outcome.occurrence = unknown
```

A completed branch is expected to resolve its declared counterfactual outcome.

Incomplete evidence SHOULD use an appropriate non-completed state rather than inventing a result.

---

# 23. Supporting Counterfactual Outcomes

When a completed necessity branch declares:

```text
branch_conclusion.assessment = supports-hypothesis
```

the counterfactual outcome SHOULD indicate that the target effect did not occur.

The reference validator requires:

```text
occurrence = not-occurred
```

For a completed supporting sufficiency branch, the reference validator requires:

```text
occurrence = occurred
```

---

# 24. Counterfactual Evidence

Counterfactual steps MAY be:

```text
observed
experimental
simulated
rule-based
model-inferred
mixed
```

Counterfactual results derived from simulation or inference MUST NOT be represented as direct observation.

Assumptions SHOULD be explicitly recorded.

---

# 25. Necessity / Sufficiency Assessment

## 25.1 Purpose

`causal-necessity-sufficiency-assessment` evaluates the causal role of a candidate factor within a declared scope.

---

## 25.2 Required Scope

Every assessment MUST include:

```text
evaluation_scope
```

The scope SHOULD clearly identify relevant:

- system configuration,
- environment,
- population,
- operating mode,
- time period,
- experimental conditions.

---

## 25.3 Claim Level

The assessment MUST declare:

```yaml
claim_level: hypothesis
```

This prevents scope-limited counterfactual support from becoming a universal causal law.

---

# 26. Necessity Status

Supported necessity states include:

```text
supported
not-supported
undetermined
not-tested
```

If necessity is declared:

```text
supported
```

the assessment MUST reference at least one necessity branch.

At least one referenced necessity branch MUST:

```text
test_type = necessity
branch_status = completed
branch_conclusion.assessment = supports-hypothesis
```

under the reference validator.

If necessity is:

```text
not-tested
```

the reference validator requires no `branch_refs`.

---

# 27. Sufficiency Status

The same rules apply symmetrically to sufficiency.

If:

```text
status = supported
```

at least one completed supporting sufficiency branch MUST be available.

---

# 28. Causal Role

Supported causal roles are:

```text
necessary-and-sufficient
necessary-only
sufficient-only
neither-supported
undetermined
```

The reference mapping is:

```text
necessity = supported
sufficiency = supported
→ necessary-and-sufficient
```

```text
necessity = supported
sufficiency = not-supported
→ necessary-only
```

```text
necessity = not-supported
sufficiency = supported
→ sufficient-only
```

```text
necessity = not-supported
sufficiency = not-supported
→ neither-supported
```

If either status is:

```text
undetermined
not-tested
```

and no more precise role follows, the causal role MUST be:

```text
undetermined
```

The declared role MUST match the status combination.

---

# 29. Causal Validation

## 29.1 Purpose

`causal-validation` evaluates one specific reconstructed causal hypothesis after supporting evidence and downstream assessments have been collected.

A validation MUST reference:

```text
reconstruction_id
hypothesis_id
temporal_assessment_id
necessity_sufficiency_assessment_id
```

It MAY reference:

```text
comparison_id
```

It MUST contain:

```text
evidence_checks
counterfactual_branch_refs
competing_hypothesis_refs
conclusion
```

according to the v0.5 schema.

---

# 30. Validation Reference Integrity

The referenced hypothesis MUST exist in the referenced reconstruction.

The temporal assessment MUST belong to the same reconstruction and hypothesis.

The necessity/sufficiency assessment MUST belong to the same reconstruction and hypothesis.

Counterfactual branches referenced by validation MUST belong to the same reconstruction and hypothesis.

If a comparison is supplied, it MUST belong to the same reconstruction.

---

# 31. Evidence Checks

Evidence checks MUST reference evidence from the reconstruction's source observation.

Evidence assessment states may include:

```text
supports
neutral
contradicts
unverifiable
```

Evidence checks MUST NOT reference unknown evidence identifiers.

---

# 32. Competing Hypotheses

`competing_hypothesis_refs` MUST reference hypotheses that exist within the same reconstruction.

A hypothesis MUST NOT list itself as a competing hypothesis.

---

# 33. Validation Conclusion

Supported conclusion states include:

```text
insufficient-evidence
plausible
supported
rejected
```

A validation status is an assessment of a hypothesis.

It is not a statement of universal causal truth.

---

# 34. Requirements for `supported`

Under the reference v0.5 semantic validator, a validation MUST NOT declare:

```text
supported
```

unless all of the following conditions are satisfied.

### 34.1 Supporting Evidence

At least one evidence check MUST have:

```text
assessment = supports
```

### 34.2 Temporal Consistency

The referenced temporal assessment MUST have:

```text
assessment_status = consistent
```

### 34.3 Counterfactual Support

At least one counterfactual branch MUST be referenced.

At least one referenced branch MUST be:

```text
branch_status = completed
branch_conclusion.assessment = supports-hypothesis
```

### 34.4 Causal Role Assessment

A valid necessity/sufficiency assessment MUST exist.

At least one of:

```text
necessity.status
sufficiency.status
```

MUST equal:

```text
supported
```

---

# 35. CTRP Conformance Assessment

## 35.1 Purpose

`ctrp-conformance-assessment` evaluates whether a causal workflow followed the required protocol stages.

It evaluates procedure.

It does not determine whether the causal claim is ultimately true.

---

# 36. Conformance Identity

A conformance assessment MUST reference:

```text
reconstruction_id
hypothesis_id
validation_id
```

All three MUST describe the same causal workflow.

The validation MUST belong to the referenced reconstruction and hypothesis.

---

# 37. Stage Checks

Supported stages include:

```text
observation
forward-trace
backward-trace
reconstruction
temporal-assessment
hypothesis-comparison
counterfactual-branching
necessity-sufficiency
causal-validation
```

Each stage check contains:

```text
stage
status
record_refs
rationale
```

Allowed stage states include:

```text
present
missing
not-required
invalid
```

A stage MUST appear at most once in a conformance assessment.

---

# 38. Core Required Stages

The reference validator defines the following as core required stages:

```text
observation
forward-trace
backward-trace
reconstruction
temporal-assessment
causal-validation
```

If a validation conclusion is:

```text
supported
```

the required stages expand to include:

```text
hypothesis-comparison
counterfactual-branching
necessity-sufficiency
```

Thus a supported end-to-end workflow requires all nine protocol stages represented by the conformance profile.

---

# 39. Stage Reference Integrity

If a stage declares:

```text
status = present
```

it MUST contain at least one `record_ref`.

A `present` stage reference MUST resolve to the expected record type and causal path.

For example:

```text
forward-trace
```

must reference a forward trace attached to the reconstruction.

A causal-validation stage MUST reference the validation identified by the conformance record.

A stage marked:

```text
missing
not-required
```

SHOULD NOT contain record references.

The reference validator rejects such references.

---

# 40. Bypass Prevention

CTRP v0.5 defines explicit bypass controls.

---

## CTRP-BYPASS-001

A causal validation MUST NOT exist outside a valid reconstruction path.

Conceptually:

```text
Validation
→ Reconstruction exists
```

---

## CTRP-BYPASS-002

A supported causal validation MUST NOT bypass temporal assessment.

---

## CTRP-BYPASS-003

A supported causal validation MUST NOT bypass counterfactual branching.

---

## CTRP-BYPASS-004

A supported causal validation MUST NOT bypass necessity/sufficiency assessment.

---

## CTRP-BYPASS-005

A supported final receipt MUST NOT be issued when the referenced conformance assessment is non-conformant.

This requirement is enforced at receipt validation.

---

## CTRP-BYPASS-006

A reconstructed causal hypothesis MUST NOT be promoted to proven causality.

A reconstruction used by the reference conformance validator is expected to retain:

```text
claim_level = hypothesis
```

where that field exists.

---

# 41. Reference Integrity Summary

The conformance assessment contains:

```text
reference_integrity.status
reference_integrity.checked_refs
reference_integrity.broken_refs
```

`checked_refs` MUST match the number of stage record references evaluated by the reference validator.

`broken_refs` MUST match the computed unresolved or invalid references.

If no broken references exist:

```text
status = valid
```

Otherwise:

```text
status = invalid
```

---

# 42. Conformance Status

Allowed statuses are:

```text
conformant
non-conformant
incomplete
```

The reference validator derives them as follows.

### Non-conformant

A workflow is non-conformant if any of the following occurs:

- an invalid stage is declared,
- a required bypass rule fails,
- broken references are detected.

### Incomplete

A workflow is incomplete when required stages are missing but no stronger structural violation requires `non-conformant`.

### Conformant

A workflow is conformant when:

- required stages are present,
- required stage references resolve,
- required bypass checks pass or are validly not applicable,
- no broken references remain.

A conformant assessment SHOULD have:

```yaml
blocking_issues: []
```

The reference validator requires this for conformant records.

---

# 43. Causal Reconstruction Receipt

## 43.1 Purpose

`causal-reconstruction-receipt` is the final audit-oriented record in a CTRP lifecycle.

It records what was concluded and how the workflow reached that conclusion.

It does not certify universal causal truth.

---

# 44. Receipt Identity

A receipt MUST reference:

```text
reconstruction_id
hypothesis_id
validation_id
conformance_id
```

These identifiers MUST belong to the same causal workflow.

The conformance assessment MUST reference the same validation.

---

# 45. Receipt Claim Level

A CTRP v0.5 final receipt MUST declare:

```yaml
claim_level: hypothesis
```

A value such as:

```yaml
claim_level: proven
```

is invalid.

---

# 46. Final Status

Receipt `final_status` MUST match:

```text
causal-validation.conclusion.status
```

For example:

```text
Validation = supported
Receipt    = supported
```

is valid.

The following is invalid:

```text
Validation = plausible
Receipt    = supported
```

A receipt MUST NOT promote a validation to a stronger final status.

---

# 47. Supported Receipt Requirement

If:

```text
final_status = supported
```

then the referenced conformance assessment MUST declare:

```text
conformance_status = conformant
```

A supported receipt MUST NOT be issued from:

```text
non-conformant
incomplete
```

workflow states under the reference rules.

---

# 48. Receipt Causal Role

Receipt:

```text
causal_role
```

MUST equal the causal role declared by the referenced necessity/sufficiency assessment used by the validation.

The receipt MUST NOT independently upgrade or alter the causal role.

---

# 49. Receipt Trace References

Receipt `trace_refs` MAY include:

- referenced forward traces,
- referenced backward traces,
- counterfactual branches attached to the validation.

Every trace reference MUST resolve.

Every trace reference MUST belong to the validated causal path.

---

# 50. Receipt Assessment References

Receipt `assessment_refs` MUST include the assessments required to reconstruct the final validation context.

The reference validator requires:

```text
validation_id
conformance_id
temporal_assessment_id
necessity_sufficiency_assessment_id
```

and, when present:

```text
comparison_id
```

Every listed assessment reference MUST resolve.

---

# 51. Remaining Uncertainty

A receipt SHOULD preserve unresolved uncertainty.

Examples include:

- unresolved timing precision,
- untested system conditions,
- unknown external mechanisms,
- limited experimental scope,
- simulator limitations,
- missing evidence.

An empty uncertainty list MUST NOT be interpreted as proof.

---

# 52. Validation Architecture

CTRP defines three machine-validation layers plus a separate epistemic claim layer.

```text
Layer 1
Schema Validation

Layer 2
Semantic Validation

Layer 3
Workflow Conformance

Layer 4
Causal Claim Interpretation
```

---

# 53. Schema Validation

JSON Schema validates:

- required fields,
- primitive types,
- enum membership,
- object structure,
- additional properties,
- numeric bounds,
- date-time format,
- version declarations.

Schema validity answers:

> Is this record structurally legal?

It does not answer:

> Is this causal reasoning coherent?

---

# 54. Semantic Validation

Semantic validation evaluates cross-record and logical relationships.

Examples include:

- evidence references resolve,
- traces share the correct observation,
- candidate paths reference valid steps,
- temporal ordering is coherent,
- comparison ranks are valid,
- tie thresholds are respected,
- necessity uses appropriate intervention,
- sufficiency uses appropriate intervention,
- causal role matches necessity/sufficiency statuses,
- validation references matching assessments.

Semantic validity answers:

> Do these records make sense together?

---

# 55. Workflow Conformance

Workflow conformance asks:

> Did this causal workflow pass through the required CTRP stages without forbidden shortcuts?

Conformance is stricter than record validity but weaker than causal proof.

---

# 56. Proven Causality

CTRP v0.5 does not define a universal proof-of-causality state.

Such proof may depend on domain-specific requirements including:

- randomized controlled experiments,
- scientific replication,
- formal verification,
- legal standards,
- physical measurement,
- independent reproduction.

CTRP therefore ends with an auditable hypothesis receipt rather than a universal proof certificate.

---

# 57. Fail Examples

Negative examples are normative test assets.

A CTRP implementation SHOULD include fail examples for conditions such as:

```text
invalid schema version
unknown evidence reference
unknown trace step
false ambiguity
invalid temporal ordering
missing temporal violation record
invalid necessity intervention
invalid sufficiency intervention
unsupported causal role
supported validation without counterfactual branch
supported validation without necessary assessments
broken conformance references
supported receipt from non-conformant workflow
receipt status stronger than validation status
receipt causal role mismatch
claim_level promoted to proven
```

A fail example is successful when the validator rejects it for the intended reason.

---

# 58. Pass Examples

Pass examples SHOULD demonstrate complete valid workflows.

The canonical thermal example may contain:

```text
obs-thermal-001
fwd-thermal-001
bwd-thermal-001
recon-thermal-002
temporal-thermal-001
temporal-workload-001
comparison-thermal-001
cf-thermal-necessity-001
cf-thermal-sufficiency-001
ns-thermal-001
validation-thermal-004
conformance-thermal-001
receipt-thermal-001
```

The identifier names are examples and are not protocol-reserved.

---

# 59. Canonical Thermal Example

A simplified example is:

```text
High Temperature
      ↓
Thermal Protection Activation
      ↓
Service Throttling
```

Candidate hypothesis:

```text
hypothesis.thermal-protection
```

Competing hypothesis:

```text
hypothesis.workload-saturation
```

The thermal hypothesis is evaluated through:

```text
Forward Trace
+
Backward Trace
+
Temporal Consistency
+
Hypothesis Comparison
+
Necessity Branch
+
Sufficiency Branch
+
Causal Role Assessment
+
Validation
+
Conformance
+
Receipt
```

Even if all stages are successful, the final claim remains:

```text
hypothesis
```

---

# 60. Ambiguity as a Valid Result

CTRP MUST NOT require a single causal winner when available evidence does not justify one.

The following are valid results:

```text
ambiguous
insufficient-evidence
undetermined
partial
```

An implementation SHOULD prefer explicit uncertainty over fabricated precision.

---

# 61. No Silent Gap Filling

When a causal path contains an unresolved gap, an implementation MUST NOT silently represent the missing transition as observed fact.

It MAY:

- infer a candidate transition,
- attach confidence,
- record assumptions,
- identify supporting evidence,
- preserve an unresolved gap.

---

# 62. No Silent Status Promotion

Status escalation MUST be traceable.

The following silent transformations are prohibited:

```text
plausible → supported
hypothesis → proven
incomplete → conformant
not-tested → supported
unknown → exact
```

unless the required new evidence or records exist and the protocol explicitly permits the transition.

---

# 63. Scope Discipline

All causal conclusions SHOULD preserve the context in which they were evaluated.

This is especially important for:

```text
necessity
sufficiency
counterfactual intervention
simulation
experimental conditions
```

A conclusion valid under one configuration MUST NOT automatically be generalized to all configurations.

---

# 64. Reference Direction

CTRP favors explicit downstream references.

Conceptually:

```text
Observation
    ↑
Trace
    ↑
Reconstruction
    ↑
Assessment
    ↑
Validation
    ↑
Conformance
    ↑
Receipt
```

Each later stage should preserve enough identifiers to reconstruct the provenance of its conclusion.

---

# 65. Immutability and Updates

CTRP does not require immutable storage.

However, implementations SHOULD NOT silently overwrite previously issued audit records.

Where records change materially, systems SHOULD issue:

- a new identifier,
- a new revision,
- or an explicit supersession record.

The history of causal reasoning SHOULD remain auditable.

---

# 66. Determinism

Schema validation SHOULD be deterministic.

Semantic validation SHOULD produce deterministic results when operating on the same record set and validator version.

Inference generation itself MAY be nondeterministic.

CTRP separates:

```text
Hypothesis Generation
```

from:

```text
Protocol Validation
```

to prevent model creativity from altering protocol constraints.

---

# 67. Implementation Independence

CTRP does not mandate a specific:

- language model,
- inference engine,
- programming language,
- database,
- storage network,
- agent framework,
- cloud provider.

A conformant implementation MAY use:

- LLMs,
- symbolic reasoning,
- rules,
- statistical models,
- simulations,
- human review,
- hybrid systems.

---

# 68. Security Considerations

Implementations SHOULD consider attacks including:

- fabricated evidence references,
- trace substitution,
- hypothesis identifier collision,
- temporal manipulation,
- counterfactual fabrication,
- branch omission,
- validation bypass,
- false conformance declaration,
- receipt status escalation.

A validator SHOULD treat referenced identifiers as untrusted until resolved.

---

# 69. Audit Considerations

A production CTRP system SHOULD preserve:

- record creation time,
- relevant version,
- reference graph,
- evidence identifiers,
- assumptions,
- unresolved gaps,
- contradictions,
- validation results,
- conformance results,
- final receipt.

Cryptographic signing MAY be added by an external provenance layer.

---

# 70. Privacy Considerations

CTRP records MAY contain sensitive evidence or causal descriptions.

Implementations SHOULD minimize unnecessary personal or confidential information.

References MAY be used instead of embedding raw evidence where appropriate.

CTRP itself does not define access control.

---

# 71. Interoperability

Stable record types and identifier references are intended to support interoperability.

Implementations SHOULD avoid embedding system-specific meaning into generic identifiers where that would prevent exchange.

Adapters MAY translate CTRP records into external audit or provenance formats.

---

# 72. Minimal Conformance Definition

An implementation MAY claim **CTRP v0.5 record compatibility** if it can parse and validate the v0.5 schemas.

An implementation MAY claim **CTRP v0.5 semantic compatibility** if it additionally implements the required semantic relationships.

An implementation MAY claim **CTRP v0.5 workflow conformance support** if it can evaluate the end-to-end conformance record and final receipt requirements.

These claims SHOULD be distinguished.

---

# 73. Reference Validator

The repository reference validator is:

```text
scripts/validate_examples.py
```

It validates:

```text
schemas/
examples/pass/
examples/fail/
```

The reference command is:

```bash
python scripts/validate_examples.py
```

A successful validation concludes with:

```text
[validation-ok]
```

---

# 74. Validation Failure

A validation run MUST return failure when:

- any pass example fails schema validation,
- any pass example fails semantic validation,
- any fail example unexpectedly passes.

Expected rejection of a fail example is considered success.

---

# 75. Evolution from v0.1 to v0.5

## v0.1

Defined:

```text
Observation
→ Forward Trace
→ Backward Trace
→ Reconstruction
→ Validation
```

Core principle:

```text
Reconstruction ≠ Proof
```

---

## v0.2

Added competing hypotheses and comparison.

```text
H1
H2
H3
 ↓
Comparison
 ↓
Selected / Ambiguous
```

Core principle:

```text
Do not force a winner.
```

---

## v0.3

Added temporal precedence.

```text
Cause
must occur
before
Effect
```

Core principle:

```text
Structural plausibility requires temporal possibility.
```

---

## v0.4

Added explicit counterfactual branches and causal role assessment.

```text
Cause removed
→ Effect?

Cause introduced
→ Effect?
```

Core principle:

```text
Test the world that did not occur.
```

---

## v0.5

Added workflow conformance and final receipts.

```text
Reasoning Path
→ Conformance
→ Receipt
```

Core principle:

```text
A conclusion must preserve the path by which it was reached.
```

---

# 76. Complete CTRP v0.5 Architecture

```text
                    ┌─────────────────────┐
                    │ Causal Observation  │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
             Forward Trace         Backward Trace
                    │                     │
                    └──────────┬──────────┘
                               ▼
                  Causal Reconstruction
                               │
                               ▼
              Temporal Precedence Assessment
                               │
                               ▼
                  Hypothesis Comparison
                               │
                               ▼
                 Counterfactual Branches
                     │                 │
                     ▼                 ▼
                Necessity         Sufficiency
                     └────────┬────────┘
                              ▼
            Necessity / Sufficiency Assessment
                              │
                              ▼
                     Causal Validation
                              │
                              ▼
                CTRP Conformance Assessment
                              │
                              ▼
               Causal Reconstruction Receipt
```

---

# 77. Formal Separation of Concerns

CTRP intentionally separates four questions.

## Question 1

```text
Is the record structurally valid?
```

Answer:

```text
JSON Schema Validation
```

## Question 2

```text
Do the referenced records and conclusions make logical sense?
```

Answer:

```text
Semantic Validation
```

## Question 3

```text
Did the workflow pass through the required causal reasoning stages?
```

Answer:

```text
CTRP Conformance
```

## Question 4

```text
Has causality been universally proven?
```

Answer in CTRP v0.5:

```text
Not determined by this protocol.
```

---

# 78. Final Normative Principles

A CTRP v0.5 implementation MUST preserve the following principles.

### Principle 1 — Evidence Traceability

Causal reasoning must remain connected to its evidence.

### Principle 2 — Bidirectional Reconstruction

Missing paths should be tested from both cause-forward and outcome-backward directions where applicable.

### Principle 3 — Alternative Preservation

Competing causal explanations must not be discarded without justification.

### Principle 4 — Temporal Validity

Effects must not precede the causes required to explain them.

### Principle 5 — Counterfactual Explicitness

Alternate causal worlds should be represented as traceable branches rather than opaque claims.

### Principle 6 — Scope-Limited Causal Roles

Necessity and sufficiency claims must remain bounded by evaluation scope.

### Principle 7 — No Validation Bypass

Strong causal support must not skip required protocol stages.

### Principle 8 — Receipt Integrity

A receipt must faithfully represent the validation and conformance state that produced it.

### Principle 9 — No Silent Promotion

Hypotheses must not become proof merely by passing protocol validation.

### Principle 10 — Uncertainty Preservation

Unknowns, contradictions, unresolved gaps, and scope limitations must remain visible.

---

# 79. Canonical CTRP Statement

CTRP can be summarized as:

> Reconstruct the missing causal path from both directions.  
> Preserve competing explanations.  
> Verify that causes precede effects.  
> Test alternate worlds through explicit interventions.  
> Assess necessity and sufficiency only within declared scope.  
> Validate the hypothesis without converting inference into proof.  
> Verify that no required reasoning stage was bypassed.  
> Issue an auditable receipt that preserves both the conclusion and its remaining uncertainty.

---

# 80. Protocol Boundary

The final CTRP v0.5 pipeline is:

```text
Observation
    ↓
Trace
    ↓
Reconstruction
    ↓
Comparison
    ↓
Temporal Verification
    ↓
Counterfactual Reconstruction
    ↓
Necessity / Sufficiency
    ↓
Validation
    ↓
Conformance
    ↓
Receipt
```

The protocol terminates at the receipt.

External systems MAY continue with:

```text
Receipt
  ↓
Audit
  ↓
Attribution
  ↓
Governance
  ↓
Settlement
  ↓
Royalty
```

but these later stages are outside the normative scope of CTRP v0.5.

---

# 81. Final Safety Statement

A CTRP-compliant system may conclude:

```text
This causal hypothesis is supported
within the evaluated scope
and the recorded CTRP workflow is conformant.
```

It MUST NOT infer from that statement alone:

```text
This causal relationship is universally proven.
```

Therefore the final invariant of CTRP v0.5 is:

```text
Schema Valid
        ≠
Semantic Valid
        ≠
Workflow Conformant
        ≠
Causality Proven
```

---

**End of Causal Trace Reconstruction Protocol Specification v0.5.0**
