grammar AccessSQL;

parse: statement+;

statement: selectStatement | insertStatement | updateStatement | deleteStatement | createTableStatement;

selectStatement: SELECT columnList FROM tableSource (JOIN joinClause)* (WHERE expression)? (ORDER BY ordering)?;

insertStatement: INSERT INTO tableName (columnList)? VALUES valueList;

updateStatement: UPDATE tableName SET assignmentList (WHERE expression)?;

deleteStatement: DELETE FROM tableName (WHERE expression)?;

createTableStatement: CREATE TABLE tableName '(' columnDefinitionList ')';

columnDefinitionList: columnDefinition (',' columnDefinition)*;

columnDefinition: columnName dataType (PRIMARY KEY)?;

dataType: INT | LONG | FLOAT | DOUBLE | DECIMAL | VARCHAR | TEXT | DATETIME;

ordering: column (ASC | DESC)?;

valueList: value (',' value)*;

value: STRING | NUMBER | BOOL | NULL;

assignmentList: assignment (',' assignment)*;

assignment: column '=' expression;

tableSource: tableName (',' tableName)*;

joinClause: JOIN tableName ON expression;

columnList: column (',' column)*;

column: (tableName '.')? columnName;

expression: '(' expression ')'
    | expression (AND | OR) expression
    | expression (EQ | NEQ | LT | LTE | GT | GTE) expression
    | NOT expression
    | functionCall
    | column
    | value;

functionCall: functionName '(' argumentList? ')';

argumentList: expression (',' expression)*;

functionName: AVG | COUNT | MAX | MIN | SUM | UCASE | LCASE | MID | LEN | ROUND | NOW | FORMAT | IIF;

tableName: ID;

columnName: ID;

fragment A: [Aa];
fragment B: [Bb];
fragment C: [Cc];
fragment D: [Dd];
fragment E: [Ee];
fragment F: [Ff];
fragment G: [Gg];
fragment H: [Hh];
fragment I: [Ii];
fragment J: [Jj];
fragment K: [Kk];
fragment L: [Ll];
fragment M: [Mm];
fragment N: [Nn];
fragment O: [Oo];
fragment P: [Pp];
fragment Q: [Qq];
fragment R: [Rr];
fragment S: [Ss];
fragment T: [Tt];
fragment U: [Uu];
fragment V: [Vv];
fragment W: [Ww];
fragment X: [Xx];
fragment Y: [Yy];
fragment Z: [Zz];

AVG: A V G;
COUNT: C O U N T;
MAX: M A X;
MIN: M I N;
SUM: S U M;
UCASE: U C A S E;
LCASE: L C A S E;
MID: M I D;
LEN: L E N;
ROUND: R O U N D;
NOW: N O W;
FORMAT: F O R M A T;
IIF: I I F;

SELECT: S E L E C T;
FROM: F R O M;
WHERE: W H E R E;
ORDER: O R D E R;
BY: B Y;
ASC: A S C;
DESC: D E S C;
INSERT: I N S E R T;
INTO: I N T O;
VALUES: V A L U E S;
UPDATE: U P D A T E;
SET: S E T;
DELETE: D E L E T E;
CREATE: C R E A T E;
TABLE: T A B L E;
PRIMARY: P R I M A R Y;
KEY: K E Y;
INT: I N T;
LONG: L O N G;
FLOAT: F L O A T;
DOUBLE: D O U B L E;
DECIMAL: D E C I M A L;
VARCHAR: V A R C H A R;
TEXT: T E X T;
DATETIME: D A T E T I M E;
AND: A N D;
OR: O R;
EQ: '=';
NEQ: '<>';
LT: '<';
LTE: '<=';
GT: '>';
GTE: '>=';
NOT: N O T;
NULL: N U L L;

STRING: '\'' (~['\''])* '\'';
NUMBER: ('+' | '-')? [0-9]+ ('.' [0-9]+)?;
BOOL: 'TRUE' | 'FALSE';

ID: [a-zA-Z_] [a-zA-Z0-9_]*;

WS: [ \t\r\n]+ -> skip;
