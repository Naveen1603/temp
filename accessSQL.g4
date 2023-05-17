grammar AccessSQL;

query: select_stmt;

select_stmt: SELECT select_clause from_clause where_clause?;

select_clause: SELECT (ALL | DISTINCT)? select_list;

select_list: (select_item (',' select_item)*)?;

select_item: (column_name | expression) (AS? column_alias)?;

column_name: (table_name '.')? column;

column_alias: ID;

from_clause: FROM table_reference_list;

table_reference_list: table_reference (',' table_reference)*;

table_reference: table_name (AS? table_alias)?;

table_name: ID;

table_alias: ID;

where_clause: WHERE expression;

expression: logical_expr;

logical_expr: comparison_expr (('AND' | 'OR') comparison_expr)*;

iif_func: 'IIF' '(' expression ',' expression ',' expression ')';

comparison_expr: operand operator operand;

operand: literal | column_name | '(' expression ')';

operator: '=' | '<>' | '<' | '>' | '<=' | '>=' | 'LIKE';

literal: (INT | FLOAT | STRING);

INT: [0-9]+;

FLOAT: [0-9]+ '.' [0-9]*;

STRING: '\'' ~('\'' | '\r' | '\n')* '\'';

ID: [a-zA-Z_][a-zA-Z_0-9]*;

WS: [ \t\r\n]+ -> skip;
