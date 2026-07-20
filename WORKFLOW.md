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

*Documented for team collaboration and workflow consistency.*
