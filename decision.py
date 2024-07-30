from control import MODE, Evaluate, Execute
from flowchart import FlowChart


def decision(s: str, header=False):
    if isinstance(MODE, Evaluate):
        FlowChart().add_decision(s, header)
    elif isinstance(MODE, Execute):
        print(s)  # TODO: Radio button or something