---
title: Post-Mortem / Incident Review - [Incident ID/Title]
status: Draft / Under Review / Finalised
date: YYYY-MM-DD (Date of Review)
incident_start_time: YYYY-MM-DD HH:MM [Timezone]
incident_end_time: YYYY-MM-DD HH:MM [Timezone]
incident_duration: [e.g., 2 hours 30 minutes]
author: [Name or Role of Post-Mortem Lead]
reviewers: [List of key reviewers/stakeholders]
version: 1.0
---

# 🔍 Post-Mortem / Incident Review: [Incident ID/Title]

This document details the analysis of Incident ID: [Incident ID, e.g., INC-2025-07-18-001], which occurred on [Date of Incident]. The purpose of this review is to understand the incident thoroughly, identify its root causes, and define actionable improvements to prevent recurrence and enhance system resilience. This is a blameless review focused on learning and systemic improvement.

---

## 1. Incident Summary

### 1.1 Incident Title

[A concise, descriptive title for the incident.]

### 1.2 Incident ID

[Unique identifier for the incident, e.g., from your incident management system.]

### 1.3 Date and Time of Incident

* **Start:** YYYY-MM-DD HH:MM [Timezone]
* **End:** YYYY-MM-DD HH:MM [Timezone]
* **Duration:** [e.g., 2 hours 30 minutes]

### 1.4 Services/Components Affected

[List all services, components, or systems that were impacted by the incident.]

* [Service/Component 1]
* [Service/Component 2]

### 1.5 Impact

[Describe the business and customer impact of the incident. Quantify where possible.]

* **Customer Impact:** [e.g., "50% of users experienced login failures," "Data for X customers was temporarily unavailable."]
* **Business Impact:** [e.g., "Loss of revenue for 2 hours," "Reputational damage," "Violation of SLA."]
* **Operational Impact:** [e.g., "Increased load on support team," "Engineers pulled from planned work."]

## 2. Incident Timeline

[Provide a chronological sequence of events, including detection, diagnosis, and resolution. Include timestamps and responsible parties.]

| Time (HH:MM [Timezone]) | Event Description | Responsible Party |
|-------------------------|-------------------|-------------------|
| HH:MM                   | [e.g., Monitoring alert triggered for high error rates on Auth Service.] | Monitoring System |
| HH:MM                   | [e.g., On-call engineer (Jane Doe) acknowledges alert.] | Jane Doe          |
| HH:MM                   | [e.g., Jane Doe investigates logs, identifies unusual traffic patterns.] | Jane Doe          |
| HH:MM                   | [e.g., Team lead (John Smith) notified, joins incident call.] | John Smith        |
| HH:MM                   | [e.g., Decision made to roll back recent deployment of Auth Service v1.2.] | John Smith        |
| HH:MM                   | [e.g., Rollback completed, error rates return to normal.] | Jane Doe          |
| HH:MM                   | [e.g., Incident declared resolved.] | John Smith        |

## 3. What Happened? (Narrative)

[A detailed narrative description of the incident from start to finish, explaining the sequence of events without immediate judgment or root cause analysis. Focus on facts.]

## 4. Why Did It Happen? (Root Cause Analysis)

[Identify the underlying causes of the incident. Use a structured technique like "5 Whys," Fishbone Diagram, or Fault Tree Analysis. Distinguish between symptoms and root causes.]

* **Root Cause 1:** [e.g., "Insufficient validation of input parameters in Auth Service v1.2."]
    * *Why:* [e.g., "Developer assumed input would always be valid based on previous version."]
    * *Why:* [e.g., "No automated integration test covered this specific edge case."]
* **Root Cause 2:** [e.g., "Lack of clear rollback procedure for Auth Service deployments."]
    * *Why:* [e.g., "Focus was on forward deployment, not rapid recovery."]
* **Contributing Factors:** [Any other factors that exacerbated the incident.]
    * [e.g., "Monitoring alert threshold was too high, delaying detection."]

## 5. What Went Well?

[Identify aspects of the incident response that were effective or positive. What did the team do well?]

* [e.g., "Quick response time from on-call engineer."]
* [e.g., "Effective communication within the incident response team."]
* [e.g., "Good collaboration with external dependency team."]

## 6. What Could Be Improved?

[Identify areas where the incident response or system could be improved. This should directly lead to action items.]

* [e.g., "Faster detection through more granular monitoring."]
* [e.g., "Better validation in code to prevent similar issues."]
* [e.g., "Clearer and automated rollback procedures."]
* [e.g., "More comprehensive testing, especially for edge cases."]

## 7. Action Items

[List specific, actionable tasks derived from the "What Could Be Improved?" section. Each action item should have an owner and a target completion date.]

| Action Item ID | Description | Owner | Target Date | Status |
|----------------|-------------|-------|-------------|--------|
| **PM-AI-001** | Implement input validation for Auth Service API endpoint `/login`. | Jane Doe | YYYY-MM-DD | Open   |
| **PM-AI-002** | Create automated integration test for Auth Service login edge cases. | John Smith | YYYY-MM-DD | Open   |
| **PM-AI-003** | Document and automate rollback procedure for Auth Service deployments. | Alice Brown | YYYY-MM-DD | Open   |
| **PM-AI-004** | Review and adjust monitoring alert thresholds for Auth Service error rates. | Bob White | YYYY-MM-DD | Open   |

## 8. Lessons Learned

[Summarize the key takeaways and learnings from this incident. These should be broader insights that can be applied across the organization or to future projects.]

* [e.g., "The importance of robust input validation, even for seemingly 'safe' inputs."]
* [e.g., "Prioritizing rapid rollback capabilities is as important as rapid deployment."]
* [e.g., "Continuous improvement of monitoring is crucial for early detection."]

## 9. Communication Plan (Post-Incident)

[How will the findings of this post-mortem be communicated to relevant stakeholders?]

* [e.g., "Summary shared with Product Management and Senior Leadership."]
* [e.g., "Full post-mortem shared with all engineering teams."]
* [e.g., "Key learnings presented in a 'Lunch & Learn' session."]

## 10. References

[List any relevant incident tickets, logs, code changes, or other documents.]
