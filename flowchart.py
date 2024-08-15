from dataclasses import dataclass, field
from typing import Literal, Union

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
            self.other = kwargs[LATEX_DETAILS]

    def toXML(self) -> str:
        return f"<instruction>{self.instr}</instruction>"
    
    def toLatex(self) -> str:
        if hasattr(self,'other'):
            return f"{self.other[SUBJECT].describe()} did {self.other[VERB]} with settings {self.other[SETTINGS]}"
        return ''

@dataclass
class Note(Node):
    instr: str

    def __init__(self, instr, other=None, **kwargs):
        self.instr = instr

    def toXML(self) -> str:
        return f"<note>{self.instr}</note>"
    
    def toLatex(self) -> str:
        if hasattr(self,'other'):
            return f"{self.other[SUBJECT].describe()} did {self.other[VERB]} with settings {self.other[SETTINGS]}"
        return ''


@dataclass
class Header(Node):
    header: str

    def toXML(self) -> str:
        return f"<header>{self.header}</header>"
    
    def toLatex(self) -> str:
        return ''


@dataclass
class Par(Node):
    nodes: list[Node]

    def toXML(self) -> str:
        return f"<in-parallel>{''.join(map(lambda x: f'<par-item>{x.toXML()}</par-item>', self.nodes))}</in-parallel>"
  
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
        return f"<loop condition=\"{self.cond}\">{''.join(map(lambda x: f'<loop-item>{x.toXML()}</loop-item>', self.nodes))}</loop>" 
    
    def toLatex(self) -> str:
        return f"Until the condition was met, we tested {' '.join([x.toLatex() for x in self.nodes])}"


class FlowChart:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FlowChart, cls).__new__(cls)
        return cls.instance

    node: Node = Empty()
    temp_node = Empty()
    temp_nodes: list[Node] = []
    in_loop: Union[Literal["parallel"], Literal["series"], str,
                   None] = None

    def reset(self):
        self.node = Empty()
        self.temp_node = Empty()
        self.temp_nodes = []
        self.in_loop = None

    def add_instruction(self, x: str, header=False, **kwargs):
        if self.in_loop:
            self.temp_node = Seq(self.temp_node,
                                 Instr(x, **kwargs) if not header else Header(x))
        else:
            self.node = Seq(self.node, Instr(x, **kwargs))

    def add_note(self, x: str, **kwargs):
        if self.in_loop:
            self.temp_node = Seq(self.temp_node,
                                 Note(x, **kwargs))
        else:
            self.node = Seq(self.node, Note(x, **kwargs))

    def enter_loop(self, kind: Union[Literal["series"], Literal["parallel"], str]):
        self.in_loop = kind

    def end_body(self):
        self.temp_nodes.append(self.temp_node)
        self.temp_node = Empty()

    def exit_loop(self):
        match self.in_loop:
            case "series":
                loop = Series(self.temp_nodes)
            case "parallel":
                loop = Par(self.temp_nodes)
            case cond:
                if isinstance(cond, str):
                    loop = Infinite(cond, self.temp_nodes)
        self.node = Seq(self.node, loop)
        self.temp_nodes = []
        self.in_loop = None
    
    def to_latex(self):
        return self.node.toLatex()