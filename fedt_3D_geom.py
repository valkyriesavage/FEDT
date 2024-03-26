from config import *

import os, sys, subprocess

sys.path.append(FREECAD_LOCATION)
import FreeCAD, Mesh, Draft

# Add label
def build_geometry(geometry_function, label_function=None, label_string="L0", *geom_args, **geom_kwargs):
    App.newDocument()
    
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