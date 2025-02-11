from numpy import arange

import control
from control import Execute, Evaluate
from instruction import instruction
from iterators import Parallel, Series, shuffle, include_last
from measurement import BatchMeasurements, ImmediateMeasurements
from flowchart import FlowChart
from flowchart_render import render_flowchart
from decorator import fedt_experiment
from lib import *


def analyze(data):
    return "Oh wow, great data!"


@fedt_experiment
def test_weight():

    def draw_rect(draw, d, CAD_vars):
        length = CAD_vars['rect_length']
        d.append(draw.Rectangle(-40, -10, length, 20,
                fill='none', stroke_width=1, stroke='red'))

    breakage_points = BatchMeasurements.empty()

    for rect_length in Parallel([50,75]):
        svg = SvgEditor.build_geometry(draw_rect, CAD_vars={'rect_length':rect_length})
        for material in Parallel(['wood','acrylic']):
            fabbed_object = Laser.fab(svg, material=material)
            breakage_points += Scale.measure_weight(fabbed_object,"total weight placed at break")
    
    analyze(breakage_points.get_all_data())

@fedt_experiment
def test_paint_layers():
    flower = Laser.fab(GeometryFile('flower.svg'), material='wood')

    photos = ImmediateMeasurements.empty()
    is_reasonable = False
    coats_of_paint = 0
    while not is_reasonable:
        coats_of_paint = coats_of_paint + 1
        flower = Human.post_process(flower, f"add a {coats_of_paint}th coat of paint")
        flower = Human.is_reasonable(flower)
        photos += Camera.take_picture(flower)
        is_reasonable = flower.metadata["human reasonableness check"]

    analyze(photos.dump_to_csv())

@fedt_experiment
def test_user_assembly_time():
    simple = Printer.slice_and_print(GeometryFile("simple_assembly.stl"))
    complex = Printer.slice_and_print(GeometryFile("complex_assembly.stl"))

    timings = ImmediateMeasurements.empty()

    treatments = shuffle(["simple_first","complex_first"])

    for (user, treatment) in Parallel(enumerate(treatments)):
        order = [simple, complex] if (treatment == 'simple_first') else [complex, simple]
        for assembly in Series(order):
            assembly = User.do(assembly, "solve the assembly", user)
            timings += Stopwatch.measure_time(assembly, "time to solve the assembly")
            instruction(f"disassemble object {assembly.uid} for next user")
            
    analyze(timings.dump_to_csv())


if __name__ == "__main__":
    render_flowchart(test_weight, pdf=True)
    render_flowchart(test_paint_layers, pdf=True)
    render_flowchart(test_user_assembly_time, pdf=True)
