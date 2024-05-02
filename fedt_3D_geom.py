from config import *

import os, sys, subprocess
sys.path.append(FREECAD_LOCATION)
import FreeCAD, Mesh, Draft


def drawcube(self, *args, **kwargs):
    App.ActiveDocument.addObject("Part::Box","Box")
    App.ActiveDocument.ActiveObject.Label = "Cube"
    App.ActiveDocument.recompute()
    FreeCAD.ActiveDocument.getObject('Box').Width = side_length
    FreeCAD.ActiveDocument.getObject('Box').Length = side_length
    FreeCAD.ActiveDocument.getObject('Box').Height = side_length
    App.ActiveDocument.recompute()

class FEDTFreeCAD():
    CAD_tool_path = ''

    def __init__(self, CAD_tool_path):
        self.CAD_tool_path = CAD_tool_path

    # Add label
    def build_geometry(self, geometry_function=drawcube, label_function=None, label_string="L0", *geom_args, **geom_kwargs):
        App.newDocument()
        
        self.geometry_function = geometry_function
        geometry_function(App, *geom_args, **geom_kwargs)

        if label_function is not None:
            label_function(label_string)

        __objs__ = []
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj,"Shape"):
                __objs__.append(obj)
        stl_path = os.path.join(MODELS_OUTPUT_LOCATION, "expt_" + label_string + ".stl")
        Mesh.export(__objs__, stl_path)
        return stl_path
    
    def __str__(self):
        setup = '''We used {cad_tool} to generate our models.'''.format(
                **{
                    'cad_tool': str(os.path.split(self.CAD_tool_path)[-1])
                })
        return setup

    def __repr__(self):
        return str(self)