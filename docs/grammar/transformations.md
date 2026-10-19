# Grammar Transformations: Left-Recursion Elimination and Left-Factoring

**Project:** Mini SQL Compiler  
**Course:** 3rd Year CSE — Compiler Design Mini-Project  
**Document Version:** 1.0.0  
**Status:** Approved Formal Specification  

---

## 1. Theoretical Motivation & Problem Formulation

In compiler syntax analysis, **top-down parsers** (such as LL(1) table-driven parsers and Recursive Descent parsers) construct parse trees from the start symbol downwards by inspecting the current lookahead token to decide which production rule to apply.

Two primary grammatical hazards prevent top-down parsing:

1. **Left-Recursion:**  
   A grammar rule is left-recursive if a non-terminal $A$ derives a sentential form beginning with itself:
   $$A \Rightarrow^+ A\alpha$$
   When a recursive descent parser executes a left-recursive rule, the procedure for `A()` immediately calls `A()` without consuming any input tokens. This produces an **infinite recursive loop**, resulting in a call-stack overflow.

2. **Non-Factored Alternates (Common Prefixes):**  
   If a non-terminal has multiple productions sharing a common prefix:
   $$A \to \alpha\beta_1 \mid \alpha\beta_2$$
   A parser with $k=1$ lookahead token cannot determine whether to choose $\alpha\beta_1$ or $\alpha\beta_2$ upon seeing the first token of $\alpha$. Without left-factoring, the parser would require expensive speculative execution and backtracking.

To ensure our parser operates deterministically with **$O(1)$ lookahead** and **$O(n)$ linear time complexity**, we perform formal Left-Recursion Elimination and Left-Factoring.

---

## 2. Left-Recursion Elimination

### 2.1 Standard Elimination Algorithm
For any immediate left-recursive production of the form:
$$A \to A\alpha_1 \mid A\alpha_2 \mid \dots \mid \beta_1 \mid \beta_2 \dots$$
Where no $\beta_i$ begins with $A$, the grammar is rewritten by introducing a new right-recursive non-terminal $A'$:
$$A \to \beta_1 A' \mid \beta_2 A' \mid \dots$$
$$A' \to \alpha_1 A' \mid \alpha_2 A' \mid \dots \mid \epsilon$$

---

### 2.2 Transformation 1: Logical Disjunction (`<OrExpr>`)

#### Original Production:
```bnf
<OrExpr> ::= <OrExpr> 'OR' <AndExpr>
           | <AndExpr>
```
* Left-recursive term: $\alpha = \text{'OR' } \langle\text{AndExpr}\rangle$
* Base term: $\beta = \langle\text{AndExpr}\rangle$

#### Transformed Production:
```bnf
<OrExpr>      ::= <AndExpr> <OrExprTail>
<OrExprTail>  ::= 'OR' <AndExpr> <OrExprTail>
                | ε
```

---

### 2.3 Transformation 2: Logical Conjunction (`<AndExpr>`)

#### Original Production:
```bnf
<AndExpr> ::= <AndExpr> 'AND' <ComparisonExpr>
            | <ComparisonExpr>
```
* Left-recursive term: $\alpha = \text{'AND' } \langle\text{ComparisonExpr}\rangle$
* Base term: $\beta = \langle\text{ComparisonExpr}\rangle$

#### Transformed Production:
```bnf
<AndExpr>     ::= <ComparisonExpr> <AndExprTail>
<AndExprTail> ::= 'AND' <ComparisonExpr> <AndExprTail>
                | ε
```

---

## 3. Left-Factoring

### 3.1 Standard Left-Factoring Algorithm
For any non-terminal having two or more productions that begin with a common prefix $\alpha$:
$$A \to \alpha\beta_1 \mid \alpha\beta_2 \mid \gamma$$
The common prefix is factored out by introducing a new non-terminal $A'$:
$$A \to \alpha A' \mid \gamma$$
$$A' \to \beta_1 \mid \beta_2$$

---

### 3.2 Transformation 3: Projection Column List (`<ColumnList>`)

#### Original Production:
```bnf
<ColumnList> ::= IDENTIFIER
               | IDENTIFIER ',' <ColumnList>
```
Both alternatives begin with the prefix $\alpha = \text{IDENTIFIER}$.

#### Factored Production:
```bnf
<ColumnList>     ::= IDENTIFIER <ColumnListTail>
<ColumnListTail> ::= ',' <ColumnList>
                   | ε
```

---

### 3.3 Transformation 4: Sorting List (`<OrderByList>`)

#### Original Production:
```bnf
<OrderByList> ::= <OrderByItem>
                | <OrderByItem> ',' <OrderByList>
```
Both alternatives begin with the prefix $\alpha = \langle\text{OrderByItem}\rangle$.

#### Factored Production:
```bnf
<OrderByList>     ::= <OrderByItem> <OrderByListTail>
<OrderByListTail> ::= ',' <OrderByList>
                    | ε
```

---

## 4. Complete Transformed LL(1) / Recursive-Descent Grammar ($G'$)

Below is the complete, unambiguous, non-left-recursive, and left-factored grammar implemented by our parser:

```bnf
1.  <Query>           ::= <SelectClause> <FromClause> <OptWhereClause> <OptOrderByClause> <OptSemicolon>

2.  <SelectClause>    ::= 'SELECT' <SelectList>
3.  <SelectList>      ::= '*'
                        | <ColumnList>
4.  <ColumnList>      ::= IDENTIFIER <ColumnListTail>
5.  <ColumnListTail>  ::= ',' <ColumnList>
                        | ε

6.  <FromClause>      ::= 'FROM' IDENTIFIER

7.  <OptWhereClause>  ::= <WhereClause>
                        | ε
8.  <WhereClause>     ::= 'WHERE' <OrExpr>

9.  <OrExpr>          ::= <AndExpr> <OrExprTail>
10. <OrExprTail>      ::= 'OR' <AndExpr> <OrExprTail>
                        | ε

11. <AndExpr>         ::= <ComparisonExpr> <AndExprTail>
12. <AndExprTail>     ::= 'AND' <ComparisonExpr> <AndExprTail>
                        | ε

13. <ComparisonExpr>  ::= <Expression> <RelOp> <Expression>
                        | '(' <OrExpr> ')'

14. <RelOp>           ::= '=' | '!=' | '<>' | '<' | '<=' | '>' | '>='

15. <Expression>      ::= IDENTIFIER
                        | <Literal>

16. <Literal>         ::= INT_LITERAL
                        | FLOAT_LITERAL
                        | STRING_LITERAL

17. <OptOrderByClause>::= <OrderByClause>
                        | ε
18. <OrderByClause>   ::= 'ORDER' 'BY' <OrderByList>

19. <OrderByList>     ::= <OrderByItem> <OrderByListTail>
20. <OrderByListTail> ::= ',' <OrderByList>
                        | ε

21. <OrderByItem>     ::= IDENTIFIER <OptDirection>
22. <OptDirection>    ::= 'ASC'
                        | 'DESC'
                        | ε

23. <OptSemicolon>    ::= ';'
                        | ε
```

---

## 5. Formal FIRST and FOLLOW Set Computation

### 5.1 Definitions
* **$\text{FIRST}(\alpha)$**: The set of terminal symbols that begin strings derived from $\alpha$. If $\alpha \Rightarrow^* \epsilon$, then $\epsilon \in \text{FIRST}(\alpha)$.
* **$\text{FOLLOW}(A)$**: The set of terminal symbols that can appear immediately to the right of non-terminal $A$ in some sentential form.

---

### 5.2 FIRST and FOLLOW Sets Reference Table

| Non-Terminal ($A$) | $\text{FIRST}(A)$ | $\text{FOLLOW}(A)$ |
| :--- | :--- | :--- |
| **`<Query>`** | `{'SELECT'}` | `{'$'}` (EOF) |
| **`<SelectClause>`** | `{'SELECT'}` | `{'FROM'}` |
| **`<SelectList>`** | `{'*', IDENTIFIER}` | `{'FROM'}` |
| **`<ColumnList>`** | `{IDENTIFIER}` | `{'FROM'}` |
| **`<ColumnListTail>`** | `{',', ε}` | `{'FROM'}` |
| **`<FromClause>`** | `{'FROM'}` | `{'WHERE', 'ORDER', ';', '$'}` |
| **`<OptWhereClause>`** | `{'WHERE', ε}` | `{'ORDER', ';', '$'}` |
| **`<WhereClause>`** | `{'WHERE'}` | `{'ORDER', ';', '$'}` |
| **`<OrExpr>`** | `{'IDENTIFIER', 'INT_LITERAL', 'FLOAT_LITERAL', 'STRING_LITERAL', '('}` | `{'ORDER', ';', '$', ')'}` |
| **`<OrExprTail>`** | `{'OR', ε}` | `{'ORDER', ';', '$', ')'}` |
| **`<AndExpr>`** | `{'IDENTIFIER', 'INT_LITERAL', 'FLOAT_LITERAL', 'STRING_LITERAL', '('}` | `{'OR', 'ORDER', ';', '$', ')'}` |
| **`<AndExprTail>`** | `{'AND', ε}` | `{'OR', 'ORDER', ';', '$', ')'}` |
| **`<ComparisonExpr>`** | `{'IDENTIFIER', 'INT_LITERAL', 'FLOAT_LITERAL', 'STRING_LITERAL', '('}` | `{'AND', 'OR', 'ORDER', ';', '$', ')'}` |
| **`<RelOp>`** | `{'=', '!=', '<>', '<', '<=', '>', '>='}` | `{'IDENTIFIER', 'INT_LITERAL', 'FLOAT_LITERAL', 'STRING_LITERAL'}` |
| **`<Expression>`** | `{'IDENTIFIER', 'INT_LITERAL', 'FLOAT_LITERAL', 'STRING_LITERAL'}` | `{'=', '!=', '<>', '<', '<=', '>', '>=', 'AND', 'OR', 'ORDER', ';', '$', ')'}` |
| **`<Literal>`** | `{'INT_LITERAL', 'FLOAT_LITERAL', 'STRING_LITERAL'}` | `{'=', '!=', '<>', '<', '<=', '>', '>=', 'AND', 'OR', 'ORDER', ';', '$', ')'}` |
| **`<OptOrderByClause>`** | `{'ORDER', ε}` | `{';', '$'}` |
| **`<OrderByClause>`** | `{'ORDER'}` | `{';', '$'}` |
| **`<OrderByList>`** | `{IDENTIFIER}` | `{';', '$'}` |
| **`<OrderByListTail>`** | `{',', ε}` | `{';', '$'}` |
| **`<OrderByItem>`** | `{IDENTIFIER}` | `{',', ';', '$'}` |
| **`<OptDirection>`** | `{'ASC', 'DESC', ε}` | `{',', ';', '$'}` |
| **`<OptSemicolon>`** | `{';', ε}` | `{'$'}` |

---

## 6. Verification of LL(1) Properties

A grammar $G$ is **LL(1)** if and only if for every pair of productions $A \to \alpha \mid \beta$:
1. $\text{FIRST}(\alpha) \cap \text{FIRST}(\beta) = \emptyset$
2. If $\epsilon \in \text{FIRST}(\alpha)$, then $\text{FIRST}(\beta) \cap \text{FOLLOW}(A) = \emptyset$

### Proof of Disjointness for Key Ambiguity Candidates:

1. **`<SelectList> ::= '*' | <ColumnList>`**
   * $\text{FIRST}(*) = \{*\}$
   * $\text{FIRST}(\langle\text{ColumnList}\rangle) = \{\text{IDENTIFIER}\}$
   * $\{*\} \cap \{\text{IDENTIFIER}\} = \emptyset$ $\implies$ **Deterministic choice.**

2. **`<OrExprTail> ::= 'OR' <AndExpr> <OrExprTail> | ε`**
   * $\text{FIRST}(\text{'OR' ...}) = \{\text{'OR'}\}$
   * $\text{FOLLOW}(\langle\text{OrExprTail}\rangle) = \text{FOLLOW}(\langle\text{OrExpr}\rangle) = \{\text{'ORDER'}, \text{';'}, \text{'\$'}, \text{')'}\}$
   * $\{\text{'OR'}\} \cap \{\text{'ORDER'}, \text{';'}, \text{'\$'}, \text{')'}\} = \emptyset$ $\implies$ **Deterministic choice.**

3. **`<OptDirection> ::= 'ASC' | 'DESC' | ε`**
   * $\text{FIRST}(\text{'ASC'}) = \{\text{'ASC'}\}$
   * $\text{FIRST}(\text{'DESC'}) = \{\text{'DESC'}\}$
   * $\text{FOLLOW}(\langle\text{OptDirection}\rangle) = \{',', ';', '\$\}$
   * All three sets are mutually disjoint $\implies$ **Deterministic choice.**

**Conclusion:** The transformed grammar $G'$ satisfies all LL(1) conditions and can be parsed deterministically without backtracking using a single lookahead token.

---

## 7. Viva Voce Defense Guide

* **Q: Why can't a top-down parser parse left-recursive grammars directly?**  
  * **Answer:** In top-down parsing, a non-terminal rule translates into a recursive function call. If rule $A \to A\alpha$ is executed, the function `A()` calls `A()` as its very first instruction without consuming any input symbol from the lexer. This results in infinite recursion and a stack overflow crash.
* **Q: How does left-recursion elimination change the parse tree shape?**  
  * **Answer:** It converts a left-skewed (left-branching) parse tree into a right-skewed (right-branching) parse tree with tail non-terminals ($A'$). The parser accumulates the tokens iteratively or re-associates operands to preserve left-associativity when building the AST.
* **Q: What is the purpose of left-factoring?**  
  * **Answer:** Left-factoring defers the decision of which production to choose until enough tokens have been seen to make an unambiguous choice. It removes common prefixes so that a 1-token lookahead ($k=1$) is sufficient.
