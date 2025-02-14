from numpy import arange

from instruction import instruction
from iterators import Parallel, Series, include_last
from measurement import BatchMeasurements
from design import GeometryFile
from decorator import fedt_experiment
from flowchart_render import render_flowchart
from lib import *


def summarize(data):
    return "Oh wow, great data!"


@fedt_experiment
def airflow_gatetypes():
    logic_gate_files = ['and.stl', 'or.stl', 'not.stl', 'xor.stl']
    input_files = ['touch.stl', 'button.stl', 'rocker.stl',
                                'dial.stl', 'slider.stl']
    all_widget_files = logic_gate_files + input_files

    results = BatchMeasurements.empty()
    for stl in Parallel(all_widget_files):
        print("i am going to try")
        fabbed_object = Printer.fab(GeometryFile(stl))
        for input_massflow in Series(['5e^-5','9.5e^-5','14e^-5','18.5e^-5']):
            instruction(f"set the air compressor to {input_massflow} and connect the object")
            results += Anemometer.measure_airflow(fabbed_object, f"input massflow at {input_massflow}")
    
    # it's possible this is two experiments?
    # summarize([result in results if result.related_object in logic_gate_files])
    # summarize([result in results if result.related_object in input_files])
    summarize(results.get_all_data())


@fedt_experiment
def or_orientations():
    or_gate = GeometryFile('or.stl')

    fabbed_objects = []

    results = BatchMeasurements.empty()
    for print_angle in Parallel(arange(0,90+include_last,22.5)):
        rotated_gate = StlEditor.rotate(or_gate, print_angle)
        for repetition in Parallel(range(4)):
            fabbed_object = Printer.fab(rotated_gate, repetition=repetition)
            fabbed_objects.append(fabbed_object)
    for fabbed_object in Parallel(fabbed_objects):    
        for input_massflow in Series(['5e^-5','9.5e^-5','14e^-5','18.5e^-5']):
            instruction(f"set the air compressor to {input_massflow} and connect the object")
            results += Anemometer.measure_airflow(fabbed_object, f"input massflow at {input_massflow}")

    summarize(results.get_all_data())

@fedt_experiment
def or_bendradius():
    or_gate = GeometryFile('or.stl')

    results = BatchMeasurements.empty()
    for bend_radius in Parallel(arange(0,20+include_last,5)):
        gate_with_bend = StlEditor.modify_design(or_gate, "bent inlet", bend_radius)
        fabbed_object = Printer.fab(gate_with_bend)
        for input_massflow in Series(['5e^-5','9.5e^-5','14e^-5','18.5e^-5']):
                instruction(f"set the air compressor to {input_massflow} and connect the object")
                results += Anemometer.measure_airflow(fabbed_object, f"input massflow at {input_massflow}")

    summarize(results.get_all_data())

@fedt_experiment
def output_airneeds():
    output_widgets = ['pin_display.stl','vibration_motor.stl',
									'whistle.stl','wiggler.stl']
									
    epsilon = '.1kPa' # ?

    airflow = BatchMeasurements.empty()
    for widget in Parallel(output_widgets):
        fabbed_object = Printer.fab(GeometryFile(widget))
        instruction(f"connect object #{fabbed_object.uid} to the air compressor", header=True)
        instruction(f"increase the air pressure by {epsilon} at a time until the object starts to work")
        airflow += Anemometer.measure_airflow(fabbed_object, 'minimum working pressure')
        instruction(f"increase the air pressure by {epsilon} at a time until the object stops working")
        airflow += Anemometer.measure_airflow(fabbed_object, 'maximum working pressure')
        
    summarize(airflow.get_all_data())

if __name__ == "__main__":
    render_flowchart(airflow_gatetypes)
    render_flowchart(or_orientations)
    render_flowchart(or_bendradius)
    render_flowchart(output_airneeds)
