from numpy import arange

from flowchart_render import render_flowchart
from instruction import instruction
from iterators import Series, Parallel, include_last
from measurement import BatchMeasurements
from decorator import fedt_experiment
from lib import *

def compare(dataset1, dataset2):
    return "Hmmmm... I think these two are pretty same-same?"

def summarize(data):
    return "Oh wow, great data!"

class CustomModellingTool:
    # call the custom modelling tool that they created
    @staticmethod
    def sphere(radius: float=10.) -> VolumeFile:
        instruction(f"use the custom tool to model a sphere with radius {radius}")
        from control import MODE, Execute
        stl_location = 'custom.stl'
        if isinstance(MODE, Execute):
            stl_location = input("what is the location of the stl file generated?")
        return VolumeFile(stl_location)

def prep_materials():
    instruction("remove pathogens by pouring boiling water through materials in strainer")
    instruction("bulk growth - 1 week")
    instruction("break up for forming growth - 3 days")
    instruction("keep in the fridge as prepared material")
    instruction("remove from fridge to reactivate 1 day before beginning experiments")

def grow_mycomaterial_from_mould(mould, myco_material):
    instruction("sterilize the prep area")
    instruction("sterlize the mould with isopropyl alcohol")
    fabbed_object = Human.post_process(mould, f"mould mycomaterial {myco_material}")
    is_reasonable = False
    while not is_reasonable:
        Environment.wait_up_to_time_single(fabbed_object, num_days=1)
        instruction("look at or poke the sample")
        fabbed_object = Human.is_reasonable(fabbed_object)
        is_reasonable = fabbed_object.metadata["human reasonableness check"]
    instruction("remove the material from the mould for open growth")
    is_reasonable = False
    # while not is_reasonable:
    #     Environment.wait_up_to_time_single(fabbed_object, num_days=1)
    #     instruction("look at or poke the sample")
    #     fabbed_object = Human.is_reasonable(fabbed_object)
    #     is_reasonable = fabbed_object.metadata["human reasonableness check"]
    # instruction("allow the material to dry in a 50-80C oven")
    # is_reasonable = False
    # while not is_reasonable:
    #     Environment.wait_up_to_time_single(fabbed_object, num_days=1)
    #     instruction("look at or poke the sample")
    #     fabbed_object = Human.is_reasonable(fabbed_object)
    #     is_reasonable = fabbed_object.metadata["human reasonableness check"]
    instruction("material is ready when it is dry")
    print(fabbed_object)
    return fabbed_object

@fedt_experiment
def mushroom_types():
    pass
    # there was no digital fabrication element in this experiment, so I skipped implementing it

@fedt_experiment
def geometric_features():
    shrinkage_results = BatchMeasurements.empty()
    scanning_results = BatchMeasurements.empty()

    geometries = [VolumeFile(f) for f in ['ramps.stl', 'circular.stl', 'patterns.stl']]

    prep_materials()
    instruction("ensure you wear gloves")
    instruction("sterilize the prep space")

    for geometry_file in Parallel(geometries):
        mould = Printer.slice_and_print(geometry_file)
        for myco_material in Series(['30% coffee inclusions', 'no inclusions']):
            fabbed_object = grow_mycomaterial_from_mould(mould, myco_material)
            shrinkage_results += Calipers.measure_size(fabbed_object, "important dimension")
            if geometry_file.stl_location != 'ramps.stl':
                scan = Scanner.scan(fabbed_object)
                scanning_results += scan
            if geometry_file.stl_location == 'circular.stl':
                oneoff_object = grow_mycomaterial_from_mould(mould, myco_material)
                oneoff_object = Human.post_process(oneoff_object, 'glycerine treatment')
                shrinkage_results += Calipers.measure_size(oneoff_object, "important dimension")
                scanning_results += Scanner.scan(oneoff_object)
    
    # several derivative measurement operations are ignored here for simplicity; e.g., the extraction of 2D profiles from the scans

    shrinkage_results = shrinkage_results.get_all_data()
    scanning_results = scanning_results.get_all_data()
			
    summarize(shrinkage_results)
    summarize(scanning_results)


@fedt_experiment
def mechanical_and_shrinkage_features():
    target_cube = StlEditor.cube((30,60,16))
    scaled_mould = StlEditor.cube((30, 60, 16), scale=1/.92)
    scaled_mould_all = StlEditor.edit(scaled_mould, "include four cubes in one file")

    shrinkage_results = BatchMeasurements.empty()
    mechanical_results = BatchMeasurements.empty()
    mould = Printer.slice_and_print(scaled_mould_all)

    fabbed_objects = []

    prep_materials()

    for myco_material in Series(['30% coffee inclusions', 'no inclusions']):
        fabbed_object = grow_mycomaterial_from_mould(mould, myco_material)
        shrinkage_results += Calipers.measure_size(fabbed_object, "x-axis")
        shrinkage_results += Calipers.measure_size(fabbed_object, "y-axis")
        shrinkage_results += Calipers.measure_size(fabbed_object, "z-axis")
        fabbed_objects.append(fabbed_object)
    
    for fabbed_object in Parallel(fabbed_objects):
        for repetition_mechanical in Series(range(5)):
            instruction("ensure fabbed object is appropriately arranged on testing stand")
            for depth in Series(arange(0,5+include_last,.5)):
                fabbed_object = Human.post_process(fabbed_object, f"compress the object to {str(depth)} ({repetition_mechanical}th time)")
                mechanical_results += ForceGauge.measure_force(fabbed_object)
            for depth in Series(arange(5,0-include_last,-.5)):
                fabbed_object = Human.post_process(fabbed_object, f"release the object to {str(depth)} ({repetition_mechanical}th time)")
                mechanical_results += ForceGauge.measure_force(fabbed_object)
    
    summarize(shrinkage_results.get_all_data())
    summarize(mechanical_results.get_all_data())

@fedt_experiment
def test_software_tool():
    target_sphere = StlEditor.sphere(20) # radius
    software_generated_mould = CustomModellingTool.sphere(20)

    prep_materials()

    results = BatchMeasurements.empty()
    mould = Printer.slice_and_print(software_generated_mould)
    myco_material = "30% coffee inclusions"
    for repetition in Parallel(range(3)):
        fabbed_object = grow_mycomaterial_from_mould(mould, myco_material)
        fabbed_object.metadata.update({'repetition': repetition})
        measurement_points = range(0,90+include_last,45)
        for x_axis_point in measurement_points:
            results += Calipers.measure_size(fabbed_object, f"{x_axis_point} degrees along the x axis")
        for y_axis_point in measurement_points:
            results += Calipers.measure_size(fabbed_object, f"{y_axis_point} degrees along the y axis")
        for z_axis_point in measurement_points:
            results += Calipers.measure_size(fabbed_object, f"{z_axis_point} degrees along the z axis")

    summarize(results.get_all_data())

@fedt_experiment
def test_functions():
    prep_materials()

    results = BatchMeasurements.empty()
    mould = Printer.slice_and_print(VolumeFile("some.stl"))
    myco_material = "30% coffee inclusions"
    # fabbed_object = grow_mycomaterial_from_mould(mould, myco_material) # doesn't work
    fabbed_object = Human.post_process(mould, f"mould mycomaterial {myco_material}") # this code copy/pasted from function, it works.
    is_reasonable = False
    while not is_reasonable:
        Environment.wait_up_to_time_single(fabbed_object, num_days=1)
        instruction("look at or poke the sample")
        fabbed_object = Human.is_reasonable(fabbed_object)
        is_reasonable = fabbed_object.metadata["human reasonableness check"]
    instruction("remove the material from the mould for open growth")
    results += Calipers.measure_size(fabbed_object, f"0 degrees along the x axis")
    results += Calipers.measure_size(fabbed_object, f"0 degrees along the y axis")
    results += Calipers.measure_size(fabbed_object, f"0 degrees along the z axis")

    summarize(results.get_all_data())


if __name__ == "__main__":
    # render_flowchart(geometric_features)
    # render_flowchart(mechanical_and_shrinkage_features)
    # render_flowchart(test_software_tool)
    render_flowchart(test_functions)
