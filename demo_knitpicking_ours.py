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
        textures_from_db.append(GeometryFile("texture{}.knit".format(i)))

    knitted = []
    weights = BatchMeasurements.empty()
    for texture in Parallel(textures_from_db):
        CustomProgram.modify_design(texture, "tile", "60x60 (fill gaps with knit stitches)") # automatable or manual?
        CustomProgram.modify_design(texture, "edge", "12-stitch checkered knit/purl to edges")
        single_knitted = KnittingMachine.knit(texture)
        Human.post_process(single_knitted, "add eyelets to centre and end of each edge (8 eyelets)")
        knitted.append(single_knitted)
        weights += Scale.measure_weight(single_knitted)
    
    summarize(weights.get_all_data())

    dims = ImmediateMeasurements.empty()
    photos = ImmediateMeasurements.empty()

    for single_knitted in Parallel(knitted):
        Human.post_process(single_knitted, "lay on sandpaper")
        photos += Camera.take_picture(single_knitted)
        dims += Calipers.measure_size(single_knitted, "unstretched length")
        dims += Calipers.measure_size(single_knitted, "unstreteched width")
        Human.post_process(single_knitted, "hook onto the rig and load with 608g")
        photos += Camera.take_picture(single_knitted) # was there a photo of it stretched? I'm not clear on where opacity results are
        dims += Calipers.measure_size(single_knitted, "stretched length")
        dims += Calipers.measure_size(single_knitted, "stretched width")

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
        carve_level = worker % 5 + 1
        comparator = naive if worker % 2 else carve # do I understand assignments per this line and the one above it correctly?
        for texture in Parallel(shuffle(textures)):
            CustomProgram.showToCrowdworker(comparator[carve_level][texture], worker)
            CustomProgram.showToCrowdworker(base[texture], worker)
            for aspect in Series(['skew','size','number of whole repetitions','stretch','opacity']):
                ratings += Human.judge_something(comparator[carve_level][texture], "worker {} compare to {} based on {}".format(worker, base[texture], aspect))
            
    summarize(ratings.get_all_data())

if __name__ == "__main__":
    render_flowchart(compare_knit_textures_from_dbs)
    render_flowchart(crowdsource_knitcarve_comparison)