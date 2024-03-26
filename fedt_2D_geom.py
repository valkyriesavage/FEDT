import os
import drawsvg as draw

from config import *
from fedt import *

laser_bed = {
    'width': 24 * 2.54 * 10, # in mm
    'height': 18 * 2.54 * 10 # in mm
}

def build_geometry(geometry_function, label_function=None, label = "L0", svg_location = "./expt_svgs/", CAD_vars=[]):
    d = draw.Drawing(laser_bed['width'], laser_bed['height'], origin='center', displayInline=False)
    
    geometry_function(draw, d, CAD_vars)
    if label_function is not None:
        label_function(draw, d, label)

    if not os.path.exists(svg_location):
        os.path.makedirs(svg_location)

    svg_fname = "expt_" + label + ".svg"
    svg_fullpath = os.path.join(svg_location, svg_fname)
    d.save_svg(svg_fullpath)
    #d.savePng('example.png')
    return svg_fullpath