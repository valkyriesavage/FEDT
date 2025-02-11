from math import floor
import random

from numpy import arange

from flowchart import FlowChart
from instruction import instruction
from iterators import Series, Parallel, include_last, shuffle
from measurement import BatchMeasurements, ImmediateMeasurements
from decorator import fedt_experiment
from flowchart_render import render_flowchart
from lib import *

def summarize(data):
    return "Oh wow, great data!"

class CustomProgram:
    def edit(knitfile: VirtualWorldObject, specification: str):
        instruction("edit: {}".format(specification))
        knitfile.updateVersion("edit", specification)
        return knitfile

@fedt_experiment
def compare_sizings():
    knit_texture = GeometryFile("fgcat_bgtile.knit")

    photos = BatchMeasurements.empty()
    knitted = []
    for size in Parallel(['small','medium','large']):
        CustomProgram.edit(knit_texture, "resize to {}".format(size))
        single_knitted = KnittingMachine.knit(knit_texture)
        Human.post_process(single_knitted, "stretch out (as much as possible?) and insert pins")
        photos += Camera.take_picture(single_knitted, "whole object")
    
    summarize(photos.get_all_data())

if __name__ == "__main__":
    render_flowchart(compare_sizings)