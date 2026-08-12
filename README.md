# Causal Trace Reconstruction Protocol

**CTRP — Causal Trace Reconstruction Protocol**

A protocol for reconstructing missing causal paths through forward inference, backward inference, meet-in-the-middle reconciliation, temporal validation, hypothesis comparison, counterfactual branching, necessity/sufficiency assessment, workflow conformance, and final audit receipts.

**Current version:** `v0.5.0`

---

## 1. Overview

Causal Trace Reconstruction Protocol (CTRP) is a protocol for reconstructing and evaluating missing causal paths between observed causes, intermediate states, and outcomes.

CTRP is designed around a simple problem:

> Observing that two states are related does not explain why one state led to the other.

Traditional pattern matching may identify structural similarity, correlation, or repeated sequences.

CTRP instead asks:

> What causal path could connect the observed origin and outcome, and what evidence would be required to support that reconstruction?

The protocol combines:

- cause-forward inference
- outcome-backward inference
- meet-in-the-middle reconciliation
- competing hypothesis comparison
- temporal precedence checking
- counterfactual branching
- necessity and sufficiency assessment
- semantic validation
- workflow conformance
- final reconstruction receipts

CTRP does **not** treat reconstructed causal paths as automatically proven facts.

Its central safety principle is:

```text
Reconstruction ≠ Proof
Counterfactual Support ≠ Proof
Workflow Conformance ≠ Proven Causality
```

---

## 2. Core Problem

Many AI systems can recognize patterns such as:

```text
A resembles B
A often precedes B
A and B frequently co-occur
```

But causal reasoning requires a stronger question:

```text
Why would A produce B?
```

In real systems, causal traces are often incomplete.

For example:

```text
Observed Cause
      ↓
      ?
      ?
      ↓
Observed Outcome
```

The intermediate mechanism may be partially missing, distributed across multiple evidence sources, or only indirectly observable.

CTRP reconstructs candidate paths rather than silently filling these gaps.

---

## 3. Core Architecture

The complete CTRP v0.5 workflow is:

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

The protocol therefore separates:

```text
Observation
→ Reconstruction
→ Evaluation
→ Validation
→ Conformance
→ Receipt
```

---

## 4. Cause-Forward and Outcome-Backward Reasoning

CTRP uses two independent reasoning directions.

### Cause-Forward Inference

Cause-forward inference begins with a known or observed initiating condition.

```text
Known Cause
   ↓
Possible Intermediate State
   ↓
Possible Intermediate State
   ↓
Observed Outcome
```

The forward trace asks:

> If this cause were active, what states should follow?

---

### Outcome-Backward Inference

Outcome-backward inference starts from the observed result.

```text
Observed Outcome
       ↑
Required Prior State?
       ↑
Required Prior State?
       ↑
Possible Cause
```

The backward trace asks:

> What conditions would have been required for this outcome to occur?

---

### Meet-in-the-Middle Reconstruction

The two directions are then reconciled.

```text
Cause
 ↓
Forward Trace
 ↓
Possible State
      ↘
       Meeting Point
      ↗
Possible State
 ↑
Backward Trace
 ↑
Outcome
```

A meeting point does not prove a causal mechanism.

It identifies a candidate causal structure that can be evaluated further.

---

## 5. Multiple Causal Hypotheses

A single observation may support more than one explanation.

CTRP therefore allows:

```text
Observation
   ↓
 ┌─┼────────────┐
 ↓ ↓            ↓
H1 H2           H3
```

For example:

```text
Observed service throttling

H1: Thermal protection
H2: Workload saturation
H3: Network congestion
```

Each candidate may contain:

- reconstructed causal path
- supporting evidence
- contradictions
- unresolved gaps
- confidence
- meeting points
- active or rejected status

CTRP explicitly avoids forcing a winner when evidence does not justify one.

Valid outcomes include:

```text
selected
ambiguous
insufficient-evidence
all-rejected
```

---

## 6. Temporal Causal Reconstruction

A plausible causal story is invalid if its required cause occurs after its effect.

CTRP therefore includes temporal precedence assessment.

Core rule:

```text
Cause must precede Effect
```

Supported timing models include:

```text
exact
interval
unknown
```

Example:

```text
00:00:00  High temperature
     ↓
00:00:02  Protection activated
     ↓
00:00:04  Service throttled
```

Possible assessment states include:

```text
consistent
partially-ordered
violated
insufficient-temporal-evidence
```

Temporal uncertainty is preserved instead of silently converted into certainty.

---

## 7. Counterfactual Branch Reconstruction

CTRP v0.4 introduced explicit counterfactual branches.

Instead of storing counterfactual reasoning as a short test result, CTRP represents it as a traceable alternate causal path.

### Necessity Branch

A necessity test asks:

> If the proposed cause were removed, would the outcome disappear?

Conceptually:

```text
Cause removed
      ↓
Alternative Trace
      ↓
Outcome absent?
```

---

### Sufficiency Branch

A sufficiency test asks:

> If the proposed cause were introduced, would the expected outcome occur?

```text
Cause introduced
       ↓
Alternative Trace
       ↓
Outcome occurs?
```

Counterfactual branches may record:

- intervention
- intervention target
- baseline outcome
- alternate trace steps
- evidence references
- assumptions
- counterfactual outcome
- branch conclusion
- completion status

---

## 8. Necessity and Sufficiency Assessment

CTRP distinguishes causal roles including:

```text
necessary-and-sufficient
necessary-only
sufficient-only
neither-supported
undetermined
```

However, these roles are always scoped.

Every necessity/sufficiency assessment includes:

```text
evaluation_scope
claim_level: hypothesis
```

Therefore:

```text
Supported within tested scope
≠
Universal causal law
```

This prevents local experimental or simulated results from being silently promoted into unrestricted causal claims.

---

## 9. End-to-End CTRP Conformance

CTRP v0.5 introduces workflow conformance.

Schema-valid data alone is insufficient.

A causal workflow may contain valid JSON or YAML while still bypassing required reasoning stages.

CTRP therefore distinguishes:

```text
Schema Validity
≠
Semantic Validity
≠
Workflow Conformance
≠
Proven Causality
```

### Conformance Checks

A conformant workflow may verify the presence and integrity of:

- causal observation
- forward trace
- backward trace
- causal reconstruction
- temporal assessment
- hypothesis comparison
- counterfactual branching
- necessity/sufficiency assessment
- causal validation

---

## 10. Bypass Prevention

CTRP v0.5 defines explicit safeguards against causal reasoning shortcuts.

Representative rules include:

### CTRP-BYPASS-001

A validation must not bypass causal reconstruction.

### CTRP-BYPASS-002

A `supported` validation must not bypass temporal assessment.

### CTRP-BYPASS-003

A `supported` validation must not bypass counterfactual branching.

### CTRP-BYPASS-004

A `supported` validation must not bypass necessity/sufficiency assessment.

### CTRP-BYPASS-005

A supported final receipt must not be issued from a non-conformant workflow.

### CTRP-BYPASS-006

A reconstructed hypothesis must not be silently promoted into proven causality.

---

## 11. Final Causal Reconstruction Receipt

The final CTRP record is:

```text
causal-reconstruction-receipt
```

The receipt summarizes the completed reconstruction workflow.

It may contain:

- reconstruction reference
- hypothesis reference
- validation reference
- conformance reference
- final status
- causal role
- confidence
- trace references
- assessment references
- remaining uncertainties

The receipt is an audit record.

It is **not** a proof-of-causality certificate.

The protocol therefore fixes:

```yaml
claim_level: hypothesis
```

even at the final receipt stage.

---

## 12. Record Types

CTRP v0.5 defines eleven primary record types.

| Record Type | Purpose |
|---|---|
| `causal-observation` | Defines observed states and evidence |
| `forward-trace` | Reconstructs possible causal progression from the cause |
| `backward-trace` | Reconstructs required prior states from the outcome |
| `causal-reconstruction` | Reconciles traces into candidate causal hypotheses |
| `temporal-precedence-assessment` | Evaluates causal time ordering |
| `hypothesis-comparison` | Compares competing causal hypotheses |
| `counterfactual-branch` | Represents alternate causal paths under intervention |
| `causal-necessity-sufficiency-assessment` | Evaluates causal role within a declared scope |
| `causal-validation` | Produces evidence-based hypothesis validation |
| `ctrp-conformance-assessment` | Checks end-to-end CTRP workflow conformance |
| `causal-reconstruction-receipt` | Issues the final audit-oriented reconstruction receipt |

---

## 13. Repository Structure

```text
causal-trace-reconstruction-protocol/
├── .github/
│   └── workflows/
│       └── validate.yml
│
├── schemas/
│   ├── causal-observation.schema.json
│   ├── forward-trace.schema.json
│   ├── backward-trace.schema.json
│   ├── causal-reconstruction.schema.json
│   ├── temporal-precedence-assessment.schema.json
│   ├── hypothesis-comparison.schema.json
│   ├── counterfactual-branch.schema.json
│   ├── causal-necessity-sufficiency-assessment.schema.json
│   ├── causal-validation.schema.json
│   ├── ctrp-conformance-assessment.schema.json
│   └── causal-reconstruction-receipt.schema.json
│
├── examples/
│   ├── pass/
│   └── fail/
│
├── scripts/
│   └── validate_examples.py
│
├── README.md
├── SPEC.md
├── CHANGELOG.md
└── requirements.txt
```

---

## 14. Example End-to-End Flow

A simplified thermal-protection example:

```text
High Temperature
      ↓
Forward Trace
      ↓
Thermal Protection Activation
      ↓
Service Throttling
```

The backward reasoning begins from:

```text
Service Throttling
      ↑
Protection Activation?
      ↑
Thermal Threshold?
```

The resulting candidate hypotheses may include:

```text
H1: Thermal protection
H2: Workload saturation
```

CTRP then evaluates:

```text
Structural convergence
        +
Evidence support
        +
Temporal precedence
        +
Competing hypotheses
        +
Counterfactual necessity
        +
Counterfactual sufficiency
        ↓
Causal Validation
        ↓
Workflow Conformance
        ↓
Final Receipt
```

---

## 15. Validation Model

CTRP uses two main validation layers plus workflow conformance.

### JSON Schema Validation

Checks structural validity.

Examples:

- required fields
- enums
- object structure
- version identifiers
- allowed value ranges
- unknown properties

---

### Semantic Validation

Checks relationships that JSON Schema alone cannot enforce.

Examples:

- evidence references exist
- traces reference the correct observation
- hypotheses reference valid trace steps
- temporal order is logically consistent
- selected hypothesis is rank 1
- ambiguous decisions respect tie thresholds
- necessity tests use valid interventions
- sufficiency tests use valid interventions
- causal roles match necessity/sufficiency status
- validation references the correct causal path

---

### Conformance Validation

Checks the complete protocol path.

Examples:

- required stages are present
- stage references resolve
- supported conclusions do not bypass required evaluation
- final receipt agrees with validation
- final receipt agrees with conformance
- causal role agrees with necessity/sufficiency assessment

---

## 16. Running Validation

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run:

```bash
python scripts/validate_examples.py
```

A successful validation ends with:

```text
[validation-ok]
```

Pass examples are expected to satisfy both schema and semantic validation.

Fail examples are intentionally invalid and must produce an expected schema or semantic failure.

---

## 17. Pass and Fail Examples

The repository intentionally contains both successful and failing examples.

### Pass Examples

Pass examples demonstrate valid protocol usage.

Representative examples include:

```text
causal-observation.basic.example.yaml
forward-trace.basic.example.yaml
backward-trace.basic.example.yaml
causal-reconstruction.basic.example.yaml
temporal-precedence-assessment.thermal.example.yaml
temporal-precedence-assessment.workload.example.yaml
hypothesis-comparison.selected.example.yaml
counterfactual-branch.necessity.example.yaml
counterfactual-branch.sufficiency.example.yaml
causal-necessity-sufficiency-assessment.thermal.example.yaml
causal-validation.basic.example.yaml
ctrp-conformance-assessment.thermal.example.yaml
causal-reconstruction-receipt.thermal.example.yaml
```

### Fail Examples

Fail examples verify that invalid causal workflows are rejected.

Representative failures include:

- supported validation without counterfactual support
- false ambiguity despite a large comparison margin
- reversed causal time ordering
- invalid necessity intervention
- inconsistent necessity/sufficiency role
- supported receipt from a non-conformant workflow

Negative examples are part of the protocol definition, not incidental test data.

---

## 18. Design Principles

### 18.1 Reconstruction Is Not Proof

A reconstructed path remains a hypothesis.

```text
Reconstruction ≠ Proof
```

---

### 18.2 Uncertainty Must Be Preserved

Unknown or unresolved causal segments must remain explicit.

They must not be silently converted into certainty.

---

### 18.3 Competing Explanations Must Survive

A system should not discard alternatives merely to produce a single answer.

`ambiguous` is a legitimate protocol outcome.

---

### 18.4 Temporal Order Matters

A causal explanation that requires an effect to precede its cause is invalid.

---

### 18.5 Counterfactuals Must Be Traceable

Counterfactual reasoning should preserve:

- intervention
- assumptions
- alternate transitions
- evidence basis
- outcome difference

---

### 18.6 Causal Claims Must Be Scoped

Necessity and sufficiency claims are limited to an explicit evaluation scope.

---

### 18.7 Conformance Is Not Truth

A workflow may be perfectly CTRP-conformant while its hypothesis later turns out to be wrong.

Conformance means:

> The required reasoning procedure was followed and recorded.

It does not mean:

> The causal claim has become universal truth.

---

## 19. Relationship to Provenance and Audit Systems

CTRP may be used as an intermediate causal layer in larger provenance or governance systems.

For example:

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

CTRP focuses specifically on the reconstruction and evaluation of the causal path.

It does not itself define economic settlement or ownership rights.

---

## 20. Potential Applications

Possible uses include:

- AI agent reasoning audits
- system incident reconstruction
- scientific hypothesis support
- provenance analysis
- policy reasoning
- autonomous-system explainability
- fault diagnosis
- safety analysis
- multi-agent reasoning
- knowledge propagation analysis
- attribution systems
- governance systems

CTRP is intentionally domain-neutral.

---

## 21. Version Evolution

```text
v0.1
Causal path reconstruction

v0.2
Multiple competing hypotheses

v0.3
Temporal causal validation

v0.4
Counterfactual branching and necessity/sufficiency

v0.5
End-to-end conformance and final reconstruction receipt
```

The v0.5 release represents the first minimal complete CTRP lifecycle.

---

## 22. Protocol Summary

CTRP transforms:

```text
A and B look related
```

into:

```text
What causal path could connect A and B?
What evidence supports that path?
What alternatives exist?
Did the cause precede the effect?
What happens if the proposed cause is removed?
What happens if the cause is introduced?
Is the factor necessary or sufficient within the tested scope?
Did the reasoning workflow follow the required protocol?
What uncertainty remains?
```

The final architecture is:

```text
Observation
    ↓
Forward / Backward Trace
    ↓
Reconstruction
    ↓
Temporal Assessment
    ↓
Hypothesis Comparison
    ↓
Counterfactual Branching
    ↓
Necessity / Sufficiency
    ↓
Validation
    ↓
Conformance
    ↓
Receipt
```

---

## 23. Core Statement

> CTRP does not attempt to manufacture certainty from missing causal information.
>
> It reconstructs the missing path, preserves the uncertainty, tests alternative worlds, records the reasoning procedure, and makes the resulting causal claim auditable.

---

## License

See the repository license file for applicable terms.
