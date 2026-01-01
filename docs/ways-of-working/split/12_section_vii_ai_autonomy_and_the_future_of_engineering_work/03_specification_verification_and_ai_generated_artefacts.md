## Specification, Verification, and AI-Generated Artefacts

As AI reduces the cost of producing artefacts, it fundamentally shifts where engineering effort and risk reside.

Implementation is no longer the bottleneck.
**Intent, specification, and verification are.**

This chapter makes explicit a central Cornerstone position:

> In AI-assisted engineering systems, **specification quality becomes the dominant determinant of correctness, safety, and value**.

Poor specification combined with fast generation does not merely fail faster.  
It fails *more convincingly*.



### The Collapse of Implementation Cost and Its Consequences

Historically, engineering effort was dominated by:
- manual coding
- detailed drafting
- slow iteration cycles

AI dramatically compresses these costs. Code, tests, designs, and documentation can now be produced at a pace that outstrips human review capacity.

This creates a dangerous inversion:
- execution becomes cheap
- mistakes become scalable
- confidence becomes decoupled from correctness

Cornerstone recognises this inversion and responds by **re-centering the system around specification and verification**, not generation.



### Specification as the Primary Engineering Discipline

In Cornerstone, specification is not:
- a phase
- a document
- or a handoff

It is a **continuous discipline** that shapes everything downstream.

Effective specification defines:
- intent and purpose
- boundaries and constraints
- acceptance criteria
- failure modes
- non-functional requirements
- regulatory and ethical limits

AI amplifies whatever is specified.
If intent is vague, AI will fill the gaps with plausible but incorrect assumptions.



### From “Requirements” to Intent, Constraints, and Acceptance

Traditional requirements often fail because they:
- describe behaviour without context
- omit constraints
- hide trade-offs
- assume shared understanding

Cornerstone reframes specification around three explicit elements:

**Intent**
What outcome is being sought, and why it matters.

**Constraints**
What must not be violated, including safety, regulatory, architectural, economic, and ethical limits.

**Acceptance**
What evidence will demonstrate that intent has been met within constraints.

AI systems must be fed all three.
Anything omitted will be invented.



### AI-Generated Artefacts Are Hypotheses, Not Facts

Cornerstone is explicit:

> AI-generated artefacts are **hypotheses requiring validation**, not authoritative outputs.

This applies equally to:
- code
- tests
- designs
- documentation
- analyses
- architectural suggestions

Treating AI output as fact introduces silent risk.
Treating it as a hypothesis invites verification, challenge, and improvement.

Verification effort must scale with:
- risk
- irreversibility
- exposure
- coupling



### Verification Must Tighten as Generation Accelerates

As generation speed increases, verification must become:
- more systematic
- more automated where possible
- more intentional where judgement is required

Cornerstone reinforces several verification principles:

- Verification is continuous, not staged
- Evidence must be objective where possible
- Human review is focused on *meaningful decisions*, not syntax
- Verification depth is risk-driven, not uniform

AI reduces the cost of creating artefacts.
It does not reduce the cost of being wrong.



### The False Comfort of AI-Generated Tests

A particularly dangerous anti-pattern is trusting AI-generated tests as proof of correctness.

AI-generated tests:
- often mirror the assumptions of the implementation
- may validate behaviour without validating intent
- can give high coverage with low confidence

Cornerstone requires:
- independent thinking between specification and verification
- tests derived from intent and acceptance criteria, not code structure
- explicit review of what tests do *not* cover

Verification that shares the same blind spots as generation is not verification.



### Specification and Verification Across System Types

Specification and verification must address all system layers defined earlier:

- **Human systems:** workload, usability, operational clarity
- **Organisational systems:** ownership, escalation, governance
- **Socio-technical systems:** tool behaviour, automation boundaries
- **Delivery systems:** flow, batching, feedback loops
- **Technical systems:** correctness, performance, resilience
- **Economic systems:** cost, value, opportunity trade-offs

AI tends to focus narrowly on technical artefacts.
Cornerstone insists on system-level verification.



### Traceability Becomes More Important, Not Less

When artefacts are cheap to generate, **provenance becomes critical**.

Cornerstone requires that teams can always answer:
- who defined the intent
- who accepted the constraints
- how acceptance was verified
- where AI was used
- where human judgement intervened

This is not about blame.
It is about understanding and learning.

Traceability protects against both error and overconfidence.



### Human Judgement as the Final Verification Layer

No amount of automation replaces the need for human judgement at:
- risk acceptance points
- release decisions
- architectural trade-offs
- ethical boundaries

AI can surface options.
Only humans can accept consequences.

Cornerstone therefore mandates **explicit human acceptance** at decision points with irreversible impact.



### Slack as a Verification Requirement

Verification requires:
- time to review
- space to challenge
- capacity to reflect

AI increases pressure to remove slack.
Cornerstone explicitly resists this.

Without slack:
- review becomes superficial
- acceptance becomes implicit
- AI output becomes trusted by default

Slack is not inefficiency.
It is the margin that keeps fast systems safe.



### Leadership Responsibilities in AI-Assisted Specification

Leadership responsibilities intensify in AI-assisted systems.

Leaders must:
- insist on clear intent
- protect verification capacity
- prevent output-driven metrics
- reward correctness over speed
- resist automation bias

Delegating specification quality to tools is a leadership failure.



### Summary

In Cornerstone:
- AI collapses implementation cost
- specification becomes the primary engineering skill
- AI output is hypothesis, not truth
- verification must tighten as speed increases
- traceability preserves understanding
- human judgement remains final
- slack enables safe verification

Fast systems without clear intent fail convincingly.
Cornerstone exists to prevent that.

The next chapter builds directly on this by addressing **governance, risk, and ethics in AI-assisted delivery**, where technical correctness alone is insufficient.

