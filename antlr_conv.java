import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.tree.*;
import org.antlr.v4.runtime.misc.*;

public class AccessSQLToPostgreSQLVisitor extends AccessSQLBaseVisitor<String> {
    @Override
    public String visitComparison_expr(AccessSQLParser.Comparison_exprContext ctx) {
        // Check if the expression is an IIF statement
        if (ctx.operand(0) instanceof AccessSQLParser.Iif_funcContext) {
            AccessSQLParser.Iif_funcContext iifCtx = (AccessSQLParser.Iif_funcContext) ctx.operand(0);
            String condition = visit(iifCtx.expression(0));
            String trueValue = visit(iifCtx.expression(1));
            String falseValue = visit(iifCtx.expression(2));
            return "(CASE WHEN " + condition + " THEN " + trueValue + " ELSE " + falseValue + " END)";
        }

        // Process other comparison expressions
        String operand1 = visit(ctx.operand(0));
        String operator = visit(ctx.operator());
        String operand2 = visit(ctx.operand(1));
        return operand1 + " " + operator + " " + operand2;
    }

    @Override
    public String visitIif_func(AccessSQLParser.Iif_funcContext ctx) {
        // Convert IIF function to CASE WHEN
        String condition = visit(ctx.expression(0));
        String trueValue = visit(ctx.expression(1));
        String falseValue = visit(ctx.expression(2));
        return "(CASE WHEN " + condition + " THEN " + trueValue + " ELSE " + falseValue + " END)";
    }

    // Override other visit methods as needed

    public static void main(String[] args) {
        // Create the lexer and parser
        CharStream input = CharStreams.fromString("SELECT IIF(column = 'value', 'true', 'false') FROM table");
        AccessSQLLexer lexer = new AccessSQLLexer(input);
        CommonTokenStream tokenStream = new CommonTokenStream(lexer);
        AccessSQLParser parser = new AccessSQLParser(tokenStream);

        // Parse the input and obtain the root of the AST
        ParseTree tree = parser.query();

        // Create an instance of your visitor class
        AccessSQLToPostgreSQLVisitor visitor = new AccessSQLToPostgreSQLVisitor();

        // Visit the root of the AST to start the conversion
        String postgresQuery = visitor.visit(tree);

        System.out.println(postgresQuery);
    }
}
