# Formal Context-Free Grammar (CFG) Specification for Mini SQL

**Project:** Mini SQL Compiler  
**Course:** 3rd Year CSE — Compiler Design Mini-Project  
**Document Version:** 1.0.0  
**Status:** Approved Specification  

---

## 1. Mathematical Definition of the Grammar

Formally, the Context-Free Grammar $G$ is defined as a 4-tuple:

$$G = (V, \Sigma, R, S)$$

Where:
* **$V$** is the finite set of **Non-Terminal** symbols.
* **$\Sigma$** is the finite set of **Terminal** symbols (Tokens), disjoint from $V$ ($V \cap \Sigma = \emptyset$).
* **$R$** is the finite set of **Production Rules** mapping $V \to (V \cup \Sigma)^*$.
* **$S \in V$** is the **Start Symbol** ($S = \text{\<Query\>}$).

---

## 2. Terminal Symbols ($\Sigma$)

The alphabet of terminals corresponds to the tokens emitted by the Lexical Analyzer:

### 2.1 Keywords (Case-Insensitive)
* `SELECT`, `FROM`, `WHERE`, `ORDER`, `BY`, `ASC`, `DESC`, `AND`, `OR`

### 2.2 Punctuation & Delimiters
* `*` (Asterisk / Wildcard)
* `,` (Comma)
* `;` (Semicolon / Statement Terminator)
* `(` (Left Parenthesis)
* `)` (Right Parenthesis)

### 2.3 Relational Operators (`RelOp`)
* `=` (Equal)
* `!=` or `<>` (Not Equal)
* `<` (Less Than)
* `<=` (Less Than or Equal)
* `>` (Greater Than)
* `>=` (Greater Than or Equal)

### 2.4 Lexical Classes / Literals
* `IDENTIFIER`: Column or Table name ($[a\text{-}zA\text{-}Z\_][a\text{-}zA\text{-}Z0\text{-}9\_]*$)
* `INT_LITERAL`: Integer numeric constant ($[0\text{-}9]+$)
* `FLOAT_LITERAL`: Floating-point numeric constant ($[0\text{-}9]+\.[0\text{-}9]+$)
* `STRING_LITERAL`: Character sequence enclosed in single quotes ($'[^']*'$)

---

## 3. Non-Terminal Symbols ($V$)

The set of non-terminals represents syntactic structures and expression hierarchies:

```text
V = {
    <Query>,
    <SelectClause>,
    <SelectList>,
    <ColumnList>,
    <FromClause>,
    <WhereClause>,
    <OrExpr>,
    <AndExpr>,
    <ComparisonExpr>,
    <RelOp>,
    <Expression>,
    <Literal>,
    <OrderByClause>,
    <OrderByList>,
    <OrderByItem>,
    <Direction>
}
```

---

## 4. Production Rules ($R$) in Backus-Naur Form (BNF)

### 4.1 Top-Level Query Structure
A valid query must strictly follow the standard SQL clause order: `SELECT` $\to$ `FROM` $\to$ [optional `WHERE`] $\to$ [optional `ORDER BY`] $\to$ [optional `;`].

```bnf
<Query> ::= <SelectClause> <FromClause> <OptWhereClause> <OptOrderByClause> <OptSemicolon>

<OptWhereClause> ::= <WhereClause>
                   | ε

<OptOrderByClause> ::= <OrderByClause>
                     | ε

<OptSemicolon> ::= ';'
                 | ε
```

---

### 4.2 Projections (`SELECT` Clause)
The query selects either all columns using wildcard `*` or a non-empty, comma-separated list of column identifiers.

```bnf
<SelectClause> ::= 'SELECT' <SelectList>

<SelectList> ::= '*'
               | <ColumnList>

<ColumnList> ::= IDENTIFIER
               | IDENTIFIER ',' <ColumnList>
```

---

### 4.3 Table Source (`FROM` Clause)
Restricted to a single base table name (no `JOIN` or comma-separated cross-joins).

```bnf
<FromClause> ::= 'FROM' IDENTIFIER
```

---

### 4.4 Filter Conditions (`WHERE` Clause) & Precedence Hierarchy
To prevent syntactic ambiguity, the conditional expression grammar strictly encodes **operator precedence**:
1. **Parentheses `( ... )`** (Highest precedence)
2. **Relational Operators** (`=`, `!=`, `<`, `>`, `<=`, `>=`)
3. **`AND`** (Conjunction, higher precedence than `OR`, left-associative)
4. **`OR`** (Disjunction, lowest logical precedence, left-associative)

```bnf
<WhereClause> ::= 'WHERE' <OrExpr>

<OrExpr> ::= <AndExpr>
           | <OrExpr> 'OR' <AndExpr>

<AndExpr> ::= <ComparisonExpr>
            | <AndExpr> 'AND' <ComparisonExpr>

<ComparisonExpr> ::= <Expression> <RelOp> <Expression>
                   | '(' <OrExpr> ')'

<RelOp> ::= '=' | '!=' | '<>' | '<' | '<=' | '>' | '>='

<Expression> ::= IDENTIFIER
               | <Literal>

<Literal> ::= INT_LITERAL
            | FLOAT_LITERAL
            | STRING_LITERAL
```

---

### 4.5 Sorting Specifications (`ORDER BY` Clause)
The `ORDER BY` clause consists of one or more column sorting items, each with an optional direction (`ASC` or `DESC`, defaulting to `ASC`).

```bnf
<OrderByClause> ::= 'ORDER' 'BY' <OrderByList>

<OrderByList> ::= <OrderByItem>
                | <OrderByItem> ',' <OrderByList>

<OrderByItem> ::= IDENTIFIER <OptDirection>

<OptDirection> ::= 'ASC'
                 | 'DESC'
                 | ε
```

---

## 5. Ambiguity Analysis and Precedence Guarantees

1. **Clause Ordering:** Clause reordering (e.g., placing `WHERE` before `FROM` or after `ORDER BY`) is impossible in this grammar because `<Query>` strictly enforces sequential non-terminal expansion.
2. **Dangling Logical Operators:** In expressions like `a = 1 OR b = 2 AND c = 3`, the layered production chain `<OrExpr> -> <AndExpr> -> <ComparisonExpr>` forces `b = 2 AND c = 3` to bind more tightly than `a = 1 OR ...`, guaranteeing standard Boolean evaluation semantics without ambiguity.
3. **Associativity:** The left-recursive formulation of `<OrExpr>` and `<AndExpr>` encodes left-associativity. *(Note: in Phase 3 / Issue #5, this left-recursion is formally eliminated to produce the LL(1) / Recursive Descent compatible grammar).*

---

## 6. Sample Derivation Walkthrough

### Example Query:
```sql
SELECT name, age FROM students WHERE age >= 18 ORDER BY name ASC;
```

### Derivation Steps:
```text
<Query>
=> <SelectClause> <FromClause> <OptWhereClause> <OptOrderByClause> <OptSemicolon>
=> 'SELECT' <SelectList> <FromClause> <OptWhereClause> <OptOrderByClause> <OptSemicolon>
=> 'SELECT' <ColumnList> <FromClause> <OptWhereClause> <OptOrderByClause> <OptSemicolon>
=> 'SELECT' IDENTIFIER(name) ',' <ColumnList> <FromClause> <OptWhereClause> <OptOrderByClause> <OptSemicolon>
=> 'SELECT' IDENTIFIER(name) ',' IDENTIFIER(age) <FromClause> <OptWhereClause> <OptOrderByClause> <OptSemicolon>
=> 'SELECT' IDENTIFIER(name) ',' IDENTIFIER(age) 'FROM' IDENTIFIER(students) <OptWhereClause> <OptOrderByClause> <OptSemicolon>
=> 'SELECT' IDENTIFIER(name) ',' IDENTIFIER(age) 'FROM' IDENTIFIER(students) <WhereClause> <OptOrderByClause> <OptSemicolon>
=> 'SELECT' IDENTIFIER(name) ',' IDENTIFIER(age) 'FROM' IDENTIFIER(students) 'WHERE' <OrExpr> <OptOrderByClause> <OptSemicolon>
=> 'SELECT' IDENTIFIER(name) ',' IDENTIFIER(age) 'FROM' IDENTIFIER(students) 'WHERE' <AndExpr> <OptOrderByClause> <OptSemicolon>
=> 'SELECT' IDENTIFIER(name) ',' IDENTIFIER(age) 'FROM' IDENTIFIER(students) 'WHERE' <ComparisonExpr> <OptOrderByClause> <OptSemicolon>
=> 'SELECT' IDENTIFIER(name) ',' IDENTIFIER(age) 'FROM' IDENTIFIER(students) 'WHERE' <Expression> <RelOp> <Expression> <OptOrderByClause> <OptSemicolon>
=> 'SELECT' IDENTIFIER(name) ',' IDENTIFIER(age) 'FROM' IDENTIFIER(students) 'WHERE' IDENTIFIER(age) '>=' INT_LITERAL(18) <OptOrderByClause> <OptSemicolon>
=> 'SELECT' IDENTIFIER(name) ',' IDENTIFIER(age) 'FROM' IDENTIFIER(students) 'WHERE' IDENTIFIER(age) '>=' INT_LITERAL(18) <OrderByClause> <OptSemicolon>
=> 'SELECT' IDENTIFIER(name) ',' IDENTIFIER(age) 'FROM' IDENTIFIER(students) 'WHERE' IDENTIFIER(age) '>=' INT_LITERAL(18) 'ORDER' 'BY' <OrderByList> <OptSemicolon>
=> 'SELECT' IDENTIFIER(name) ',' IDENTIFIER(age) 'FROM' IDENTIFIER(students) 'WHERE' IDENTIFIER(age) '>=' INT_LITERAL(18) 'ORDER' 'BY' <OrderByItem> <OptSemicolon>
=> 'SELECT' IDENTIFIER(name) ',' IDENTIFIER(age) 'FROM' IDENTIFIER(students) 'WHERE' IDENTIFIER(age) '>=' INT_LITERAL(18) 'ORDER' 'BY' IDENTIFIER(name) 'ASC' <OptSemicolon>
=> 'SELECT' IDENTIFIER(name) ',' IDENTIFIER(age) 'FROM' IDENTIFIER(students) 'WHERE' IDENTIFIER(age) '>=' INT_LITERAL(18) 'ORDER' 'BY' IDENTIFIER(name) 'ASC' ';'
```
The query string is successfully generated by $G$, proving syntactic membership.
