%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ast.h"

extern int yylex();
extern int current_line;
extern int current_col;
void yyerror(const char* s);

ASTNode* root_ast = NULL;
%}

%union {
    int ival;
    double fval;
    char* str;
    struct ASTNode* node;
}

%token TOKEN_SELECT TOKEN_FROM TOKEN_WHERE TOKEN_ORDER TOKEN_BY TOKEN_ASC TOKEN_DESC
%token TOKEN_AND TOKEN_OR
%token TOKEN_STAR TOKEN_COMMA TOKEN_SEMI TOKEN_LPAREN TOKEN_RPAREN
%token <str> TOKEN_EQ TOKEN_NEQ TOKEN_LT TOKEN_LTE TOKEN_GT TOKEN_GTE
%token <str> TOKEN_IDENTIFIER TOKEN_STRING
%token <ival> TOKEN_INT
%token <fval> TOKEN_FLOAT

%type <node> query select_clause projection_list from_clause
%type <node> opt_where_clause where_clause or_expr and_expr comparison_expr expression
%type <node> opt_order_by_clause order_by_clause order_by_list order_by_item
%type <str> opt_direction rel_op

/* Precedence declarations */
%left TOKEN_OR
%left TOKEN_AND
%nonassoc TOKEN_EQ TOKEN_NEQ TOKEN_LT TOKEN_LTE TOKEN_GT TOKEN_GTE

%%

query:
    select_clause from_clause opt_where_clause opt_order_by_clause opt_semicolon
    {
        root_ast = create_select_query($1, $2, $3, $4);
        $$ = root_ast;
    }
    ;

opt_semicolon:
    TOKEN_SEMI
    | /* empty */
    ;

select_clause:
    TOKEN_SELECT projection_list
    {
        $$ = $2;
    }
    ;

projection_list:
    TOKEN_STAR
    {
        $$ = create_wildcard();
    }
    | TOKEN_IDENTIFIER
    {
        $$ = create_identifier($1);
    }
    | TOKEN_IDENTIFIER TOKEN_COMMA projection_list
    {
        ASTNode* id = create_identifier($1);
        id->next = $3;
        $$ = id;
    }
    ;

from_clause:
    TOKEN_FROM TOKEN_IDENTIFIER
    {
        $$ = create_table($2);
    }
    ;

opt_where_clause:
    where_clause
    {
        $$ = $1;
    }
    | /* empty */
    {
        $$ = NULL;
    }
    ;

where_clause:
    TOKEN_WHERE or_expr
    {
        $$ = $2;
    }
    ;

or_expr:
    and_expr
    {
        $$ = $1;
    }
    | or_expr TOKEN_OR and_expr
    {
        $$ = create_binary_expr("OR", $1, $3);
    }
    ;

and_expr:
    comparison_expr
    {
        $$ = $1;
    }
    | and_expr TOKEN_AND comparison_expr
    {
        $$ = create_binary_expr("AND", $1, $3);
    }
    ;

comparison_expr:
    TOKEN_LPAREN or_expr TOKEN_RPAREN
    {
        $$ = $2;
    }
    | expression rel_op expression
    {
        $$ = create_binary_expr($2, $1, $3);
    }
    ;

rel_op:
    TOKEN_EQ   { $$ = "="; }
    | TOKEN_NEQ  { $$ = "!="; }
    | TOKEN_LT   { $$ = "<"; }
    | TOKEN_LTE  { $$ = "<="; }
    | TOKEN_GT   { $$ = ">"; }
    | TOKEN_GTE  { $$ = ">="; }
    ;

expression:
    TOKEN_IDENTIFIER
    {
        $$ = create_identifier($1);
    }
    | TOKEN_INT
    {
        $$ = create_literal_int($1);
    }
    | TOKEN_FLOAT
    {
        $$ = create_literal_float($1);
    }
    | TOKEN_STRING
    {
        $$ = create_literal_string($1);
    }
    ;

opt_order_by_clause:
    order_by_clause
    {
        $$ = $1;
    }
    | /* empty */
    {
        $$ = NULL;
    }
    ;

order_by_clause:
    TOKEN_ORDER TOKEN_BY order_by_list
    {
        $$ = $3;
    }
    ;

order_by_list:
    order_by_item
    {
        $$ = $1;
    }
    | order_by_item TOKEN_COMMA order_by_list
    {
        $1->next = $3;
        $$ = $1;
    }
    ;

order_by_item:
    TOKEN_IDENTIFIER opt_direction
    {
        $$ = create_order_item($1, $2);
    }
    ;

opt_direction:
    TOKEN_ASC  { $$ = "ASC"; }
    | TOKEN_DESC { $$ = "DESC"; }
    | /* empty */ { $$ = "ASC"; }
    ;

%%

void yyerror(const char* s) {
    fprintf(stderr, "Syntax Error at line %d, col %d: %s\n", current_line, current_col, s);
}

int main(int argc, char** argv) {
    printf("Mini SQL Compiler (Lex & Yacc Reference Engine)\n");
    printf("Enter SQL Query followed by Ctrl+D:\n> ");
    if (yyparse() == 0) {
        printf("\n[SUCCESS] Query parsed successfully by YACC!\n");
        if (root_ast) {
            printf("\nAbstract Syntax Tree:\n");
            print_ast(root_ast, 0);
            free_ast(root_ast);
        }
    } else {
        printf("\n[FAILURE] Syntax validation failed.\n");
    }
    return 0;
}
