/**
 * Mini SQL Compiler Studio — Client Controller
 * Handles Theme Toggle, Gutter Sync, AST Visualizer, Token Filter, and Modals.
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM References
  const htmlRoot = document.documentElement;
  const btnThemeToggle = document.getElementById("btnThemeToggle");
  const sqlInput = document.getElementById("sqlInput");
  const lineGutter = document.getElementById("lineGutter");
  const btnCompile = document.getElementById("btnCompile");
  const btnClearEditor = document.getElementById("btnClearEditor");
  const btnCopyQuery = document.getElementById("btnCopyQuery");

  const compilerStatusPill = document.getElementById("compilerStatusPill");
  const compilerStatusText = document.getElementById("compilerStatusText");
  const diagnosticAlert = document.getElementById("diagnosticAlert");
  const alertStage = document.getElementById("alertStage");
  const alertCoords = document.getElementById("alertCoords");
  const alertMessage = document.getElementById("alertMessage");

  const tokenCountBadge = document.getElementById("tokenCountBadge");
  const tokensTableBody = document.getElementById("tokensTableBody");
  const tokenFilterInput = document.getElementById("tokenFilterInput");
  const semStatusDot = document.getElementById("semStatusDot");

  const astVisualTree = document.getElementById("astVisualTree");
  const astTextView = document.getElementById("astTextView");
  const astJsonView = document.getElementById("astJsonView");
  const astSegBtns = document.querySelectorAll(".seg-btn");
  const semanticReportView = document.getElementById("semanticReportView");

  const chips = document.querySelectorAll(".chip");
  const tabItems = document.querySelectorAll(".tab-item");
  const tabViewports = document.querySelectorAll(".tab-viewport");

  const btnOpenSchema = document.getElementById("btnOpenSchema");
  const btnCloseSchema = document.getElementById("btnCloseSchema");
  const schemaModal = document.getElementById("schemaModal");
  const schemaModalBody = document.getElementById("schemaModalBody");

  const btnOpenTeam = document.getElementById("btnOpenTeam");
  const btnCloseTeam = document.getElementById("btnCloseTeam");
  const teamModal = document.getElementById("teamModal");

  // Query Presets Dictionary
  const PRESET_QUERIES = {
    full_pipeline: "SELECT name, age FROM students WHERE age >= 18 AND gpa > 3.0 ORDER BY name ASC;",
    select_basic: "SELECT id, name FROM students;",
    select_wildcard: "SELECT * FROM employees;",
    where_compound: "SELECT id, amount FROM orders WHERE amount > 100 AND status = 'COMPLETED' OR customer_id = 5;",
    order_by_desc: "SELECT name, salary FROM employees ORDER BY salary DESC;",
    err_syntax_comma: "SELECT id, name, FROM students;",
    err_semantic_type: "SELECT name FROM students WHERE age = 'twenty';"
  };

  let cachedTokens = [];

  // =========================================================================
  // 1. Theme Management (Dark / Light)
  // =========================================================================
  const savedTheme = localStorage.getItem("mini_sql_theme") || "dark";
  setTheme(savedTheme);

  btnThemeToggle.addEventListener("click", () => {
    const currentTheme = htmlRoot.getAttribute("data-theme");
    const nextTheme = currentTheme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
  });

  function setTheme(theme) {
    htmlRoot.setAttribute("data-theme", theme);
    localStorage.setItem("mini_sql_theme", theme);
  }

  // =========================================================================
  // 2. Editor Gutter & Input Handling
  // =========================================================================
  function updateLineNumbers() {
    const lines = sqlInput.value.split("\n").length;
    let numbers = [];
    for (let i = 1; i <= Math.max(lines, 1); i++) {
      numbers.push(i);
    }
    lineGutter.textContent = numbers.join("\n");
  }

  sqlInput.addEventListener("input", updateLineNumbers);
  sqlInput.addEventListener("scroll", () => {
    lineGutter.scrollTop = sqlInput.scrollTop;
  });
  updateLineNumbers();

  // Clear & Copy Actions
  btnClearEditor.addEventListener("click", () => {
    sqlInput.value = "";
    updateLineNumbers();
    sqlInput.focus();
    resetDisplay();
  });

  btnCopyQuery.addEventListener("click", () => {
    navigator.clipboard.writeText(sqlInput.value);
    btnCopyQuery.textContent = "Copied!";
    setTimeout(() => { btnCopyQuery.textContent = "Copy"; }, 1500);
  });

  // Ctrl + Enter shortcut
  sqlInput.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      runCompilation();
    }
  });

  // Quick Query Chips
  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      chips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");

      const key = chip.getAttribute("data-preset");
      if (PRESET_QUERIES[key]) {
        sqlInput.value = PRESET_QUERIES[key];
        updateLineNumbers();
        runCompilation();
      }
    });
  });

  // Tab Switching
  tabItems.forEach(tab => {
    tab.addEventListener("click", () => {
      tabItems.forEach(t => t.classList.remove("active"));
      tabViewports.forEach(v => v.classList.remove("active"));

      tab.classList.add("active");
      const targetId = tab.getAttribute("data-tab");
      document.getElementById(targetId).classList.add("active");
    });
  });

  // AST View Switching (Tree / Indented / JSON)
  astSegBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      astSegBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      const view = btn.getAttribute("data-ast-view");
      astVisualTree.classList.toggle("hidden", view !== "visual");
      astTextView.classList.toggle("hidden", view !== "text");
      astJsonView.classList.toggle("hidden", view !== "json");
    });
  });

  // Token Filter Input
  tokenFilterInput.addEventListener("input", (e) => {
    const term = e.target.value.toLowerCase().trim();
    if (!term) {
      renderTokensTable(cachedTokens);
      return;
    }
    const filtered = cachedTokens.filter(t => 
      t.type.toLowerCase().includes(term) || 
      (t.lexeme && t.lexeme.toLowerCase().includes(term))
    );
    renderTokensTable(filtered);
  });

  // =========================================================================
  // 3. Modals (Schema & Team)
  // =========================================================================
  btnOpenSchema.addEventListener("click", () => {
    schemaModal.classList.remove("hidden");
    loadSchemaCatalog();
  });
  btnCloseSchema.addEventListener("click", () => {
    schemaModal.classList.add("hidden");
  });
  schemaModal.addEventListener("click", (e) => {
    if (e.target === schemaModal) schemaModal.classList.add("hidden");
  });

  btnOpenTeam.addEventListener("click", () => {
    teamModal.classList.remove("hidden");
  });
  btnCloseTeam.addEventListener("click", () => {
    teamModal.classList.add("hidden");
  });
  teamModal.addEventListener("click", (e) => {
    if (e.target === teamModal) teamModal.classList.add("hidden");
  });

  // =========================================================================
  // 4. Compilation Pipeline
  // =========================================================================
  btnCompile.addEventListener("click", runCompilation);

  async function runCompilation() {
    const query = sqlInput.value.trim();
    if (!query) {
      resetDisplay();
      return;
    }

    setCompilerStatus("ready", "Analyzing...");
    btnCompile.disabled = true;

    try {
      const res = await fetch("/api/compile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query })
      });
      const data = await res.json();
      renderOutputs(data);
    } catch (err) {
      console.error("Compilation error:", err);
      setCompilerStatus("error", "Network Error");
      showDiagnostic("Server", "Failed to connect to local compiler backend.");
    } finally {
      btnCompile.disabled = false;
    }
  }

  function setCompilerStatus(state, label) {
    compilerStatusPill.className = `compiler-badge ${state}`;
    compilerStatusText.textContent = label;
  }

  function resetDisplay() {
    setCompilerStatus("ready", "Ready");
    diagnosticAlert.classList.add("hidden");
    astVisualTree.innerHTML = '<div class="placeholder-state"><div class="placeholder-icon">🌲</div><p>Run compilation to explore the interactive Abstract Syntax Tree.</p></div>';
    astTextView.querySelector("code").textContent = "";
    astJsonView.querySelector("code").textContent = "";
    tokenCountBadge.textContent = "0";
    tokensTableBody.innerHTML = '<tr><td colspan="6" class="cell-empty">No tokens generated yet.</td></tr>';
    semanticReportView.innerHTML = '<div class="placeholder-state"><div class="placeholder-icon">🛡️</div><p>Compile a query to inspect schema verification and type safety.</p></div>';
    semStatusDot.style.backgroundColor = "var(--text-muted)";
  }

  function renderOutputs(data) {
    // 1. Tokens
    cachedTokens = data.tokens || [];
    tokenCountBadge.textContent = cachedTokens.length;
    renderTokensTable(cachedTokens);

    // 2. Diagnostics
    if (!data.success && data.errors && data.errors.length > 0) {
      setCompilerStatus("error", "Error Found");
      const err = data.errors[0];
      const coords = err.line ? `Line ${err.line}, Column ${err.column}` : "Contextual Verification";
      showDiagnostic(err.stage || "Error", err.message, coords);
    } else {
      setCompilerStatus("success", "Valid Query");
      diagnosticAlert.classList.add("hidden");
    }

    // 3. AST
    if (data.ast) {
      renderVisualAst(data.ast);
      astTextView.querySelector("code").textContent = data.ast_pretty || "";
      astJsonView.querySelector("code").textContent = JSON.stringify(data.ast, null, 2);
    } else {
      astVisualTree.innerHTML = '<div class="placeholder-state"><p class="text-muted">AST generation halted due to syntax errors.</p></div>';
      astTextView.querySelector("code").textContent = "";
      astJsonView.querySelector("code").textContent = "";
    }

    // 4. Semantic Report
    renderSemanticReport(data.semantic_report, data.warnings || []);
  }

  function showDiagnostic(stage, msg, coords = "") {
    alertStage.textContent = stage;
    alertCoords.textContent = coords;
    alertMessage.textContent = msg;
    diagnosticAlert.classList.remove("hidden");
  }

  // Tokens Table Rendering
  function renderTokensTable(tokens) {
    if (tokens.length === 0) {
      tokensTableBody.innerHTML = '<tr><td colspan="6" class="cell-empty">No matching tokens found.</td></tr>';
      return;
    }

    tokensTableBody.innerHTML = tokens.map((t, idx) => {
      let badge = "tok-delim";
      if (t.type.includes("SELECT") || t.type.includes("FROM") || t.type.includes("WHERE") || t.type.includes("ORDER") || t.type.includes("BY") || t.type.includes("AND") || t.type.includes("OR")) {
        badge = "tok-kw";
      } else if (t.type === "IDENTIFIER") {
        badge = "tok-id";
      } else if (t.type.includes("LITERAL")) {
        badge = "tok-lit";
      } else if (t.type.includes("EQUALS") || t.type.includes("THAN")) {
        badge = "tok-op";
      }

      return `
        <tr>
          <td>${idx + 1}</td>
          <td><span class="badge-tok ${badge}">${t.type}</span></td>
          <td><code>${escapeHtml(t.lexeme || t.type)}</code></td>
          <td><code>${escapeHtml(String(t.value ?? ""))}</code></td>
          <td>${t.line}</td>
          <td>${t.column}</td>
        </tr>
      `;
    }).join("");
  }

  // Visual AST Tree Rendering
  function renderVisualAst(ast) {
    astVisualTree.innerHTML = "";
    const root = createAstNode("SelectQuery", "SelectQuery (Root)", "tag-query");

    // Projections
    const projBranch = createAstNode("Projections", "Projection Columns", "tag-proj");
    (ast.projections || []).forEach(p => {
      if (p.type === "Wildcard") {
        projBranch.appendChild(createAstNode("Wildcard", "Wildcard (*)", "tag-val"));
      } else {
        projBranch.appendChild(createAstNode("Identifier", `Column: ${p.name}`, "tag-val"));
      }
    });
    root.appendChild(projBranch);

    // From Table
    const fromBranch = createAstNode("FromTable", `Table: ${ast.from_table.name}`, "tag-from");
    root.appendChild(fromBranch);

    // Where
    if (ast.where) {
      const whereBranch = createAstNode("WhereClause", "Condition (WHERE)", "tag-op");
      whereBranch.appendChild(renderAstSubtree(ast.where));
      root.appendChild(whereBranch);
    }

    // Order By
    if (ast.order_by && ast.order_by.length > 0) {
      const orderBranch = createAstNode("OrderBy", "Sorting (ORDER BY)", "tag-proj");
      ast.order_by.forEach(item => {
        orderBranch.appendChild(createAstNode("SortItem", `${item.column.name} [${item.direction}]`, "tag-val"));
      });
      root.appendChild(orderBranch);
    }

    astVisualTree.appendChild(root);
  }

  function renderAstSubtree(node) {
    if (!node) return document.createTextNode("");

    if (node.type === "BinaryExpr") {
      const branch = createAstNode("BinaryExpr", `Operator: [${node.operator}]`, "tag-op");
      branch.appendChild(renderAstSubtree(node.left));
      branch.appendChild(renderAstSubtree(node.right));
      return branch;
    }

    if (node.type === "Identifier") {
      return createAstNode("Identifier", `Column: ${node.name}`, "tag-val");
    }

    if (node.type === "Literal") {
      return createAstNode("Literal", `${node.literal_type}: ${node.value}`, "tag-val");
    }

    return createAstNode("Node", JSON.stringify(node), "tag-val");
  }

  function createAstNode(tag, label, tagClass) {
    const branch = document.createElement("div");
    branch.className = "ast-branch";

    const card = document.createElement("div");
    card.className = "ast-card";

    const tagEl = document.createElement("span");
    tagEl.className = `ast-tag ${tagClass}`;
    tagEl.textContent = tag;

    const labelEl = document.createElement("span");
    labelEl.className = "ast-label";
    labelEl.textContent = label;

    card.appendChild(tagEl);
    card.appendChild(labelEl);
    branch.appendChild(card);
    return branch;
  }

  // Semantic Report Rendering
  function renderSemanticReport(report, warnings) {
    if (!report) {
      semanticReportView.innerHTML = '<div class="placeholder-state"><p class="text-muted">No semantic analysis available.</p></div>';
      semStatusDot.style.backgroundColor = "var(--text-muted)";
      return;
    }

    semStatusDot.style.backgroundColor = report.is_valid ? "var(--accent-green)" : "var(--accent-red)";

    let html = `
      <div class="sem-box">
        <h4>Schema Symbol Resolution</h4>
        <div class="sem-detail-row">
          <span class="sem-detail-label">Validation Status:</span>
          <span class="pill-status ${report.is_valid ? 'pill-valid' : 'pill-invalid'}">${report.is_valid ? 'VALIDATED' : 'FAILED'}</span>
        </div>
        <div class="sem-detail-row">
          <span class="sem-detail-label">Target Table:</span>
          <span class="sem-detail-val"><code>${report.resolved_table || 'None'}</code></span>
        </div>
        <div class="sem-detail-row">
          <span class="sem-detail-label">Resolved Columns:</span>
          <span class="sem-detail-val">${report.resolved_columns.length ? report.resolved_columns.map(c => `<code>${c}</code>`).join(", ") : 'None'}</span>
        </div>
      </div>
    `;

    if (report.errors && report.errors.length > 0) {
      html += `
        <div class="sem-box" style="border-color: var(--accent-red);">
          <h4 style="color: var(--accent-red);">Semantic Violations (${report.errors.length})</h4>
          <ul style="padding-left: 20px; font-size: 12px; color: var(--accent-red); display: flex; flex-direction: column; gap: 4px;">
            ${report.errors.map(e => `<li><strong>[${e.code}]</strong> ${escapeHtml(e.message)}</li>`).join("")}
          </ul>
        </div>
      `;
    }

    if (warnings && warnings.length > 0) {
      html += `
        <div class="sem-box" style="border-color: var(--accent-amber);">
          <h4 style="color: var(--accent-amber);">Compiler Warnings (${warnings.length})</h4>
          <ul style="padding-left: 20px; font-size: 12px; color: var(--accent-amber); display: flex; flex-direction: column; gap: 4px;">
            ${warnings.map(w => `<li>${escapeHtml(w)}</li>`).join("")}
          </ul>
        </div>
      `;
    }

    semanticReportView.innerHTML = html;
  }

  // Load Schema Catalog
  async function loadSchemaCatalog() {
    try {
      const res = await fetch("/api/schema");
      const data = await res.json();
      const tables = Object.values(data.tables || {});
      schemaModalBody.innerHTML = `
        <div class="schema-grid">
          ${tables.map(t => `
            <div class="schema-card">
              <div class="schema-table-name">📁 ${t.name}</div>
              <div class="schema-col-list">
                ${t.columns.map(c => `
                  <div class="schema-col-row">
                    <span>${c.name}</span>
                    <span class="schema-col-type">${c.data_type}</span>
                  </div>
                `).join("")}
              </div>
            </div>
          `).join("")}
        </div>
      `;
    } catch (e) {
      console.error("Failed to load schema:", e);
    }
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Auto-run first compile
  runCompilation();
});
