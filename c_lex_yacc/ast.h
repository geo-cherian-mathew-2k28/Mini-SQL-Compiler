/*
 * Mini SQL Compiler — C AST Node Definitions (Reference Implementation)
 */

#ifndef AST_H
#define AST_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum {
    NODE_SELECT_QUERY,
    NODE_WILDCARD,
    NODE_IDENTIFIER,
    NODE_TABLE,
    NODE_LITERAL_INT,
    NODE_LITERAL_FLOAT,
    NODE_LITERAL_STRING,
    NODE_BINARY_EXPR,
    NODE_ORDER_ITEM
} NodeType;

typedef struct ASTNode {
    NodeType type;
    union {
        struct {
            struct ASTNode* projections;
            struct ASTNode* from_table;
            struct ASTNode* where_clause;
            struct ASTNode* order_by_clause;
        } select_query;

        struct {
            char* name;
        } identifier;

        struct {
            char* name;
        } table;

        struct {
            int int_val;
            double float_val;
            char* str_val;
        } literal;

        struct {
            char* op;
            struct ASTNode* left;
            struct ASTNode* right;
        } binary_expr;

        struct {
            char* column_name;
            char* direction; // "ASC" or "DESC"
        } order_item;

        struct {
            struct ASTNode** items;
            int count;
        } list;
    } data;
    struct ASTNode* next; // for linked lists
} ASTNode;

ASTNode* create_identifier(char* name);
ASTNode* create_table(char* name);
ASTNode* create_wildcard();
ASTNode* create_literal_int(int val);
ASTNode* create_literal_float(double val);
ASTNode* create_literal_string(char* val);
ASTNode* create_binary_expr(char* op, ASTNode* left, ASTNode* right);
ASTNode* create_order_item(char* col, char* dir);
ASTNode* create_select_query(ASTNode* projs, ASTNode* from, ASTNode* where, ASTNode* order);

void print_ast(ASTNode* node, int indent);
void free_ast(ASTNode* node);

#endif
