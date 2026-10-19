%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ast.h"
#include "parser.tab.h"

int current_line = 1;
int current_col = 1;

void count_tokens(const char* text) {
    for (int i = 0; text[i] != '\0'; i++) {
        if (text[i] == '\n') {
            current_line++;
            current_col = 1;
        } else {
            current_col++;
        }
    }
}
%}

%option noyywrap
%option case-insensitive

%%

"SELECT"            { count_tokens(yytext); return TOKEN_SELECT; }
"FROM"              { count_tokens(yytext); return TOKEN_FROM; }
"WHERE"             { count_tokens(yytext); return TOKEN_WHERE; }
"ORDER"             { count_tokens(yytext); return TOKEN_ORDER; }
"BY"                { count_tokens(yytext); return TOKEN_BY; }
"ASC"               { count_tokens(yytext); return TOKEN_ASC; }
"DESC"              { count_tokens(yytext); return TOKEN_DESC; }
"AND"               { count_tokens(yytext); return TOKEN_AND; }
"OR"                { count_tokens(yytext); return TOKEN_OR; }

"="                 { count_tokens(yytext); yylval.str = strdup(yytext); return TOKEN_EQ; }
"!="                { count_tokens(yytext); yylval.str = strdup(yytext); return TOKEN_NEQ; }
"<>"                { count_tokens(yytext); yylval.str = strdup("!="); return TOKEN_NEQ; }
"<="                { count_tokens(yytext); yylval.str = strdup(yytext); return TOKEN_LTE; }
">="                { count_tokens(yytext); yylval.str = strdup(yytext); return TOKEN_GTE; }
"<"                 { count_tokens(yytext); yylval.str = strdup(yytext); return TOKEN_LT; }
">"                 { count_tokens(yytext); yylval.str = strdup(yytext); return TOKEN_GT; }

"*"                 { count_tokens(yytext); return TOKEN_STAR; }
","                 { count_tokens(yytext); return TOKEN_COMMA; }
";"                 { count_tokens(yytext); return TOKEN_SEMI; }
"("                 { count_tokens(yytext); return TOKEN_LPAREN; }
")"                 { count_tokens(yytext); return TOKEN_RPAREN; }

[0-9]+\.[0-9]+      { count_tokens(yytext); yylval.fval = atof(yytext); return TOKEN_FLOAT; }
[0-9]+              { count_tokens(yytext); yylval.ival = atoi(yytext); return TOKEN_INT; }
'([^'\\]|\\.)*'     { 
                        count_tokens(yytext);
                        // Strip surrounding single quotes
                        int len = strlen(yytext);
                        char* clean = (char*)malloc(len - 1);
                        strncpy(clean, yytext + 1, len - 2);
                        clean[len - 2] = '\0';
                        yylval.str = clean;
                        return TOKEN_STRING; 
                    }

[a-zA-Z_][a-zA-Z0-9_]* { count_tokens(yytext); yylval.str = strdup(yytext); return TOKEN_IDENTIFIER; }

"--".*              { count_tokens(yytext); /* Single line comment */ }
[ \t\r]+            { count_tokens(yytext); /* Ignore whitespace */ }
\n                  { current_line++; current_col = 1; }

.                   { 
                        fprintf(stderr, "Lexical Error: Unexpected character '%s' at line %d, col %d\n", yytext, current_line, current_col);
                        count_tokens(yytext);
                    }

%%
