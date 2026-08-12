# Changelog

All notable changes to the Causal Trace Reconstruction Protocol (CTRP) are documented in this file.

The protocol follows an iterative specification model.

```text
v0.1
→ v0.2
→ v0.3
→ v0.4
→ v0.5

The v0.5 release represents the first minimal end-to-end CTRP lifecycle.

[0.5.0] - 2026-08-12
Added

Introduced end-to-end CTRP workflow conformance.

Added two final protocol record types:

ctrp-conformance-assessment
causal-reconstruction-receipt
End-to-End Conformance

CTRP can now verify whether a causal reconstruction passed through the required reasoning and validation stages before a final result is issued.

Conformance assessment can cover:

causal observation
forward trace
backward trace
causal reconstruction
temporal precedence assessment
hypothesis comparison
counterfactual branching
necessity/sufficiency assessment
causal validation
Required Stage Checks

Added structured stage checks containing:

stage
status
record references
rationale

Supported stage statuses include:

present
missing
not-required
invalid
Reference Integrity

Added explicit end-to-end reference integrity assessment.

Conformance records can now report:

total checked references
broken references
reference integrity status
Bypass Prevention

Introduced explicit safeguards against causal reasoning shortcuts.

Representative rules include:

CTRP-BYPASS-001 — validation must not bypass causal reconstruction
CTRP-BYPASS-002 — supported validation must not bypass temporal assessment
CTRP-BYPASS-003 — supported validation must not bypass counterfactual branching
CTRP-BYPASS-004 — supported validation must not bypass necessity/sufficiency assessment
CTRP-BYPASS-005 — a supported final receipt must not originate from a non-conformant workflow
CTRP-BYPASS-006 — reconstructed causality must not be silently promoted to proven causality
Conformance Status

Added:

conformant
non-conformant
incomplete

The conformance layer evaluates protocol procedure, not ultimate causal truth.

Final Causal Reconstruction Receipt

Added causal-reconstruction-receipt.

The receipt records:

reconstruction reference
hypothesis reference
validation reference
conformance reference
final validation status
causal role
confidence
trace references
assessment references
remaining uncertainty
issuance time
Receipt Integrity

Added semantic validation requiring:

receipt reconstruction to match validation reconstruction
receipt hypothesis to match validation hypothesis
receipt conformance record to reference the same causal path
receipt final status to match validation conclusion
receipt causal role to match necessity/sufficiency assessment
trace references to resolve to the validated causal path
required assessment references to be present
Supported Receipt Safety

A receipt with:

final_status: supported

requires:

conformance_status: conformant
Claim Safety

Final receipts remain constrained to:

claim_level: hypothesis

A CTRP receipt is therefore not a proof-of-causality certificate.

Validation Model

v0.5 formalizes four distinct layers:

Schema Validity
≠
Semantic Validity
≠
Workflow Conformance
≠
Proven Causality
Core Lifecycle

v0.5 completes the minimum CTRP lifecycle:

Observation
→ Forward / Backward Trace
→ Reconstruction
→ Temporal Assessment
→ Hypothesis Comparison
→ Counterfactual Branching
→ Necessity / Sufficiency
→ Causal Validation
→ Conformance Assessment
→ Reconstruction Receipt
[0.4.0] - 2026-08-12
Added

Introduced structured counterfactual branch reconstruction.

Added:

counterfactual-branch
causal-necessity-sufficiency-assessment
Counterfactual Branching

Counterfactual tests are no longer represented only as compact validation fields.

Counterfactual reasoning can now be represented as explicit causal branches containing:

intervention
intervention target
baseline outcome
counterfactual trace steps
counterfactual outcome
evidence references
assumptions
branch conclusion
branch completion status
Necessity Testing

Introduced explicit necessity-oriented interventions.

A necessity branch asks whether suppressing or replacing the proposed causal factor prevents the predicted outcome.

Conceptually:

Cause removed
→ Alternate causal path
→ Outcome absent?
Sufficiency Testing

Introduced explicit sufficiency-oriented interventions.

A sufficiency branch asks whether forcing the proposed causal factor produces the predicted outcome.

Conceptually:

Cause introduced
→ Alternate causal path
→ Outcome occurs?
Intervention Validation

Added semantic validation for intervention direction.

Necessity branches must use an intervention compatible with removing or replacing the proposed cause.

Sufficiency branches must force the proposed causal condition.

Counterfactual Outcome Validation

Completed supporting branches now require outcomes consistent with the type of counterfactual test.

For example:

Necessity support
→ outcome should not occur after cause suppression

Sufficiency support
→ outcome should occur after cause introduction
Causal Role Assessment

Added structured necessity/sufficiency classification:

necessary-and-sufficient
necessary-only
sufficient-only
neither-supported
undetermined
Scope Safety

Added mandatory:

evaluation_scope
claim_level: hypothesis

for necessity and sufficiency assessment.

This prevents local experimental, simulated, or inferred findings from being interpreted as universal causal laws.

Causal Validation

Updated causal-validation.

The previous compact:

counterfactual_tests

representation was replaced by:

counterfactual_branch_refs
necessity_sufficiency_assessment_id
Supported Validation

A supported causal validation now requires:

supporting evidence
consistent temporal assessment
at least one completed supporting counterfactual branch
a valid necessity/sufficiency assessment
necessity or sufficiency support
Core Principle

v0.4 extends CTRP from:

Does the causal hypothesis fit the observed world?

to:

What changes when the proposed cause is removed,
introduced, replaced, or held constant?

Counterfactual support remains hypothesis-level evidence rather than causal proof.

[0.3.0] - 2026-08-12
Added

Introduced Temporal Causal Reconstruction.

Added:

temporal-precedence-assessment
Temporal Precedence

CTRP can now test whether the proposed causal sequence is compatible with observed or inferred time ordering.

Core rule:

A cause cannot explain an effect if the required cause occurs after the effect.
Timing Models

Added support for:

exact timestamps
temporal intervals
unknown timing
Exact Timing

Example:

timing:
  kind: exact
  at: "2026-08-12T00:00:00Z"
Interval Timing

Example:

timing:
  kind: interval
  earliest_at: "2026-08-12T00:00:00Z"
  latest_at: "2026-08-12T00:00:03Z"
Unknown Timing

Example:

timing:
  kind: unknown
  rationale: No reliable timing evidence is available.
Precedence Relations

Added:

strict-before
before-or-equal
Causal Windows

Added optional causal lag constraints:

min_lag_seconds
max_lag_seconds

This allows CTRP to distinguish between merely correct ordering and temporally plausible causal transmission.

Temporal Assessment Status

Added:

consistent
partially-ordered
violated
insufficient-temporal-evidence
Temporal Semantic Validation

The validator now computes temporal states from event bounds.

For strict-before:

cause_latest < effect_earliest
→ satisfied
cause_earliest >= effect_latest
→ violated

Otherwise:

unresolved
Causal Window Evaluation

The validator also evaluates the possible lag interval between cause and effect.

Temporal uncertainty is preserved when timing intervals overlap only partially with the permitted causal window.

Hypothesis Comparison

Added temporal references to hypothesis comparison entries:

temporal_assessment_id
temporal_consistency
Supported Validation

A supported conclusion now requires temporal assessment status:

consistent
Negative Validation Example

Added a reversed-cause example demonstrating rejection of a causal explanation whose proposed cause occurs after its effect.

Core Principle

v0.3 adds:

Plausible structure
+
Valid temporal order

as a prerequisite for stronger causal support.

[0.2.0] - 2026-08-12
Added

Expanded CTRP from a single reconstructed hypothesis to multiple competing causal hypotheses.

Added:

hypothesis-comparison
Multiple Candidate Hypotheses

causal-reconstruction now supports:

multiple forward traces
multiple backward traces
multiple candidate causal hypotheses

Each candidate hypothesis can contain:

hypothesis identifier
statement
meeting points
candidate causal path
evidence references
contradictions
unresolved gaps
confidence
active/rejected status
Reconstruction Status

Added:

converged
partial
ambiguous
no-convergence
Hypothesis Comparison

Added structured comparison fields including:

path coherence
evidence support
contradiction penalty
gap penalty
final score
rank
rationale
Decision Outcomes

Added:

selected
ambiguous
insufficient-evidence
all-rejected
Tie Threshold

Introduced explicit tie_threshold.

A hypothesis comparison is allowed to return:

ambiguous

when competing explanations are too close to justify selecting a winner.

Selection Margin

Added selection_margin.

For two leading hypotheses:

selection_margin
=
rank_1_score - rank_2_score
Semantic Comparison Validation

The validator checks:

every active hypothesis is compared exactly once
hypothesis identifiers resolve
ranks are complete and unique
final scores follow rank order
selection margin matches the score difference
selected hypothesis is rank 1
false ambiguity is rejected
unjustified winner selection is rejected
Causal Validation

Validation now targets a specific:

hypothesis_id

rather than only the reconstruction as a whole.

Added competing hypothesis references.

Core Principle

v0.2 formalizes:

Do not force a winner when the evidence does not justify one.

Ambiguity is treated as a valid causal reasoning result.

[0.1.0] - 2026-08-12
Added

Introduced the initial Causal Trace Reconstruction Protocol.

Core Pipeline

Defined the minimum reconstruction lifecycle:

Observation
→ Forward Trace
→ Backward Trace
→ Reconstruction
→ Validation
Causal Observation

Added causal-observation.

The record captures:

observed causal context
origin state
outcome state
supporting evidence
Forward Trace

Added forward-trace.

Forward trace reasoning begins from a known or observed initiating state and predicts possible downstream causal transitions.

Backward Trace

Added backward-trace.

Backward trace reasoning begins from an observed outcome and reconstructs possible required prior states.

Meet-in-the-Middle Reconstruction

Added causal-reconstruction.

Forward and backward reasoning traces may converge at one or more meeting points.

This creates an explicit candidate causal path instead of silently filling missing causal information.

Causal Validation

Added causal-validation.

Validation initially evaluated:

evidence support
reconstructed causal path
counterfactual checks
remaining uncertainty
Claim Safety

Introduced the foundational restriction:

claim_level: hypothesis

The protocol does not permit reconstructed causality to be represented as automatically proven.

Semantic Validation

Introduced Python-based semantic validation in addition to JSON Schema validation.

The validator checks relationships including:

observation references
evidence references
trace references
reconstruction references
candidate path consistency
Pass and Fail Examples

Introduced explicit positive and negative examples.

Fail examples are treated as part of the protocol definition.

Core Principle

The initial CTRP principle is:

Reconstruction ≠ Proof

A missing causal path may be reconstructed, evaluated, challenged, and audited without converting inference into certainty.

Protocol Evolution Summary

The development path from v0.1 through v0.5 is:

v0.1
Reconstruct the missing causal path.

v0.2
Compare competing causal explanations.

v0.3
Verify temporal causal order.

v0.4
Construct and evaluate counterfactual worlds.

v0.5
Verify the full reasoning workflow and issue an auditable receipt.

The resulting minimum architecture is:

Observation
    ↓
Forward + Backward Trace
    ↓
Causal Reconstruction
    ↓
Temporal Assessment
    ↓
Hypothesis Comparison
    ↓
Counterfactual Branching
    ↓
Necessity / Sufficiency
    ↓
Causal Validation
    ↓
Workflow Conformance
    ↓
Final Receipt

The protocol maintains the distinction:

Schema Valid
≠
Semantic Valid
≠
Workflow Conformant
≠
Causality Proven
