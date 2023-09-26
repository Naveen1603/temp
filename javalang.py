import javalang
from javalang.tree import CompilationUnit, ClassDeclaration, MethodDeclaration, BlockStatement, Statement, SwitchStatement, SwitchCase

# Create a CompilationUnit
cu = CompilationUnit()

# Create a ClassDeclaration for the Factory class
factory_class = ClassDeclaration(
    modifiers={'public'},
    name='Factory',
    members=[],
)

# Create a MethodDeclaration for the createProduct method
create_method = MethodDeclaration(
    modifiers={'public', 'static'},
    return_type='Product',
    name='createProduct',
    parameters=[('String', 'methodName')],
    body=BlockStatement(statements=[
        Statement(
            SwitchStatement(
                selector='methodName',
                cases=[
                    SwitchCase(
                        value='\"ProductA\"',
                        statements=[
                            Statement('return new ConcreteProductA();')
                        ]
                    ),
                    SwitchCase(
                        value='\"ProductB\"',
                        statements=[
                            Statement('return new ConcreteProductB();')
                        ]
                    ),
                    # Add more cases as needed
                    SwitchCase(
                        value='default',
                        statements=[
                            Statement('return null;')
                        ]
                    )
                ]
            )
        )
    ])
)

# Add the createProduct method to the Factory class
factory_class.members.append(create_method)

# Add the Factory class to the CompilationUnit
cu.types.append(factory_class)

# Convert the AST to Java code
java_code = cu.encode()

# Write the Java code to a file
with open('Factory.java', 'w') as java_file:
    java_file.write(java_code)
