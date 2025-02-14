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

class CustomProgram(DesignSoftware):
    @staticmethod
    def modify_design(knitfile: GeometryFile, feature_name: str, feature_value: str|int):
        knitfile.updateVersion(feature_name, feature_value, f"modify design: {knitfile.file_location} by setting {feature_name} to {feature_value}")
        return knitfile

@fedt_experiment
def compare_sizings():
    knit_texture = GeometryFile("fgcat_bgtile.knit")

    photos = BatchMeasurements.empty()
    for size in Parallel(['small','medium','large']):
        CustomProgram.modify_design(knit_texture, "size", size)
        single_knitted = KnittingMachine.knit(knit_texture)
        Human.post_process(single_knitted, "stretch out (as much as possible?) and insert pins")
        photos += Camera.take_picture(single_knitted, "whole object")
    
    summarize(photos.get_all_data())

if __name__ == "__main__":
    render_flowchart(compare_sizings)