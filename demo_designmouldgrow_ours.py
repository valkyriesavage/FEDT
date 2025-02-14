from numpy import arange

from design import DesignSoftware
from flowchart_render import render_flowchart
from instruction import instruction
from iterators import Series, Parallel, include_last
from measurement import BatchMeasurements
from decorator import fedt_experiment
from lib import *

def compare(dataset1, dataset2):
    return "Hmmmm... I think these two are pretty same-same??"

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
    instruction("remove pathogens by pouring boiling water through strainer")
    instruction("bulk growth - 1 week")
    instruction("break up for forming growth - 3 days")

@fedt_experiment
def mushroom_types():
    pass
    # there was no digital fabrication element in this experiment, so I skipped implementing it

@fedt_experiment
def geometric_features():
    shrinkage_results = BatchMeasurements.empty()
    scanning_results = BatchMeasurements.empty()

    geometries = [GeometryFile(f) for f in ['ramps.stl', 'circular.stl', 'patterns.stl']]

    prep_materials() # how was this timed? just constant prepping in rotation, or?

    for geometry_file in Parallel(geometries):
        mould = Printer.fab(geometry_file)
        for myco_material in Series(['30% coffee inclusions', 'no inclusions']):
            fabbed_object = Human.post_process(mould, f"mould mycomaterial {myco_material}")
            Environment.wait_up_to_time_single(fabbed_object, num_weeks=1)
            instruction("remove the material from the mould")
            Environment.wait_up_to_time_single(fabbed_object, num_days=3)
            instruction("allow the material to dry in a 50-80C oven")
            Environment.wait_up_to_time_single(fabbed_object, num_weeks=7) # 1 day to 1 week
            shrinkage_results += Calipers.measure_size(fabbed_object, "important dimension")
            if geometry_file.file_location != 'ramps.stl':
                scan = Scanner.scan(fabbed_object)
                scanning_results += scan
            if geometry_file.file_location == 'circular.stl':
                oneoff_object = Human.post_process(mould, f"mould mycomaterial {myco_material}")
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

    shrinkage_results = BatchMeasurements.empty()
    mechanical_results = BatchMeasurements.empty()
    mould = Printer.fab(scaled_mould)

    fabbed_objects = []

    prep_materials()

    for myco_material in Series(['30% coffee inclusions', 'no inclusions']):
        for repetition in Series(range(4)):
            fabbed_object = Human.post_process(mould, f"mould mycomaterial {myco_material} ({repetition}th copy)")
            Environment.wait_up_to_time_single(fabbed_object, num_weeks=1)
            instruction("remove the material from the mould")
            Environment.wait_up_to_time_single(fabbed_object, num_days=3)
            instruction("allow the material to dry in a 50-80C oven")
            Environment.wait_up_to_time_single(fabbed_object, num_weeks=7) # 1 day to 1 week
            instruction("remove the object from the mould")
            shrinkage_results += Calipers.measure_size(fabbed_object, "x-axis")
            shrinkage_results += Calipers.measure_size(fabbed_object, "y-axis")
            shrinkage_results += Calipers.measure_size(fabbed_object, "z-axis")
            fabbed_objects.append(fabbed_object)
    
    for fabbed_object in Parallel(fabbed_objects):
        for repetition_mechanical in Series(range(5)):
            for depth in Series(arange(0,5+include_last,.5)):
                instruction("ensure fabbed object is appropriately arranged on testing stand")
                fabbed_object = Human.post_process(fabbed_object, f"compress the object to {str(depth)} ({repetition_mechanical}th time)")
                # not clear who/what does the compressing?
                mechanical_results += ForceGauge.measure_force(fabbed_object)
    
    summarize(shrinkage_results.get_all_data())
    summarize(mechanical_results.get_all_data())

@fedt_experiment
def test_software_tool():
    target_sphere = StlEditor.sphere(radius=20.)
    software_generated_mould = CustomModellingTool.sphere(radius=20.)

    prep_materials()

    results = BatchMeasurements.empty()
    mould = Printer.fab(software_generated_mould)
    myco_material = "30% coffee inclusions"
    for repetition in Parallel(arange(1,3+include_last)):
        fabbed_object = Human.post_process(mould, f"mould mycomaterial {myco_material}")
        fabbed_object.metadata.update({'repetition':repetition})
        Environment.wait_up_to_time_single(fabbed_object, num_weeks=1)
        instruction("remove the material from the mould")
        Environment.wait_up_to_time_single(fabbed_object, num_days=3)
        instruction("allow the material to dry in a 50-80C oven")
        Environment.wait_up_to_time_single(fabbed_object, num_weeks=7) # 1 day to 1 week
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
