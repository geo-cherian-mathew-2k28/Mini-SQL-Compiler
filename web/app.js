/**
 * Mini SQL Compiler — Web IDE Client Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const sqlInput = document.getElementById("sqlInput");
  const btnCompile = document.getElementById("btnCompile");
  const btnClear = document.getElementById("btnClear");
  const queryPresets = document.getElementById("queryPresets");
  const statusPill = document.getElementById("statusPill");
  const statusText = document.getElementById("statusText");

  const diagnosticBanner = document.getElementById("diagnosticBanner");
  const diagStage = document.getElementById("diagStage");
  const diagMessage = document.getElementById("diagMessage");

  const astVisualTree = document.getElementById("astVisualTree");
  const astJsonView = document.getElementById("astJsonView");
  const btnToggleAstJson = document.getElementById("btnToggleAstJson");
  const tokenCount = document.getElementById("tokenCount");
  const tokensTableBody = document.getElementById("tokensTableBody");
  const semanticReportContainer = document.getElementById("semanticReportContainer");

  const btnToggleSchema = document.getElementById("btnToggleSchema");
  const btnCloseSchema = document.getElementById("btnCloseSchema");
  const schemaDrawer = document.getElementById("schemaDrawer");
  const schemaDrawerBody = document.getElementById("schemaDrawerBody");

  // Presets Dictionary
  const PRESETS = {
    select_basic: "SELECT name, age FROM students;",
    select_wildcard: "SELECT * FROM employees;",
    where_compound: "SELECT id, amount FROM orders WHERE amount > 100 AND status = 'COMPLETED' OR customer_id = 5;",
    order_by_desc: "SELECT name, salary FROM employees ORDER BY salary DESC;",
    full_pipeline: "SELECT name, age FROM students WHERE age >= 18 AND gpa > 3.0 ORDER BY name ASC;",
    err_syntax_clause: "SELECT id WHERE age > 18 FROM students;",
    err_syntax_comma: "SELECT id, name, FROM students;",
    err_semantic_table: "SELECT id FROM non_existent_table;",
    err_semantic_type: "SELECT name FROM students WHERE age = 'twenty';",
    err_lexical_char: "SELECT id @ FROM students;"
  };

  // Tab Navigation
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      document.getElementById(targetId).classList.add("active");
    });
  });

  // Query Presets Dropdown Change
  queryPresets.addEventListener("change", (e) => {
    const val = e.target.value;
    if (PRESETS[val]) {
      sqlInput.value = PRESETS[val];
      compileQuery();
    }
  });

  // Clear Editor
  btnClear.addEventListener("click", () => {
    sqlInput.value = "";
    sqlInput.focus();
    resetState();
  });

  // Keyboard shortcut: Ctrl + Enter
  sqlInput.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      compileQuery();
    }
  });

  // Compile Button
  btnCompile.addEventListener("click", compileQuery);

  // Toggle AST JSON / Visual View
  let showAstJson = false;
  btnToggleAstJson.addEventListener("click", () => {
    showAstJson = !showAstJson;
    if (showAstJson) {
      astVisualTree.classList.add("hidden");
      astJsonView.classList.remove("hidden");
      btnToggleAstJson.textContent = "View Visual Tree";
    } else {
      astVisualTree.classList.remove("hidden");
      astJsonView.classList.add("hidden");
      btnToggleAstJson.textContent = "View JSON";
    }
  });

  // Schema Drawer Open/Close
  btnToggleSchema.addEventListener("click", () => {
    schemaDrawer.classList.remove("hidden");
    loadSchema();
  });
  btnCloseSchema.addEventListener("click", () => {
    schemaDrawer.classList.add("hidden");
  });
  schemaDrawer.addEventListener("click", (e) => {
    if (e.target === schemaDrawer) {
      schemaDrawer.classList.add("hidden");
    }
  });

  function setStatus(state, text) {
    statusPill.className = "status-pill status-" + state;
    statusText.textContent = text;
  }

  function resetState() {
    setStatus("ready", "Ready");
    diagnosticBanner.classList.add("hidden");
    astVisualTree.innerHTML = '<div class="empty-state"><p>Click <strong>Compile & Analyze</strong> to generate the AST.</p></div>';
    astJsonView.querySelector("code").textContent = "";
    tokenCount.textContent = "0";
    tokensTableBody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No tokens generated yet.</td></tr>';
    semanticReportContainer.innerHTML = '<div class="empty-state"><p>Compile a query to run semantic checks.</p></div>';
  }

  // Master Compile Function
  async function compileQuery() {
    const query = sqlInput.value.trim();
    if (!query) {
      resetState();
      return;
    }

    setStatus("ready", "Compiling...");
    btnCompile.disabled = true;

    try {
      const res = await fetch("/api/compile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query })
      });

      const data = await res.json();
      renderCompilationResults(data);
    } catch (err) {
      console.error("Compilation network error:", err);
      setStatus("error", "Network Error");
      showDiagnostic("Server Error", "Could not reach local compiler server.");
    } finally {
      btnCompile.disabled = false;
    }
  }

  function renderCompilationResults(data) {
    // 1. Tokens Stage
    renderTokens(data.tokens || []);

    // 2. Diagnostics / Errors
    if (!data.success && data.errors && data.errors.length > 0) {
      setStatus("error", "Compilation Failed");
      const err = data.errors[0];
      const loc = err.line ? ` [Line ${err.line}, Column ${err.column}]` : "";
      showDiagnostic(err.stage || "Compiler Error", `${err.message}${loc}`);
    } else {
      setStatus("success", "Compiled Successfully");
      diagnosticBanner.classList.add("hidden");
    }

    // 3. AST Rendering
    if (data.ast) {
      renderVisualAst(data.ast);
      astJsonView.querySelector("code").textContent = JSON.stringify(data.ast, null, 2);
    } else {
      astVisualTree.innerHTML = '<div class="empty-state"><p class="text-muted">AST construction failed due to syntax errors.</p></div>';
      astJsonView.querySelector("code").textContent = "";
    }

    // 4. Semantic Report
    renderSemanticReport(data.semantic_report, data.warnings || []);
  }

  function showDiagnostic(stage, msg) {
    diagStage.textContent = stage;
    diagMessage.textContent = msg;
    diagnosticBanner.classList.remove("hidden");
  }

  // Render Token Table
  function renderTokens(tokens) {
    tokenCount.textContent = tokens.length;
    if (tokens.length === 0) {
      tokensTableBody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No tokens found.</td></tr>';
      return;
    }

    tokensTableBody.innerHTML = tokens.map((t, idx) => {
      let badgeClass = "token-punct";
      if (t.type.includes("SELECT") || t.type.includes("FROM") || t.type.includes("WHERE") || t.type.includes("ORDER") || t.type.includes("BY") || t.type.includes("AND") || t.type.includes("OR")) {
        badgeClass = "token-keyword";
      } else if (t.type === "IDENTIFIER") {
        badgeClass = "token-identifier";
      } else if (t.type.includes("LITERAL")) {
        badgeClass = "token-literal";
      } else if (t.type.includes("EQUALS") || t.type.includes("THAN")) {
        badgeClass = "token-operator";
      }

      return `
        <tr>
          <td>${idx + 1}</td>
          <td><span class="token-type-badge ${badgeClass}">${t.type}</span></td>
          <td><code>${escapeHtml(t.lexeme || t.type)}</code></td>
          <td><code>${escapeHtml(String(t.value ?? ""))}</code></td>
          <td>${t.line}</td>
          <td>${t.column}</td>
        </tr>
      `;
    }).join("");
  }

  // Render Visual AST
  function renderVisualAst(ast) {
    astVisualTree.innerHTML = "";
    const rootEl = createTreeNode("SelectQuery", "SelectQuery (Root)", "tag-query");

    // Projections
    const projsNode = createTreeNode("Projections", "Projections List", "tag-proj");
    (ast.projections || []).forEach(p => {
      if (p.type === "Wildcard") {
        projsNode.appendChild(createTreeNode("Wildcard", "Wildcard (*)", "tag-literal"));
      } else if (p.type === "Identifier") {
        projsNode.appendChild(createTreeNode("Identifier", `Column: ${p.name}`, "tag-literal"));
      }
    });
    rootEl.appendChild(projsNode);

    // From
    const fromNode = createTreeNode("FromTable", `From Table: ${ast.from_table.name}`, "tag-from");
    rootEl.appendChild(fromNode);

    // Where
    if (ast.where) {
      const whereNode = createTreeNode("Where", "Filter Condition (WHERE)", "tag-binary");
      whereNode.appendChild(renderAstSubtree(ast.where));
      rootEl.appendChild(whereNode);
    }

    // Order By
    if (ast.order_by && ast.order_by.length > 0) {
      const orderNode = createTreeNode("OrderBy", "Sorting (ORDER BY)", "tag-order");
      ast.order_by.forEach(item => {
        orderNode.appendChild(createTreeNode("SortItem", `${item.column.name} [${item.direction}]`, "tag-order"));
      });
      rootEl.appendChild(orderNode);
    }

    astVisualTree.appendChild(rootEl);
  }

  function renderAstSubtree(node) {
    if (!node) return document.createTextNode("");

    if (node.type === "BinaryExpr") {
      const el = createTreeNode("BinaryExpr", `Binary Operator: [${node.operator}]`, "tag-binary");
      el.appendChild(renderAstSubtree(node.left));
      el.appendChild(renderAstSubtree(node.right));
      return el;
    }

    if (node.type === "Identifier") {
      return createTreeNode("Identifier", `Column: ${node.name}`, "tag-literal");
    }

    if (node.type === "Literal") {
      return createTreeNode("Literal", `${node.literal_type}: ${node.value}`, "tag-literal");
    }

    return createTreeNode("Node", JSON.stringify(node), "tag-literal");
  }

  function createTreeNode(tag, label, tagClass) {
    const node = document.createElement("div");
    node.className = "tree-node";

    const content = document.createElement("div");
    content.className = "tree-node-content";

    const tagSpan = document.createElement("span");
    tagSpan.className = `tree-node-tag ${tagClass}`;
    tagSpan.textContent = tag;

    const labelSpan = document.createElement("span");
    labelSpan.className = "tree-node-label";
    labelSpan.textContent = label;

    content.appendChild(tagSpan);
    content.appendChild(labelSpan);
    node.appendChild(content);
    return node;
  }

  // Render Semantic Report
  function renderSemanticReport(report, warnings) {
    if (!report) {
      semanticReportContainer.innerHTML = '<div class="empty-state"><p class="text-muted">No semantic analysis performed.</p></div>';
      return;
    }

    let html = `
      <div class="sem-card">
        <h3>Symbol Resolution & Schema Check</h3>
        <p>Overall Status: <span class="badge-pill ${report.is_valid ? 'badge-success' : 'badge-fail'}">${report.is_valid ? 'PASSED' : 'FAILED'}</span></p>
        <p style="margin-top: 8px;"><strong>Target Table:</strong> <code>${report.resolved_table || 'None'}</code></p>
        <p style="margin-top: 4px;"><strong>Resolved Columns:</strong> ${report.resolved_columns.length ? report.resolved_columns.map(c => `<code>${c}</code>`).join(", ") : 'None'}</p>
      </div>
    `;

    if (report.errors && report.errors.length > 0) {
      html += `
        <div class="sem-card" style="border-color: var(--accent-red);">
          <h3 style="color: var(--accent-red);">Semantic Violations (${report.errors.length})</h3>
          <ul style="padding-left: 20px; font-size: 13px; color: #ff7b72;">
            ${report.errors.map(e => `<li><strong>[${e.code}]</strong> ${escapeHtml(e.message)}</li>`).join("")}
          </ul>
        </div>
      `;
    }

    if (warnings && warnings.length > 0) {
      html += `
        <div class="sem-card" style="border-color: var(--accent-amber);">
          <h3 style="color: var(--accent-amber);">Compiler Warnings (${warnings.length})</h3>
          <ul style="padding-left: 20px; font-size: 13px; color: #e3b341;">
            ${warnings.map(w => `<li>${escapeHtml(w)}</li>`).join("")}
          </ul>
        </div>
      `;
    }

    semanticReportContainer.innerHTML = html;
  }

  // Load Schema Catalog
  async function loadSchema() {
    try {
      const res = await fetch("/api/schema");
      const data = await res.json();
      renderSchemaDrawer(data.tables || {});
    } catch (err) {
      console.error("Failed to load schema:", err);
    }
  }

  function renderSchemaDrawer(tables) {
    schemaDrawerBody.innerHTML = Object.values(tables).map(tbl => `
      <div class="schema-table-card">
        <div class="schema-table-title">📁 Table: ${tbl.name}</div>
        <div class="schema-col-list">
          ${tbl.columns.map(col => `
            <div class="schema-col-item">
              <span>${col.name}</span>
              <span class="schema-col-type">${col.data_type}</span>
            </div>
          `).join("")}
        </div>
      </div>
    `).join("");
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Initial Auto-Compile on load
  compileQuery();
});
