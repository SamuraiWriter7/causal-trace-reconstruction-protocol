# Causal Trace Reconstruction Protocol Specification

Version: 0.1.0

## 1. Scope

Causal Trace Reconstruction Protocol (CTRP) specifies a structured method
for representing missing causal-path reconstruction.

The protocol begins with:

1. a known origin,
2. a known outcome,
3. zero or more partially known intermediate states,
4. available evidence.

It then represents:

1. forward causal inference,
2. backward causal inference,
3. reconciliation,
4. hypothesis construction,
5. validation.

CTRP does not define a universal causal inference algorithm.

It defines the records through which such reasoning may be exchanged,
audited, and evaluated.

---

# 2. Normative Language

The terms MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are used
in their conventional standards-document sense.

---

# 3. Conceptual Model

The minimal CTRP model is:

```text
O = known origin
R = known outcome

F(O) = forward inference from origin
B(R) = backward inference from outcome

M = meeting region between F(O) and B(R)

H = reconstructed causal hypothesis

V(H) = validation of H

Conceptually:

F(O) ∩ B(R) → M
M → H
V(H) → assessment

The meeting region does not need to consist of one exact state.

It MAY consist of:

one matching state,
one matching mechanism,
a compatible state transition,
several partially compatible states.
4. Record Types

CTRP v0.1 defines five record types.

causal-observation
forward-trace
backward-trace
causal-reconstruction
causal-validation

All records MUST contain:

schema_version: "0.1.0"
record_type: ...
5. Causal Observation

A Causal Observation defines the reconstruction boundary.

It MUST contain:

observation identifier
known origin state
known outcome state
available evidence
recording timestamp

The origin represents the earliest known state relevant to the reconstruction.

The outcome represents the later state that requires explanation.

Neither field means that every causal process between the two is known.

6. Forward Trace

A Forward Trace represents reasoning from a known origin toward later states.

Its direction MUST be:

direction: cause-forward

Each forward step MUST identify:

previous state
next inferred or observed state
proposed mechanism
inference basis
confidence
evidence references

Example:

High Temperature
      ↓
Protection Controller Activated
      ↓
Service Throttling

Forward steps MAY contain assumptions.

Inference basis MAY be:

observed
rule-based
statistical
analogical
model-inferred
mixed
7. Backward Trace

A Backward Trace represents reasoning from a known outcome toward states
that would have been required or likely before that outcome.

Its direction MUST be:

direction: outcome-backward

Example:

Service Throttling
      ↑
Protection Controller Required
      ↑
Thermal Threshold Exceeded

Backward reasoning MUST NOT automatically be interpreted as evidence that
the required predecessor actually occurred.

It is an inferential requirement or candidate predecessor until validated.

8. Independent Trace Principle

Forward and backward traces SHOULD be generated independently where practical.

A system SHOULD avoid forcing one trace to conform to the other during
initial generation.

This preserves the value of meet-in-the-middle reconciliation.

The protocol therefore distinguishes:

generate

from:

reconcile
9. Reconciliation

A Causal Reconstruction compares one Forward Trace with one Backward Trace.

The reconciliation process SHOULD search for:

matching states
compatible states
matching mechanisms
compatible transitions
contradictions
unresolved gaps

One or more meeting points MAY be recorded.

Each meeting point contains a match score between:

0.0

and:

1.0

The score represents compatibility, not causal proof.

10. Reconstruction Status

A reconstruction MUST use one of:

converged
partial
no-convergence
converged

Forward and backward traces contain a sufficiently compatible meeting region.

partial

Some compatible states or mechanisms exist, but material causal gaps remain.

no-convergence

The traces cannot currently be reconciled into a coherent candidate path.

A no-convergence result is valid and SHOULD NOT be transformed into
a fabricated narrative merely to produce an answer.

11. Claim Level

Every Causal Reconstruction in CTRP v0.1 MUST contain:

claim_level: hypothesis

No other value is permitted.

Specifically:

claim_level: proven

is invalid.

This is a protocol-level safeguard against converting generated explanations
into claims of established causality.

12. Confidence

Confidence scores use:

0.0 <= confidence <= 1.0

Confidence represents the system's assessed strength of the inference.

Confidence MUST NOT be interpreted as a statistical probability unless
the implementation explicitly defines it as such.

13. Evidence References

Inference steps SHOULD reference evidence from the corresponding
Causal Observation.

Example:

evidence_refs:
  - ev-001
  - ev-002

A referenced evidence identifier SHOULD exist in the source observation.

Evidence references support traceability but do not independently establish
causal validity.

14. Counterfactual Validation

Causal Validation MAY contain one or more counterfactual tests.

A counterfactual asks conceptually:

If the proposed causal factor had been absent or altered,
would the predicted outcome still have occurred?

Example:

Observed:
High temperature → protection → throttling

Counterfactual:
Temperature below threshold

Expected:
Protection does not activate

A hypothesis classified as supported SHOULD contain at least one meaningful
counterfactual test unless counterfactual testing is impossible
and the limitation is explicitly recorded.

The reference validator for v0.1 requires at least one supporting
counterfactual test for supported.

15. Competing Hypotheses

Validation MAY contain alternative causal explanations.

Example:

H1:
Thermal protection caused throttling

H2:
Workload saturation caused throttling

A causal reconstruction system SHOULD preserve meaningful alternative
hypotheses instead of deleting them simply because one explanation
currently has higher confidence.

16. Validation Status

A validation conclusion MUST use one of:

insufficient-evidence
plausible
supported
rejected
insufficient-evidence

Available evidence cannot adequately evaluate the reconstruction.

plausible

The reconstruction is structurally coherent but not sufficiently validated.

supported

Available evidence and tests materially support the hypothesis.

rejected

Available evidence materially contradicts the hypothesis.

None of these values mean:

proven causality
17. Contradictions

Implementations SHOULD preserve contradictions discovered during
reconciliation or validation.

Contradictory evidence MUST NOT simply be deleted to increase confidence.

This enables:

audit
later re-evaluation
alternative hypothesis generation
adversarial review
18. Unresolved Gaps

Forward traces, backward traces, and reconstructions MAY contain
unresolved gaps.

Example:

unresolved_gaps:
  - "The exact activation latency is unknown."

An unresolved gap is preferable to an unsupported inferred fact.

19. Minimum Reconstruction Pipeline

A conforming v0.1 implementation SHOULD be able to represent:

Causal Observation
       ↓
Forward Trace
       +
Backward Trace
       ↓
Causal Reconstruction
       ↓
Causal Validation

The protocol does not require all stages to be generated by the same AI,
model, agent, or organization.

20. Interoperability Direction

CTRP is designed to operate between provenance and audit layers.

Origin / Provenance
        ↓
Observed Trace
        ↓
Causal Trace Reconstruction
        ↓
Audit
        ↓
Attribution
        ↓
Settlement / Royalty

Future protocol versions may define formal interfaces for these layers.

21. Non-Goals of v0.1

v0.1 does not define:

causal discovery algorithms
Bayesian network formats
structural causal model syntax
cryptographic provenance
signatures
distributed consensus
model reputation
automatic monetary settlement
full temporal logic
recursive causal decomposition
causal graph storage engines

These are intentionally deferred.

22. Core Principle

The central principle of CTRP v0.1 is:

Reconstruct the missing causal path explicitly,
preserve uncertainty,
and keep the reconstruction distinguishable from fact.
