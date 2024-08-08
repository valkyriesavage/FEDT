import math

from numpy import arange

from instruction import instruction
from iterators import Series, Parallel, Infinite, include_last
from measurement import Measurements
from fabricate import RealWorldObject
from decorator import fedt_experiment
from lib import *

def summarize(data):
    return "Oh wow, great data!"

def configure_for_electripop():
    Laser.default_laser_settings[Laser.MATERIAL] = 'mylar'
    Laser.default_laser_settings[Laser.CUT_SPEED] = 100
    Laser.default_laser_settings[Laser.CUT_POWER] = 5

class CustomSimulator:
    def runsimulation(*args, **kwargs):
        pass

@fedt_experiment
def optimize_simulation():
    configure_for_electripop()

    test_files = [LineFile(fname) for fname in ['compound_slits.svg', 'nested_flaps.svg', 'dragonfly.svg']]

    ground_truths = Measurements.empty()
    simmed = Measurements.empty()

    for f in Parallel(test_files):
        fabbed_object = Laser.fab(f) # not 100% clear what machine was used. they also mention vinyl cutters and scissors
        ground_truths += Scanner.scan(fabbed_object) # they did this manually and not with a scanner, but this shorthand seems ok
        for weight_of_be_exp in Parallel(arange(-3,6+include_last)):
            for weight_of_ee_exp in Parallel(arange(-1, 1+include_last, .2)):
                sim = VirtualWorldObject({'weight of bending energy': math.pow(10,weight_of_be_exp),
                                          'weight of electrical energy': math.pow(10, weight_of_ee_exp),
                                          'file': CustomSimulator.runsimulation(weight_of_be_exp,weight_of_ee_exp)})
                simmed += Scanner.scan(sim)
        
    summarize(ground_truths.get_data())
    summarize(simmed.get_data())

@fedt_experiment
def electrical_inflation():
    # not quite an experiment. they say that it takes "on the order of 10ms to fully saturate the mylar with charge"
    # but it's not clear if this was tested on more than one object or more than one repetition
    pass

@fedt_experiment
def physical_inflation():
    configure_for_electripop()

    fabbed_objects = [Laser.fab(LineFile(fname)) for fname in ['snowman.svg','christmas_tree.svg']]
    
    elapsed_times = Measurements.empty()
    for obj in Parallel(fabbed_objects):
        # were there repeitions? were there other objects? they mention "remarkably consistent", and imply that some others were tested
        elapsed_times += Stopwatch.measure_time(obj, "inflate to full")
    
    summarize(elapsed_times.get_data())
    

@fedt_experiment
def electrical_deflation():
    configure_for_electripop()
    snowman = Laser.fab(LineFile('snowman.svg'))

    current_measures = Measurements.empty()
    instruction('connect a 1kOhm resistor to the plate')
    for time_elapsing in Infinite(range(10000)):
        current = Multimeter.measure_current(snowman)
        timestamp = Timestamper.get_ts(snowman)
        current_measures += current
        current_measures += timestamp
        if current.get_data() == 0: # TODO how to do this in FEDT?
            # we are done
            break

    summarize(current_measures.get_data())

@fedt_experiment
def physical_deflation():
    # not 100% convinced this is an experiment, although it _is_ a measurement/characterization
    configure_for_electripop()
    snowman = Laser.fab(LineFile('snowman.svg'))
    elapsed_times = Measurements.empty()
    elapsed_times += Stopwatch.measure_time(snowman, "deflate fully")
    summarize(elapsed_times.get_data())

@fedt_experiment
def volumetric_change():
    # not 100% convinced this is an experiment, although it _is_ a measurement/characterization
    configure_for_electripop()
    snowman_virt = LineFile('snowman.svg')
    snowman_phys = Laser.fab(snowman_virt)
    volumes = Measurements.empty()
    volumes += Scanner.scan(snowman_phys)
    volumes += Scanner.scan(snowman_virt)
    summarize(volumes.get_data())

@fedt_experiment
def fabrication_time():
    # not 100% convinced this is an experiment, although it _is_ a measurement/characterization
    configure_for_electripop()
    snowman = LineFile('snowman.svg')
    elapsed_times = Measurements.empty()
    elapsed_times += Stopwatch.measure_time(snowman, "fabricate on the laser")
    summarize(elapsed_times.get_data())

@fedt_experiment
def geometric_accuracy():
    configure_for_electripop()

    test_files = [LineFile(fname) for fname in ['rose.svg', 'snowman.svg', 'christmas_tree.svg']]

    ground_truths = Measurements.empty()
    simmed = Measurements.empty()
    elapsed_times = Measurements.empty()

    for f in Parallel(test_files):
        fabbed_object = Laser.fab(f) # not 100% clear what machine was used. they also mention vinyl cutters and scissors
        ground_truths += Scanner.scan(fabbed_object) # they did this manually and not with a scanner, but this shorthand seems ok
        for sim_repetition in Parallel(range(100)):
            sim = VirtualWorldObject({'file': CustomSimulator.runsimulation(f)})
            simmed += Scanner.scan(sim)
            elapsed_times += Stopwatch.measure_time(sim, "converge simulation")
        
    summarize(ground_truths.get_data())
    summarize(simmed.get_data())
    summarize(elapsed_times.get_data())

@fedt_experiment
def user_experience():
    # not an experiment, but rather a study
    pass

if __name__ == "__main__":
    print(geometric_accuracy())
