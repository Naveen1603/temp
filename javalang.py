from javalang import tree
from javalang.tree import MethodInvocation, MethodDeclaration, Statement, BlockStatement, IfStatement, SwitchStatement, \
    SwitchStatementCase, ClassDeclaration, ClassCreator, ClassDeclarationBody, ClassBodyDeclaration, \
    MethodDeclaration, \
    FormalParameter, TypeDeclaration, BasicType, Literal, ReturnStatement, StatementExpression, \
    MemberReference, \
    ReferenceType, ClassCreator, VariableDeclaration, VariableDeclarator, ExpressionStatement, \
    BasicTypeArgument, \
    TypeArgument, ClassReference, TypeArgument
from javalang.tree import TypeArguments, Type

# Generate the method implementation for each case
def generate_case_methods(case_values):
    methods = []
    for value in case_values:
        method = MethodDeclaration(
            modifiers=set(['public', 'static']),
            name=value,
            parameters=[FormalParameter(type_=tree.Type(name='String'), name='methodName')],
            return_type=tree.Type(name='void'),
            body=BlockStatement(
                statements=[
                    StatementExpression(
                        MethodInvocation(
                            member=MemberReference(
                                prefix=tree.This(),
                                member=value
                            ),
                            arguments=[
                                tree.This(),
                                Literal(value=value, type_='String')
                            ]
                        )
                    )
                ]
            )
        )
        methods.append(method)
    return methods

# Generate the factory class
def generate_factory_class(class_name, case_values):
    methods = generate_case_methods(case_values)
    factory_class = ClassDeclaration(
        modifiers=set(['public', 'class']),
        name=class_name,
        extends=tree.Node(),
        implements=None,
        body=ClassDeclarationBody(
            declarations=[
                ClassBodyDeclaration(
                    declaration=MethodDeclaration(
                        modifiers=set(['public', 'static']),
                        name='createInstance',
                        parameters=[FormalParameter(type_=tree.Type(name='String'), name='methodName')],
                        return_type=tree.Type(name='void'),
                        body=BlockStatement(
                            statements=[
                                SwitchStatement(
                                    selector=tree.VariableDeclarator(
                                        type_=tree.Type(name='String'),
                                        name='methodName'
                                    ),
                                    cases=[
                                        SwitchStatementCase(
                                            labels=[Literal(value=value, type_='String')],
                                            statements=[
                                                StatementExpression(
                                                    MethodInvocation(
                                                        member=MemberReference(
                                                            prefix=tree.This(),
                                                            member=value
                                                        ),
                                                        arguments=[
                                                            tree.This(),
                                                            Literal(value=value, type_='String')
                                                        ]
                                                    )
                                                )
                                            ]
                                        )
                                        for value in case_values
                                    ]
                                )
                            ]
                        )
                    )
                )
            ] + methods
        )
    )

    return factory_class

# Generate the Java source code
def generate_java_code(factory_class):
    type_declaration = TypeDeclaration(
        type_declaration=ClassDeclaration(
            modifiers=set(['public']),
            name='MyFactory',
            extends=tree.Node(),
            implements=None,
            body=ClassDeclarationBody(
                declarations=[
                    ClassBodyDeclaration(
                        declaration=factory_class
                    )
                ]
            )
        )
    )
    compilation_unit = tree.CompilationUnit(
        type_declarations=[type_declaration]
    )
    return compilation_unit

# Example usage
case_values = ['method1', 'method2', 'method3']
factory_class = generate_factory_class('MyFactory', case_values)
java_code = generate_java_code(factory_class)
print(java_code)
