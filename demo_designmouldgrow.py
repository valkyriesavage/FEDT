from numpy import arange

from instruction import instruction
from measurement import Measurements
from fabricate import RealWorldObject
from decorator import fedt_experiment
from lib import *

include_last = .001

def compare(dataset1, dataset2):
    return "Hmmmm... I think these two are pretty same-same??"

def summarize(data):
    return "Oh wow, great data!"

class CustomModellingTool:
    # call the custom modelling tool that they created
    @staticmethod
    def sphere(radius: float=10.) -> VolumeFile:
        instruction(f"use the custom tool to make a sphere with radius {radius}")
        from control import MODE, Execute
        stl_location = ''
        if isinstance(MODE, Execute):
            stl_location = input("what is the location of the stl file generated?")
        return VolumeFile(stl_location)

@fedt_experiment
def geometric_features():
    shrinkage_results = Measurements.empty()
    scanning_results = Measurements.empty()
    for geometry_file in ['ramps.stl', 'circular.stl', 'patterns.stl']:
        mould = Printer.slice_and_print(geometry_file)
        for myco_material in ['30% coffee inclusions', 'no inclusions']:
            fabbed_object = Human.mould_mycomaterial(mould, myco_material)
            Environment.wait_up_to_time_single(fabbed_object, num_weeks=1)
            # this loop should unroll somehow so all the grow takes place at once...
            # although each mould is used for 2 different, sequential grows :thinking_face:
            shrinkage_results += Calipers.measure_size(fabbed_object, "important dimension")
            if geometry_file != 'ramps.stl':
                scanning_results += Scanner.scan(fabbed_object)
        if geometry_file == 'circular.stl':
            oneoff_object = Human.mould_mycomaterial(mould, 'no inclusions')
            oneoff_object = Human.post_process(oneoff_object, 'glycerine treatment')
            shrinkage_results += Calipers.measure_size(oneoff_object, "important dimension")
            scanning_results += Scanner.scan(oneoff_object)

    shrinkage_results = shrinkage_results.get_data()
    scanning_results = scanning_results.get_data()

    for result in scanning_results:
        real = None
        digital = None
        if result.geometry_file == 'circular': # TODO how to do this?
            for angle in arange(7.5, 82.5+include_last, 7.5):
                real = StlEditor.extract_profile(result, angle)
                digital = StlEditor.extract_profile(result.geometry_file, angle)
                result.comparison = compare(real, digital)
        if result.geometry_file == 'patterns':
            for offset in arange(0, 1.5+include_last, 0.1):
                real = StlEditor.extract_profile(result, offset)
                digital = StlEditor.extract_profile(result.geometry_file, offset)
                result.comparison = compare(real, digital)
        if Human.is_reasonable(result) and real is not None and digital is not None:
            # only process the ones that seem reasonable (they skipped the non-inclusion patterns one)
            result.error = StlEditor.uniform_sample_error(real, digital)
            if result.geometry_file == 'patterns':
                result.convexity_error = StlEditor.sample_convex(real, digital)
                result.concavity_error = StlEditor.sample_concave(real, digital)
			
    summarize(shrinkage_results)
    summarize(scanning_results)


@fedt_experiment
def mechanical_and_shrinkage_features():
    target_cube = StlEditor.cube((30,60,16))
    scaled_mould = StlEditor.cube((30, 60, 16), scale=1/.92)

    shrinkage_results = Measurements.empty()
    mechanical_results = Measurements.empty()
    mould = Printer.slice_and_print(scaled_mould)
    for myco_material in ['30% coffee inclusions', 'no inclusions']:
        for repetition in range(4):
            fabbed_object = Human.mould_mycomaterial(mould, myco_material)
            Environment.wait_up_to_time_single(fabbed_object, num_weeks=1)
            shrinkage_results += Calipers.measure_size(fabbed_object, "x-axis")
            shrinkage_results += Calipers.measure_size(fabbed_object, "y-axis")
            shrinkage_results += Calipers.measure_size(fabbed_object, "z-axis")
            for repetition_mechanical in range(5):
                for depth in arange(0,5,.5):
                    instruction("ensure fabbed object is appropriately arranged on testing stand")
                    fabbed_object = Human.post_process(fabbed_object, "compress the object to " + str(depth)) # not clear who/what does the compressing?
                    mechanical_results += ForceGauge.measure_force(fabbed_object)           
    
    summarize(shrinkage_results.get_data())
    summarize(mechanical_results.get_data())

@fedt_experiment
def test_software_tool():
    target_sphere = StlEditor.sphere(20)
    software_generated_mould = CustomModellingTool.sphere(20)

    results = Measurements.empty()
    mould = Printer.slice_and_print(software_generated_mould)
    myco_material = "30% coffee inclusions"
    for repetition in range(3):
        fabbed_object = Human.mould_mycomaterial(mould, myco_material)
        Environment.wait_up_to_time_single(fabbed_object, num_weeks=1)
        measurement_points = range(0,90,45)
        for x_axis_point in measurement_points:
            results += Calipers.measure_size(fabbed_object, f"{x_axis_point} degrees along the x axis")
        for y_axis_point in measurement_points:
            results += Calipers.measure_size(fabbed_object, f"{y_axis_point} degrees along the y axis")
        for z_axis_point in measurement_points:
            results += Calipers.measure_size(fabbed_object, f"{z_axis_point} degrees along the z axis")
                
    summarize(results.get_data())


if __name__ == "__main__":
    print(mechanical_and_shrinkage_features())
