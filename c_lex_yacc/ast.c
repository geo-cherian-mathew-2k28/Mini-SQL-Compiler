#include "ast.h"

ASTNode* create_node(NodeType type) {
    ASTNode* node = (ASTNode*)malloc(sizeof(ASTNode));
    node->type = type;
    node->next = NULL;
    return node;
}

ASTNode* create_identifier(char* name) {
    ASTNode* node = create_node(NODE_IDENTIFIER);
    node->data.identifier.name = strdup(name);
    return node;
}

ASTNode* create_table(char* name) {
    ASTNode* node = create_node(NODE_TABLE);
    node->data.table.name = strdup(name);
    return node;
}

ASTNode* create_wildcard() {
    return create_node(NODE_WILDCARD);
}

ASTNode* create_literal_int(int val) {
    ASTNode* node = create_node(NODE_LITERAL_INT);
    node->data.literal.int_val = val;
    return node;
}

ASTNode* create_literal_float(double val) {
    ASTNode* node = create_node(NODE_LITERAL_FLOAT);
    node->data.literal.float_val = val;
    return node;
}

ASTNode* create_literal_string(char* val) {
    ASTNode* node = create_node(NODE_LITERAL_STRING);
    node->data.literal.str_val = strdup(val);
    return node;
}

ASTNode* create_binary_expr(char* op, ASTNode* left, ASTNode* right) {
    ASTNode* node = create_node(NODE_BINARY_EXPR);
    node->data.binary_expr.op = strdup(op);
    node->data.binary_expr.left = left;
    node->data.binary_expr.right = right;
    return node;
}

ASTNode* create_order_item(char* col, char* dir) {
    ASTNode* node = create_node(NODE_ORDER_ITEM);
    node->data.order_item.column_name = strdup(col);
    node->data.order_item.direction = strdup(dir);
    return node;
}

ASTNode* create_select_query(ASTNode* projs, ASTNode* from, ASTNode* where, ASTNode* order) {
    ASTNode* node = create_node(NODE_SELECT_QUERY);
    node->data.select_query.projections = projs;
    node->data.select_query.from_table = from;
    node->data.select_query.where_clause = where;
    node->data.select_query.order_by_clause = order;
    return node;
}

void print_indent(int indent) {
    for (int i = 0; i < indent; i++) printf("  ");
}

void print_ast(ASTNode* node, int indent) {
    if (!node) return;
    print_indent(indent);

    switch (node->type) {
        case NODE_SELECT_QUERY:
            printf("SelectQuery\n");
            print_indent(indent + 1); printf("├── Projections:\n");
            print_ast(node->data.select_query.projections, indent + 2);

            print_indent(indent + 1); printf("├── From:\n");
            print_ast(node->data.select_query.from_table, indent + 2);

            print_indent(indent + 1); printf("├── Where:\n");
            if (node->data.select_query.where_clause)
                print_ast(node->data.select_query.where_clause, indent + 2);
            else {
                print_indent(indent + 2); printf("None\n");
            }

            print_indent(indent + 1); printf("└── OrderBy:\n");
            if (node->data.select_query.order_by_clause)
                print_ast(node->data.select_query.order_by_clause, indent + 2);
            else {
                print_indent(indent + 2); printf("None\n");
            }
            break;

        case NODE_WILDCARD:
            printf("Wildcard(*)\n");
            break;

        case NODE_IDENTIFIER:
            printf("Identifier(%s)\n", node->data.identifier.name);
            break;

        case NODE_TABLE:
            printf("Table(%s)\n", node->data.table.name);
            break;

        case NODE_LITERAL_INT:
            printf("Literal(INT: %d)\n", node->data.literal.int_val);
            break;

        case NODE_LITERAL_FLOAT:
            printf("Literal(FLOAT: %f)\n", node->data.literal.float_val);
            break;

        case NODE_LITERAL_STRING:
            printf("Literal(STRING: '%s')\n", node->data.literal.str_val);
            break;

        case NODE_BINARY_EXPR:
            printf("BinaryExpr(%s)\n", node->data.binary_expr.op);
            print_ast(node->data.binary_expr.left, indent + 1);
            print_ast(node->data.binary_expr.right, indent + 1);
            break;

        case NODE_ORDER_ITEM:
            printf("OrderByItem(col=%s, dir=%s)\n", node->data.order_item.column_name, node->data.order_item.direction);
            break;
    }

    if (node->next) {
        print_ast(node->next, indent);
    }
}

void free_ast(ASTNode* node) {
    if (!node) return;
    if (node->next) free_ast(node->next);

    switch (node->type) {
        case NODE_IDENTIFIER:
            free(node->data.identifier.name);
            break;
        case NODE_TABLE:
            free(node->data.table.name);
            break;
        case NODE_LITERAL_STRING:
            free(node->data.literal.str_val);
            break;
        case NODE_BINARY_EXPR:
            free(node->data.binary_expr.op);
            free_ast(node->data.binary_expr.left);
            free_ast(node->data.binary_expr.right);
            break;
        case NODE_ORDER_ITEM:
            free(node->data.order_item.column_name);
            free(node->data.order_item.direction);
            break;
        case NODE_SELECT_QUERY:
            free_ast(node->data.select_query.projections);
            free_ast(node->data.select_query.from_table);
            if (node->data.select_query.where_clause) free_ast(node->data.select_query.where_clause);
            if (node->data.select_query.order_by_clause) free_ast(node->data.select_query.order_by_clause);
            break;
        default:
            break;
    }
    free(node);
}
