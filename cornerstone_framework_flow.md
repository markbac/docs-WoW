# Cornerstone framework flow

```puml
@startuml
!theme cerulean
skinparam activityFontSize 14
skinparam activityArrowFontSize 12
skinparam defaultFontName "Arial"

title Cornerstone Lifecycle - Simplified View

start

|Product Owner|
:Define product vision and goals;
:Gather and refine high-level requirements;
:Prioritise program backlog;

|Solution Architect|
:Create system architecture (C4 Context/Container);
:Document architectural guardrails and key decisions (ADRs);
:Review high-level requirements;

|All Disciplines (Dev, QA)|
:Conduct trade-off analysis on technologies;
:Approve initial project scope and design;
note right
  **Transition Gate 1:**
  A "check-in" to confirm a solid
  foundation before development starts.
end note

|Development Teams|
repeat
  :Break down features into stories;
  :Detailed design & implementation;
  :Build, test & integrate increment;
  :Refine detailed requirements;
  :Provide continuous feedback;
  note right
    The Iterative Core:
    This is where agile principles live,
    with continuous feedback loops and
    lightweight documentation.
end note
repeat while (Are features delivered and integrated?) is (no)

|Quality Assurance|
:Execute formal system-level tests;
:Conduct user acceptance testing;

|Product Owner|
:Validate product against vision;
:Accept final deliverables;
note right
  **Transition Gate 2:**
  Final readiness check before release.
end note

|Program Management|
:Prepare for product release;
:Launch and monitor product in the market;

|All Disciplines|
:Gather feedback from production;
:Use data to inform next iteration;

stop

@enduml
```
