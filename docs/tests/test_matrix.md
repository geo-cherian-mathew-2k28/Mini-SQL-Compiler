# Mini SQL Compiler — Test Execution Matrix & Verification Protocol

## 1. Quality Assurance Protocol & Methodology
This verification protocol establishes the master Quality Assurance (QA) traceability matrix for the **Mini SQL Compiler**. 

### Verification Stages
1. **Lexical Analysis (Stage 1):** Validates regular expression token matching, line/column tracking, whitespace tolerance, and rejection of unmapped characters.
2. **Syntax Analysis & AST Construction (Stage 2):** Validates deterministic LL(1) recursive descent parsing, Context-Free Grammar (CFG) rules, operator precedence layering, and AST node generation.
3. **Semantic Analysis (Stage 3):** Validates symbol resolution against the pre-defined catalog schema (table/column existence, type compatibility, and unambiguous projection rules).

---

## 2. Master Test Execution Matrix (45 Test Cases)

### Part A: Valid Queries (Functional & Pipeline Verification)

| Test ID | Query Category | SQL Query Snippet | Target Stage | Expected Outcome | Execution Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-VAL-01** | Wildcard Select | `SELECT * FROM students;` | Pipeline | 3 Tokens, AST root `SelectQuery`, Validated against schema | **PASS** |
| **TC-VAL-02** | Attribute Projection | `SELECT name, age FROM students;` | Pipeline | 6 Tokens, Projections `[name, age]`, Validated | **PASS** |
| **TC-VAL-03** | Simple WHERE Numeric | `SELECT name FROM students WHERE age >= 20;` | Pipeline | BinaryExpr(`>=`, `age`, `20`), Validated | **PASS** |
| **TC-VAL-04** | WHERE String Literal | `SELECT name, building FROM departments WHERE name = 'Computer Science';` | Pipeline | Literal string match, Validated | **PASS** |
| **TC-VAL-05** | Logical AND Condition | `SELECT title, credits FROM courses WHERE credits >= 3 AND department_id = 1;` | Pipeline | BinaryExpr(`AND`), Validated | **PASS** |
| **TC-VAL-06** | Logical OR Condition | `SELECT name FROM students WHERE age = 18 OR age = 19;` | Pipeline | BinaryExpr(`OR`), Validated | **PASS** |
| **TC-VAL-07** | ORDER BY ASC | `SELECT name FROM students ORDER BY name ASC;` | Pipeline | OrderByItem(`name`, `ASC`), Validated | **PASS** |
| **TC-VAL-08** | ORDER BY DESC | `SELECT name, gpa FROM students ORDER BY gpa DESC;` | Pipeline | OrderByItem(`gpa`, `DESC`), Validated | **PASS** |
| **TC-VAL-09** | Default Sort Direction | `SELECT title FROM courses ORDER BY title;` | Parser | Implicitly resolves direction to `ASC` | **PASS** |
| **TC-VAL-10** | Multi-Column Sorting | `SELECT name, department_id, gpa FROM students ORDER BY department_id ASC, gpa DESC;` | Pipeline | Multi-node `OrderByItem` list, Validated | **PASS** |
| **TC-VAL-11** | Full 4-Clause Query | `SELECT name, age FROM students WHERE age >= 18 ORDER BY name ASC;` | Pipeline | Complete 4-clause compilation | **PASS** |
| **TC-VAL-12** | Omitted Semicolon | `SELECT * FROM courses` | Lexer/Parser | Successfully parses without trailing `;` | **PASS** |
| **TC-VAL-13** | Boolean Literal | `SELECT name FROM students WHERE is_active = TRUE;` | Semantic | Validated with boolean literal | **PASS** |
| **TC-VAL-14** | NULL Check | `SELECT student_id FROM enrollments WHERE grade != NULL;` | Semantic | Validated with NULL literal | **PASS** |
| **TC-VAL-15** | Compound Parentheses | `SELECT name FROM students WHERE (age >= 18 AND gpa > 3.0) OR department_id = 1;` | Parser/AST | Precedence override, nested subtrees | **PASS** |

---

### Part B: Negative Test Cases (Error Detection & Diagnostics)

| Test ID | Failure Stage | SQL Query Snippet | Failing Token | Expected Diagnostic Error | Execution Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-INV-01** | Syntax Error | `name, age FROM students;` | `name` | `Expected 'SELECT' (statement initiation)` | **PASS** |
| **TC-INV-02** | Syntax Error | `SELECT name, age students;` | `students` | `Expected 'FROM' keyword, but found 'id'` | **PASS** |
| **TC-INV-03** | Syntax Error | `SELECT id FROM;` | `;` | `Expected table identifier after 'FROM'` | **PASS** |
| **TC-INV-04** | Syntax Error | `SELECT id, name, FROM students;` | `FROM` | `Trailing comma in SELECT clause` | **PASS** |
| **TC-INV-05** | Syntax Error | `SELECT id,, name FROM students;` | `,` | `Expected identifier after comma` | **PASS** |
| **TC-INV-06** | Syntax Error | `SELECT FROM students;` | `FROM` | `Expected column list or '*' after 'SELECT'` | **PASS** |
| **TC-INV-07** | Syntax Error | `SELECT name WHERE age >= 18 FROM students;` | `WHERE` | `Expected 'FROM' keyword, but found 'WHERE'` | **PASS** |
| **TC-INV-08** | Syntax Error | `SELECT id FROM students ORDER BY name ASC WHERE age > 20;` | `WHERE` | `Unexpected token 'WHERE' after ORDER BY` | **PASS** |
| **TC-INV-09** | Syntax Error | `SELECT name FROM students SELECT age FROM students;` | `SELECT` | `Unexpected trailing token 'SELECT'` | **PASS** |
| **TC-INV-10** | Syntax Error | `SELECT id FROM students WHERE age >;` | `;` | `Expected literal, column identifier, or '('` | **PASS** |
| **TC-INV-11** | Syntax Error | `SELECT id FROM students WHERE;` | `;` | `Expected boolean condition after 'WHERE'` | **PASS** |
| **TC-INV-12** | Syntax Error | `SELECT name FROM students WHERE age >= 18 AND;` | `;` | `Expected expression following 'AND'` | **PASS** |
| **TC-INV-13** | Syntax Error | `SELECT name FROM students WHERE (age >= 18));` | `)` | `Unexpected token ')'` | **PASS** |
| **TC-INV-14** | Syntax Error | `SELECT name FROM students WHERE (age >= 18;` | `;` | `Expected matching ')' to close condition` | **PASS** |
| **TC-INV-15** | Syntax Error | `SELECT id FROM students ORDER BY;` | `;` | `Expected column identifier after 'ORDER BY'` | **PASS** |
| **TC-INV-16** | Syntax Error | `SELECT name FROM students ORDER BY name SIDEWAYS;`| `SIDEWAYS`| `Expected sort direction ('ASC' or 'DESC')` | **PASS** |
| **TC-INV-17** | Lexical Error | `SELECT name, @salary FROM students;` | `@` | `Lexical Error: Unexpected character '@'` | **PASS** |
| **TC-INV-18** | Lexical Error | `SELECT name FROM students WHERE name = 'John;` | `'John;` | `Lexical Error: Unterminated string literal` | **PASS** |
| **TC-INV-19** | Lexical Error | `SELECT # FROM students;` | `#` | `Lexical Error: Unexpected character '#'` | **PASS** |
| **TC-INV-20** | Semantic Error| `SELECT name FROM unknown_tbl;` | `unknown_tbl` | `Table 'unknown_tbl' does not exist` | **PASS** |
| **TC-INV-21** | Semantic Error| `SELECT salary FROM students;` | `salary` | `Column 'salary' does not exist in 'students'` | **PASS** |
| **TC-INV-22** | Semantic Error| `SELECT *, name FROM students;` | `*` | `Wildcard '*' cannot be combined with columns` | **PASS** |

---

### Part C: Edge Cases & Boundary Conditions

| Test ID | Hazard Focus | SQL Query Snippet | Mechanism Under Test | Execution Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-EDGE-01**| Tight Operators | `SELECT name,age FROM students WHERE age>=18 AND gpa<=4.0;` | Lookahead disambiguation without spaces | **PASS** |
| **TC-EDGE-02**| Inequality Substring | `SELECT id,name FROM departments WHERE id<>1 AND name!='Physics';` | Distinct tokenization of `<>` and `!=` | **PASS** |
| **TC-EDGE-03**| Whitespace Tolerance | Multiline formatted query with indentation & tabs | Lexer whitespace suppression | **PASS** |
| **TC-EDGE-04**| Alphanumeric Identifiers | `SELECT student_id,course_id FROM enrollments WHERE student_id=101;` | `[a-zA-Z_][a-zA-Z0-9_]*` regex verification | **PASS** |
| **TC-EDGE-05**| String Punctuation | `SELECT name,building FROM departments WHERE building='Block-A, North';`| Non-breaking string delimiter scanning | **PASS** |
| **TC-EDGE-06**| Operator Precedence | `SELECT name FROM students WHERE dept=1 OR age>=21 AND gpa>=3.8;` | Verifies `AND` binds tighter than `OR` | **PASS** |
| **TC-EDGE-07**| Deep Nesting | `SELECT name FROM students WHERE ((age>=18 AND dept=1) OR (gpa>=3.5)) AND id>10;` | Mutual recursion of expression parser | **PASS** |
| **TC-EDGE-08**| Mixed Multi-Sort | `SELECT name,gpa FROM students ORDER BY dept ASC, gpa DESC, name ASC;` | Repeated `OrderByItem` iteration | **PASS** |

---

## 3. Automated Test Verification Summary
- **Unit Test Discovery:** 46 automated regression test cases passing in `python -m unittest discover tests`.
- **AST Golden Reference Suite:** 5 golden reference fixtures validated with JSON diff checking (`tests/test_golden_ast.py`).
- **Interactive Verification:** CLI (`python run.py --cli`) and Web Studio IDE (`python run.py`) tested with all 45 matrix queries.
