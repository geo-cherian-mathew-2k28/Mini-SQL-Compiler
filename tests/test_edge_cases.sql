-- ============================================================================
-- Mini SQL Compiler — Boundary Conditions & Complex Edge-Case Query Suite
-- Target: Lookahead disambiguation, whitespace tolerance, operator binding,
--         nested boolean precedence, and mixed multi-column ordering.
-- ============================================================================

-- TC-EDGE-01: Dense operator tokenization without surrounding whitespace
SELECT name,age FROM students WHERE age>=18 AND gpa<=4.0;

-- TC-EDGE-02: Mixed inequality operators (<> vs !=) without spaces
SELECT id,name FROM departments WHERE id<>1 AND name!='Physics';

-- TC-EDGE-03: Heavy whitespace, indentation, tabulations, and multi-line breaks
SELECT
    id,
    name,
    gpa
FROM
    students
WHERE
    age   >=   20
    AND
    gpa   >    3.5
ORDER BY
    gpa   DESC;

-- TC-EDGE-04: Identifiers with internal numbers and snake_case underscores
SELECT student_id,course_id,grade FROM enrollments WHERE student_id=101 AND course_id=202;

-- TC-EDGE-05: String literals containing embedded punctuation, spaces, and commas
SELECT name,building FROM departments WHERE building='Block-A, North Wing 3';

-- TC-EDGE-06: Operator precedence — AND binding tighter than OR without explicit parentheses
-- Expected AST: (department_id = 1) OR ((age >= 21) AND (gpa >= 3.8))
SELECT name,age,gpa FROM students WHERE department_id = 1 OR age >= 21 AND gpa >= 3.8;

-- TC-EDGE-07: Overriding operator precedence with deep nested parenthetical groupings
SELECT name,gpa FROM students WHERE ((age >= 18 AND department_id = 1) OR (gpa >= 3.5 AND is_active = TRUE)) AND id > 10;

-- TC-EDGE-08: Compound multi-column sorting with mixed ascending/descending directions
SELECT name,department_id,gpa FROM students ORDER BY department_id ASC, gpa DESC, name ASC;

-- TC-EDGE-09: Unary NOT operator preceding a grouped parenthetical condition
SELECT id,title FROM courses WHERE NOT (credits < 3 OR department_id = 4);

-- TC-EDGE-10: Filtering against SQL Boolean and NULL literal keywords
SELECT id,name FROM students WHERE is_active = TRUE AND gpa != NULL;

-- TC-EDGE-11: Trailing whitespace, line feed, and query without terminating semicolon
SELECT name,building FROM departments WHERE id = 1

-- TC-EDGE-12: Single attribute projection with ORDER BY omitting explicit ASC keyword
SELECT title FROM courses WHERE credits >= 3 ORDER BY title;
