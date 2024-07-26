import ast
import ast
from functools import wraps
import inspect
import types


from flowchart import FlowChart


class WrapFor(ast.NodeTransformer):

    def visit_For(self, node):

        def flowchart_call(fname):
            return ast.Expr(
                ast.Call(
                    ast.Attribute(
                        ast.Call(ast.Name("FlowChart", ast.Load()), [], []),
                        fname, ast.Load()), [], []))

        def instruction_call():
            return ast.Expr(
                ast.Call(ast.Name("instruction", ast.Load()),
                         [ast.Constant("Loop for TODO"),
                          ast.Constant(True)], []))

        for n in node.body:
            self.generic_visit(n)

        return [
            ast.ImportFrom("flowchart", [ast.alias("FlowChart")], 0),
            flowchart_call("enter_loop"),
            ast.For(node.target, node.iter, [instruction_call()] + node.body +
                    [flowchart_call("end_body")], node.orelse,
                    node.type_comment),
            flowchart_call("exit_loop")
        ]


def fedt_experiment(f):
    source = inspect.getsource(f)
    tree = ast.parse(source)
    new_ast = ast.fix_missing_locations(WrapFor().visit(tree))
    new_code = compile(new_ast, f.__code__.co_filename, "exec")
    new_f = types.FunctionType(new_code.co_consts[0], f.__globals__)

    def new_new_f(*args, **kwargs):
        new_f(*args, **kwargs)
        instructions = FlowChart().node
        FlowChart().reset()
        return instructions.toXML()

    return new_new_f


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


def fedt_fabricate(instruction):

    def inner(f):
        source = inspect.getsource(f)
        tree = ast.parse(source)
        new_ast = ast.fix_missing_locations(
            AddModeBranch(instruction).visit(tree))
        print(ast.unparse(new_ast))
        new_code = compile(new_ast, f.__code__.co_filename, "exec")
        new_f = types.FunctionType(new_code.co_consts[2], f.__globals__)

        return new_f

    return inner


def fedt_measure():

    def inner(f):
        source = inspect.getsource(f)
        tree = ast.parse(source)
        new_ast = ast.fix_missing_locations(AddModeBranch().visit(tree))
        print(ast.unparse(new_ast))
        new_code = compile(new_ast, f.__code__.co_filename, "exec")
        new_f = types.FunctionType(new_code.co_consts[2], f.__globals__)

        return new_f

    return inner

# from https://stackoverflow.com/questions/14749328/how-to-check-whether-optional-function-parameter-is-set/58166804#58166804
def explicit_checker(f):
    varnames = inspect.getfullargspec(f)[0]
    @wraps(f)
    def wrapper(*a, **kw):
        kw['explicit_params'] = set(list(varnames[:len(a)]) + list(kw.keys()))
        return f(*a, **kw)
    return wrapper