from config import *

import subprocess

PRUSA = "PRUSA"
PRUSA_SLICER_LOCATION = '/Applications/PrusaSlicer.app/Contents/MacOS/PrusaSlicer'
PRUSA_CONFIG_LOCATION = '/Users/vwn277/projects/fedtlike/FEDT/config.ini'

BAMBU = "BAMBU"
BAMBU_SLICER_LOCATION = '/Applications/BambuStudio.app/Contents/MacOS/BambuStudio'
BAMBU_MACHINE_SETTINGS_LOCATION = '/Users/vwn277/projects/fedtlike/FEDT/machine.json'
BAMBU_PROCESS_SETTINGS_LOCATION = '/Users/vwn277/projects/fedtlike/FEDT/process.json'

class FEDTPrinter:
    printer = 'Creality Ender 3'

    slicer=PRUSA
    slicer_location = PRUSA_SLICER_LOCATION
    config_location = PRUSA_CONFIG_LOCATION
    process_settings_location = ''

    def __init__(self, printer='Creality Ender 3', config_location=PRUSA_CONFIG_LOCATION, slicer=PRUSA, process_settings_location=''):
        self.printer = printer
        self.slicer = slicer
        self.config_location = config_location
        self.process_settings_location = process_settings_location

    def prep_cam(self, CAM_variables):
        # this would be the place to edit settings into ini files (if required) and so forth
        return

    def do_cam(self, stl_location, argdict={}):
        if self.slicer is PRUSA:
            slice_command = [self.slicer_location,
                            '--load', self.config_location]
            for keyval in argdict.items():
                slice_command.extend(list(keyval))
            slice_command.extend(['--export-gcode', stl_location])
            results = subprocess.check_output(slice_command)
        
            # the last line from Prusa Slicer is "Slicing result exported to ..."
            last_line = results.decode('utf-8').strip().split("\n")[-1]
            location = last_line.split(" exported to ")[1]

        elif self.slicer is BAMBU:
            self.prep_cam(argdict)
            slice_command = [self.slicer_location,
                            '--debug 2',
                            '--load-settings "%s;%s"'.format(self.config_location, self.process_settings_location),
                            stl_location]
            location = subprocess.check_output(slice_command)

        else:
            Exception("unknown slicer")

        return location

    def fabricate(self, gcode_file):
        print("go print ", gcode_file)

    def __str__(self):
        setup = '''We used a {machine} with {material}. For our slicer, we used {slicer}. XXX we also need to extract some interesting info from the config file XXX'''.format(
                **{
                    'machine': str(self.printer),
                    'material': str(self.config_location),
                    'slicer': str(self.slicer)
                })
        return setup

    def __repr__(self):
        return str(self)