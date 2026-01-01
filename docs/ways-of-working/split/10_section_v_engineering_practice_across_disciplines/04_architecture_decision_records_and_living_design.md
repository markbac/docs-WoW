## Architecture Decision Records and Living Design

Architecture is not a phase.
It is not a document.
It is not a role.

Architecture is the **accumulated set of decisions that shape how a system behaves, changes, fails, and evolves over time**.

Cornerstone treats architecture as a continuous, decision-centric activity that must remain visible, reviewable, and evolvable throughout the life of a product. Architecture Decision Records (ADRs) and living design artefacts are the primary mechanisms by which this happens.

This chapter formalises how Cornerstone uses ADRs and living design to turn architecture from an implicit, fragile knowledge base into an explicit, resilient system.



### Architecture as a Decision System

Every meaningful architectural choice encodes assumptions about:
- change frequency
- ownership boundaries
- failure modes
- performance constraints
- cost and risk tolerance

When these assumptions remain implicit, they:
- become invisible constraints
- are rediscovered through failure
- are defended emotionally rather than rationally

Cornerstone reframes architecture as a **decision system**, where:
- decisions are surfaced explicitly
- trade-offs are documented
- and rationale is preserved over time

ADRs are not bureaucracy. They are memory.



### Why Traditional Architecture Documentation Fails

Traditional architecture documentation often fails because it:
- attempts to be comprehensive rather than decision-focused
- is produced upfront and decays rapidly
- is detached from actual delivery work
- serves compliance rather than understanding

The result is shelfware that:
- no one trusts
- no one updates
- and no one uses when it matters

Cornerstone deliberately rejects “big design up front” and “big documents later”.
Instead, it optimises for **just enough design, captured at the moment of decision**.



### What an Architecture Decision Record Is (and Is Not)

An ADR is a lightweight, structured record of a **significant architectural decision**.

It exists to answer:
- What decision did we make?
- Why did we make it?
- What alternatives did we consider?
- What trade-offs did we accept?
- What are the consequences?

An ADR is:
- narrow in scope
- explicit about context
- honest about uncertainty

An ADR is not:
- a design specification
- a justification after the fact
- a permanent truth

Decisions can be revisited. ADRs make that possible without rewriting history.



### When to Create an ADR

Cornerstone does not mandate ADRs for every choice.
They are used when a decision:
- is hard to reverse
- affects multiple teams or systems
- introduces long-term constraints
- carries significant risk or cost
- is likely to be questioned later

Examples include:
- architectural patterns and styles
- protocol or platform selection
- data ownership boundaries
- build vs buy decisions
- deployment and operational models

The trigger is **decision significance**, not hierarchy or ceremony.



### ADRs as Socio-Technical Artefacts

ADRs are not just technical records.
They are socio-technical artefacts that:
- shape how teams communicate
- clarify who decides what
- reduce conflict by making trade-offs explicit

Well-written ADRs:
- depersonalise disagreement
- enable asynchronous collaboration
- reduce reliance on tribal knowledge

They shift conversations from “who decided this?” to “under what assumptions did we decide this?”.



### Living Design Over Static Blueprints

Cornerstone pairs ADRs with **living design artefacts**.

Living design means:
- diagrams evolve as the system evolves
- documentation reflects reality, not aspiration
- design artefacts are version-controlled
- updates happen alongside code changes

Common living design artefacts include:
- C4 diagrams at appropriate levels
- interface definitions
- deployment views
- data flow diagrams
- failure and resilience models

The goal is shared understanding, not exhaustive description.



### Diagrams as Thinking Tools, Not Decoration

In Cornerstone, diagrams exist to:
- reduce cognitive load
- support reasoning
- expose coupling and assumptions

They are not marketing material.

Good diagrams:
- answer a specific question
- target a defined audience
- avoid false precision
- are easy to update

Bad diagrams attempt to explain everything and end up explaining nothing.



### Version Control and Review of Design Decisions

All ADRs and living design artefacts are:
- stored in version control
- reviewed via pull requests
- evolved incrementally

This achieves several things:
- design changes are auditable
- rationale is preserved alongside implementation
- discussion happens close to the decision
- ownership is explicit

Design review becomes part of normal engineering flow, not a separate governance ritual.



### ADRs and Governance Without Bureaucracy

Cornerstone uses ADRs to enable **lightweight governance**.

Rather than central approval boards:
- guardrails are expressed through principles
- significant deviations are documented via ADRs
- accountability is achieved through transparency

This allows:
- decentralised decision-making
- central visibility
- and post-hoc review without control theatre

Governance emerges from shared understanding, not enforcement.



### Revisiting and Superseding Decisions

Systems change.
Assumptions expire.
Constraints shift.

Cornerstone expects ADRs to be:
- revisited when context changes
- superseded when better options emerge
- referenced when diagnosing problems

A superseded ADR is not a failure.
It is evidence of learning.

What matters is that change is **conscious**, not accidental.



### Architectural Integrity Over Time

Architectural decay rarely comes from bad initial design.
It comes from:
- unrecorded decisions
- local optimisations
- silent trade-offs
- time pressure without reflection

ADRs and living design provide friction in the right places:
- they slow down irreversible decisions just enough
- they force trade-offs into the open
- they preserve intent across team and time boundaries

This protects long-term system health without paralysing delivery.



### Leadership Responsibilities Around Architecture

Engineering leaders are responsible for:
- ensuring architectural decisions are visible
- protecting time for design thinking
- discouraging undocumented shortcuts
- valuing clarity over heroics

They do not need to make every decision.
They must ensure that decisions are made **well, consciously, and transparently**.

Architecture fails most often when leadership treats it as someone else’s problem.



### Summary

In Cornerstone:
- architecture is a continuous decision process
- ADRs capture intent, trade-offs, and consequences
- living design maintains shared understanding
- governance is achieved through transparency
- learning is preserved over time

Architecture is not about predicting the future.
It is about **making today’s decisions survivable tomorrow**.

The next chapter builds directly on this foundation by formalising **documentation itself as a delivery enabler**, rather than an overhead.

