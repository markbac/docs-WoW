# About This Documentation Site 📚

This documentation follows the **Docs as Code** philosophy, emphasizing traceability and lightweight, meaningful content. As we deal with complex systems, knowing the exact source of documentation is crucial for architectural traceability, especially in real-time, embedded, and defence domains.

## Build and Version Information

This data is dynamically injected at build time via a Python hook, ensuring this page and the PDF cover reflect the precise state of the repository when the documentation artifact was generated.

Detail

Value

**Generated On (UTC)**

`{{ config.extra.build_metadata.generated_on }}`

**Git Commit Hash (Short)**

`{{ config.extra.build_metadata.git_hash }}`

**Local Changes Present**

`{{ config.extra.build_metadata.dirty_status }}`

**MkDocs Version**

`{{ config.extra.build_metadata.mkdocs_version }}`

**Repository URL**

\[{{ config.repo\_url }}\]({{ config.repo\_url }})

**MkDocs Theme**

Material for MkDocs

## Toolchain & Contribution

This site is generated using the following key tools and practices. We champion the use of open and standard approaches to improve process, system architecture, and collaboration across teams.

-   **Primary Tool:** **MkDocs** (version `{{ config.extra.build_metadata.mkdocs_version }}`)
    
-   **Theme:** **Material for MkDocs**
    
-   **Modeling:** The site supports diagrams using **PlantUML** and **Mermaid** for architectural clarity (leveraging C4 model principles).
    
-   **Source Repository:** \[Source Code on GitHub\]({{ config.repo\_url }})
    
-   **Contributing:** We encourage contributions! The "Docs as Code" approach means documentation lives next to code. Please refer to the repository contribution guidelines for details on submitting changes and new templates.
    

## Licensing

The source code and content for this documentation is released under the license included below.

    {{ config.extra.build_metadata.license_content }}


