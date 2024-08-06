import math

from numpy import arange

from instruction import instruction
from measurement import Measurements
from fabricate import RealWorldObject
from decorator import fedt_experiment
from lib import *


def summarize(data):
    return "Oh wow, great data!"


@fedt_experiment
def effect_of_b_horizontal():

    A = 41
    C = 10
    D = 14

    delta = (27.5-4)/3 # ? -> there are 3 values in the figure, so probably?
    include_top = .001

    results = Measurements.empty()
    for B in arange(4, 27.5+include_top, delta):
        linefile = SvgEditor.design(vars = {'A':A, 'B':B, 'C':C, 'D':D})
        fabbed_object = Laser.fab(linefile)
        for repetition in range(5):
            fabbed_object = Human.post_process(fabbed_object, "heat with the heat gun") # ? -> not sure if it is heat gun or plate
            fabbed_object = Human.post_process(fabbed_object, "inject air to inflate the object") # ? -> probably human does this, based on the video
            results += Protractor.measure_angle(fabbed_object,"overall bend")
            fabbed_object = Human.post_process(fabbed_object, "heat with the heat gun") # ? -> not sure if it is heat gun or plate
            fabbed_object = Human.post_process(fabbed_object, "flatten the object") # ? -> it's not specified that they are flattened
    
    summarize(results.get_data())

@fedt_experiment
def effect_of_incision_number():
    A = 41
    B = 14
    C = 10
    D = 14

    results = Measurements.empty()
    for num_incisions in [6,12]:
        linefile = SvgEditor.design(vars = {'A':A, 'B':B, 'C':C, 'D':D, 'num_incisions':num_incisions})
        fabbed_object = Laser.fab(linefile)
        fabbed_object = Human.post_process(fabbed_object, "heat with the heat gun") # ? -> not sure if it is heat gun or plate
        fabbed_object = Human.post_process(fabbed_object, "inject air to inflate the object") # ? -> probably human does this, based on the video
        results += Protractor.measure_angle(fabbed_object,"overall bend")
    
    summarize(results.get_data())

@fedt_experiment
def effect_of_interplate_distance_vertical():
    outer_size = (100, 40)
    airbag_size = (45, 28)

    results = Measurements.empty()
    for distance in [0,30]:
        linefile = SvgEditor.design(vars = {'outer size': outer_size, 'airbag size': airbag_size, 'distance': distance})
        instruction("place polycarbonate in the laser bed with spacing %d".format(distance))
        fabbed_object = Laser.fab(linefile)
        for repetition in range(5):
            fabbed_object = Human.post_process(fabbed_object, "heat with the heat gun") # ? -> not sure if it is heat gun or plate
            fabbed_object = Human.post_process(fabbed_object, "inject air to inflate the object") # ? -> probably human does this, based on the video
            results += Protractor.measure_angle(fabbed_object,"overall bend")
            fabbed_object = Human.post_process(fabbed_object, "heat with the heat gun") # ? -> not sure if it is heat gun or plate
            fabbed_object = Human.post_process(fabbed_object, "flatten the object") # ? -> it's not specified that they are flattened
    summarize(results.get_data())

if __name__ == "__main__":
    print(effect_of_interplate_distance_vertical())
