import math

from numpy import arange

from instruction import instruction
from iterators import Series, Parallel, include_last
from measurement import BatchMeasurements
from fabricate import RealWorldObject
from flowchart_render import render_flowchart
from decorator import fedt_experiment
from lib import *


def summarize(data):
    return "Oh wow, great data!"


@fedt_experiment
def effect_of_b_horizontal():

    A = 41
    C = 10
    D = 14

    delta = (27.5-4)/3 # ? -> there are 3 values in the figure

    results = BatchMeasurements.empty()
    for B in Parallel(arange(4, 27.5+include_last, delta)):
        linefile = SvgEditor.design(vars = {'A':A, 'B':B, 'C':C, 'D':D})
        fabbed_object = Laser.fab(linefile)
        for repetition in Series(range(5)):
            fabbed_object = Human.post_process(fabbed_object, "heat with the heat gun") # ? -> not sure if it is heat gun or plate
            fabbed_object = Human.post_process(fabbed_object, "inject air to inflate the object") # ? -> probably human does this, based on the video
            results += Protractor.measure_angle(fabbed_object,"overall bend")
            fabbed_object = Human.post_process(fabbed_object, "heat with the heat gun") # ? -> not sure if it is heat gun or plate
            fabbed_object = Human.post_process(fabbed_object, "flatten the object") # ? -> it's not specified that they are flattened, but they must be

    summarize(results.get_all_data())

@fedt_experiment
def effect_of_incision_number():
    A = 41
    B = 14
    C = 10
    D = 14

    results = BatchMeasurements.empty()
    for num_incisions in Parallel([6,12]):
        linefile = SvgEditor.design(vars = {'A':A, 'B':B, 'C':C, 'D':D, 'num_incisions':num_incisions})
        fabbed_object = Laser.fab(linefile)
        fabbed_object = Human.post_process(fabbed_object, "heat with the heat gun") # ? -> not sure if it is heat gun or plate
        fabbed_object = Human.post_process(fabbed_object, "inject air to inflate the object") # ? -> probably human does this, based on the video
        results += Protractor.measure_angle(fabbed_object,"overall bend")
    
    summarize(results.get_all_data())

@fedt_experiment
def effect_of_interplate_distance_vertical():
    outer_size = (100, 40)
    airbag_size = (45, 28)

    results = BatchMeasurements.empty()
    for distance in Parallel([0,30]):
        linefile = SvgEditor.design(vars = {'outer size': outer_size, 'airbag size': airbag_size, 'distance': distance})
        instruction(f"place polycarbonate in the laser bed with spacing {distance}")
        fabbed_object = Laser.fab(linefile)
        for repetition in Parallel(range(5)):
            fabbed_object = Human.post_process(fabbed_object, "heat with the heat gun") # ? -> not sure if it is heat gun or plate
            fabbed_object = Human.post_process(fabbed_object, "inject air to inflate the object") # ? -> probably human does this, based on the video
            results += Protractor.measure_angle(fabbed_object,"overall bend")
            fabbed_object = Human.post_process(fabbed_object, "heat with the heat gun") # ? -> not sure if it is heat gun or plate
            fabbed_object = Human.post_process(fabbed_object, "flatten the object") # ? -> it's not specified that they are flattened, but they must be
    summarize(results.get_all_data())
    # more objects got made. maybe 3 or 4.

if __name__ == "__main__":
    render_flowchart(effect_of_b_horizontal)
    render_flowchart(effect_of_incision_number)
    render_flowchart(effect_of_interplate_distance_vertical)
