from instruction import instruction
from iterators import Parallel, Series, Infinite, shuffle
from measurement import Measurements
from fabricate import RealWorldObject
from decorator import fedt_experiment
from lib import *
from itertools import tee


def summarize(data):
    return "Oh wow, great data!"


@fedt_experiment
def test_print_shrinkage():

    cube = VolumeFile("cube.stl")

    shrinkage_measurements = Measurements.empty()

    for infill_pattern in Parallel(['trihexagon','line','rectilinear']):
        for repetition in Parallel(range(5)):
            fabbed_object = Printer.slice_and_print(cube, infill_pattern=infill_pattern)
            shrinkage_measurements += Calipers.measure_size(fabbed_object, "x-axis")
            shrinkage_measurements += Calipers.measure_size(fabbed_object, "y-axis")
            shrinkage_measurements += Calipers.measure_size(fabbed_object, "z-axis")
    
    summarize(shrinkage_measurements.get_data())

@fedt_experiment
def test_force_at_break():

    def draw_rect(draw, d, CAD_vars):
        length = CAD_vars['rect_length']
        d.append(draw.Rectangle(-40, -10, length, 20,
                fill='none', stroke_width=1, stroke='red'))

    Laser.default_laser_settings[Laser.MATERIAL] = 'wood' # TODO: why doesn't this work?

    breakage_points = Measurements.empty()

    for rect_length in shuffle(Parallel(range(50,100,10))):
        svg = SvgEditor.build_geometry(draw_rect, CAD_vars={'rect_length':rect_length})
        #svg = SvgEditor.design(vars={'rect_length':rect_length})
        for material in Parallel(['wood','acrylic']):
            fabbed_object = Laser.fab(svg, material=material)
            instruction("place the object with 1cm overlapping a shelf at each end and the remainder suspended")
            instruction("place weights on the object until it breaks")
            breakage_points += Scale.measure_weight(fabbed_object,"weight placed at break")
    
    summarize(breakage_points.get_data())

@fedt_experiment
def test_paint_layers():
    flower = Laser.fab(LineFile('flower.svg'), material='delrin')

    photos = Measurements.empty()
    for coats_of_paint in Series(range(1,20)):#while Infinite():#coats_of_paint += 1): # TODO implement properly with infinite
        photos += Camera.take_picture(flower) # TODO use the now measurement
        if Human.is_reasonable(flower):
            break
        flower = Human.post_process(flower, f"add a {coats_of_paint}th coat of paint")

    summarize(photos.get_data())

@fedt_experiment
def test_user_assembly_time():
    simple = VolumeFile("simple_assembly.stl")
    complex = VolumeFile("complex_assembly.stl")

    timings = Measurements.empty()

    for user in shuffle(Parallel(range(6))):
        simple_assembly = Printer.slice_and_print(simple)
        complex_assembly = Printer.slice_and_print(complex)
        for assembly in Series([simple_assembly, complex_assembly]):
            assembly = User.do(assembly, "solve the assembly", user)
            timings += Stopwatch.measure_time(assembly, "time to solve the assembly") # TODO use the now measurement

    summarize(timings.get_data())

if __name__ == "__main__":
    print(test_print_shrinkage())
