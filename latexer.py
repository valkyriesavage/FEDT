import ast
import copy
from functools import wraps
import inspect
import types

class AddModeBranch(ast.NodeTransformer):

    def __init__(self, instruction=None):
        self.instruction = instruction

    def visit_FunctionDef(self, node):

        def flowchart_call(fname, args):
            return ast.Expr(
                ast.Call(
                    ast.Attribute(
                        ast.Call(ast.Name("FlowChart", ast.Load()), [], []),
                        fname, ast.Load()), args, []))

        node.body = [
            ast.ImportFrom(
                "control",
                [ast.alias("MODE"), ast.alias("Execute")], 0),
            ast.Global(["MODE"]),
            ast.If(
                ast.Call(ast.Name("isinstance", ast.Load()), [
                    ast.Name("MODE", ast.Load()),
                    ast.Name("Execute", ast.Load())
                ], []), node.body, [
                    flowchart_call("add_instruction",
                                   [ast.Constant(self.instruction)])
                ] if self.instruction else [])
        ]
        return node

def fedt_latex(f):
    source = inspect.getsource(f)
    tree = ast.parse(source)
    new_ast = ast.fix_missing_locations(AddModeBranch("blelel?").visit(tree))
    print(ast.unparse(new_ast))
    new_code = compile(new_ast, f.__code__.co_filename, "exec")
    new_f = types.FunctionType(new_code.co_consts[2], f.__globals__)

    return new_f