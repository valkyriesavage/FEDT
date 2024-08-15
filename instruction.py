from control import MODE, Evaluate, Execute
from flowchart import FlowChart


def instruction(s: str, header=False, **kwargs):
    if isinstance(MODE, Evaluate):
        FlowChart().add_instruction(s, header, **kwargs)
    elif isinstance(MODE, Execute):
        input(f"{s} Press enter when done.")


def note(s: str, header=False, **kwargs):
    if isinstance(MODE, Evaluate):
        FlowChart().add_instruction(s, header, **kwargs)
    elif isinstance(MODE, Execute):
        print(s)  # TODO: Checkbox or something