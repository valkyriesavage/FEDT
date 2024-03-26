from config import *

import subprocess

def prep_cam(CAM_variables):
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

def say_go_print(gcode_file):
    print("go print ", gcode_file)

def fabricate(gcode_file, printing_function=say_go_print):
    printing_function(gcode_file)