# Contributing to Mini SQL Compiler

Welcome to the **Mini SQL Compiler** project repository! This guide provides clear, step-by-step instructions for team members to collaborate, create feature branches, commit code and documentation, and submit Pull Requests (PRs) following standard academic software engineering practices.

---

## 1. Core Collaboration Principles
- **Protected `main` Branch:** Never commit or push directly to `main`. All changes must be developed in a dedicated feature/documentation branch and merged via a reviewed Pull Request.
- **Traceability:** Every branch and PR must reference its corresponding GitHub Issue number (e.g., `closes #3`).
- **Clean Sync:** Always synchronize your local repository with `origin/main` before creating a new branch.

---

## 2. Branch Naming Conventions
Use descriptive, hyphen-separated branch names prefixed by the task category:

| Prefix | Usage Category | Example |
| :--- | :--- | :--- |
| `docs/` | Documentation, grammar specs, reports | `docs/project-readme`, `docs/sql-specification` |
| `test/` | Test suites, test matrices, fixtures | `test/valid-queries`, `test/invalid-queries` |
| `feature/` | Core compiler implementation | `feature/lexer-engine`, `feature/ast-nodes` |
| `fix/` | Bug fixes or diagnostic corrections | `fix/cli-banner-font`, `fix/lookahead-parsing` |

---

## 3. Git CLI Workflow (Command Line)

### Step 1: Sync with Latest `main`
```bash
git checkout main
git pull origin main
```

### Step 2: Create and Switch to a New Branch
```bash
git checkout -b docs/my-task-topic
```

### Step 3: Implement Your Changes & Check Status
```bash
git status
```

### Step 4: Stage and Commit Changes
Write clear, conventional commit messages:
```bash
git add path/to/file.ext
git commit -m "docs: establish project documentation structure (closes #3)"
```

### Step 5: Push Branch to GitHub
```bash
git push -u origin docs/my-task-topic
```

### Step 6: Create Pull Request via GitHub CLI or Web
Using GitHub CLI:
```bash
gh pr create --title "docs: establish documentation structure" --body "Closes #3" --base main
```
Or navigate to the repository on GitHub and click **Compare & pull request**.

---

## 4. GitHub Web Interface Workflow (No Terminal Required)
For documentation tasks where you prefer working directly in your browser:
1. Navigate to the repository page: `https://github.com/geo-cherian-mathew-2k28/Mini-SQL-Compiler`.
2. Browse to the file you want to edit or click **Add file** -> **Create new file**.
3. At the bottom of the editor under **Commit changes**:
   - Write a descriptive commit summary.
   - Select **"Create a new branch for this commit and start a pull request"**.
   - Name your branch according to convention (e.g., `docs/report-draft`).
4. Click **Propose changes** / **Create pull request**.

---

## 5. Pull Request & Review Checklist
Before marking your PR as ready for review:
- [ ] Code or markdown files adhere to project formatting standards.
- [ ] All unit tests pass: `python -m unittest discover tests`.
- [ ] The PR description references the related GitHub Issue (e.g., `Closes #3`).
- [ ] No extraneous temporary files or IDE folders (`.vscode/`, `__pycache__/`) are committed.
