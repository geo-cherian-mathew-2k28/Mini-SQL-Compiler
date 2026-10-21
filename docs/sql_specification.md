# Mini SQL Language Specification

## 1. Scope and Purpose
This document establishes the formal language specification for the **Mini SQL Compiler**, engineered as a modular front-end pipeline for 3rd-year Computer Science & Engineering (Compiler Design Mini-Project).

Standard ANSI SQL is an expansive, Turing-complete declarative language comprising Data Definition Language (DDL), Data Manipulation Language (DML), Data Control Language (DCL), transaction semantics, procedural extensions, and advanced relational operators. For the academic objectives of lexical analysis, deterministic top-down parsing (LL(1) recursive descent), Abstract Syntax Tree (AST) synthesis, and symbol-table-driven semantic verification, this compiler targets a rigorous, deterministic subset centered on relational projection, filtering, and ordering.

---

## 2. Mandatory Clause Ordering
Every valid Mini SQL statement follows a strict, non-negotiable clause sequence:

$$\text{SELECT} \longrightarrow \text{FROM} \longrightarrow [\text{WHERE}] \longrightarrow [\text{ORDER BY}] \longrightarrow [;]$$

Unlike commercial DBMS engines with extensive pre-processors, the parser strictly rejects queries with out-of-order clauses at the syntax level:
1. **`SELECT` clause** (Mandatory): Defines the projection attributes.
2. **`FROM` clause** (Mandatory): Declares the source relation / table identifier.
3. **`WHERE` clause** (Optional): Specifies the filtering predicate expression.
4. **`ORDER BY` clause** (Optional): Specifies the ordering attributes and sort direction.
5. **Statement Terminator** (Optional): Semicolon (`;`).

---

## 3. Supported Clauses & Detailed Syntax

### 3.1 `SELECT` (Projections)
The `SELECT` clause designates the attributes to be extracted from the source table.
- **Wildcard Selection (`*`):** Selects all attributes present in the resolved relation schema.
  ```sql
  SELECT * FROM students;
  ```
- **Explicit Attribute List:** A comma-separated list of valid attribute identifiers.
  ```sql
  SELECT name, age, gpa FROM students;
  ```
- **Restrictions:**
  - Trailing commas are strictly prohibited (e.g., `SELECT id, FROM tbl;` triggers a syntax error).
  - Mixing wildcard with explicit attributes (e.g., `SELECT *, name FROM tbl;`) is treated as a semantic violation.

### 3.2 `FROM` (Relation Reference)
The `FROM` clause identifies the target relation in the schema catalog.
- Only a single table identifier is supported per query:
  ```sql
  FROM students
  ```
- Table aliases (e.g., `FROM students s`) are intentionally omitted to keep the grammar LL(1) without complex alias resolution in the symbol table.

### 3.3 `WHERE` (Filtering Predicates)
The `WHERE` clause defines a boolean predicate expression used to filter tuples.
- **Binary Comparison Operators:**
  - Equal: `=`
  - Not Equal: `!=` or `<>`
  - Less Than: `<`
  - Less Than or Equal: `<=`
  - Greater Than: `>`
  - Greater Than or Equal: `>=`
- **Supported Literals:**
  - `INTEGER`: Sequences of digits (e.g., `18`, `2026`).
  - `FLOAT`: Numbers containing decimal points (e.g., `3.75`, `0.05`).
  - `STRING`: Single-quoted character sequences (e.g., `'Computer Science'`, `'Alice'`).
  - `BOOLEAN`: Keyword literals `TRUE` or `FALSE`.
  - `NULL`: Keyword literal `NULL`.
- **Logical Connectives:**
  - `AND`: Higher precedence logical conjunction.
  - `OR`: Lower precedence logical disjunction.
  - `NOT`: Unary logical negation.
- **Parenthetical Grouping:**
  - Parentheses `(` and `)` are fully supported to override default operator precedence.
  ```sql
  WHERE (age >= 18 AND gpa > 3.0) OR department_id = 1
  ```

### 3.4 `ORDER BY` (Tuple Sorting)
The `ORDER BY` clause designates sorting specifications.
- **Ordering Columns:** Column identifier followed by an optional sort direction.
- **Sort Directions:**
  - `ASC`: Ascending order (default when omitted).
  - `DESC`: Descending order.
- **Multiple Columns:** Supports comma-separated columns with individual directions.
  ```sql
  ORDER BY department_id ASC, gpa DESC
  ```

---

## 4. Predefined Database Catalog
Semantic validation checks all queries against the built-in catalog schema:

| Table Name | Attributes (Columns) & Types | Primary Key / Nullability |
| :--- | :--- | :--- |
| **`students`** | `id` (INTEGER), `name` (VARCHAR), `age` (INTEGER), `gpa` (FLOAT), `department_id` (INTEGER), `is_active` (BOOLEAN) | `id` (PK, NOT NULL) |
| **`departments`** | `id` (INTEGER), `name` (VARCHAR), `building` (VARCHAR) | `id` (PK, NOT NULL) |
| **`courses`** | `id` (INTEGER), `title` (VARCHAR), `credits` (INTEGER), `department_id` (INTEGER) | `id` (PK, NOT NULL) |
| **`enrollments`** | `student_id` (INTEGER), `course_id` (INTEGER), `grade` (VARCHAR) | Composite (`student_id`, `course_id`) |

---

## 5. Explicitly Unsupported SQL Features (Boundary Declaration)

To prevent scope ambiguity during evaluation, the following ANSI SQL constructs are declared **outside the language boundary**:

1. **Relational Joins:** `INNER JOIN`, `LEFT JOIN`, `RIGHT JOIN`, `FULL OUTER JOIN`, `CROSS JOIN`, implicit comma joins (`FROM table1, table2`).
2. **Aggregations & Grouping:** `GROUP BY`, `HAVING`, and aggregate functions (`COUNT()`, `SUM()`, `AVG()`, `MIN()`, `MAX()`).
3. **Data Modification (DML):** `INSERT INTO`, `UPDATE`, `DELETE`, `MERGE`.
4. **Data Definition (DDL):** `CREATE TABLE`, `ALTER TABLE`, `DROP TABLE`, `TRUNCATE`.
5. **Subqueries & Set Operations:** Nested `SELECT` queries, `UNION`, `INTERSECT`, `EXCEPT`.
6. **Transactions & Session Control:** `BEGIN`, `COMMIT`, `ROLLBACK`, `SET`.

---

## 6. Representative Valid Queries

### Query 1: Universal Projection
```sql
SELECT * FROM students;
```

### Query 2: Column Selection with Numeric Filter
```sql
SELECT name, age FROM students WHERE age >= 20;
```

### Query 3: Multi-condition Predicate with Parentheses
```sql
SELECT title, credits FROM courses WHERE (credits >= 3 AND department_id = 2) OR credits = 4;
```

### Query 4: Filtering with String Literal and Directional Sort
```sql
SELECT name, building FROM departments WHERE name = 'Computer Science' ORDER BY building ASC;
```

### Query 5: Full Four-Clause Query with Compound Sorting
```sql
SELECT name, gpa, age FROM students WHERE is_active = TRUE AND gpa >= 3.5 ORDER BY department_id ASC, gpa DESC;
```
