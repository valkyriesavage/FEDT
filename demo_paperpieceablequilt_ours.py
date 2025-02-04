from math import floor
import random

from numpy import arange

from flowchart import FlowChart
from instruction import instruction
from iterators import Series, Parallel, include_last, shuffle
from measurement import BatchMeasurements, ImmediateMeasurements
from design import VolumeFile
from decorator import fedt_experiment
from flowchart_render import render_flowchart
from lib import *

def summarize(data):
    return "Oh wow, great data!"

class CustomProgram:
    def section_and_optimize(sketch: VirtualWorldObject):
        instruction("section and optimize {}".format(sketch))
        sketch.updateVersion("Section", sketch)
        return sketch

@fedt_experiment
def measure_runtime():
    partial_sketches = []
    edgeCounts = BatchMeasurements.empty()
    for i in Parallel(range(15)): # how many different things were tried? I see 15 different designs in the paper
        sketch = LineFile("sample{}.sketch".format(i))
        partial_sketches.append(sketch)
        edgeCounts += Human.judge_something(sketch, "how many edges?")

    starts = ImmediateMeasurements.empty()
    finishes = ImmediateMeasurements.empty()
    for sketch in Parallel(partial_sketches):
        starts += Timestamper.get_ts(sketch)
        CustomProgram.section_and_optimize(sketch)
        finishes += Timestamper.get_ts(sketch)

    summarize(edgeCounts.get_all_data())
    summarize(starts.get_all_data())
    summarize(finishes.get_all_data())

if __name__ == "__main__":
    render_flowchart(measure_runtime)