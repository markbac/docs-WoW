# 🚀 Our Ways of Working: Engineering Leadership & Product Delivery

Welcome to the "Ways of Working" repository! This space is dedicated to documenting our evolving philosophy and frameworks for effective engineering leadership and product development. Here, you'll find principles, guidelines, and practical approaches designed to help our teams think clearly, build effectively, and deliver meaningful outcomes.

We believe in lightweight, meaningful documentation and embrace the **"Docs as Code"** approach, ensuring our practices are living, version-controlled, and integrated into our workflows.

### The Philosophy and The Framework 🧠➡️🛠️

It can seem a bit strange to have two documents covering what appears to be the same topic. From a solution architect's perspective, this split is intentional and crucial:

* [**An Approach to Engineering Leadership and Delivery**](https://www.google.com/search?q=An-Approach-to-Engineering-Leadership-and-Delivery.md "null") is our **Foundational Philosophy**. It’s the "what" and the "why." This document sets the high-level principles and vision. It's our guiding map, ensuring everyone understands the values that drive our decisions, regardless of the specific project or technology. Without this shared philosophy, any framework we adopt would just be a list of rules without purpose.

* [**Cornerstone**](https://www.google.com/search?q=cornerstone_framework.md "null") is our **Practical Framework**. It’s the "how." This is the detailed, actionable blueprint that puts the philosophy into practice. It provides the specific processes, team structures, and artifacts (like ADRs and RTMs) needed to build complex products. It's the detailed itinerary that helps us navigate the real world, complete with clear steps and contingency plans.

Together, they create a powerful combination: a clear strategic direction grounded in core values, with a flexible, pragmatic approach for real-world delivery.

## 🌟 Our Core Philosophy: An Integrative Approach to Engineering Leadership and Delivery

At the heart of our "Ways of Working" is an **integrative philosophy** that synthesizes insights from leading thinkers in leadership, systems engineering, and software architecture. This foundational document, [An Approach to Engineering Leadership and Delivery](https://www.google.com/search?q=An-Approach-to-Engineering-and-Delivery.md "null"), outlines *what* matters and *why* these elements are critical for effective engineering.

It focuses on key tenets like:

* **Leading with Context, Not Control:** Emphasising purpose, autonomy, mastery, psychological safety, and sustainability.

* **Architectural Thinking:** Promoting simplicity, modularity, lightweight governance, and an evolutionary approach.

* **Process: Structure Without Bureaucracy:** Advocating for Docs-as-Code, data-informed decisions, and iterative delivery.

* **Teams as Systems:** Organising for flow with stream-aligned, enabling, and platform teams.

* **Outcomes, Not Outputs:** Shifting focus to delivering tangible value for users and the business.

* **Partnering with the Business:** Fostering transparent roadmapping and strategic collaboration.

* **Sustainability, Resilience, and Incident Management:** Building systems and cultures that learn and adapt.

* **Strategy and Portfolio-Level Thinking:** Ensuring engineering efforts scale sustainably.

* **Navigating Inherent Tensions:** Understanding and resolving conflicts between principles for systemic health.

This document serves as our guiding star, providing the philosophical underpinning for all our practical frameworks.

## 🌉 Cornerstone: A Hybrid Delivery Framework for Product Development

[Cornerstone](https://www.google.com/search?q=cornerstone_framework.md "null") introduces "Cornerstone," our comprehensive framework designed to navigate the complexities of modern product development, especially for integrated products involving software, firmware, hardware, and mechanical components.

Cornerstone is a pragmatic synthesis, blending the rigour of the V-model with the adaptability of Agile. It's about finding the "sweet spot" for integrated product development, ensuring predictability and traceability while maintaining agility and responsiveness.

### How We Organise for Flow in Cornerstone

Cornerstone champions the use of different team types to optimise for value delivery and reduce cognitive load. Here's a visual of how these teams interact:

```
graph TD
    A[Product Manager] --> B(Stream-Aligned Team A)
    A --> C(Stream-Aligned Team B)
    B --> D[Platform Team]
    C --> D
    D --> E[Shared Tooling/Services]
    B --> F[Customer]
    C --> F
    
    subgraph Stream-Aligned Teams
        B
        C
    end
    
    subgraph Enabling/Platform Teams
        D
    end
```

* **Core Principles:** Operationalising concepts like iterative product evolution, continuous verification, cross-functional collaboration, and adaptive planning.

* **Living Artifacts:** Practical guidance on implementing **"Docs as Code"** for key documents like Architecture Decision Records (ADRs), Interface Control Documents (ICDs), and Requirements Traceability Matrices (RTMs).

**Note:** The `cornerstone_framework.md` file is currently a comprehensive outline. As this repository develops, this content will be split into multiple, more focused markdown files for better organisation and maintainability.

## 🔮 Our Roadmap: What's Next?

Our "Ways of Working" are continuously evolving. Here's what's on the horizon for this repository.

### Practical Guides & Templates 📝

We will break down the `cornerstone_framework.md` outline into detailed, focused guides for specific topics and provide ready-to-use templates for key artifacts. This will make it easier for teams to adopt our practices and maintain consistent, lightweight documentation.

Some of the guides we'll be adding include:

* **Iterative Product Evolution:** Guides on structuring and executing iterative cycles for multi-disciplinary teams.

* **Continuous Verification & Validation:** Strategies for shifting testing left and integrating it throughout the lifecycle.

* **Docs as Code Implementation:** Detailed workflows for version-controlling, generating, and publishing documentation.

* **Managing Complex Dependencies:** Strategies for mapping and tracking dependencies, especially with long hardware lead times.

* **Tailoring Cornerstone:** How to adapt the framework for different business contexts, product complexities, and regulatory environments (Lightweight, Balanced, Heavyweight).

We'll also create templates for:

* **Architecture Decision Records (ADRs):** To capture and communicate critical architectural choices.

* **C4 Model Diagrams:** Guidelines for creating Context, Container, Component, and Code diagrams.

* **Requirements Traceability Matrix (RTM) Snippets:** To ensure end-to-end traceability.

* **Interface Control Documents (ICDs):** For defining clear interfaces between interconnected components.

* **Risk Register:** A living document for tracking identified risks and mitigation strategies.

### Tooling & Ecosystem Guides 🛠️

We'll provide recommendations and setup guides for the tools that support our ways of working. These guides will focus on how to integrate the tools within the Cornerstone framework to create a seamless development ecosystem.

We'll cover:

* **Version Control Systems (Git):** Advanced branching strategies for managing all artifacts (code, documentation, design files).

* **CI/CD:** Setting up pipelines for automated builds, tests (software, firmware, hardware), and documentation publishing.

* **Documentation & Modeling Toolchain:** How to use Markdown editors, Static Site Generators (e.g., MkDocs), and diagramming tools (Mermaid, PlantUML) for living documentation.

We aim for this repository to be a continuously evolving resource, reflecting our commitment to learning and improvement.

## 📂 Repository Contents

* [An Approach to Engineering Leadership and Delivery](https://www.google.com/search?q=An-Approach-to-Engineering-Leadership-and-Delivery.md "null"): Our foundational philosophy on engineering leadership and delivery.

* [Cornerstone](https://www.google.com/search?q=cornerstone_framework.md "null"): The detailed outline for the Cornerstone hybrid delivery framework.

* [LICENSE](https://www.google.com/search?q=LICENSE.txt "null"): The licensing information for this repository.

## 🤝 Contributions & Feedback

This repository is a living document! We welcome feedback, suggestions, and contributions to refine and expand our "Ways of Working." If you have ideas or insights, please feel free to open an issue or submit a pull request.

## 📄 License

This repository is licensed under the MIT License. See the [LICENSE](https://www.google.com/search?q=LICENSE.txt "null") file for full details.
