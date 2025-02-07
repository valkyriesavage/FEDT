from math import floor
import random

from numpy import arange

from flowchart import FlowChart
from instruction import instruction
from iterators import Series, Parallel, include_last, shuffle
from measurement import BatchMeasurements, ImmediateMeasurements
from design import VolumeFile
from decorator import fedt_experiment
from flowchart_render import render_flowchart
from lib import *

def summarize(data):
    return "Oh wow, great data!"

class CustomProgram:
    def modify_knitdesign(knitfile: VirtualWorldObject, specification: str):
        instruction("modify design: {}".format(specification))
        knitfile.updateVersion("edit", specification)
        return knitfile

    def knitcarve(knitfile: VirtualWorldObject, specification: str):
        instruction("knitcarve: {}".format(specification))
        knitfile.updateVersion("KnitCarve", specification)
        return knitfile

    def basicremove(knitfile: VirtualWorldObject, specification: str):
        instruction("naive remove: {}".format(specification))
        knitfile.updateVersion("NaiveCarve", specification)
        return knitfile
    
    def showToCrowdworker(obj: RealWorldObject, worker: int):
        pass

@fedt_experiment
def compare_knit_textures_from_dbs():
    textures_from_db = []
    for i in Parallel(range(300)):
        textures_from_db.append(LineFile("texture{}.knit".format(i)))

    for texture in Parallel(textures_from_db):
        CustomProgram.modify_knitdesign(texture, "tile to 60x60, fill gaps with knit stitches")
        CustomProgram.modify_knitdesign(texture, "add 12-stitch checkered knit/purl to edges")

    knitted = []
    weights = BatchMeasurements.empty()
    for texture in Parallel(textures_from_db):
        single_knitted = KnittingMachine.knit(texture)
        Human.post_process(single_knitted, "add eyelets to centre and end of each edge (8 eyelets)")
        knitted.append(single_knitted)
        weights += Scale.measure_weight(single_knitted)
    
    summarize(weights.get_all_data())

    unstretched_dims = BatchMeasurements.empty()
    photos = BatchMeasurements.empty()

    for single_knitted in Parallel(knitted):
        Human.post_process(single_knitted, "lay on sandpaper")
        photos += Camera.take_picture(single_knitted)
        unstretched_dims += Calipers.measure_size(single_knitted, "length")
        unstretched_dims += Calipers.measure_size(single_knitted, "width")

    summarize(unstretched_dims.get_all_data())
    summarize(photos.get_all_data())

    stretched_dims = BatchMeasurements.empty()

    for single_knitted in Parallel(knitted):
        Human.post_process(single_knitted, "hook onto the rig and load with 608g")
        stretched_dims += Calipers.measure_size(single_knitted, "length")
        stretched_dims += Calipers.measure_size(single_knitted, "width")

    summarize(stretched_dims.get_all_data())

@fedt_experiment
def crowdsource_knitcarve_comparison():
    textures = [LineFile(f) for f in ['knitpurl_large.knit', 'knitpurl_small.knit',
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
            
    
    workerpool_size = 20 #200
    ratings = ImmediateMeasurements.empty()
    textures = list(base.keys())
    for worker in Parallel(arange(1,workerpool_size+include_last)):
        carve_level = worker % 5 + 1
        comparator = naive if worker % 2 else carve
        for texture in Parallel(shuffle(textures)):
            CustomProgram.showToCrowdworker(comparator[carve_level][texture], worker)
            CustomProgram.showToCrowdworker(base[texture], worker)
            for aspect in Series(['skew','size','number of whole repetitions','stretch','opacity']):
                ratings += Human.judge_something(comparator[carve_level][texture], "worker {} compare to {} based on {}".format(worker, base[texture], aspect))
            
    summarize(ratings.get_all_data())

if __name__ == "__main__":
    render_flowchart(compare_knit_textures_from_dbs)
    render_flowchart(crowdsource_knitcarve_comparison)