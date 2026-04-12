## Communication Patterns and Information Flow

Engineering organisations do not fail primarily because of poor technical decisions. They fail because information does not move when, where, or how it needs to. Decisions are delayed, intent is lost, assumptions go unchallenged, and risk accumulates silently until it surfaces as rework, outages, or missed commitments.

In Firmitas, communication is treated as a **designed system**, not an emergent by-product of good intentions or individual effort. How information flows, who is allowed to decide, what must be made explicit, and what can remain implicit are all first-class engineering concerns.

This chapter establishes communication and information flow as **structural properties of the system**, tightly coupled to architecture, team boundaries, governance, and leadership behaviour.



### Communication Is a System, Not a Skill

Most organisations treat communication as a personal competency problem. When things go wrong, the diagnosis is often framed in terms of “misalignment”, “stakeholder management”, or “poor communication”, implicitly blaming individuals.

Firmitas rejects this framing.

People communicate *exactly as the system allows them to*. If information is fragmented, delayed, distorted, or withheld, the cause is almost always systemic:

- Reporting lines that discourage candour  
- Incentives that reward local optimisation  
- Overloaded teams with no slack to reflect or document  
- Toolchains that fragment knowledge across silos  
- Decision rights that are unclear or constantly overridden  

Communication quality is therefore an **output of system design**, not a function of effort or goodwill.

Engineering leadership is responsible for designing systems in which the *right information flows to the right people at the right time, with minimal friction and minimal noise*.



### Information Flow as a Constraint on Delivery

Delivery speed, quality, and predictability are constrained less by coding capacity and more by **information latency**.

Common failure modes include:

- Decisions waiting for meetings instead of being documented and reviewed asynchronously  
- Architectural intent living in people’s heads rather than artefacts  
- Risks known by individuals but not visible to the system  
- Status reporting that hides uncertainty instead of exposing it  

In Firmitas, information flow is explicitly optimised for:

- **Early risk exposure**, not late escalation  
- **Asynchronous clarity**, not synchronous dependency  
- **Decision transparency**, not consensus theatre  
- **Traceability of intent**, not bureaucratic documentation  

Fast delivery without fast information flow is an illusion. It only accelerates the accumulation of invisible debt.



### Types of Information That Must Flow

Not all information is equal. One of the most common anti-patterns is treating *all communication as status updates*.

Firmitas distinguishes several **critical information flows**, each with different requirements:

#### Intent and Purpose

Teams must understand *why* work exists, not just *what* is being done. This includes:

- Business objectives  
- Customer outcomes  
- Constraints and non-goals  

Intent must be persistent, discoverable, and stable enough to guide local decisions without constant escalation.

#### Decisions and Rationale

What was decided matters less than *why* it was decided.

Decision rationale must flow through the system via:

- Architecture Decision Records (ADRs)  
- RFCs and design proposals  
- Explicit trade-off documentation  

This preserves organisational memory and enables future teams to evolve the system without repeating old mistakes.

#### Risk and Uncertainty

Risk does not become dangerous when it exists. It becomes dangerous when it is hidden.

Firmitas requires:

- Explicit risk articulation  
- Visible ownership  
- Continuous re-evaluation  

Silence is treated as a risk signal, not reassurance.

#### State and Reality

Operational reality must override plan narratives.

This includes:

- Actual system behaviour  
- Test outcomes  
- Incident learnings  
- Capacity constraints  

Information that contradicts the plan is more valuable than information that confirms it.



### Communication Boundaries Follow Architectural Boundaries

Conway’s Law is not a warning. It is a design constraint.

Communication paths will shape system architecture whether acknowledged or not. Firmitas therefore aligns:

- **Team boundaries**
- **Ownership boundaries**
- **Architectural boundaries**
- **Decision boundaries**

When communication crosses boundaries frequently, that boundary is either:

- In the wrong place, or  
- Carrying the wrong type of information  

Healthy systems minimise *coordination overhead* while maximising *local autonomy*. This requires deliberate boundary design, not optimism.



### Asynchronous by Default, Synchronous by Exception

Synchronous communication does not scale. It also hides thinking.

Firmitas strongly biases towards **asynchronous communication**, supported by living artefacts:

- ADRs instead of verbal decisions  
- RFCs instead of design meetings  
- Written risk registers instead of verbal escalation  
- Docs-as-Code instead of slide decks  

Synchronous forums still exist, but only where they add unique value:

- Conflict resolution  
- High-ambiguity alignment  
- Incident response  
- Relationship repair  

Meetings are used to *resolve*, not to *discover*. Discovery belongs in artefacts.



### Documentation as a Communication Accelerator

Documentation is not an overhead. Poor documentation is.

Firmitas treats documentation as:

- A **coordination mechanism**
- A **decision record**
- A **communication equaliser**
- A **scaling tool**

Docs-as-Code enables:

- Versioned intent  
- Reviewable change  
- Traceable evolution  
- Distributed understanding  

Crucially, documentation reduces **interruption cost**, allowing teams to remain in flow while still sharing context.



### Leadership’s Role in Information Flow

Leadership behaviour either enables or collapses communication systems.

Leaders are responsible for:

- Making uncertainty safe to surface  
- Rewarding clarity over optimism  
- Accepting bad news early  
- Protecting slack for thinking and documentation  
- Enforcing decision discipline  

When leaders punish transparency or override decisions without explanation, the system adapts by hiding information.

Firmitas explicitly frames **information suppression as a leadership failure**, not a team failure.



### Slack as a Communication Enabler

Slack is not wasted capacity. It is what allows systems to think.

Without slack:

- Documentation decays  
- Decisions go undocumented  
- Risks go unspoken  
- Learning stops  

Firmitas requires slack at multiple levels:

- Team capacity  
- Review bandwidth  
- Cognitive load  
- Decision latency  

Slack is the space in which communication quality emerges. Systems without slack eventually become loud, brittle, and blind.



### Signals, Noise, and Information Hygiene

More communication does not mean better communication.

Firmitas emphasises **signal quality** over volume:

- Fewer dashboards, but meaningful ones  
- Fewer metrics, but decision-relevant ones  
- Fewer documents, but actively maintained ones  

Information hygiene is maintained through:

- Clear ownership  
- Explicit audiences  
- Sunset rules for artefacts  
- Regular pruning  

Noise is treated as a form of waste.



### Communication as a Continuous Design Activity

Communication systems cannot be designed once and left alone.

As organisations scale, evolve, and integrate new technologies (including AI), communication patterns must be revisited:

- Are decisions still visible?  
- Are risks still flowing?  
- Is intent still clear?  
- Are teams overloaded with coordination?  

Firmitas treats communication design as an **ongoing leadership responsibility**, inseparable from architecture and delivery.



### Summary

Communication and information flow are not soft concerns. They are **structural properties of engineering systems**.

In Firmitas:

- Communication is designed, not assumed  
- Information flow constrains delivery more than tooling  
- Documentation accelerates rather than slows work  
- Slack enables clarity and learning  
- Leadership behaviour shapes system honesty  

Healthy systems speak early, clearly, and truthfully.  
Unhealthy systems stay quiet until they fail.

The difference is design.

