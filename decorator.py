import ast
import ast
import copy
from functools import wraps
import inspect
import types

from flowchart import FlowChart

UNIQUE_ID = 0


def fresh_name():
    global UNIQUE_ID
    UNIQUE_ID += 1
    return f"__FEDT_identifier_{UNIQUE_ID}"


class UseVariables(ast.NodeTransformer):

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            node.ctx = ast.Load()
        return self.generic_visit(node)

    def visit_Tuple(self, node):
        if isinstance(node.ctx, ast.Store):
            node.ctx = ast.Load()
        return self.generic_visit(node)


class WrapFor(ast.NodeTransformer):

    def visit_For(self, node):

        def flowchart_call(fname):
            return ast.Expr(
                ast.Call(
                    ast.Attribute(
                        ast.Call(ast.Name("FlowChart", ast.Load()), [], []),
                        fname, ast.Load()), [], []))

        def enter_loop_call(iter):
            arg = ast.Call(ast.Attribute(iter, "kind", ast.Load()), [], [])
            return ast.Expr(
                ast.Call(
                    ast.Attribute(
                        ast.Call(ast.Name("FlowChart", ast.Load()), [], []),
                        "enter_loop", ast.Load()), [arg], []))

        def instruction_call(item):
            return ast.Expr(
                ast.Call(ast.Name("instruction", ast.Load()), [
                    ast.BinOp(
                        ast.Constant(f"Loop for "), ast.Add(),
                        ast.Call(ast.Name("str", ast.Load()), [item], [])),
                    ast.Constant(True)
                ], []))

        for n in node.body:
            self.generic_visit(n)

        target_use = copy.deepcopy(node.target)
        UseVariables().visit(target_use)
        iter_name = fresh_name()

        return [
            ast.ImportFrom("flowchart", [ast.alias("FlowChart")], 0),
            ast.Assign([ast.Name(iter_name, ast.Store())], node.iter),
            enter_loop_call(ast.Name(iter_name, ast.Load())),
            ast.For(node.target, ast.Name(iter_name, ast.Load()),
                    [instruction_call(target_use)] + node.body +
                    [flowchart_call("end_body")], node.orelse,
                    node.type_comment),
            flowchart_call("exit_loop")
        ]


# TODO : Harry, help!
class WrapIf(ast.NodeTransformer):

    def visit_If(self, node):

        def flowchart_call(fname):
            return ast.Expr(
                ast.Call(
                    ast.Attribute(
                        ast.Call(ast.Name("FlowChart", ast.Load()), [], []),
                        fname, ast.Load()), [], []))

        def instruction_call():
            return ast.Expr(
                ast.Call(ast.Name("instruction", ast.Load()),
                         [ast.Constant("If for TODO"),
                          ast.Constant(True)], []))

        for n in node.body:
            self.generic_visit(n)

        return [
            ast.ImportFrom("flowchart", [ast.alias("FlowChart")], 0),
            flowchart_call("enter_if"),
            ast.For(node.target, node.iter, [instruction_call()] + node.body +
                    [flowchart_call("end_body")], node.orelse,
                    node.type_comment),
            flowchart_call("exit_if")
        ]


# TODO : Harry, help!
class WrapElse(ast.NodeTransformer):

    def visit_Else(self, node):

        def flowchart_call(fname):
            return ast.Expr(
                ast.Call(
                    ast.Attribute(
                        ast.Call(ast.Name("FlowChart", ast.Load()), [], []),
                        fname, ast.Load()), [], []))

        def instruction_call():
            return ast.Expr(
                ast.Call(ast.Name("instruction", ast.Load()),
                         [ast.Constant("Else for TODO"),
                          ast.Constant(True)], []))

        for n in node.body:
            self.generic_visit(n)

        return [
            ast.ImportFrom("flowchart", [ast.alias("FlowChart")], 0),
            flowchart_call("enter_else"),
            ast.For(node.target, node.iter, [instruction_call()] + node.body +
                    [flowchart_call("end_body")], node.orelse,
                    node.type_comment),
            flowchart_call("exit_else")
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
        explicit_dict = {}
        for explicit_arg in set(list(kw.keys())):
            explicit_dict[explicit_arg] = kw.get(explicit_arg)
        kw['explicit_args'] = explicit_dict
        return f(*a, **kw)

    return wrapper
