from math import floor

from numpy import arange

from flowchart import FlowChart
from instruction import instruction
from iterators import Series, Parallel, include_last, shuffle
from measurement import BatchMeasurements, ImmediateMeasurements
from decorator import fedt_experiment
from flowchart_render import render_flowchart
from lib import *

def summarize(data):
    return "Oh wow, great data!"

class CustomProgram(DesignSoftware):
    @staticmethod
    def modify_design(knitfile: GeometryFile, feature_name: str, feature_value: str|int):
        knitfile.updateVersion(feature_name, feature_value, f"modify design: {knitfile.file_location} by setting {feature_name} to {feature_value}")
        return knitfile

    @staticmethod
    def knitcarve(knitfile: GeometryFile, specification: str):
        return CustomProgram.modify_design(knitfile, 'knitcarve', specification)

    @staticmethod
    def basicremove(knitfile: GeometryFile, specification: str):
        return CustomProgram.modify_design(knitfile, 'knitcarve', specification)
    
    @staticmethod
    def showToCrowdworker(obj: RealWorldObject, worker: int):
        # don't increment the version, because this isn't really postprocessing
        pass

@fedt_experiment
def compare_knit_textures_from_dbs():
    textures_from_db = []
    for i in Parallel(range(306)):
        texture = design("texture{}.ks".format(i), GeometryFile, {
            'tile': '60x60 (fill gaps with knit stitches)',
            'edge': '12-stitch checkered knit/purl to edges',
            'eyelets': 'eyelets at centre and end of each edge (8 total)'
        })
        textures_from_db.append(texture)

    knitted = []
    weights = BatchMeasurements.empty()
    for texture in Parallel(textures_from_db):
        single_knitted = KnittingMachine.knit(texture)
        knitted.append(single_knitted)
        weights += Scale.measure_weight(single_knitted)
    
    summarize(weights.get_all_data())

    dims = ImmediateMeasurements.empty()
    photos = ImmediateMeasurements.empty()

    for single_knitted in Parallel(knitted):
        Human.post_process(single_knitted, "lay on sandpaper")
        photos += Camera.take_picture(single_knitted) # this is the one that went into the opacity measurement, automatic (black pixel count). data was collected and used but not reported in the paper, only in a db later.
        dims += Calipers.measure_size(single_knitted, "unstretched length") # early samples measured with photos, then automatically with a reference object
        dims += Calipers.measure_size(single_knitted, "unstreteched width")
        for dimension in Series(['length', 'width']): # no concern about being plastic, but they did the following steps in consistent order anyway
            Human.post_process(single_knitted, f"hook onto the rig and load with 608g on {dimension}")
            photos += Camera.take_picture(single_knitted)
            dims += Calipers.measure_size(single_knitted, f"stretched {dimension}")

    summarize(dims.get_all_data())
    summarize(photos.get_all_data())

@fedt_experiment
def crowdsource_knitcarve_comparison():
    textures = [GeometryFile(f) for f in ['knitpurl_large.knit', 'knitpurl_small.knit',
                                            'twist_large.knit', 'twist_small.knit',
                                            'cable_large.knit', 'cable_small.knit',
                                            'lace_large.knit', 'lace_small.knit']]

    base = {}
    carve = {}
    naive = {}
    for texture in Parallel(textures):
        unaltered = KnittingMachine.knit(texture)
        base[texture] = unaltered
        for carve_level in Series(arange(1,5+include_last)):
            carved = CustomProgram.knitcarve(texture, "remove {}/5ths of a repetition".format(carve_level))
            naive_reduced = CustomProgram.basicremove(texture, "remove {}/5ths of a repetition".format(carve_level))
            carved_phys = KnittingMachine.knit(carved)
            naive_phys = KnittingMachine.knit(naive_reduced)
            if not carve_level in carve:
                carve[carve_level] = {}
            carve[carve_level][texture] = carved_phys
            if not carve_level in naive:
                naive[carve_level] = {}
            naive[carve_level][texture] = naive_phys
            
    
    workerpool_size = 200
    ratings = ImmediateMeasurements.empty()
    textures = list(base.keys())
    for worker in Parallel(arange(1,workerpool_size+include_last)):
        carve_level = worker % 5 + 1 # to avoid them noticing the fabric is shrinking
        comparator = naive if worker % 2 else carve
        for texture in Parallel(shuffle(textures)):
            for knit_object in shuffle([comparator[carve_level][texture], base[texture]]):
                CustomProgram.showToCrowdworker(knit_object, worker)
            for aspect in Series(['skew','size','number of whole repetitions','stretch','opacity']):
                ratings += Human.judge_something(comparator[carve_level][texture], "worker {} compare to {} based on {}".format(worker, base[texture], aspect))
            
    summarize(ratings.get_all_data())

if __name__ == "__main__":
    render_flowchart(compare_knit_textures_from_dbs)
    render_flowchart(crowdsource_knitcarve_comparison)