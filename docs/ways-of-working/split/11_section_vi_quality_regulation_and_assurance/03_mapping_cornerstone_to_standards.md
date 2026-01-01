## Mapping Cornerstone to Standards
*(ISO 9001, IEC 62304 / 61508, DO-178C, and Related Frameworks)*

This chapter makes something explicit that is often left implicit or hand-waved:

**Cornerstone is not “instead of” standards.  
Cornerstone is how standards are satisfied without distorting delivery.**

Where many organisations bolt compliance on top of delivery, Cornerstone integrates assurance into the system design itself. This chapter shows how Cornerstone aligns with formal standards **by intent**, not by ritual, and why that distinction matters.



### Why Mapping Matters (and Why It Is Often Done Poorly)

Standards do not fail organisations.
**Interpretations do.**

Most compliance pain comes from:
- treating standards as prescriptive processes
- assuming documentation equals assurance
- mapping activities instead of outcomes
- creating parallel “compliance systems” disconnected from real work

This produces:
- duplicate effort
- false confidence
- and brittle audit artefacts

Cornerstone takes a different approach.

It maps:
- **system behaviours to standard intent**
- **evidence generation to real work**
- **governance to risk, not ceremony**

The result is *stronger* compliance with *less* friction.



### The Core Principle: Intent Over Form

All major standards share common intent, regardless of domain:

- clarity of purpose
- controlled change
- demonstrable quality
- risk management
- accountability
- traceability
- learning from failure

Cornerstone explicitly designs for these intents.

It does **not**:
- mandate document formats
- prescribe stage-gated sequences
- require heavyweight artefacts unless risk demands them

Instead, it ensures the system can always answer:
- *Why was this decision made?*
- *How do we know this is correct?*
- *What happens if it changes?*
- *Where is the evidence?*
- *Who is accountable?*

Those answers are what auditors are actually looking for.



### ISO 9001 – Quality Management Systems

**ISO 9001 focuses on system capability, not technical detail.**

Key ISO 9001 intents and Cornerstone alignment:

**Leadership & Accountability**
- ISO requires leadership ownership of quality.
- Cornerstone explicitly places quality and compliance as leadership responsibilities (Chapters 39–40).

**Process Control**
- ISO requires defined, controlled processes.
- Cornerstone provides *guardrails*, not rigid workflows, ensuring consistency without rigidity.

**Continuous Improvement**
- ISO mandates learning and improvement.
- Cornerstone embeds feedback loops, retrospectives, and incident learning as system features.

**Evidence-Based Decision Making**
- ISO requires objective evidence.
- Cornerstone generates evidence continuously through:
  - version control
  - test automation
  - ADRs
  - delivery metrics

ISO 9001 compliance emerges naturally from a functioning Cornerstone system, rather than being enforced externally.



### IEC 62304 / IEC 61508 – Safety-Critical Systems

Safety standards raise the bar.
Cornerstone meets it by **making safety a system concern, not a documentation exercise**.

Key intents and alignment:

**Risk Management**
- Cornerstone treats risk as a first-class input to planning, prioritisation, and design.
- Hazards drive architecture, verification depth, and gating decisions.

**Traceability**
- Requirements → design → implementation → verification is maintained as living traceability, not static matrices.

**Separation of Concerns**
- Safety-related functions are architecturally isolated where required.
- This aligns with both safety integrity levels and fault containment expectations.

**Verification Rigor**
- Verification depth scales with risk.
- Formal methods and additional controls are applied where justified, not universally.

Cornerstone supports safety-critical delivery **without flattening everything into worst-case bureaucracy**.



### DO-178C and Similar Aviation Standards

DO-178C is often cited as incompatible with modern delivery.
This is largely untrue.

DO-178C cares about:
- determinism
- traceability
- verification evidence
- configuration control
- independence of review

Cornerstone addresses these through:
- strong configuration management
- explicit decision records
- independent review via pull requests and design forums
- automated and repeatable verification pipelines
- controlled baselining at defined transition points

What Cornerstone avoids is **false sequencing**.
Learning happens continuously.
Formal acceptance happens deliberately.



### Traceability: What Standards Actually Require

Standards do not require:
- giant spreadsheets
- manual trace updates
- duplicated artefacts

They require:
- demonstrable linkage
- impact awareness
- controlled change

Cornerstone implements traceability as:
- lightweight identifiers
- tool-assisted linking
- automation where possible
- human review where judgement matters

Traceability supports **engineering confidence first**, audit confidence second.



### Configuration Management and Change Control

Cornerstone aligns strongly with configuration control expectations by default:

- version control is the system of record
- changes are reviewed, discussed, and approved
- baselines are explicit and intentional
- rollback is possible and understood

Change control is not a board.
It is a **capability**.

Formal change boards exist only where risk justifies them.



### Evidence, Audits, and “Show Me”

Auditors do not want more documents.
They want clearer stories.

Cornerstone enables this by making it easy to:
- trace decisions over time
- inspect how quality is assured
- see how risk is managed
- understand how learning happens

An audit becomes a guided walk through the system, not a defensive performance.



### Common Mapping Anti-Patterns

Cornerstone explicitly avoids:
- “one artefact per clause” thinking
- mapping tools instead of behaviours
- freezing documents to look compliant
- parallel compliance teams
- retrofitting evidence

Each of these increases cost while reducing actual assurance.



### Summary

Cornerstone does not weaken standards.
It **fulfils their intent more honestly**.

- Standards describe *what must be true*
- Cornerstone designs *systems that make it true*

Compliance emerges from:
- leadership accountability
- clear architecture
- disciplined delivery
- continuous evidence
- and sustainable pace

The next chapter builds on this by addressing **how evidence is curated, presented, and sustained over time**.

