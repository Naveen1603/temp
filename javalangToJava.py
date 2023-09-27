from javalang.tree import *

# Assuming you have the root node of the AST named "root"

def dump_ast_to_file(node, indent_level, writer):
    indent = "    " * indent_level
    writer.write(f"{indent}{node._node_type}\n")

    if isinstance(node, Node):
        for child_name, child_value in node.children:
            writer.write(f"{indent}  {child_name}: ")
            if isinstance(child_value, list):
                writer.write("[\n")
                for child in child_value:
                    dump_ast_to_file(child, indent_level + 2, writer)
                writer.write(f"{indent}  ]\n")
            else:
                dump_ast_to_file(child_value, indent_level + 1, writer)

# Write the AST to a Java code file
with open("MyClass.java", "w") as file:
    dump_ast_to_file(root, 0, file)
