import control
from control import Execute, Evaluate
from instruction import instruction
from iterators import Parallel, Series, shuffle
from measurement import BatchMeasurements, ImmediateMeasurements
from flowchart import FlowChart
from flowchart_render import render_flowchart
from decorator import fedt_experiment
from lib import *


def summarize(data):
    return "Oh wow, great data!"


@fedt_experiment
def test_print_shrinkage():

    cube = VolumeFile("expt_stls/cube.stl")

    shrinkage_measurements = BatchMeasurements.empty()

    for infill_pattern in Parallel(['concentric','line','rectilinear']):
        for repetition in Parallel(range(5)):
            fabbed_object = Printer.slice_and_print(cube,
                                                    infill_pattern=infill_pattern,
                                                    repetition=repetition)
            shrinkage_measurements += Calipers.measure_size(fabbed_object, "x-axis")
            shrinkage_measurements += Calipers.measure_size(fabbed_object, "y-axis")
            shrinkage_measurements += Calipers.measure_size(fabbed_object, "z-axis")
    
    summarize(shrinkage_measurements.get_all_data())

@fedt_experiment
def test_force_at_break():

    def draw_rect(draw, d, CAD_vars):
        length = CAD_vars['rect_length']
        d.append(draw.Rectangle(-40, -10, length, 20,
                fill='none', stroke_width=1, stroke='red'))

    breakage_points = BatchMeasurements.empty()

    for rect_length in Parallel(range(50,100,10)):
        svg = SvgEditor.build_geometry(draw_rect, CAD_vars={'rect_length':rect_length})
        #svg = SvgEditor.design(vars={'rect_length':rect_length})
        for material in Parallel(['wood','acrylic']):
            fabbed_object = Laser.fab(svg, material=material)
            instruction("place the object with 1cm overlapping a shelf at each end and the remainder suspended")
            instruction("place weights on the object until it breaks")
            breakage_points += Scale.measure_weight(fabbed_object,"total weight placed at break")
    
    summarize(breakage_points.get_all_data())

@fedt_experiment
def test_paint_layers():
    flower = Laser.fab(LineFile('flower.svg'), material='delrin')

    photos = ImmediateMeasurements.empty()
    is_reasonable = False
    coats_of_paint = 0
    while not is_reasonable:
        flower = Human.is_reasonable(flower)
        photos += Camera.take_picture(flower)
        is_reasonable = flower.metadata["human reasonableness check"]
        if not is_reasonable:
            coats_of_paint = coats_of_paint + 1
            flower = Human.post_process(flower, f"add a {coats_of_paint}th coat of paint")

    summarize(photos.dump_to_csv())

@fedt_experiment
def test_user_assembly_time():
    simple = VolumeFile("simple_assembly.stl")
    complex = VolumeFile("complex_assembly.stl")

    timings = ImmediateMeasurements.empty()

    treatments = shuffle(["simple_first"] * 3 + ["complex_first"] * 3)

    for (user, treatment) in Parallel(enumerate(treatments)):
        simple_assembly = Printer.slice_and_print(simple)
        complex_assembly = Printer.slice_and_print(complex)
        if treatment == "simple_first":
            assembly = User.do(simple_assembly, "solve the assembly", user)
            timings += Stopwatch.measure_time(assembly, "time to solve the assembly")
            assembly = User.do(complex_assembly, "solve the assembly", user)
            timings += Stopwatch.measure_time(assembly, "time to solve the assembly")
        else:
            assembly = User.do(complex_assembly, "solve the assembly", user)
            timings += Stopwatch.measure_time(assembly, "time to solve the assembly")
            assembly = User.do(simple_assembly, "solve the assembly", user)
            timings += Stopwatch.measure_time(assembly, "time to solve the assembly")
            
    summarize(timings.dump_to_csv())

if __name__ == "__main__":
    # create a flowchart
    render_flowchart(test_print_shrinkage)
    #render_flowchart(test_force_at_break)

    # run an experiment
    # from control import MODE, Execute
    # control.MODE = Execute()
    # test_paint_layers()
    # test_force_at_break()

    # render a LaTeX description - under construction
    #print(FlowChart().to_latex())

    # other sample flowcharts
    #render_flowchart(test_paint_layers)
    #render_flowchart(test_user_assembly_time)
