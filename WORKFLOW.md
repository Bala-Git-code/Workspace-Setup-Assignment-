# Team GitHub Workflow and Engineering Standards

This document establishes the collaborative engineering workflow, branching strategy, commit conventions, code review process, and issue-tracking guidelines for our data product team. Adhering to these standards prevents merge conflicts, maintains data pipeline integrity, and ensures complete traceability of all codebase changes.

---

## 1. Branching Strategy

Our team enforces a structured Git branching strategy to keep production stable while allowing independent feature development.

- **Main Branch (`main`)**: 
  - Holds production-ready, releasable code only.
  - Direct commits to `main` are strictly prohibited.
  - All changes enter `main` exclusively through approved Pull Requests.

- **Feature & Task Branches**:
  - All work takes place on isolated topic branches created from `main`.
  - Naming Convention: `[type]/[short-description]`
    - Examples: `feature/data-ingestion`, `fix/validation-logic`, `docs/data-dictionary`, `chore/dependency-update`
  - Allowed Branch Types: `feature`, `fix`, `docs`, `refactor`, `chore`, `test`

- **Branch Lifecycle & Cleanup**:
  - Branches must be kept up-to-date with `main` before submitting a PR.
  - Branches must be deleted immediately after their corresponding PR is successfully merged to prevent clutter.

---

## 2. Commit Message Convention

We adhere to the **Conventional Commits** specification to ensure clear git history and facilitate automated changelog generation.

### Format
```text
[type]: [description]

[optional body explaining why this change was made]
```

### Allowed Types
| Type | Purpose | Example |
| :--- | :--- | :--- |
| `feat` | Adding a new feature or analytical capability | `feat: add data validation function` |
| `fix` | Resolving a bug or data handling issue | `fix: resolve null check exception in ingestion` |
| `docs` | Documentation updates | `docs: document team github workflow and conventions` |
| `refactor` | Code reorganization without functional changes | `refactor: clean up pipeline transformation steps` |
| `test` | Adding or updating tests | `test: add unit tests for schema validator` |
| `chore` | Maintenance, configuration, or dependency changes | `chore: update requirements.txt with validation library` |

### Why Conventional Commits?
- **Auditing & Context**: Provides immediate clarity on what was changed and why.
- **Automation**: Enables automated semantic versioning and changelog generation.
- **Review Efficiency**: Helps reviewers quickly scan pull request history.

---

## 3. Pull Request (PR) & Code Review Process

Pull Requests serve as the primary mechanism for code quality assurance and collaborative review.

- **Submission Requirements**:
  - Every PR must target `main` from a properly named topic branch.
  - PR title must be clear and action-oriented (e.g., `Add data validation workflow and team branching guidelines`).
  - PR description must include:
    1. **Summary & Rationale**: Explanation of what changed and why.
    2. **Issue Linking**: Uses closing keywords (e.g., `Closes #1` or `Fixes #2`) to link related issues.
    3. **Commit Summary**: Itemized list of commits included in the PR.
    4. **Verification & Testing**: Summary of automated tests or manual verification conducted.

- **Review Criteria**:
  - **Review Approvals**: PRs require at least **one approval** from a team member before merging.
  - **Code Review Focus**:
    - **Correctness & Logic**: Code behaves as expected without edge-case failures.
    - **Clarity & Readability**: Clean structure, maintainable code, and inline documentation where appropriate.
    - **Data Integrity**: Schemas, transformations, and missing data logic are safely handled.
    - **Test Coverage**: Appropriate unit tests or validation scripts accompany functional changes.
    - **Commit Message Consistency**: Commit history is verified as part of the code review.

---

## 4. GitHub Issue Tracking Approach

We maintain full transparency and task traceability using GitHub Issues.

- **Issue Creation**:
  - Every new feature, bug fix, analytical task, or documentation initiative must begin with a dedicated GitHub Issue.
- **Required Metadata**:
  - **Title**: Action-oriented and descriptive (e.g., `Ingest customer transaction data into pipeline`).
  - **Description**: Must specify **why** the work matters and explicitly define **what done means** (Definition of Done).
  - **Labels**: At least one appropriate label applied (e.g., `enhancement`, `documentation`, `bug`).
  - **Assignee**: Must be assigned to the responsible developer.
- **Closing Issues**:
  - Issues are automatically closed when the associated PR is merged into `main` using keywords like `Closes #<issue_number>`.

---

## 5. Production Python Data Workflow Script Execution

Our production data pipeline is implemented as a modular script in `scripts/data_workflow.py`. This replaces interactive notebook exploration with reproducible, command-line executable code suitable for automated scheduling and CI/CD pipelines.

### How to Execute the Script
Execute the script from the project root directory using Python:
```bash
python scripts/data_workflow.py
```
Alternatively, navigate to the `scripts/` directory and execute:
```bash
cd scripts
python data_workflow.py
```

To capture execution confirmation metrics into an audit file:
```bash
python scripts/data_workflow.py > output/sample_run.txt
```

### Function Breakdown & Separated Concerns

1. **Ingestion Stage (`ingest_data`)**:
   - **Purpose**: Reads raw datasets from CSV or JSON files into a Pandas DataFrame.
   - **Path Resolution**: Handles relative paths seamlessly whether executed from root or subdirectories.
   - **Input**: Filepath string (`filepath`).
   - **Returns**: Loaded Pandas `DataFrame`.

2. **Transformation Stage (`process_data`)**:
   - **Purpose**: Cleans, standardizes, and enriches raw records into analysis-ready format.
   - **Transformations**:
     - Deduplicates records (`drop_duplicates()`).
     - Imputes missing numerical values using column median metrics.
     - Standardizes text and categorical string columns.
     - Computes derived business metrics (e.g., tax-adjusted transaction amounts).
   - **Input**: Raw Pandas `DataFrame`.
   - **Returns**: Cleaned, transformed Pandas `DataFrame`.

3. **Output & Reporting Stage (`output_results`)**:
   - **Purpose**: Saves processed results to disk and outputs confirmation metrics.
   - **Directory Management**: Creates target output directories automatically if missing.
   - **Input**: Processed `DataFrame` and target `output_path`.
   - **Outputs**: Writes CSV to disk and prints formatted success status:
     ```text
     ✓ Data successfully processed
     ✓ Rows processed: <count>
     ✓ Output saved to <output_path>
     ```

### How to Adapt the Workflow for New Datasets
- **New Data Sources**: Update the input file path in the `if __name__ == "__main__":` block or pass custom arguments to `ingest_data(new_filepath)`.
- **Custom Business Logic**: Modify `process_data(df)` to add domain-specific filtering, custom column calculations, or aggregation rules.
- **Alternative Export Formats**: Extend `output_results(df, output_path)` to export to Parquet, SQL databases, or cloud storage endpoints as pipeline requirements evolve.

---

*Documented for team collaboration and workflow consistency.*
