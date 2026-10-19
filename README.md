# The APC + Local Agent Orchestration Framework

> A battle-tested, project-agnostic architecture for pairing high-reasoning external AI planners with autonomous local coding agents, coordinated by a human operator through git and markdown.

---

## 1. Executive Summary & Core Philosophy

Large language models excel at different things depending on their execution environment:

| Entity | Strengths | Constraints | Role |
| :--- | :--- | :--- | :--- |
| **APC AI** *(Analyzer, Planner, Controller)* | Macro-architecture, reasoning, cross-task consistency, edge-case analysis. | **No filesystem access**, no bash execution, context window limits, session reset upon credit exhaustion. | **Strategic Director** |
| **Local Coding Agents** *(Claude Code, Gemini, opencode, Cursor)* | Direct filesystem access, shell execution, fast refactoring, test execution. | **Zero memory across invocations**, prone to local optimization, prone to drift without strict specs. | **Tactical Implementer** |
| **Human Operator** *(You)* | Git merges, architectural gating, budget policing, physical relay. | Context-switching fatigue if forced to read endless walls of full code. | **Air-Traffic Controller** |

### The Core Problem This Solves
In complex projects, single-agent workflows degrade over time: context windows fill with noisy terminal output, past architectural decisions are forgotten or contradicted, and agents hallucinate file states.

The **APC + Local Agent Framework** solves this through **asymmetric separation of concerns**, anchored entirely in the **Git repository as the sole source of truth**.

```
           +---------------------------------------------+
           |                   APC AI                    |
           |        (Analyzer, Planner, Controller)      |
           |  • High-level reasoning  • Task planning   |
           |  • Architectural review  • No filesystem    |
           +----------------------+----------------------+
                                  |
               Writes Standalone  |  Uploads Verified Bundles
               Task Prompts       |  & Unified Diffs
                                  v
           +---------------------------------------------+
           |                Human Operator               |
           |  • Relays prompts    • Reviews git diffs    |
           |  • Merges worktrees  • Enforces gates       |
           +----------------------+----------------------+
                                  |
               Launches Tasks in  |  Returns Reports
               Isolated Worktrees |  & Clean Diffs
                                  v
           +---------------------------------------------+
           |             Local Coding Agents             |
           |     (Claude Code, Gemini, opencode, CLI)    |
           |  • Full filesystem access • Runs tests      |
           |  • Zero cross-session mem • Writes diffs    |
           +---------------------------------------------+
                                  |
                                  v
           +---------------------------------------------+
           |        Repository (Sole Source of Truth)    |
           |  • complete-context.md   • status.md        |
           |  • decision-log.md       • docs/reports/    |
           |  • Source Code           • Automated Tests  |
           +---------------------------------------------+
```

---

## 2. The Three Cardinal Axioms

### Axiom 1: The Repository is the Sole Source of Truth (SSOT)
Neither the APC AI nor the local agents have persistent memory. Chat transcripts, ephemeral scratchpads, and AI claims are not authoritative. **If a finding, decision, or contract is not written to disk in git, it does not exist.** If the APC AI's memory conflicts with what is on disk, the disk is right.

### Axiom 2: Send Deltas, Not Full Files
Full-file pastes destroy context windows, obscure changes, and invite phantom merge conflicts. All updates to shared documents, specifications, and code must be communicated as standard **unified git diffs (`git diff`)** or targeted before/after excerpts.

### Axiom 3: Isolated Worktrees for Parallel Tasks
Local agents running concurrent tasks must never collide on the same working tree. Concurrent work operates in dedicated git worktrees (`task/<TASK-ID>`) branched from master/main.

---

## 3. Directory Structure & File Map

```text
├── AGENTS.md                                # Operational constitution for local coding agents
├── docs/
│   ├── context/
│   │   ├── complete-context.md              # North Star project orientation & architecture
│   │   ├── apc-handoff-template.md          # Inter-session APC handoff document
│   │   ├── apc-bundle-quickref.md           # Quick reference for bundle packaging
│   │   └── repo-tree.txt                    # Auto-generated repository file map
│   ├── tasks/
│   │   ├── high-level-tasks.md              # Macro roadmap, phases & milestone exit gates
│   │   └── status.md                        # Live single-pane-of-glass per-task status tracker
│   ├── decisions/
│   │   └── decision-log.md                  # Append-only immutable decision records ([D-01]...)
│   ├── reports/                             # Unit-of-work audit reports (one per task)
│   │   └── TASK-TEMPLATE.md                 # Standard task report template
│   ├── prompts/                             # Standalone task prompts sent to agents
│   │   └── STANDALONE-PROMPT-TEMPLATE.md    # Template for task prompts
│   └── guide/                               # Guides for developers and collaborators
│       └── COLLABORATOR-GUIDE.md            # Onboarding & workflow guide for contributors
├── patch/                                   # Standalone exported patch files (<TASK-ID>-*.patch)
├── scripts/
│   ├── apc-bundle.sh                        # Safe context packager with secret guards & manifest
│   ├── task-worktree.sh                     # Helper script enforcing worktree rules
│   ├── validate-report.py                   # Automated report linter and alignment checker
│   ├── manage-decisions.py                  # Decision ID reservation and check utility
│   └── README.md                            # Script guide
```

---

## 4. The End-to-End Operational Loop

```
       [Phase Plan in high-level-tasks.md]
                       │
                       ▼
       [APC drafts Standalone Task Prompt]
         (Allocates Task ID & Decision ID)
                       │
                       ▼
       [Human pastes prompt to Local Agent]
         (In dedicated task worktree)
                       │
                       ▼
       [Local Agent Implements, Verifies & Packages]
         1. Reads complete-context.md, status.md & verifies facts
         2. Executes tests (e.g. pytest, npm test, cargo test)
         3. Commits unit of work: git commit -m "<type>(<ID>): ..."
         4. Exports patch file: patch/<ID>-<agent>-<slug>.patch
         5. Writes report: docs/reports/<ID>-<agent>-<slug>.md
         6. Logs decision [D-xx] & updates docs/tasks/status.md
         7. Runs validation: ./scripts/validate-report.py
         8. Builds fresh bundle if needed: ./scripts/apc-bundle.sh
                       │
                       ▼
       [Human audits worktree: ./scripts/task-worktree.sh handoff <ID>]
                       │
                       ▼
       [Human relays report, patch & diff to APC AI]
                       │
                       ▼
       [APC verifies against acceptance criteria & merges]
         (Accepts task or issues FIX-xxx)
                       │
                       ▼
       [When APC context limits approach: Handoff]
         (Fills apc-handoff-template.md for next APC)
```

---

## 5. Bootstrapping a New Project

### Quickstart (Automated via Python Scaffolder)

Run the included `setup-apc-framework.py` script:

```bash
# Interactive setup:
python3 apc-framework-kit/setup-apc-framework.py --target-dir /path/to/my-repo

# Non-interactive CLI setup:
python3 apc-framework-kit/setup-apc-framework.py \
  --target-dir /path/to/my-repo \
  --project-name "Acme Analytics Engine" \
  --project-slug "acme-analytics" \
  --project-desc "High-performance streaming analytical database in Rust" \
  --operator-name "Alice" \
  --src-dir "crates" \
  --test-cmd "cargo test" \
  --non-interactive
```

### Manual Setup
1. Copy `templates/` into your repository, removing `.template` suffixes.
2. Search and replace placeholders:
   - `{{PROJECT_NAME}}`: e.g. "Acme Analytics"
   - `{{PROJECT_SLUG}}`: e.g. "acme-analytics"
   - `{{PROJECT_DESCRIPTION}}`: Project synopsis
   - `{{OPERATOR_NAME}}`: Human operator name
   - `{{SRC_DIR}}`: Source code directory
   - `{{TEST_RUNNER_CMD}}`: Test command (e.g., `pytest`, `cargo test`, `npm test`)
3. Make scripts executable: `chmod +x scripts/*.sh`
4. Commit initial governance files to git.

---

## 6. Recommended Agent Role Split

- **Claude Code (Lead Implementer):** Complex code refactoring, system architecture, core harness building, and end-to-end integration.
- **Gemini (Independent Auditor / Reviewer):** Verification, test suite hardening, edge-case discovery, and cross-checking claims against filesystem truth. Using a different model lineage provides genuine diversity of perspective.
- **Opencode / Cursor (Specialized Subtasks):** Modular components, test generation, and documentation alignment.

---

## 7. Operational Tooling & Guardrails (Built-In)

Drawing from hundreds of hours of production experience with this setup, the framework includes dedicated tooling to eliminate manual friction and enforce contracts:

### 1. Worktree Automation (`scripts/task-worktree.sh`)
- **Automates parallel agent isolation:** Creates dedicated task worktrees (`./scripts/task-worktree.sh start <TASK-ID>`).
- **Verbatim diff extraction:** Extracts clean git diffs with index lines (`./scripts/task-worktree.sh diff <TASK-ID>`).
- **Pre-handoff auditing:** Runs audit checks and report validation before merging (`./scripts/task-worktree.sh handoff <TASK-ID>`).

### 2. Token-Aware Bundling (`scripts/apc-bundle.sh --tokens`)
- Estimates bundle token weight prior to archive generation, preventing silent truncation or degradation in context-limited models.

### 3. Automated Report Linter & Verification (`scripts/validate-report.py`)
- Verifies report naming pattern: `<TASK-ID>-<agent-name>-<short-slug>.md`.
- Enforces presence of Executive Summary, Implementation Details, Verification, and Git Diff sections.
- Validates cross-file alignment with `docs/tasks/status.md` and `docs/decisions/decision-log.md`.

### 4. Decision ID Collision Prevention (`scripts/manage-decisions.py`)
- Queries next sequential Decision ID (`./scripts/manage-decisions.py next`).
- Reserves IDs explicitly (`./scripts/manage-decisions.py reserve --title "..."`).
- Checks ID availability to guarantee no two agents claim the same `[D-xx]` tag.

### 5. Bidirectional Diff Contract
- Enforced in `STANDALONE-ADOPTION-PROMPT.md`: Both local agents and the APC AI communicate modifications as standard unified diffs or targeted snippets, preserving context windows in both directions.

