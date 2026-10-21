-- ============================================================================
-- Mini SQL Compiler — Positive / Valid SQL Test Suite
-- Target: Verification of Lexer, Parser, AST Construction, and Grammar Permutations
-- ============================================================================

-- [Category 1: Projections & Relation Selection]
-- TC-VAL-01: Wildcard projection selecting all columns from relation
SELECT * FROM students;

-- TC-VAL-02: Multi-column explicit attribute projection list
SELECT name, age FROM students;

-- [Category 2: Filtering with Single Predicates (WHERE Clause)]
-- TC-VAL-03: Simple numeric comparison in WHERE clause
SELECT name FROM students WHERE age >= 20;

-- TC-VAL-04: String literal comparison in WHERE clause
SELECT name, building FROM departments WHERE name = 'Computer Science';

-- [Category 3: Compound Logical Predicates (AND / OR)]
-- TC-VAL-05: Compound filtering condition with logical AND
SELECT title, credits FROM courses WHERE credits >= 3 AND department_id = 1;

-- TC-VAL-06: Compound filtering condition with logical OR
SELECT name FROM students WHERE age = 18 OR age = 19;

-- [Category 4: Sorting Specifications (ORDER BY Clause)]
-- TC-VAL-07: Sorting with explicit ascending direction (ASC)
SELECT name FROM students ORDER BY name ASC;

-- TC-VAL-08: Sorting with explicit descending direction (DESC)
SELECT name, gpa FROM students ORDER BY gpa DESC;

-- TC-VAL-09: Sorting with implicit default direction (resolves to ASC)
SELECT title FROM courses ORDER BY title;

-- TC-VAL-10: Multi-column sorting with mixed ASC and DESC directions
SELECT name, department_id, gpa FROM students ORDER BY department_id ASC, gpa DESC;

-- [Category 5: Clause Combinations, Terminators & Precedence]
-- TC-VAL-11: Full four-clause statement combining SELECT, FROM, WHERE, and ORDER BY
SELECT name, age FROM students WHERE age >= 18 ORDER BY name ASC;

-- TC-VAL-12: Valid statement omitting optional terminating semicolon
SELECT * FROM courses

-- TC-VAL-13: Filtering against boolean literal keyword
SELECT name FROM students WHERE is_active = TRUE;

-- TC-VAL-14: Filtering against NULL literal keyword with inequality operator
SELECT student_id FROM enrollments WHERE grade != NULL;

-- TC-VAL-15: Compound condition with parenthetical grouping overriding default precedence
SELECT name FROM students WHERE (age >= 18 AND gpa > 3.0) OR department_id = 1;

-- [Category 6: Syntax Permutations, Whitespace & Keyword Case Invariance]
-- TC-VAL-16: Minimal query with single attribute projection and no optional clauses
SELECT id FROM students;

-- TC-VAL-17: Multi-column projection with irregular and varying whitespace
SELECT   id  ,   name , age   FROM   students ;

-- TC-VAL-18: Mixed-case and lowercase keywords testing case-insensitive tokenization
select ID from Users where AGE > 18;

-- TC-VAL-19: Floating-point numeric comparison with less-than-or-equal operator (<=)
SELECT title, price FROM products WHERE price <= 99.99;

-- TC-VAL-20: Inequality comparison using standard SQL not-equal operator (<>)
SELECT emp_id, name FROM employees WHERE department <> 'HR';
