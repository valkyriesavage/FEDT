from flowchart import FlowChart


class Mode:
    pass


class Execute(Mode):
    pass


class Evaluate(Mode):
    pass


global MODE
MODE = Evaluate()
