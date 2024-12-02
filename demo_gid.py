import random

from numpy import arange

from flowchart import FlowChart
from instruction import instruction
from iterators import Series, Parallel, include_last
from measurement import BatchMeasurements, ImmediateMeasurements
from design import VolumeFile
from decorator import fedt_experiment
from flowchart_render import render_flowchart
from lib import *

def summarize(data):
    return "Oh wow, great data!"

class Blender:
    def render_gcode(gcode: VirtualWorldObject):
        instruction("render the object in blender")
        return gcode

class ExternalApp:
    def analyze(photo):
        pass

@fedt_experiment
def find_bottom_spacings():
    large_object = VolumeFile("large from thingiverse.stl")
    medium_object = VolumeFile("medium from thingiverse.stl")
    small_object = VolumeFile("small from thingiverse.stl")

    bottom_angle_results = BatchMeasurements.empty()
    bottom_width_results = BatchMeasurements.empty()
    infill_angle_results = BatchMeasurements.empty()
    infill_density_results = BatchMeasurements.empty()
    infill_pattern_results = BatchMeasurements.empty()

    for obj_file in Parallel([large_object,medium_object,small_object]):
        for bottom_angle in Parallel(arange(0,6+include_last,1)):
            fabbed_object = Printer.slice_and_print(obj_file, bottom_angle=bottom_angle, filament_color='white') # need to add partial print option
            for photo_rep in range(16):
                bottom_angle_results += Camera.take_picture(fabbed_object, "bottom")
        
        for bottom_width in Parallel(arange(0.35,0.35+0.06+include_last,.01)):
            fabbed_object = Printer.slice_and_print(obj_file, bottom_width=bottom_width, filament_color='white')
            for photo_rep in range(16):
                bottom_width_results += Camera.take_picture(fabbed_object, "bottom")
        
        for infill_pattern in Parallel(['trihexagon','triangular','grid']):
            infill_angles = None
            if infill_pattern in ['trihexagon', 'triangular']:
                infill_angles = arange(0,6+include_last,1)
            else: # if it's grid
                infill_angles = arange(0,6+include_last,1)
            for infill_angle in Parallel(infill_angles):
                fabbed_object = Printer.slice_and_print(obj_file,
                                                        infill_pattern=infill_pattern,
                                                        infill_rotation=infill_angle,
                                                        filament_color='white')
                fabbed_object = Human.post_process(fabbed_object, "hold a light above the object")
                for photo_rep in range(16):
                    picture = Camera.take_picture(fabbed_object, "bottom")
                infill_angle_results += picture
                if infill_angle == 0:
                    infill_pattern_results += picture
        
        for infill_density in Parallel(arange(2.6, 2.6+0.7+include_last, 0.1)):
            fabbed_object = Printer.slice_and_print(obj_file,
                                                    infill_density=infill_density,
                                                    filament_color='white')
            for photo_rep in range(16):
                infill_density_results += Camera.take_picture(fabbed_object, "bottom")

    
    summarize(bottom_angle_results.get_all_data())
    summarize(bottom_width_results.get_all_data())
    summarize(infill_pattern_results.get_all_data())
    summarize(infill_angle_results.get_all_data())
    summarize(infill_density_results.get_all_data())

def random_param_set():
    infill_pattern = random.choice(['trihexagon','triangular','grid'])
    infill_rotation_range = None
    if infill_pattern in ['trihexagon', 'triangular']:
        infill_rotation_range = arange(0,60,1)
    else: # if it's grid
        infill_rotation_range = arange(0,90,1)
    return (random.choice(list(arange(5,90,5)) + list(arange(95,180,5))), # bottom angle
            random.choice(arange(0.35,0.6+include_last,.05)), # bottom width
            infill_pattern, # infill pattern
            random.choice(infill_rotation_range), # infill rotation
            random.choice(arange(2.6, 3.2+include_last, 0.6))) # infill density / width

@fedt_experiment
def cross_validation():
    large = [VolumeFile("gid_mug.stl")] * 10
    medium = [VolumeFile("gid_keysleeve.stl")] * 6
    objs = large + medium

    filament = 'white'

    all_object_results = BatchMeasurements.empty()

    for obj in Parallel(objs):
        bottom_angle, bottom_width, infill_pattern, infill_rotation, infill_density = random_param_set()
        fabbed_object = Printer.slice_and_print(obj,
                                                infill_pattern=infill_pattern,
                                                infill_rotation=infill_rotation,
                                                bottom_angle=bottom_angle,
                                                bottom_width=bottom_width,
                                                infill_density=infill_density,
                                                filament_color=filament)
        fabbed_object = Human.post_process(fabbed_object, "hold a light above the object")
        all_object_results += Camera.take_picture(fabbed_object, "bottom")

    summarize(all_object_results.get_all_data())

@fedt_experiment
def materials_lighting_thicknesses():
    model = VolumeFile("keycover.stl")
    filament_colors = ['red', 'yellow', 'blue', 'orange', 'green', 'purple', 'black', 'white']
    bottom_line_angles = list(arange(0,180+include_last,(180-0)/6))
    bottom_line_widths = list(arange(0.35,0.6+include_last,(.6-.35)/6))
    light_intensity = 0
    intensity_step = 10 # wasn't quite this formal, but this is ok

    lighted_photos = ImmediateMeasurements.empty()

    for color in Parallel(filament_colors):
        for config_id in Parallel(range(len(bottom_line_angles))):
            fabbed_object = Printer.slice_and_print(model,
                                                    filament_color=color,
                                                    bottom_line_angle=bottom_line_angles[config_id],
                                                    bottom_line_width=bottom_line_widths[config_id])
            is_detecting = False
            while not is_detecting:
                light_intensity += intensity_step
                fabbed_object = Human.post_process(fabbed_object, f"light brightness of {light_intensity}")
                photo = lighted_photos.do_measure(fabbed_object, Camera.image.set_feature("bottom"))
                is_detecting = ExternalApp.analyze(photo)
    
    summarize(lighted_photos.get_all_data())

@fedt_experiment
def different_printers():
    model = VolumeFile("keycover.stl")
    bottom_line_angles = list(arange(0,180+include_last,(180-0)/6))
    bottom_line_widths = list(arange(0.35,0.6+include_last,(.6-.35)/6))

    printers = ['Prusa i3 MK3S', 'Creality CR-10S Pro', 'Ultimaker 3']

    angular_deviation_results = BatchMeasurements.empty()
    width_deviation_results = BatchMeasurements.empty()
    photos = BatchMeasurements.empty()

    for printer in Parallel(printers):
        for config_id in Parallel(range(len(bottom_line_angles))):
            fabbed_object = Printer.slice_and_print(model,
                                                    printer=printer,
                                                    bottom_line_angle = bottom_line_angles[config_id],
                                                    bottom_line_width = bottom_line_widths[config_id])
            photos += Camera.take_picture(fabbed_object, "bottom")
            instruction("Use a microscope to make the following measurements")
            width_deviation_results += Calipers.measure_size(fabbed_object, "width of trace")
            angular_deviation_results += Protractor.measure_angle(fabbed_object, "angle of trace to base")
    
    summarize(angular_deviation_results.get_all_data())
    summarize(width_deviation_results.get_all_data())
    summarize(photos.get_all_data())

@fedt_experiment
def camera_distance():
    cameras = ['iPhone 5s', 'Pixel 2', 'OnePlus 6']

    fabbed_objects = [Printer.slice_and_print(x) for x in ['file_from_above.stl']]

    camera_data = BatchMeasurements.empty()

    for camera in Parallel(cameras):
        for fabbed_object in Parallel(fabbed_objects):
            camera_data += Camera.take_picture(fabbed_object, f"bottom with {camera}")
        
    summarize(camera_data.get_all_data())

@fedt_experiment
def camera_angle():
    models = [VolumeFile('thingi10kdb.stl')] * 600
    angles = [f"at {deg} deg, along azimuth {azimuth}" for deg in [4, 6, 8, 10, 12] for azimuth in range(8)]

    images = BatchMeasurements.empty()
    
    for model in Parallel(models):
        bottom_angle, bottom_width, infill_pattern, infill_rotation, infill_density = random_param_set()
        gcode = Slicer.slice(model,
                                infill_pattern=infill_pattern,
                                infill_rotation=infill_rotation,
                                bottom_angle=bottom_angle,
                                bottom_width=bottom_width,
                                infill_density=infill_density)
        virtual_render = Blender.render_gcode(gcode)
        for angle in Parallel(angles):
            images += Camera.take_picture(virtual_render, angle)
    
    summarize(images.get_all_data())


if __name__ == "__main__":
    # render_flowchart(find_bottom_spacings)
    render_flowchart(cross_validation, pdf=True)
    # render_flowchart(materials_lighting_thicknesses)
    # render_flowchart(different_printers)
    # render_flowchart(camera_distance)
    # render_flowchart(camera_angle)
    # import control
    # from control import MODE, Execute
    # control.MODE = Execute()
    # cross_validation()