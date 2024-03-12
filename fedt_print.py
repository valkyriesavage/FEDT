from config import *

import os, sys, subprocess

sys.path.append(FREECAD_LOCATION)
import FreeCAD, Mesh, Draft

# Add label
def make_labelled_stl(geometry_function, label_string="L0", *geom_args, **geom_kwargs):
    App.newDocument()
    
    geometry_function(App, geom_args, geom_kwargs)
    
    # https://wiki.freecad.org/Draft_ShapeString_tutorial
    ss=Draft.make_shapestring(String=label_string, FontFile=FONT_LOCATION, Size=5.0, Tracking=0.0)
    plm=FreeCAD.Placement()
    plm.Base=FreeCAD.Vector(4.0, 4.0, side=20)
    plm.Rotation.Q=(0.0, 0.0, 0, 1.0)
    ss.Placement=plm
    ss.Support=None
    Draft.autogroup(ss)
    FreeCAD.ActiveDocument.recompute()
    
    App.ActiveDocument.addObject('Part::Extrusion','Extrude')
    f = App.ActiveDocument.getObject('Extrude')
    f.Base = App.ActiveDocument.getObject('ShapeString')
    f.DirMode = "Normal"
    f.DirLink = None
    f.LengthFwd = 5.000000000000000
    f.LengthRev = 0.000000000000000
    f.Solid = False
    f.Reversed = False
    f.Symmetric = False
    f.TaperAngle = 0.000000000000000
    f.TaperAngleRev = 0.000000000000000
    App.ActiveDocument.recompute()
    App.ActiveDocument.getObject('ShapeString').Visibility = False
    App.ActiveDocument.recompute()
    App.ActiveDocument.getObject('Extrude').Placement = App.Placement(App.Vector(2,2,0),App.Rotation(App.Vector(0,0,1),0))
    App.ActiveDocument.recompute()
    #FreeCAD.ActiveDocument.getObject('Extrude').Shape.exportStl('ext.stl')
    __objs__ = []
    __objs__.append(FreeCAD.ActiveDocument.getObject("Box"))
    __objs__.append(FreeCAD.ActiveDocument.getObject("Extrude"))
    stl_path = os.path.join(MODELS_OUTPUT_LOCATION, "expt_" + label_string + ".stl")
    Mesh.export(__objs__, stl_path)
    return stl_path

def slice_mesh(stl_location, argdict={}, slicer=PRUSA):
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

def execute_print(gcode_file):
    print("go print ", gcode_file)