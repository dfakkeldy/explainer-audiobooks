# Curriculum Patterns

Choose and record a learning shape before writing the canonical outline. The
pattern is a reasoned curriculum decision, not a decorative label.

## Mechanism-first spiral

Use when the listener needs one stable mechanism before larger systems make
sense. Teach a small complete case, then revisit it at increasing scale or
depth. Guard against repeating the same explanation without a new learning job.

## End-to-end trace

Use when the learner's main goal is to follow one request, object, or event
through a system. Start with the whole route, then open each stage when its
inputs and outputs are meaningful. Guard against introducing outer stages whose
prerequisites have not been established.

## Problem progression

Use when the subject is best understood as a sequence of constraints or
failures. Each chapter establishes a problem, the response it motivated, and
the new tradeoff or boundary. Guard against turning history into chronology
without a cumulative mental model.

## Required record

Add this object to `learning-outline.json`:

```json
{
  "curriculumPattern": {
    "name": "mechanism-first-spiral",
    "reason": "The learner needs one stable mechanism before larger systems.",
    "fitEvidence": "The approved outcome starts with a calculable small case."
  }
}
```

Allowed names are `mechanism-first-spiral`, `end-to-end-trace`, and
`problem-progression`. Record why the pattern fits this learner and subject.
Preserve it across handoffs unless the user approves a new progression.

A terminology inventory is not a curriculum pattern. Terms belong in complete
explanation paths inside an authorized learning progression.
