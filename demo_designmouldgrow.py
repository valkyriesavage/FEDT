from instruction import instruction
from measurement import Measurements
from fabricate import RealWorldObject
from decorator import fedt_experiment
from lib import *


def compare(dataset1, dataset2):
    return "Hmmmm... I think these two are pretty same-same??"

def summarize(data):
    return "Oh wow, great data!"


@fedt_experiment
def geometric_features():
    shrinkage_results = Measurements.empty()
    scanning_results = Measurements.empty()
    for geometry_file in ['ramps.stl', 'circular.stl', 'patterns.stl']:
        mould = Printer.slice_and_print(geometry_file)
        for myco_material in ['30\% coffee inclusions', 'no inclusions']:
            fabbed_object = Human.mould_mycomaterial(myco_material, mould)
            Environment.wait_up_to_times(num_weeks=1)
            fabbed_object.grow() # this loop should unroll somehow so all the grow takes place at once...
            # although each mould is used for 2 different, sequential grows :thinking_face:
            shrinkage_results.push(Calipers.measure_size(fabbed_object, "important dimension"))
            if geometry_file is not 'ramps':
                scanning_results.push(Scanner.scan(fabbed_object))
        if geometry_file == 'circular.stl':
            oneoff_object = Human.mould_mycomaterial('no inclusions', mould)
            oneoff_object = Human.post_process(oneoff_object, 'glycerine treatment')
            shrinkage_results += Calipers.measure_size(oneoff_object, "important dimension")
            scanning_results += Scanner.scan(oneoff_object)

    for result in scanning_results:
        if result.geometry_file == 'circular': # how to do this?
            real = None
            digital = None
            for angle in range(7.5, 82.5, 7.5):
                real = StlEditor.extract_profile(result, angle)
                digital = StlEditor.extract_profile(result.geometry_file, angle)
                result.comparison = compare(real, digital)
        if result.geometry_file == 'patterns':
            for offset in range(0, 1.5, 0.1):
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
    target_cube = StlEditor.cube(30,60,16)
    scaled_mould = StlEditor.cube(30, 60, 16, scale=1/.92)

    shrinkage_results = Measurements.empty()
    mechanical_results = Measurements.empty()
    mould = Printer.slice_and_print(scaled_mould)
    for myco_material in ['30% coffee inclusions', 'no inclusions']:
        for repetition in range(4):
            fabbed_object = Human.mould_mycomaterial(myco_material, mould)
            fabbed_object.grow()
            shrinkage_results += Calipers.measure_size(fabbed_object, "interesting dimension")
            for repetition_mechanical in range(5):
                for depth in range(0,5,.5):
                    assert("fabbed object is appropriately arranged on testing stand")
                    Human.compress_to(depth, fabbed_object) # not clear who compresses in their work?
                    mechanical_results += force_gauge.measure_force()
                
    summarize(shrinkage_results)
    summarize(mechanical_results)

@fedt_experiment
def test_software_tool():
    target_sphere = StlEditor.sphere(20)
    software_generated_mould = custom_modelling_tool.sphere(20)

    results = Measurements.empty()
    mould = Printer.slice_and_print(software_generated_mould)
    myco_material = "TODO best from before"
    for repetition in range(3):
        fabbed_object = Human.mould_mycomaterial(myco_material, mould)
        fabbed_object.grow() # this loop should unroll somehow so all the grow takes place at once...
        measurement_points = range(0,90,45)
        for x_axis_point in measurement_points:
            results += Calipers.measure_size(fabbed_object, x_axis_point)
        for y_axis_point in measurement_points:
            results += Calipers.measure_size(fabbed_object, y_axis_point)
        for z_axis_point in measurement_points:
            results += Calipers.measure_size(fabbed_object, z_axis_point)
                
    summarize(results)


if __name__ == "__main__":
    print(geometric_features())
