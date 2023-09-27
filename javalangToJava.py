javafrom javalang.tree import *

# Assuming you have the root node of the AST named "root"

def dump_ast_to_file(node, writer):
    if isinstance(node, CompilationUnit):
        for child in node.types:
            dump_ast_to_file(child, writer)
    elif isinstance(node, TypeDeclaration):
        writer.write(node._position.source)
    elif isinstance(node, MethodDeclaration):
        writer.write(node._position.source)

# Write the AST to a Java code file
with open("MyClass.java", "w") as file:
    dump_ast_to_file(root, file)
