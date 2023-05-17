from antlr4 import *
from AccessSQLLexer import AccessSQLLexer
from AccessSQLParser import AccessSQLParser
from antlr_ast import ASTVisitor

class AccessSQLToPostgreSQLVisitor(ASTVisitor):
    def visitComparison_expr(self, ctx):
        # Check if the expression is an IIF statement
        if isinstance(ctx.operand(0), AccessSQLParser.Iif_funcContext):
            iif_ctx = ctx.operand(0)
            condition = self.visit(iif_ctx.expression(0))
            true_value = self.visit(iif_ctx.expression(1))
            false_value = self.visit(iif_ctx.expression(2))
            return f"(CASE WHEN {condition} THEN {true_value} ELSE {false_value} END)"

        # Process other comparison expressions
        operand1 = self.visit(ctx.operand(0))
        operator = self.visit(ctx.operator())
        operand2 = self.visit(ctx.operand(1))
        return f"{operand1} {operator} {operand2}"

    def visitIif_func(self, ctx):
        # Convert IIF function to CASE WHEN
        condition = self.visit(ctx.expression(0))
        true_value = self.visit(ctx.expression(1))
        false_value = self.visit(ctx.expression(2))
        return f"(CASE WHEN {condition} THEN {true_value} ELSE {false_value} END)"

    # Override other visit methods as needed

# Create an instance of your visitor class
visitor = AccessSQLToPostgreSQLVisitor()

# Create an input stream from your Access SQL query
input_stream = InputStream("SELECT IIF(column = 'value', 'true', 'false') FROM table")

# Create a lexer and parser
lexer = AccessSQLLexer(input_stream)
token_stream = CommonTokenStream(lexer)
parser = AccessSQLParser(token_stream)

# Parse the input and obtain the root of the AST
ast = parser.query()

# Visit the root of the AST to start the conversion
postgres_query = visitor.visit(ast)

print(postgres_query)
