from sqlglot import Dialect
from sqlglot.parser import Parser
from sqlglot.visitors import BaseVisitor
from sqlglot.tokens import Name, Punctuation, Keyword, String, Operator, Number

class MSAccessDialect(Dialect):
    """Custom dialect for MS Access queries"""
    
    @property
    def tokens(self):
        return {
            Name: {
                'start': ('[',),
                'end': (']',),
            },
            Punctuation: {
                'value': ('[', ']', '.', '*', ',', ';', '(', ')', '=', '<', '>', '<=', '>=', '<>', '!=', '<=>', ':', '::'),
            },
            Keyword: {
                'value': ('SELECT', 'FROM', 'WHERE', 'GROUP', 'BY', 'HAVING', 'ORDER', 'ASC', 'DESC', 'NULLS', 'FIRST', 'LAST', 'INNER', 'OUTER', 'LEFT', 'RIGHT', 'JOIN', 'ON', 'AND', 'OR', 'NOT', 'LIKE', 'IN', 'BETWEEN', 'IS', 'NULL', 'DISTINCT', 'TOP', 'AS', 'COUNT', 'SUM', 'MAX', 'MIN', 'AVG', 'INTO', 'VALUES', 'INSERT', 'INT', 'DOUBLE', 'FLOAT', 'CHAR', 'VARCHAR', 'TEXT', 'DATE', 'TIME', 'DATETIME'),
            },
        }
        
    def parse(self, sql):
        """Parse the input SQL statement"""
        parser = Parser(sql, dialect=self)
        return parser.parse()

class MSAccessToPostgresVisitor(BaseVisitor):
    """Visitor to transform MS Access operators to PostgreSQL operators"""
    
    def visit_operator(self, node, visited_children):
        """Transform MS Access string concatenation to PostgreSQL string concatenation"""
        if node.value == '&':
            return 'concat'
        else:
            return super().visit_operator(node, visited_children)

# Example MS Access SQL statement with string concatenation
ms_access_sql = "SELECT [First Name] & ' ' & [Last Name] AS [Full Name] FROM [Customers]"

# Create an instance of the custom dialect and parse the MS Access SQL statement
ms_access_dialect = MSAccessDialect()
parser = Parser(ms_access_sql, dialect=ms_access_dialect)
ast = parser.parse()

# Use the visitor to transform string concatenation from MS Access to PostgreSQL
postgres_visitor = MSAccessToPostgresVisitor()
postgres_sql = postgres_visitor.visit(ast)

# Print the transformed PostgreSQL SQL statement
print(postgres_sql)
