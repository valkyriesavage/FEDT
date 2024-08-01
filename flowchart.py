from dataclasses import dataclass


class Node:

    def toXML(self) -> str:
        ...


@dataclass
class Empty(Node):
    pass

    def toXML(self) -> str:
        return ""


@dataclass
class Seq(Node):
    prev: Node
    next: Node

    def toXML(self) -> str:
        return self.prev.toXML() + "\n" + self.next.toXML()


@dataclass
class Instr(Node):
    instr: str

    def toXML(self) -> str:
        return f"<instruction>{self.instr}</instruction>"

@dataclass
class Decis(Node):
    instr: str

    def toXML(self) -> str:
        return f"<decision>{self.instr}</decision>"


@dataclass
class Header(Node):
    header: str

    def toXML(self) -> str:
        return f"<header>{self.header}</header>"


@dataclass
class Par(Node):
    nodes: list[Node]

    def toXML(self) -> str:
        return f"<in-parallel>{''.join(map(lambda x: f'<par-item>{x.toXML()}</par-item>', self.nodes))}</in-parallel>"

@dataclass
class Yes(Node):
    nodes: list[Node]

    def toXML(self) -> str:
        return f"<if-yes>{''.join(map(lambda x: f'<yes-item>{x.toXML()}</yes-item>', self.nodes))}</if-yes>"

@dataclass
class No(Node):
    nodes: list[Node]

    def toXML(self) -> str:
        return f"<if-no>{''.join(map(lambda x: f'<no-item>{x.toXML()}</no-item>', self.nodes))}</if-no>"


class FlowChart:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FlowChart, cls).__new__(cls)
        return cls.instance

    node: Node = Empty()
    temp_node = Empty()
    temp_nodes: list[Node] = []
    in_loop: bool = False
    in_if: bool = False

    def reset(self):
        self.node = Empty()
        self.temp_node = Empty()
        self.temp_nodes = []
        self.in_loop = False
        self.in_if = False
        self.in_else = False

    def add_instruction(self, x: str, header=False):
        if self.in_loop:
            self.temp_node = Seq(self.temp_node,
                                 Instr(x) if not header else Header(x))
        else:
            self.node = Seq(self.node, Instr(x))

    def add_decision(self, x: str, header=False):
        if self.in_if or self.in_else:
            self.temp_node = Seq(self.temp_node,
                                 Decis(x) if not header else Header(x))
        else:
            self.node = Seq(self.node, Decis(x))

    def enter_loop(self):
        self.in_loop = True
    
    def enter_if(self):
        self.in_if = True

    def enter_else(self):
        self.in_else = True

    def end_body(self):
        self.temp_nodes.append(self.temp_node)
        self.temp_node = Empty()

    def exit_loop(self):
        self.node = Seq(self.node, Par(self.temp_nodes))
        self.temp_nodes = []
        self.in_loop = False

    def exit_if(self):
        self.node = Seq(self.node, Yes(self.temp_nodes))
        self.temp_nodes = []
        self.in_if = False
    
    def exit_else(self):
        self.node = Seq(self.node, No(self.temp_nodes))
        self.temp_nodes = []
        self.in_else = False
