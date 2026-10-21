-- ============================================================================
-- Mini SQL Compiler — Negative / Invalid SQL Test Suite
-- Target: Verification of Syntax, Lexical, and Semantic Error Diagnostics
-- ============================================================================

-- [Category 1: Missing Mandatory Keywords]
-- TC-INV-01: Missing SELECT keyword (statement begins with projection)
name, age FROM students;

-- TC-INV-02: Missing FROM keyword
SELECT name, age students;

-- TC-INV-03: Missing table name after FROM keyword
SELECT id FROM;

-- [Category 2: Malformed Projections & Trailing Syntax]
-- TC-INV-04: Trailing comma in column projection list
SELECT id, name, FROM students;

-- TC-INV-05: Missing column identifier between commas
SELECT id,, name FROM students;

-- TC-INV-06: Empty SELECT clause without wildcard or identifier
SELECT FROM students;

-- [Category 3: Clause Ordering Violations]
-- TC-INV-07: WHERE clause preceding FROM clause
SELECT name WHERE age >= 18 FROM students;

-- TC-INV-08: ORDER BY clause preceding WHERE clause
SELECT id, name FROM students ORDER BY name ASC WHERE age > 20;

-- TC-INV-09: Repeated SELECT statement
SELECT name FROM students SELECT age FROM students;

-- [Category 4: Incomplete & Malformed Expressions]
-- TC-INV-10: Incomplete WHERE clause (missing right-hand operand)
SELECT id FROM students WHERE age >;

-- TC-INV-11: Empty WHERE clause without boolean condition
SELECT id FROM students WHERE;

-- TC-INV-12: Dangling binary logical operator in condition
SELECT name FROM students WHERE age >= 18 AND;

-- TC-INV-13: Unmatched closing parenthesis in WHERE condition
SELECT name FROM students WHERE (age >= 18 AND gpa > 3.0));

-- TC-INV-14: Unmatched opening parenthesis in WHERE condition
SELECT name FROM students WHERE (age >= 18 AND gpa > 3.0;

-- [Category 5: Malformed ORDER BY Clause]
-- TC-INV-15: ORDER BY missing target column identifier
SELECT id FROM students ORDER BY;

-- TC-INV-16: Invalid sorting direction keyword
SELECT name FROM students ORDER BY name SIDEWAYS;

-- [Category 6: Lexical Errors (Tokens & Characters)]
-- TC-INV-17: Illegal character / unmapped symbol (@ symbol)
SELECT name, @salary FROM students;

-- TC-INV-18: Unterminated single-quoted string literal
SELECT name FROM students WHERE name = 'John;

-- TC-INV-19: Illegal character (# symbol)
SELECT # FROM students;

-- [Category 7: Semantic & Catalog Violations]
-- TC-INV-20: Non-existent relation / table name
SELECT name FROM non_existent_table;

-- TC-INV-21: Non-existent column / attribute name
SELECT non_existent_col FROM students;

-- TC-INV-22: Ambiguous projection mixing wildcard and column identifiers
SELECT *, name FROM students;
