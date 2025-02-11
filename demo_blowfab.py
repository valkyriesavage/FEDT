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

    delta = (27.5-4)/5 # only 3 shown in image, but 5 were tested

    results = BatchMeasurements.empty()
    for B in Parallel(arange(4, 27.5+include_last, delta)):
        linefile = SvgEditor.design(vars = {'A':A, 'B':B, 'C':C, 'D':D})
        fabbed_object = Laser.fab(linefile, material="PET")
        for repetition in Series(range(5)):
            fabbed_object = Human.post_process(fabbed_object, "heat with the heat plate")
            fabbed_object = Human.post_process(fabbed_object, "inject air with the air compressor to inflate the object")
            instruction("slowly turn the valve on the air compressor to inflate just to the point of fullness")
            results += Camera.take_picture(fabbed_object, "overall bend")
            instruction("extract the bend angle from the photograph")
            fabbed_object = Human.post_process(fabbed_object, "heat with the heat plate")
            fabbed_object = Human.post_process(fabbed_object, "flatten the object")

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
        fabbed_object = Laser.fab(linefile, material="PET")
        fabbed_object = Human.post_process(fabbed_object, "heat with the heat plate")
        fabbed_object = Human.post_process(fabbed_object, "inject air with the air compressor to inflate the object")
        instruction("slowly turn the valve on the air compressor to inflate just to the point of fullness")
        results += Camera.take_picture(fabbed_object, "overall bend")
        instruction("extract the bend angle from the photograph")
    
    summarize(results.get_all_data())

@fedt_experiment
def effect_of_interplate_distance_vertical():
    outer_size = (100, 40)
    airbag_size = (45, 28)

    results = BatchMeasurements.empty()
    for distance in Parallel([0,30]):
        for repetition in Parallel(range(2)):
            linefile = SvgEditor.design(vars = {'outer size': outer_size, 'airbag size': airbag_size, 'distance': distance})
            instruction(f"place polycarbonate in the laser bed with spacing {distance}")
            fabbed_object = Laser.fab(linefile, material="PET")
            for repetition in Parallel(range(5)):
                fabbed_object = Human.post_process(fabbed_object, "heat with the heat plate")
                fabbed_object = Human.post_process(fabbed_object, "inject air with the air compressor to inflate the object")
                instruction("slowly turn the valve on the air compressor to inflate just to the point of fullness")
                results += Camera.take_picture(fabbed_object, "overall bend")
                instruction("extract the bend angle from the photograph")
                fabbed_object = Human.post_process(fabbed_object, "heat with the heat plate")
                fabbed_object = Human.post_process(fabbed_object, "flatten the object")
    summarize(results.get_all_data())

if __name__ == "__main__":
    render_flowchart(effect_of_b_horizontal)
    render_flowchart(effect_of_incision_number)
    render_flowchart(effect_of_interplate_distance_vertical)
