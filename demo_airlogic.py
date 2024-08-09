from numpy import arange

from instruction import instruction
from iterators import Parallel, Series, include_last
from measurement import BatchMeasurements
from design import VolumeFile
from decorator import fedt_experiment
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
        fabbed_object = Printer.slice_and_print(VolumeFile(stl))
        for input_massflow in Series(['5e^-5','9.5e^-5','14e^-5','18.5e^-5']):
            instruction(f"set the air compressor to {input_massflow} and connect the object")
            results += Anemometer.measure_airflow(fabbed_object, f"input massflow at {input_massflow}")
    
    # I'm not totally sure about how to write this last bit. it's possible this is two experiments...
    # summarize([result in results if result.related_object in logic_gate_files])
    # summarize([result in results if result.related_object in input_files])
    summarize(results.get_all_data())


@fedt_experiment
def or_orientations():
    or_gate = VolumeFile('or.stl')

    results = BatchMeasurements.empty()
    for print_angle in Parallel(arange(0,90+include_last,22.5)):
        for repetition in Parallel(range(4)):
            rotated_gate = StlEditor.rotate(or_gate, print_angle)
            fabbed_object = Printer.slice_and_print(rotated_gate)
            for input_massflow in Series(['5e^-5','9.5e^-5','14e^-5','18.5e^-5']):
                instruction(f"set the air compressor to {input_massflow} and connect the object")
                results += Anemometer.measure_airflow(fabbed_object, f"input massflow at {input_massflow}")

    summarize(results.get_all_data())

@fedt_experiment
def or_bendradius():
    or_gate = VolumeFile('or.stl')

    results = BatchMeasurements.empty()
    for bend_radius in Parallel(range(0,20+include_last,5)):
        gate_with_bend = StlEditor.modify_feature_by_hand(or_gate, "bent inlet", bend_radius)
        fabbed_object = Printer.slice_and_print(gate_with_bend)
        for input_massflow in Series(['5e^-5','9.5e^-5','14e^-5','18.5e^-5']):
                instruction(f"set the air compressor to {input_massflow} and connect the object")
                results += Anemometer.measure_airflow(fabbed_object, f"input massflow at {input_massflow}")

    summarize(results.get_all_data())

@fedt_experiment
def output_airneeds():
    output_widgets = ['pin_display.stl','vibration_motor.stl',
									'whistle.stl','wiggler.stl']
									
    epsilon = '.1kPa' # ?

    mins = BatchMeasurements.empty()
    maxs = BatchMeasurements.empty()
    for widget in Parallel(output_widgets):
        fabbed_object = Printer.slice_and_print(VolumeFile(widget))
        instruction(f"connect object #{fabbed_object.uid} to the air compressor", header=True)
        instruction(f"increase the air pressure by {epsilon} at a time until the object starts to work")
        mins += Anemometer.measure_airflow(fabbed_object)
        instruction(f"increase the air pressure by {epsilon} at a time until the object stops working")
        maxs += Anemometer.measure_airflow(fabbed_object)
        
    summarize(mins.get_all_data())
    summarize(maxs.get_all_data())

if __name__ == "__main__":
    print(or_orientations())
