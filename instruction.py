from control import MODE, Evaluate, Execute
from flowchart import FlowChart


def instruction(s: str, header=False):
    if isinstance(MODE, Evaluate):
        FlowChart().add_instruction(s, header)
    elif isinstance(MODE, Execute):
        print(s)  # TODO: Checkbox or something


# class FEDTLoopEnder:

# class FEDTLoop:

#     def __enter__(self):
#         FEDTLoopBody

#     def __exit__(self, *args):
#         pass
