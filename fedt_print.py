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

def prep_cam():
    # this would be the place to edit settings into ini files (if required) and so forth
    return

def do_cam(stl_location, argdict={}, slicer=PRUSA):
    if slicer is PRUSA:
        slice_command = [PRUSA_SLICER_LOCATION,
                        '--load', 'config.ini']
        for keyval in argdict.items():
            slice_command.extend(list(keyval))
        slice_command.extend(['--export-gcode', stl_location])
        results = subprocess.check_output(slice_command)
    
        # the last line from Prusa Slicer is "Slicing result exported to ..."
        last_line = results.decode('utf-8').strip().split("\n")[-1]
        location = last_line.split(" exported to ")[1]

    elif slicer is BAMBU:
        slice_command = [BAMBU_PROCESS_SETTINGS_LOCATION,
                        '--debug 2',
                        '--load-settings "machine.json;process.json"',
                        stl_location]
        location = subprocess.check_output(slice_command)

    else:
        Exception("unknown slicer")

    return location

def fabricate(gcode_file):
    print("go print ", gcode_file)