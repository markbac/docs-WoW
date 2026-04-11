## Chapter 2 — The Sandbag Assumption

There is a belief, held widely and often unconsciously, by the people who govern engineering programmes. It runs something like this:

*Engineers are conservative by nature. When they estimate, they build in protection. When they flag risks, they are managing expectations. When they say a programme will take seventeen months, what they mean is that they would like seventeen months, and that with appropriate pressure and commercial discipline, twelve is probably achievable.*

This belief has a name in the industry. Sandbagging. The padding of estimates. The inflation of timescales. The engineering team playing it safe at the organisation's expense.

It is one of the most consequential beliefs in engineering programme management. And it is almost always wrong.

---

### Where the belief comes from

The sandbag assumption does not emerge from nowhere. It has a history, and that history contains enough partial truth to make the belief feel empirically grounded.

Programmes do overrun. Estimates do prove optimistic. Engineering teams do, on occasion, build contingency into timelines in ways that are not fully visible to the people reading those timelines. These things happen. The manager who has overseen several programmes, watched them all run over their original estimates, and concluded that engineering estimates are systematically inflated is not being irrational. They are drawing a conclusion from evidence.

The problem is that the conclusion is wrong — not because the evidence is fabricated, but because the cause has been misread.

Programmes overrun their original estimates for a reason. That reason, in the overwhelming majority of cases, is not that the engineering team added padding that pressure can remove. It is that the estimate was produced under conditions that made honesty difficult or impossible, or that the conditions the estimate depended on were changed after the estimate was made, or that risks identified in the estimate were not managed and materialised on schedule.

The programme in Chapter 1 overran. But it did not overrun because the engineering team's most likely estimate of seventeen months was padded. It overran because the programme board accepted a fourteen-month commitment without accepting the conditions that a fourteen-month delivery would have required — early resolution of the hardware-software interface ambiguities, independent validation of the third-party component, prompt procurement of the test environment. When those conditions were not met, the most likely case became unachievable and the worst case began to materialise.

The overrun was not extracted from a padded estimate by commercial pressure. It was produced by the failure to act on the risks that the engineering team had named, priced, and presented at week three. The estimate was honest. The response to it was not.

---

### What the assumption costs

The sandbag assumption has a specific, measurable effect on how programmes are governed — and that effect consistently makes outcomes worse rather than better.

When a senior leader believes that engineering estimates are padded, they apply pressure to reduce them. That pressure takes several forms. The direct form: the estimate is challenged in a programme review and the engineering team is asked to find a way to do it faster. The indirect form: the commercial commitment is made at a lower number than the estimate, with the implicit expectation that engineering will close the gap. The structural form: the organisation routinely accepts bids and makes commitments at best-case numbers, treating the most likely and worst-case estimates as negotiating positions to be discarded.

In each case, the effect is the same. The engineering team's honest assessment is replaced by a number that is more commercially convenient. The risks attached to that assessment — the specific conditions that would need to be true for the lower number to be achievable — are separated from the number and filed in a risk register that will be reviewed, noted, and not acted on.

The programme then proceeds on a plan that everyone involved knows is not achievable under the conditions that actually exist. The engineering team knows it. The programme management layer knows it. The only people who do not know it are the ones at the top of the governance structure — who are reading a plan rather than a programme.

This is where the damage compounds. Because when the programme eventually fails — as it will, because it was always going to — the failure is attributed to the engineering team. They did not deliver what they committed to. The commitment they are held against was not theirs. It was the number produced when their honest estimate was replaced by a commercially convenient one. But the attribution travels downward nonetheless, landing on the people who told the truth and were overridden.

And what does the organisation learn? Not that the estimate was honest and the response to it was wrong. It learns that engineering estimates are unreliable, that engineering teams cannot deliver what they commit to, and that tighter control and more pressure are the appropriate response next time. The sandbag assumption is not just a belief. It is a self-reinforcing cycle. It creates the conditions that appear to confirm it, which strengthens it, which worsens the conditions further.

---

### The honest estimate under pressure

To understand why the sandbag assumption is wrong, it helps to understand what happens to estimation accuracy when pressure is applied.

When an engineering team produces an estimate in an environment where they believe the honest number will be accepted, used as the basis for planning, and supported with the resources and decisions it requires, their estimates are broadly accurate. The most likely case reflects genuine professional judgement about what the work requires. The risks are real risks, not padding dressed as risk. The worst case is what happens if specific named conditions materialise, not a buffer invented to protect the team.

When the same team produces an estimate in an environment where they have learned — through experience, through observation, through the institutional memory of previous programmes — that honest estimates will be challenged, compressed, and overridden, their estimation behaviour changes. Not because they become dishonest, but because they become rational.

In an environment where estimates are routinely challenged downward, an engineer who produces a genuinely honest estimate is making themselves a target. They will be asked to justify every week of contingency, every risk buffer, every assumption that inflates the number beyond what management wants to hear. If they hold their position, they will be perceived as obstructive. If they concede, they will have produced a number they do not believe in, against which they will be held accountable when it proves wrong.

The rational response, in that environment, is one of two things. Either produce a number that is high enough to survive the inevitable compression and still be achievable — which looks like sandbagging from the outside, because it is — or produce the number management wants to hear and manage the consequences when they arrive. Both responses are rational. Neither produces an honest estimate.

The sandbag assumption, when applied as a management tool, creates the sandbagging it claims to be correcting. And it destroys the honest estimation it depends on — because once an engineering team has learned that honest estimates are punished, they stop producing them.

---

### The authority-experience gap

There is a structural condition that makes the sandbag assumption both more common and more damaging than it would otherwise be. It is worth naming directly.

The people who govern engineering programmes — who set dates, approve budgets, review risk registers, and make the decisions that determine whether a programme succeeds or fails — frequently have not delivered the kind of programmes they are governing. They may have managed them, sponsored them, or been commercially accountable for them. They have not necessarily done the engineering work, written the firmware, designed the hardware, or integrated the system. They have not personally experienced what it takes to build what they are being asked to build.

This is not a criticism. Career paths in most organisations lead away from technical work rather than deeper into it. Engineers who are good at engineering get promoted into management. As they move up, they move away from the coal face. By the time they have the authority to make the decisions that matter, they have often been away from direct delivery for years. Their intuitions about what is possible and what is reasonable are based on a set of experiences that may no longer be current or relevant to the programme they are governing.

The result is an authority-experience gap: the people with the most authority over delivery decisions have the least direct experience of what delivery requires, and the people with the most current, accurate understanding of what delivery requires have the least authority to act on it.

This gap is not the only cause of the sandbag assumption — but it is one reason why the assumption persists even in the face of evidence that it is wrong. A leader who has never personally experienced the conditions under which engineering estimates are produced does not have the experiential reference point to distinguish between an estimate that has been padded for protection and an estimate that is honestly representing the complexity of the work. Both may look the same from a distance. The only reliable way to tell them apart is to understand the work — and that understanding takes time and proximity that many programme governors no longer have.

This does not mean that leaders without direct technical experience cannot govern engineering programmes well. Many do. The ones who do have something in common: they know what they do not know. They create the conditions for honest engineering input rather than overriding it. They treat the risk register as a decision instrument rather than a reporting artefact. They defer to engineering judgement on matters of technical complexity while exercising their own judgement on matters of commercial and strategic priority. They have developed, through observation and deliberate effort, a working model of how delivery actually functions — even if they have not personally experienced it.

The ones who struggle are not the ones who lack direct experience. They are the ones who do not know they lack it. Who mistake commercial confidence for delivery understanding. Who treat engineering estimates as negotiating positions because they have no framework for evaluating them differently. Who apply pressure because it has worked before — or appeared to work before — without understanding that what looked like pressure extracting performance was usually pressure transferring risk downward until it materialised somewhere too late to recover.

---

### What honest estimation looks like

If the sandbag assumption is wrong, and if pressure does not extract better estimates but instead destroys honest ones, then the question becomes: what does honest estimation actually look like, and how do you know when you are getting it?

Honest estimation has three properties that are often absent in organisations where the sandbag assumption prevails.

The first is that the estimate is produced by the people who will do the work. Not by a project manager working from a work breakdown structure. Not by a senior engineer extrapolating from a previous programme. By the people who understand the specific work, the specific system, the specific constraints, and the specific risks that apply to this programme. Estimation by proxy — by anyone who is not close enough to the work to understand what it actually requires — is not estimation. It is guessing with a spreadsheet.

The second is that the estimate comes in three points, not one. A single-point estimate is not an estimate. It is a commitment masquerading as an estimate, because it contains no information about the conditions that would need to be true for the number to be accurate. A three-point estimate — best case, most likely, worst case — contains that information. Best case is what happens if everything goes well, and the estimate should state explicitly what going well requires. Most likely is the genuine professional judgement of what this programme will take under realistic conditions. Worst case is what happens if the named risks materialise, and the estimate should state explicitly which risks, with what probability, would produce that outcome.

The third is that the estimate and the risk register are the same document, not two separate ones. The risks that could push the outcome from most likely to worst case are not a separate list to be reviewed and noted. They are the conditions attached to the estimate. Accepting the most likely estimate without accepting the risk register is not acceptance. It is selective reading. The programme board in Chapter 1 accepted the fourteen-month commitment while noting the risk register and moving on. That is not how the two documents work together. They are one document. You cannot accept the number without accepting the conditions.

---

### Breaking the cycle

The sandbag assumption is self-reinforcing, but it is not unbreakable. The organisations that have moved past it share a specific set of conditions.

Estimates are produced by the people who will do the work, from a genuine understanding of scope and context. They are three-point estimates with conditions and risks explicitly attached. They are presented to programme governance in a forum where the risks are treated as decision requests rather than reporting items. The response to a three-point estimate is not to compress the most likely case toward the best case. It is to make the decisions required to make the most likely case achievable — and to accept that if those decisions are not made, the outcome will trend toward worst case.

When this is the norm, something interesting happens to the estimates. They become more accurate. Not because engineers have stopped being conservative — but because engineers have stopped needing to be. The protection that sandbagging provides in a low-trust environment becomes unnecessary in a high-trust one. When an honest estimate will be accepted, used, and supported, there is no rational incentive to produce any other kind.

The organisations that apply pressure to estimates and believe it extracts better performance are conducting a slow and expensive experiment whose results have been available for decades. The lesson is consistent: pressure does not improve estimates. It improves the appearance of estimates while degrading their accuracy. The result is programmes that look controlled on paper and fail in reality — exactly as described in Chapter 1.

---

### A note on genuine sandbagging

It would be dishonest to claim that sandbagging never occurs. It does. In low-trust environments where engineers have learned that honest estimates are punished, some engineers do pad their numbers as rational self-protection. This is the behaviour that the sandbag assumption claims to be correcting.

The problem is that applying pressure to a sandbagged estimate produces the right outcome for the wrong reason in the short term, and the wrong outcome for any reason in the long term. It may extract a more aggressive commitment. It does not change the underlying conditions — the scope, the risks, the complexity — that produced the padded estimate. The commitment is lower. The programme is not faster. The gap between the two is the risk that was never managed.

The correct response to sandbagging is not pressure. It is the creation of conditions where sandbagging is unnecessary — where honest estimates are accepted, where risk registers generate decisions rather than notes, and where the people making the commitments are the people who have to keep them.

When those conditions exist, estimates become more accurate, programmes become more predictable, and the belief that engineers are sandbagging becomes harder to sustain — because the evidence that previously appeared to support it no longer accumulates.

---

### The next step

The sandbag assumption is a belief about engineers. What this chapter has argued is that it is primarily a belief about the wrong thing — that it looks at the behaviour of engineers and sees character where it should see structure.

Engineers produce inflated estimates when the system makes honest estimation irrational. They produce accurate estimates when the system makes honest estimation safe. The variable is not the engineer. The variable is the system.

The next chapter examines the specific structural mechanism that most commonly makes honest estimation unsafe: the commitment that arrives from above, already made, by people who were not in the room when the work was assessed and will not be in the room when the consequences arrive.
