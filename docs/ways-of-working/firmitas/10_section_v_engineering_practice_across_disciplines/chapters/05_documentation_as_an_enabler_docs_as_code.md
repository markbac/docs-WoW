## Documentation as an Enabler (Docs as Code)

Documentation is not a by-product of engineering.
It is not evidence created after the fact.
It is not something to be “kept in sync” if time allows.

In Firmitas, documentation is treated as a **first-class delivery mechanism**.
It is part of the socio-technical system through which intent, decisions, risk, quality, and learning flow.

This chapter defines how Firmitas reframes documentation from overhead into leverage through a **Docs-as-Code** approach.



### Why Documentation Fails in Most Organisations

Most documentation fails for systemic reasons, not because engineers are careless.

Common failure modes include:
- documentation created to satisfy a gate or audit, then abandoned
- large documents written upfront, divorced from delivery
- ownership assigned to “someone else”
- tools optimised for publishing rather than thinking
- documentation treated as static truth rather than evolving knowledge

The result is predictable:
- engineers stop trusting documentation
- decisions move into chat logs and heads
- audits become painful archaeology exercises
- organisations relearn the same lessons repeatedly

Firmitas starts from a different premise:
**documentation exists to support decision-making, learning, and coordination under uncertainty**.



### Documentation as a Socio-Technical System

Documentation is not just text.
It is a socio-technical system spanning:
- people and incentives
- tools and workflows
- governance and quality expectations
- organisational memory

Every documentation system encodes assumptions about:
- who is allowed to change what
- what level of precision is expected
- how disagreement is resolved
- what “good enough” looks like

Firmitas explicitly designs this system rather than letting it emerge accidentally.



### The Core Principle: Documentation Must Live Where Work Lives

In Firmitas:
- documentation lives alongside code
- documentation changes follow the same workflow as code
- documentation is version-controlled
- documentation is reviewed, not approved in isolation

This has several effects:
- documentation stays close to reality
- changes are incremental, not heroic
- ownership is clear
- history is preserved automatically

If a document cannot be changed with a pull request, it will decay.



### What “Docs as Code” Means in Practice

Docs-as-Code is not a tool choice.
It is a way of working.

Practically, it means:
- text-based formats (Markdown, AsciiDoc) by default
- diagrams as text where possible (Mermaid, PlantUML)
- Git as the source of truth
- CI pipelines for validation and publishing
- pull requests for review and discussion

This aligns documentation with the same delivery system engineers already understand.



### Documentation Types in Firmitas

Firmitas deliberately limits the number of documentation types, focusing on **decision-bearing artefacts**.

Key categories include:

#### Vision and Intent
Documents that explain:
- why the product exists
- who it serves
- what success means

These are concise, narrative, and stable.

#### Requirements and Constraints
Statements of:
- functional intent
- non-functional constraints
- regulatory and safety obligations

They evolve, but changes are explicit and traceable.

#### Architectural and Design Artefacts
Living views of:
- system structure
- interfaces
- deployment
- failure modes

Paired with ADRs to preserve rationale.

#### Verification, Validation, and Evidence
Test plans, results, and traceability that:
- demonstrate conformance
- support audits
- enable learning

These are generated continuously, not assembled at the end.



### Documentation and Cognitive Load

Documentation exists to **reduce cognitive load**, not increase it.

Firmitas applies the same principles here as for team design:
- minimise duplication
- avoid unnecessary precision
- surface only what matters to the audience

This means:
- different views for different needs
- no single “master document”
- clarity over completeness

A document that tries to answer every question answers none well.



### Documentation and Decision Transparency

Documentation is the primary mechanism for decision transparency.

In Firmitas:
- significant decisions are documented explicitly
- rationale is preserved
- alternatives are visible
- consequences are acknowledged

This reduces:
- repeated debates
- personalisation of disagreement
- institutional memory loss

It also enables new team members to onboard into *why*, not just *what*.



### Docs as Code and Governance Without Friction

Docs-as-Code enables governance without heavyweight process.

Instead of:
- formal review boards
- static templates
- central approval queues

Firmitas relies on:
- shared standards
- visible changes
- peer review
- automated checks

Governance becomes an emergent property of the system, not an external control layer.



### Documentation in Regulated and Safety-Critical Contexts

Firmitas does not reject formal documentation.
It rejects **wasteful documentation**.

Docs-as-Code works particularly well in regulated environments because:
- version history is automatic
- traceability can be generated, not curated
- evidence is produced as work happens
- audits become queries, not archaeology

Formal outputs (PDFs, baselined documents) are treated as **snapshots of a living system**, not the system itself.



### Documentation, Slack, and Long-Term Performance

High-quality documentation requires slack.

When teams are permanently overloaded:
- documentation degrades first
- decisions go undocumented
- risk accumulates silently

Firmitas treats slack as a **system investment**:
- time to explain
- time to reflect
- time to improve artefacts

This is not inefficiency.
It is what allows systems to remain understandable and adaptable over time.



### Leadership Responsibilities Around Documentation

Leaders are responsible for:
- valuing clarity over volume
- protecting time for documentation
- modelling good documentation behaviour
- resisting performative documentation demands

When leaders treat documentation as “admin”, teams follow.
When leaders treat it as infrastructure, teams invest.



### Anti-Patterns to Avoid

Firmitas explicitly warns against:
- documentation owned by a single role
- “final” documents
- copy-paste templates without intent
- documentation created purely for audits
- tools chosen for aesthetics over integration

Each of these undermines trust and long-term system health.



### Summary

In Firmitas:
- documentation is part of the delivery system
- Docs-as-Code aligns documentation with engineering flow
- living artefacts preserve intent and learning
- governance emerges from transparency
- slack enables quality documentation

Documentation is not about recording the past.
It is about **enabling better decisions in the future**.

The next chapter builds on this by examining how **toolchains and automation** shape the socio-technical system that Firmitas operates within.

