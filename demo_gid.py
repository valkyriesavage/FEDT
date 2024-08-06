import random

from numpy import arange

from instruction import instruction
from measurement import Measurements
from design import VolumeFile
from decorator import fedt_experiment
from lib import *

include_last = .001

def summarize(data):
    return "Oh wow, great data!"

@fedt_experiment
def find_bottom_spacings():
    large_object = VolumeFile("large from thingiverse.stl")
    medium_object = VolumeFile("medium from thingiverse.stl")
    small_object = VolumeFile("small from thingiverse.stl")

    bottom_angle_results = Measurements.empty()
    bottom_width_results = Measurements.empty()
    infill_angle_results = Measurements.empty()
    infill_density_results = Measurements.empty()
    infill_pattern_results = Measurements.empty()

    # these guesses are made based on the labels in the figure at the top of page 8, which has no caption or name
    for obj_file in [large_object,medium_object,small_object]:

        for bottom_angle in arange(0,6+include_last,1):
            fabbed_object = Printer.slice_and_print(obj_file, bottom_angle=bottom_angle)
            bottom_angle_results += Camera.take_picture(fabbed_object, "bottom")
        
        for bottom_width in arange(0.35,0.35+0.06+include_last,.01):
            fabbed_object = Printer.slice_and_print(obj_file, bottom_width=bottom_width)
            bottom_width_results += Camera.take_picture(fabbed_object, "bottom")
        
        for infill_type in ['trihexagon','triangular','grid']:
            infill_rotations = None
            if infill_type in ['trihexagon', 'triangular']:
                infill_rotations = arange(0,6+include_last,1)
            else: # if it's grid
                infill_rotations = arange(0,6+include_last,1) # not clear if they did it the same way?
            for infill_rotation in infill_rotations:
                fabbed_object = Printer.slice_and_print(obj_file,
                                                        infill_pattern=infill_type,
                                                        infill_rotation=infill_rotation)
                instruction("hold a light above the object")
                picture = Camera.take_picture(fabbed_object, "bottom")
                infill_angle_results += picture
                if infill_rotation == 0:
                    infill_pattern_results += picture
        
        for infill_density in arange(2.6, 2.6+0.7+include_last, 0.1):
            fabbed_object = Printer.slice_and_print(obj_file,
                                                    infill_density=infill_density)
            infill_density_results += Camera.take_picture(fabbed_object, "bottom")

    
    summarize(bottom_angle_results.get_data())
    summarize(bottom_width_results.get_data())
    summarize(infill_pattern_results.get_data())
    summarize(infill_angle_results.get_data())
    summarize(infill_density_results.get_data())

@fedt_experiment
def force_response():
    pass


if __name__ == "__main__":
    print(find_bottom_spacings())
