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
class Header(Node):
    header: str

    def toXML(self) -> str:
        return f"<header>{self.header}</header>"


@dataclass
class Par(Node):
    nodes: list[Node]

    def toXML(self) -> str:
        return f"<in-parallel>{''.join(map(lambda x: f'<par-item>{x.toXML()}</par-item>', self.nodes))}</in-parallel>"


class FlowChart:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FlowChart, cls).__new__(cls)
        return cls.instance

    node: Node = Empty()
    temp_node = Empty()
    temp_nodes: list[Node] = []
    in_loop: bool = False

    def reset(self):
        self.node = Empty()
        self.temp_node = Empty()
        self.temp_nodes = []
        self.in_loop = False

    def add_instruction(self, x: str, header=False):
        if self.in_loop:
            self.temp_node = Seq(self.temp_node,
                                 Instr(x) if not header else Header(x))
        else:
            self.node = Seq(self.node, Instr(x))

    def enter_loop(self):
        self.in_loop = True

    def end_body(self):
        self.temp_nodes.append(self.temp_node)
        self.temp_node = Empty()

    def exit_loop(self):
        self.node = Seq(self.node, Par(self.temp_nodes))
        self.temp_nodes = []
        self.in_loop = False
