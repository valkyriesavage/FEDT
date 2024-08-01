from instruction import instruction
from measurement import Measurements
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

    results = Measurements.empty()
    for stl in all_widget_files:
        fabbed_object = Printer.slice_and_print(VolumeFile(stl))
        for input_massflow in ['5e^-5','9.5e^-5','14e^-5','18.5e^-5']:
            instruction(f"set the air compressor to {input_massflow} and connect the object")
            results += Anemometer.measure_airflow(fabbed_object, f"input massflow at {input_massflow}")
    
    # I'm not totally sure about how to write this last bit. it will depend
    # upon how we structure this data piece.
    # summarize([result in results if result.related_object in logic_gate_files])
    # summarize([result in results if result.related_object in input_files])
    summarize(results.get_data())


@fedt_experiment
def or_orientations():
    or_gate = VolumeFile('or.stl')

    results = Measurements.empty()
    for print_angle in range(0,90,22.5):
        for repetition in range(4):
            rotated_gate = StlEditor.rotate(or_gate, print_angle)
            fabbed_object = Printer.slice_and_print(rotated_gate)
            for input_massflow in ['5e^-5','9.5e^-5','14e^-5','18.5e^-5']:
                instruction(f"set the air compressor to {input_massflow} and connect the object")
                results += Anemometer.measure_airflow(fabbed_object, f"input massflow at {input_massflow}")

    summarize(results.get_data())

@fedt_experiment
def or_bendradius():
    or_gate = VolumeFile('or.stl')

    results = Measurements.empty()
    for bend_radius in range(0,20,5):
        gate_with_bend = StlEditor.add_bent_path(or_gate, bend_radius)
        fabbed_object = Printer.slice_and_print(gate_with_bend)
        for input_massflow in ['5e^-5','9.5e^-5','14e^-5','18.5e^-5']:
                instruction(f"set the air compressor to {input_massflow} and connect the object")
                results += Anemometer.measure_airflow(fabbed_object, f"input massflow at {input_massflow}")

    summarize(results.get_data())

@fedt_experiment
def output_airneeds():
    output_widgets = ['pin_display.stl','vibration_motor.stl',
									'whistle.stl','wiggler.stl']
									
    epsilon = '.1kPa' # ?

    mins = []
    maxs = []
    for widget in output_widgets:
        gcode = slicer.slice(widget)
        fabbed_object = printer.print(gcode)
        aircompressor.connect(fabbed_object)
        while not human.judge_working(fabbed_object):
            air_compressor.increase_output_pressure(epsilon)
        mins.push(anemometer.measure_output_pressure(air_compressor))
        while human.judge_working(fabbed_object):
            air_compressor.increase_ouput_pressure(epsilon)
        maxs.push(anemometer.measure_output_pressure(air_compressor))
        
    summarize(mins, maxs)

if __name__ == "__main__":
    print(or_bendradius())
