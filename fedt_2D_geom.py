import os
import drawsvg as draw

from config import *
from fedt import *
import fedt_laser


def drawcircle(draw, d, CAD_vars):
    radius = CAD_vars['radius']
    d.append(draw.Circle(-40, -10, radius,
            fill='none', stroke_width=1, stroke='red'))

class FEDTdrawsvg:
    def __init__(self, laserdevice=fedt_laser.FEDTLaser()):
        self.laser_bed = laserdevice.laser_bed

    def build_geometry(self, geometry_function=drawcircle, label_function=None, label = "L0", svg_location = "./expt_svgs/", CAD_vars={}):
        d = draw.Drawing(self.laser_bed['width'], self.laser_bed['height'], origin='center', displayInline=False)
        
        self.geometry_function = geometry_function
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
    
    def __str__(self):
        setup = '''We used drawsvg to create our geometries.'''
        return setup

    def __repr__(self):
        return str(self)