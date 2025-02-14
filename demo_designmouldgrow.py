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

class CustomModellingTool(DesignSoftware):
    # call the custom modelling tool that they created
    @staticmethod
    def sphere(radius: float=10.) -> GeometryFile:
        return design('custom.stl', GeometryFile,
                      {'target_radius':radius},
                      f"use the custom tool to model a sphere with radius {radius}")
    
    @staticmethod
    def create_design(features: dict[str,object]) -> GeometryFile:
        return design('custom.stl', GeometryFile,
                      features,
                      f"use the custom tool to model {features}")

    @staticmethod
    def modify_design(design: GeometryFile,
                      feature_name: str, feature_value: str|int) -> GeometryFile:
        from control import MODE, Execute
        file_location = design.file_location
        if isinstance(MODE, Execute):
            file_location = input(f"What is the location of the modified geometry file?")
        
        design.updateVersion(feature_name, feature_value)
        design.file_location = file_location
        return design

def prep_materials():
    instruction("remove pathogens by pouring boiling water through materials in strainer")
    instruction("bulk growth - 1 week")
    instruction("break up for forming growth - 3 days")
    instruction("keep in the fridge as prepared material")
    instruction("remove from fridge to reactivate 1 day before beginning experiments")
    instruction("ensure you wear gloves")
    instruction("sterilize the prep space")

@fedt_experiment
def mushroom_types():
    pass
    # there was no digital fabrication element in this experiment, so I skipped implementing it

@fedt_experiment
def geometric_features():
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
        while not is_reasonable:
            Environment.wait_up_to_time_single(fabbed_object, num_days=1)
            instruction("look at or poke the sample")
            fabbed_object = Human.is_reasonable(fabbed_object)
            is_reasonable = fabbed_object.metadata["human reasonableness check"]
        instruction("allow the material to dry in a 50-80C oven")
        is_reasonable = False
        while not is_reasonable:
            Environment.wait_up_to_time_single(fabbed_object, num_days=1)
            instruction("look at or poke the sample")
            fabbed_object = Human.is_reasonable(fabbed_object)
            is_reasonable = fabbed_object.metadata["human reasonableness check"]
        instruction("material is ready when it is dry")
        print(fabbed_object)
        return fabbed_object

    shrinkage_results = BatchMeasurements.empty()
    scanning_results = BatchMeasurements.empty()

    geometries = [GeometryFile(f) for f in ['ramps.stl', 'circular.stl', 'patterns.stl']]

    prep_materials()

    for geometry_file in Parallel(geometries):
        mould = Printer.fab(geometry_file)
        for myco_material in Series(['30% coffee inclusions', 'no inclusions']):
            fabbed_object = grow_mycomaterial_from_mould(mould, myco_material)
            shrinkage_results += Calipers.measure_size(fabbed_object, "important dimension")
            if geometry_file.file_location != 'ramps.stl':
                scan = Scanner.scan(fabbed_object)
                scanning_results += scan
            if geometry_file.file_location == 'circular.stl':
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
    def grow_mycomaterial_from_mould(mould, myco_material):
        # helper as above
        return fabricate({'mould':mould, 'mycomaterial':myco_material}, f'prepare {myco_material} and mould as before')

    target_cube = StlEditor.cube((30,60,16))
    scaled_mould = StlEditor.cube((30, 60, 16), scale=1/.92)
    scaled_mould_all = StlEditor.modify_design(scaled_mould, 'number of cubes in file', '4')

    shrinkage_results = BatchMeasurements.empty()
    mechanical_results = BatchMeasurements.empty()
    mould = Printer.fab(scaled_mould_all)

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
    def grow_mycomaterial_from_mould(mould, myco_material):
        # helper as above
        return fabricate({'mould':mould, 'mycomaterial':myco_material}, f'prepare {myco_material} and mould as before')

    target_sphere = StlEditor.sphere(radius=20)
    software_generated_mould = CustomModellingTool.sphere(radius=20)

    prep_materials()

    results = BatchMeasurements.empty()
    mould = Printer.fab(software_generated_mould)
    myco_material = "30% coffee inclusions"
    for repetition in Parallel(arange(1,3+include_last)):
        fabbed_object = grow_mycomaterial_from_mould(mould, myco_material)
        fabbed_object.metadata.update({'repetition': repetition})
        measurement_points = arange(0,90+include_last,45)
        for x_axis_point in Parallel(measurement_points):
            results += Calipers.measure_size(fabbed_object, f"{x_axis_point} degrees along the x axis")
        for y_axis_point in Parallel(measurement_points):
            results += Calipers.measure_size(fabbed_object, f"{y_axis_point} degrees along the y axis")
        for z_axis_point in Parallel(measurement_points):
            results += Calipers.measure_size(fabbed_object, f"{z_axis_point} degrees along the z axis")

    summarize(results.get_all_data())


if __name__ == "__main__":
    render_flowchart(geometric_features)
    render_flowchart(mechanical_and_shrinkage_features)
    render_flowchart(test_software_tool)
