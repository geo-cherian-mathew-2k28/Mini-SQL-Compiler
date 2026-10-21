/**
 * Mini SQL Compiler Studio — Client Controller
 * Handles Theme Toggle, Gutter Sync, Parse Tree & AST Visualizer, Token Filter, and Modals.
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
  let currentCompilationData = null;
  let currentTreeMode = "parse_tree"; // 'parse_tree', 'ast', 'text', 'json'

  // =========================================================================
  // 1. Theme Management (Dark / Light with LocalStorage Persistence)
  // =========================================================================
  const savedTheme = localStorage.getItem("minisql_theme") || "dark";
  setTheme(savedTheme);

  btnThemeToggle.addEventListener("click", () => {
    const current = htmlRoot.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    setTheme(next);
  });

  function setTheme(theme) {
    htmlRoot.setAttribute("data-theme", theme);
    localStorage.setItem("minisql_theme", theme);
  }

  // =========================================================================
  // 2. Editor Mechanics: Line Number Gutter & Synchronization
  // =========================================================================
  function updateLineNumbers() {
    const lines = sqlInput.value.split("\n").length;
    let gutterHtml = "";
    for (let i = 1; i <= lines; i++) {
      gutterHtml += `<span>${i}</span>`;
    }
    lineGutter.innerHTML = gutterHtml;
  }

  sqlInput.addEventListener("input", updateLineNumbers);
  sqlInput.addEventListener("scroll", () => {
    lineGutter.scrollTop = sqlInput.scrollTop;
  });
  updateLineNumbers();

  // Keyboard shortcut: Ctrl+Enter / Cmd+Enter runs compilation
  sqlInput.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      runCompilation();
    }
  });

  // Editor Actions
  btnClearEditor.addEventListener("click", () => {
    sqlInput.value = "";
    updateLineNumbers();
    resetDisplay();
    sqlInput.focus();
  });

  btnCopyQuery.addEventListener("click", () => {
    if (!sqlInput.value.trim()) return;
    navigator.clipboard.writeText(sqlInput.value).then(() => {
      const orig = btnCopyQuery.textContent;
      btnCopyQuery.textContent = "Copied!";
      setTimeout(() => (btnCopyQuery.textContent = orig), 1500);
    });
  });

  // Quick Preset Chips
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

  // Tree Mode Switching (Parse Tree / AST / Indented / JSON)
  astSegBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      astSegBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      currentTreeMode = btn.getAttribute("data-tree-mode");
      renderTreeByMode();
    });
  });

  function renderTreeByMode() {
    if (!currentCompilationData) return;

    if (currentTreeMode === "parse_tree") {
      astVisualTree.classList.remove("hidden");
      astTextView.classList.add("hidden");
      astJsonView.classList.add("hidden");
      if (currentCompilationData.parse_tree) {
        renderConcreteParseTree(currentCompilationData.parse_tree);
      }
    } else if (currentTreeMode === "ast") {
      astVisualTree.classList.remove("hidden");
      astTextView.classList.add("hidden");
      astJsonView.classList.add("hidden");
      if (currentCompilationData.ast) {
        renderVisualAst(currentCompilationData.ast);
      }
    } else if (currentTreeMode === "text") {
      astVisualTree.classList.add("hidden");
      astTextView.classList.remove("hidden");
      astJsonView.classList.add("hidden");
      const textOutput = currentCompilationData.parse_tree_pretty || currentCompilationData.ast_pretty || "";
      astTextView.querySelector("code").textContent = textOutput;
    } else if (currentTreeMode === "json") {
      astVisualTree.classList.add("hidden");
      astTextView.classList.add("hidden");
      astJsonView.classList.remove("hidden");
      const jsonOutput = currentCompilationData.parse_tree || currentCompilationData.ast || {};
      astJsonView.querySelector("code").textContent = JSON.stringify(jsonOutput, null, 2);
    }
  }

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
      currentCompilationData = data;
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
    astVisualTree.innerHTML = '<div class="placeholder-state"><div class="placeholder-icon">🌲</div><p>Run compilation to inspect the formal Concrete Parse Tree (CST) and Abstract Syntax Tree.</p></div>';
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

    // 3. Tree Rendering
    if (data.parse_tree || data.ast) {
      renderTreeByMode();
    } else {
      astVisualTree.innerHTML = '<div class="placeholder-state"><p class="text-muted">Parse tree generation halted due to syntax errors.</p></div>';
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

  // =========================================================================
  // 5. Concrete Parse Tree (CST) Rendering (Non-Terminals & Terminals)
  // =========================================================================
  function renderConcreteParseTree(parseTree) {
    astVisualTree.innerHTML = "";
    const diagramWrapper = document.createElement("div");
    diagramWrapper.className = "ast-diagram-card";

    function buildParseTreeNode(node, isChild = false) {
      const el = document.createElement("div");
      el.className = isChild ? "ast-tree-node is-child" : "ast-tree-node";

      const pill = document.createElement("div");
      if (node.is_terminal) {
        if (node.symbol === "EPSILON" || node.symbol === "ε") {
          pill.className = "ast-pill ast-pill-green";
          pill.textContent = `ε`;
        } else if (node.symbol === "SELECT" || node.symbol === "FROM" || node.symbol === "WHERE" || node.symbol === "ORDER" || node.symbol === "BY") {
          pill.className = "ast-pill ast-pill-blue";
          pill.textContent = `${node.symbol}`;
        } else if (node.symbol === "IDENTIFIER") {
          pill.className = "ast-pill ast-pill-red";
          pill.textContent = `${node.lexeme}`;
        } else {
          pill.className = "ast-pill ast-pill-green";
          pill.textContent = `'${node.lexeme}'`;
        }
      } else {
        pill.className = "ast-pill ast-pill-dark";
        pill.textContent = node.symbol;
      }
      el.appendChild(pill);

      if (node.children && node.children.length > 0) {
        const subtree = document.createElement("div");
        subtree.className = "ast-subtree";
        node.children.forEach(child => {
          subtree.appendChild(buildParseTreeNode(child, true));
        });
        el.appendChild(subtree);
      }

      return el;
    }

    diagramWrapper.appendChild(buildParseTreeNode(parseTree, false));
    astVisualTree.appendChild(diagramWrapper);
  }

  // =========================================================================
  // 6. Abstract Syntax Tree (AST) Rendering
  // =========================================================================
  function renderVisualAst(ast) {
    astVisualTree.innerHTML = "";

    const diagramWrapper = document.createElement("div");
    diagramWrapper.className = "ast-diagram-card";

    // 1. Root: SelectQuery (Dark Node)
    const rootNode = document.createElement("div");
    rootNode.className = "ast-tree-node";

    const rootPill = document.createElement("div");
    rootPill.className = "ast-pill ast-pill-dark";
    rootPill.textContent = "SelectQuery";
    rootNode.appendChild(rootPill);

    const rootSubtree = document.createElement("div");
    rootSubtree.className = "ast-subtree";

    // 2. Projections Branch
    const projNode = document.createElement("div");
    projNode.className = "ast-tree-node is-child";
    const projPill = document.createElement("div");
    projPill.className = "ast-pill ast-pill-dark";
    projPill.textContent = "Projections";
    projNode.appendChild(projPill);

    const projSubtree = document.createElement("div");
    projSubtree.className = "ast-subtree";
    (ast.projections || []).forEach(p => {
      const pNode = document.createElement("div");
      pNode.className = "ast-tree-node is-child";
      const pPill = document.createElement("div");
      if (p.type === "Wildcard") {
        pPill.className = "ast-pill ast-pill-blue";
        pPill.textContent = "Wildcard (*)";
      } else {
        pPill.className = "ast-pill ast-pill-red";
        pPill.textContent = p.name;
      }
      pNode.appendChild(pPill);
      projSubtree.appendChild(pNode);
    });
    projNode.appendChild(projSubtree);
    rootSubtree.appendChild(projNode);

    // 3. From Clause
    const fromNode = document.createElement("div");
    fromNode.className = "ast-tree-node is-child";
    const fromPill = document.createElement("div");
    fromPill.className = "ast-pill ast-pill-dark";
    fromPill.textContent = "FromClause";
    fromNode.appendChild(fromPill);

    const fromSubtree = document.createElement("div");
    fromSubtree.className = "ast-subtree";
    const tableNode = document.createElement("div");
    tableNode.className = "ast-tree-node is-child";
    const tablePill = document.createElement("div");
    tablePill.className = "ast-pill ast-pill-red";
    tablePill.textContent = ast.from_table ? ast.from_table.name : "";
    tableNode.appendChild(tablePill);
    fromSubtree.appendChild(tableNode);
    fromNode.appendChild(fromSubtree);
    rootSubtree.appendChild(fromNode);

    // 4. Where Clause
    if (ast.where) {
      const whereNode = document.createElement("div");
      whereNode.className = "ast-tree-node is-child";
      const wherePill = document.createElement("div");
      wherePill.className = "ast-pill ast-pill-dark";
      wherePill.textContent = "WhereClause";
      whereNode.appendChild(wherePill);

      const whereSubtree = document.createElement("div");
      whereSubtree.className = "ast-subtree";
      whereSubtree.appendChild(buildAstDiagramNode(ast.where));
      whereNode.appendChild(whereSubtree);
      rootSubtree.appendChild(whereNode);
    }

    // 5. Order By Clause
    if (ast.order_by && ast.order_by.length > 0) {
      const orderNode = document.createElement("div");
      orderNode.className = "ast-tree-node is-child";
      const orderPill = document.createElement("div");
      orderPill.className = "ast-pill ast-pill-dark";
      orderPill.textContent = "OrderByClause";
      orderNode.appendChild(orderPill);

      const orderSubtree = document.createElement("div");
      orderSubtree.className = "ast-subtree";
      ast.order_by.forEach(item => {
        const itemNode = document.createElement("div");
        itemNode.className = "ast-tree-node is-child";
        const itemPill = document.createElement("div");
        itemPill.className = "ast-pill ast-pill-blue";
        itemPill.textContent = `${item.column.name} ${item.direction}`;
        itemNode.appendChild(itemPill);
        orderSubtree.appendChild(itemNode);
      });
      orderNode.appendChild(orderSubtree);
      rootSubtree.appendChild(orderNode);
    }

    rootNode.appendChild(rootSubtree);
    diagramWrapper.appendChild(rootNode);
    astVisualTree.appendChild(diagramWrapper);
  }

  function buildAstDiagramNode(node) {
    const wrapper = document.createElement("div");
    wrapper.className = "ast-tree-node is-child";

    if (!node) return wrapper;

    if (node.type === "BinaryExpr") {
      const pill = document.createElement("div");
      pill.className = "ast-pill ast-pill-dark";
      pill.textContent = `BinaryExpr (${node.operator})`;
      wrapper.appendChild(pill);

      const subtree = document.createElement("div");
      subtree.className = "ast-subtree";
      subtree.appendChild(buildAstDiagramNode(node.left));
      subtree.appendChild(buildAstDiagramNode(node.right));
      wrapper.appendChild(subtree);
      return wrapper;
    }

    if (node.type === "Identifier") {
      const pill = document.createElement("div");
      pill.className = "ast-pill ast-pill-red";
      pill.textContent = node.name;
      wrapper.appendChild(pill);
      return wrapper;
    }

    if (node.type === "Literal") {
      const pill = document.createElement("div");
      pill.className = "ast-pill ast-pill-green";
      pill.textContent = typeof node.value === "string" ? `'${node.value}'` : String(node.value);
      wrapper.appendChild(pill);
      return wrapper;
    }

    const pill = document.createElement("div");
    pill.className = "ast-pill ast-pill-blue";
    pill.textContent = JSON.stringify(node);
    wrapper.appendChild(pill);
    return wrapper;
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
