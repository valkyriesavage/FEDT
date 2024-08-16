from dataclasses import dataclass
from flowchart import FlowChart


class Mode:
    pass


@dataclass
class Execute(Mode):
    pass


@dataclass
class Evaluate(Mode):
    pass


global MODE
MODE = Evaluate()
