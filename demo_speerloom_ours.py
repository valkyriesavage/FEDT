from math import floor

from numpy import arange

from fabricate import NameableDevice
from flowchart import FlowChart
from instruction import instruction
from iterators import Series, Parallel, include_last, shuffle
from measurement import BatchMeasurements, ImmediateMeasurements
from decorator import fedt_experiment
from flowchart_render import render_flowchart
from lib import *

def summarize(data):
    return "Oh wow, great data!"

class SPEERLoomGUI(DesignSoftware, ConfigSoftware, ToolpathSoftware):
    def create_design(features: dict[str,object]) -> GeometryFile:
        return design('file.csv', GeometryFile, features, 'create the design in SPEERLoomGUI')

    @staticmethod
    def modify_design(design: GeometryFile,
                      feature_name: str, feature_value: str|int) -> GeometryFile:
        instruction(f"update {feature_name} to {feature_value} in SPEERLoomGUI")
        design.updateVersion(feature_name,feature_value)

    @staticmethod
    def create_config(defaults=dict[str,object]|None, **kwargs) -> ConfigurationFile:
        return design('file.csv', ConfigurationFile, defaults, 'create the configuration in SPEERLoomGUI')
    
    @staticmethod
    def modify_config(config: ConfigurationFile,
                      feature_name: str, feature_value: str|int) -> ConfigurationFile:
        instruction(f"update {feature_name} to {feature_value} in SPEERLoomGUI")
        config.updateVersion(feature_name,feature_value)

    @staticmethod
    def create_toolpath(design: GeometryFile,
                        config: ConfigurationFile, **kwargs) -> CAMFile:
        instruction("render the toolpath in SPEERLoomGUI")
        return design('file.serial', CAMFile, 'create the serial code in SPEERLoomGUI')
     
    @staticmethod
    def modify_toolpath(toolpath: CAMFile,
                        feature_name: str, feature_value: str|int) -> CAMFile:
        instruction(f"update {feature_name} to {feature_value} in SPEERLoomGUI")
        toolpath.updateVersion(feature_name,feature_value)


class SPEERLoom(FabricationDevice, metaclass=NameableDevice):
    uid = 'SPEERLOOM'
    @staticmethod
    def configure(settings: dict[str, object]):
        instruction(f"configure SPEERLoom like {settings}")

    @staticmethod
    @explicit_checker
    def fab(input_geometry: GeometryFile|None=None,
            configuration: ConfigurationFile|None=None,
            toolpath: CAMFile|None=None,
            default_settings: dict[str, object]|None=None,
            **kwargs) -> RealWorldObject:
        return fabricate({'geometry':input_geometry, 'configuration':configuration, 'toolpath':toolpath, 'non-default':kwargs},
                         'run the arduino code on the SPEERLoom')

    @staticmethod
    def create_object(non_default_settings: dict[str, object], instr: str|None) -> RealWorldObject:
        return fabricate(non_default_settings, instr)
    
    @staticmethod
    def describe(default_settings):
        return f"a custom-made SPEERLoom with settings {default_settings}"
    
class TC2Loom(FabricationDevice, metaclass=NameableDevice):
    uid = 'TC2LOOM'
    @staticmethod
    def configure(settings: dict[str, object]):
        instruction(f"configure loom like {settings}")
    
    @staticmethod
    @explicit_checker
    def fab(input_geometry: GeometryFile|None=None,
            configuration: ConfigurationFile|None=None,
            toolpath: CAMFile|None=None,
            default_settings: dict[str, object]|None=None,
            **kwargs) -> RealWorldObject:
        return fabricate({'geometry':input_geometry, 'configuration':configuration, 'toolpath':toolpath, 'non-default':kwargs},
                         'run the toolpath on the TC2Loom')
    
    @staticmethod
    def create_object(non_default_settings: dict[str, object], instr: str|None) -> RealWorldObject:
        return fabricate(non_default_settings, instr)
    
    @staticmethod
    def describe(default_settings):
        return f"an off-the-shelf TC2 Loom with settings {default_settings}"

class Jacq3GLoom(FabricationDevice, metaclass=NameableDevice):
    uid = 'JACQ3GLOOM'
    @staticmethod
    def configure(settings: dict[str, object]):
        instruction(f"configure loom like {settings}")

    @staticmethod
    @explicit_checker
    def fab(input_geometry: GeometryFile|None=None,
            configuration: ConfigurationFile|None=None,
            toolpath: CAMFile|None=None,
            default_settings: dict[str, object]|None=None,
            **kwargs) -> RealWorldObject:
        return fabricate({'geometry':input_geometry, 'configuration':configuration, 'toolpath':toolpath, 'non-default':kwargs},
                         'run the toolpath on the Jacq3G Loom')
    
    @staticmethod
    def create_object(non_default_settings: dict[str, object], instr: str|None) -> RealWorldObject:
        return fabricate(non_default_settings, instr)
    
    @staticmethod
    def describe(default_settings):
        return f"an off-the-shelf Jacq3G Loom with settings {default_settings}"  

class AlbaughLoom(FabricationDevice, metaclass=NameableDevice):
    uid = 'ALBAUGHLOOM'
    @staticmethod
    def configure(settings: dict[str, object]):
        instruction(f"configure loom like {settings}")

    @staticmethod
    @explicit_checker
    def fab(input_geometry: GeometryFile|None=None,
            configuration: ConfigurationFile|None=None,
            toolpath: CAMFile|None=None,
            default_settings: dict[str, object]|None=None,
            **kwargs) -> RealWorldObject:
        return fabricate({'geometry':input_geometry, 'configuration':configuration, 'toolpath':toolpath, 'non-default':kwargs},
                         'run the toolpath on the Albaugh Loom')
    
    @staticmethod
    def create_object(non_default_settings: dict[str, object], instr: str|None) -> RealWorldObject:
        return fabricate(non_default_settings, instr)
    
    @staticmethod
    def describe(default_settings):
        return f"a custom-made Albaugh Loom with settings {default_settings}"

class AshfordLoom(FabricationDevice, metaclass=NameableDevice):
    uid = 'ASHFORDLOOM'
    @staticmethod
    def configure(settings: dict[str, object]):
        instruction(f"configure loom like {settings}")

    @staticmethod
    @explicit_checker
    def fab(input_geometry: GeometryFile|None=None,
            configuration: ConfigurationFile|None=None,
            toolpath: CAMFile|None=None,
            default_settings: dict[str, object]|None=None,
            **kwargs) -> RealWorldObject:
        return fabricate({'geometry':input_geometry, 'configuration':configuration, 'toolpath':toolpath, 'non-default':kwargs},
                         'run the toolpath on the Ashford Loom')
    
    @staticmethod
    def create_object(non_default_settings: dict[str, object], instr: str|None) -> RealWorldObject:
        return fabricate(non_default_settings, instr)
    
    @staticmethod
    def describe(default_settings):
        return f"an off-the-shelf Ashford Loom with settings {default_settings}"

class Tensiometer:
    tension = Measurement(
        name="tension",
        description="The tension of a particular yarn.",
        procedure="""
            Insert the yarn to be measured into the device, read the display.
            """,
        units="grams",
        feature="final stage")

    @staticmethod
    def measure_tension(obj: RealWorldObject, feature: str=tension.feature) -> BatchMeasurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Tensiometer.tension.procedure)
        return BatchMeasurements.single(obj, Tensiometer.tension.set_feature(feature))


@fedt_experiment
def evaluate_weaving_quality():
    pattern = GeometryFile('basicpattern.csv') # how many patterns?
    all_objects = []

    # tension
    u1_tensions = BatchMeasurements.empty()
    u2_tensions = BatchMeasurements.empty()
    for loom in Parallel([SPEERLoom, AshfordLoom]):
        woven = loom.fab(pattern)
        all_objects.append(woven)
        for N in Series(range(10)): # what is N? what values can it take? is this series or parallel?
            Human.post_process(woven, f"set N to {N}")
            for stage in Series(["T1", "T2"]):
                u1_tensions += Tensiometer.measure_tension(woven, f"stage {stage}")
        for T2 in Series(range(10)): # what values did T2 take? is this series or parallel?
            Human.post_process(woven, f"set T2 to {T2}")
            u2_tensions += Tensiometer.measure_tension(woven, f"stage T3")
    
    summarize(u1_tensions.get_all_data())
    summarize(u2_tensions.get_all_data())

    # warp yarns and EPI
    quality = BatchMeasurements.empty()
    for loom in Parallel([SPEERLoom, Jacq3GLoom, AlbaughLoom, AshfordLoom, TC2Loom]):
        woven = loom.fab(pattern)
        all_objects.append(woven)
        quality += Human.judge_something(woven, "number of warp yarns")
        quality += Human.judge_something(woven, "ends per inch")

    summarize(quality.get_all_data())

@fedt_experiment
def evaluate_warping_efficiency():
    timings = ImmediateMeasurements.empty()
    for loom in Parallel([SPEERLoom, Jacq3GLoom, AlbaughLoom, AshfordLoom, TC2Loom]):
        if loom == TC2Loom:
            timings += Human.judge_something(loom, "how long it takes to set up")
        else:
            timings += Stopwatch.measure_time(loom, "set up warps")
    summarize(timings.get_all_data())

@fedt_experiment
def evaluate_weaving_efficiency():
    pattern = GeometryFile("basicpattern.csv") # how many patterns? does shedding time depend on pattern?
    timings = BatchMeasurements.empty()
    for loom in Parallel([SPEERLoom, Jacq3GLoom, AlbaughLoom, AshfordLoom, TC2Loom]):
        physical_object = loom.fab(pattern)
        timings += Stopwatch.measure_time(physical_object, "shed the loom")
    
    summarize(timings.get_all_data())

@fedt_experiment
def evaluate_cost_requirements():
    pass # not a digital fabrication experiment

if __name__ == "__main__":
    render_flowchart(evaluate_weaving_quality)
    render_flowchart(evaluate_warping_efficiency)
    render_flowchart(evaluate_weaving_efficiency)
    # render_flowchart(evaluate_cost_requirements)