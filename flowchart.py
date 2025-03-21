from dataclasses import dataclass, field
from difflib import SequenceMatcher
import inspect
from typing import Literal, Union
from xml.sax.saxutils import escape

LATEX_DETAILS = 'latex_details'
SUBJECT = 'subject'
VERB = 'verb'
OBJECT = 'object'
SETTINGS = 'settings'
FABBED_SOMETHING = 'fabricated'

class Node:
    def toXML(self) -> str:
        ...

    def toLatex(self) -> str:
        ...

    def FindFabbedCount(self) -> int:
        ...


@dataclass
class Empty(Node):
    pass

    def toXML(self) -> str:
        return ""

    def toLatex(self) -> str:
        return ''


@dataclass
class Seq(Node):
    prev: Node
    next: Node

    def toXML(self) -> str:
        return self.prev.toXML() + "\n" + self.next.toXML()

    def toLatex(self) -> str:
        return self.prev.toLatex() + "\n" + self.next.toLatex()


@dataclass
class Instr(Node):
    instr: str

    def __init__(self, instr, **kwargs):
        self.instr = instr
        if LATEX_DETAILS in kwargs:
            self.latexable = kwargs[LATEX_DETAILS]
            if SUBJECT in self.latexable and inspect.isclass(self.latexable[SUBJECT]):
                self.latexable[SUBJECT] = self.latexable[SUBJECT].describe()

    def toXML(self) -> str:
        return f"<instruction>{escape(self.instr)}</instruction>"

    def toLatex(self) -> str:
        if hasattr(self,"latexable"):
            return f"{self.latexable[SUBJECT]} did {self.latexable[VERB]} to {self.latexable[OBJECT]} with additional settings {self.latexable[SETTINGS]}"
        return ''

@dataclass
class Note(Node):
    instr: str

    def __init__(self, instr, **kwargs):
        self.instr = instr
        if LATEX_DETAILS in kwargs:
            self.latexable = kwargs[LATEX_DETAILS]
            if SUBJECT in self.latexable and inspect.isclass(self.latexable[SUBJECT]):
                self.latexable[SUBJECT] = self.latexable[SUBJECT].describe()

    def toXML(self) -> str:
        return f"<note>{escape(self.instr)}</note>"

    def toLatex(self) -> str:
        if hasattr(self,"latexable"):
            return f"{self.latexable[SUBJECT]} did {self.latexable[VERB]} with settings {self.latexable[SETTINGS]}"
        return ''


@dataclass
class Header(Node):
    header: str

    def toXML(self) -> str:
        return f"<header>{escape(self.header)}</header>"

    def toLatex(self) -> str:
        return ''

    def FindFabbedCount(self) -> int:
        return 0

@dataclass
class Par(Node):
    nodes: list[Node]

    def toXML(self) -> str:
        return f"<in-parallel>{''.join(map(lambda x: f'<par-item>{x.toXML()}</par-item>', self.nodes))}</in-parallel>"

    def find_differences_in_children(self) -> str:
        base_case = self.nodes[0]
        # ok, do something painful like evaluate all the values :sob:
        if not hasattr(base_case, "other"):
            # hmmm... we are a bit in trouble.
            pass

    def toLatex(self) -> str:
        return f"In no particular order, we tested {' '.join([x.toLatex() for x in self.nodes])}"


@dataclass
class Series(Node):
    nodes: list[Node]

    def toXML(self) -> str:
        return f"<in-series>{''.join(map(lambda x: f'<series-item>{x.toXML()}</series-item>', self.nodes))}</in-series>"

    def toLatex(self) -> str:
        return f"In sequence, we tested {' '.join([x.toLatex() for x in self.nodes])}"

@dataclass
class Infinite(Node):
    cond: str
    nodes: list[Node]

    def toXML(self) -> str:
        return f"<loop condition=\"{escape(self.cond)}\">{''.join(map(lambda x: f'<loop-item>{x.toXML()}</loop-item>', self.nodes))}</loop>"

    def toLatex(self) -> str:
        return f"Until the condition was met, we tested {' '.join([x.toLatex() for x in self.nodes])}"


class FlowChart:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FlowChart, cls).__new__(cls)
        return cls.instance

    node: Node = Empty()
    in_loop: list[Node] = []

    fabbed_objects: int = 0

    def reset(self):
        self.node = Empty()
        self.in_loop = []
        self.fabbed_objects = 0

    def _append_node(self, node):
        if len(self.in_loop) > 0:
            self.in_loop[-1].nodes[-1] = Seq(self.in_loop[-1].nodes[-1], # type: ignore
                                 node)
            # (Safe because in_loop always has loops)
        else:
            self.node = Seq(self.node, node)


    def add_instruction(self, x: str, header=False, fabbing=False, **kwargs):
        self._append_node(Instr(x, **kwargs) if not header else Header(x))
        if fabbing:
            self.fabbed_objects += 1

    def add_note(self, x: str, fabbing=False, **kwargs):
        self._append_node(Note(x, **kwargs))
        if fabbing:
            self.fabbed_objects += 1

    def enter_loop(self, kind: Union[Literal["series"], Literal["parallel"], str]):
        match kind:
            case "series":
                loop = Series([Empty()])
            case "parallel":
                loop = Par([Empty()])
            case cond:
                if isinstance(cond, str):
                    loop = Infinite(cond, [Empty()])

        self.in_loop.append(loop)

    def end_body(self):
        self.in_loop[-1].nodes.append(Empty()) # type: ignore
        # (Safe because in_loop always has loops, and in_loop must have at least one element since
        # we're in a body)

    def exit_loop(self):
        loop = self.in_loop[-1]
        self.in_loop = self.in_loop[:-1]
        self._append_node(loop)

    def to_latex(self):
        print(f"We fabricated {self.fabbed_objects} objects in total.")
        return self.node.toLatex()