import copy
from datetime import date
from typing import List
import datetime
from dateutil.relativedelta import relativedelta
import json
import math
import os
import random
import subprocess
import traceback
from zipfile import ZipFile

from flowchart import SUBJECT, VERB, OBJECT, SETTINGS, FABBED_SOMETHING
from instruction import instruction, note
from measurement import Measurement, BatchMeasurements
from fabricate import fabricate, RealWorldObject, FabricationDevice, CURRENT_UID
from design import design, GeometryFile, ConfigurationFile, CAMFile, DesignSoftware, \
                    ConfigSoftware, ToolpathSoftware, NotApplicableInThisWorkflowException
from decorator import explicit_checker

from config import *


NAME = "name"
TEST_VALUES = "test_values"
INSTRUCTION = "instruction"
DATA_TYPE = 'data type'
ARGNAME = 'argname'

CAD = 'CAD'
CAM = 'CAM'
FAB = 'fab'
POST_PROCESS = 'post-process'
INTERACTION = 'interaction'
TIME = 'time'

class Laser(ConfigSoftware, ToolpathSoftware, FabricationDevice):
    CUT_POWER = "cut_power"
    CUT_SPEED = "cut_speed"
    CUT_FREQUENCY = "frequency"
    MATERIAL = "material"
    THICKNESS = "thickness"
    FOCAL_HEIGHT_MM = "focal_height_mm"
    LASERDEVICE = "laserdevice"
    LASER_BED_MM = "laser_bed_mm"
    MAPPINGS = "mappings"

    LASERVARS = [CUT_POWER,CUT_SPEED,CUT_FREQUENCY,MATERIAL,THICKNESS,FOCAL_HEIGHT_MM]

    class SvgColor:
        RED = (255,0,0)
        GREEN = (0,255,0)
        BLUE = (0,0,255)

    default_laser_settings = {
        CUT_POWER: 100,
        CUT_SPEED: 100,
        CUT_FREQUENCY: 5000,
        MATERIAL: "Acrylic",
        THICKNESS: "3.0mm",
        FOCAL_HEIGHT_MM: "2.5mm",
        LASERDEVICE: "Epilog Helix",
        LASER_BED_MM: {
            'width': 24 * 2.54 * 10, # in mm
            'height': 18 * 2.54 * 10 # in mm
        },
        MAPPINGS: {SvgColor.RED: "cut", SvgColor.BLUE: "mark"}
    }

    generated_setting_names = {}

    @staticmethod
    def generate_setting_key(material=default_laser_settings[MATERIAL],
                             thickness=default_laser_settings[THICKNESS],
                             cut_power=default_laser_settings[CUT_POWER],
                             cut_speed=default_laser_settings[CUT_SPEED],
                             frequency=default_laser_settings[CUT_FREQUENCY]):
        return "{}.{}.{}.{}.{}".format(material,thickness,cut_power,cut_speed,frequency)

    @staticmethod
    def create_config(defaults=default_laser_settings,
                    cut_powers=[default_laser_settings[CUT_POWER]],
                    cut_speeds=[default_laser_settings[CUT_SPEED]],
                    frequencies=[default_laser_settings[CUT_FREQUENCY]],
                    materials=[default_laser_settings[MATERIAL]],
                    thicknesses=[default_laser_settings[THICKNESS]]):

        # the vcsettings file cannot be added from commandline...
        # so we need to do something like... build a huge one and ask the user to open manually to import.
        template_string = '''
    <?xml version="1.0" encoding="UTF-8"?>

    <linked-list version="0.0.0.0">
    <PowerSpeedFocusFrequencyProperty>
        <power>{cut_power}</power>
        <speed>{cut_speed}</speed>
        <focus>0.0</focus>
        <hideFocus>false</hideFocus>
        <frequency>{frequency}</frequency>
    </PowerSpeedFocusFrequencyProperty>
    </linked-list>'''

        temp_zf = 'fedt_generated.zip'

        generated_setting_names = {}

        with ZipFile(temp_zf, 'w') as myzip:
            for root, dirs, files in os.walk("./laser_settings_base/"):
                for name in files:
                    fpath = os.path.join(root,name)
                    myzip.write(fpath, fpath.split("laser_settings_base/")[1])
            for cut_power in cut_powers:
                for cut_speed in cut_speeds:
                    for frequency in frequencies:
                        for material in materials:
                            for thickness in thicknesses:
                                xmlstr = template_string.format(cut_power=cut_power,
                                                                cut_speed=cut_speed,
                                                                frequency=frequency)
                                cut_setting_fname = "fedt_{}.xml".format(hash("{}.{}.{}".format(cut_power,cut_speed,frequency)))
                                generated_setting_names[Laser.generate_setting_key(material,thickness,cut_power,cut_speed,frequency)] = cut_setting_fname
                                with open(cut_setting_fname, "w+") as f:
                                    f.write(xmlstr)
                                myzip.write(cut_setting_fname, "profiles/{}".format(cut_setting_fname))            
                                for material in materials:
                                    for thickness in thicknesses:
                                        myzip.write(cut_setting_fname, "laserprofiles/Epilog_32_Helix/{}/{}/{}".format(material,thickness,cut_setting_fname))
                                os.remove(cut_setting_fname)
            
        temp_vcsettings = temp_zf.replace('.zip','.vcsettings')
        os.rename(temp_zf, temp_vcsettings)

        instruction("please open Visicut and Options > Import Settings > " + temp_vcsettings)

        config_file = ConfigurationFile(temp_vcsettings)
        config_file.setting_names = generated_setting_names

        return config_file
    
    @staticmethod
    def modify_config(config: ConfigurationFile,
                      feature_name: str, feature_value: str|int) -> ConfigurationFile:
        # TODO: likely there is a way to do this, but modifying a config on the fly hasn't been needed
        # in any of the papers we looked at. starting from scratch seems fine.
        raise NotImplemented("just create a config from scratch; don't try to edit one")
    

    @staticmethod
    def create_toolpath(design: GeometryFile,
                        config: ConfigurationFile) -> CAMFile:
        raise NotApplicableInThisWorkflowException("Lasers run by Visicut don't create explicit toolpaths")
    
    @staticmethod
    def modify_toolpath(toolpath: CAMFile,
                        feature_name: str, feature_value: str|int) -> CAMFile:
        raise NotApplicableInThisWorkflowException("Lasers run by Visicut don't create explicit toolpaths")
        
    @staticmethod
    def do_fab(line_file: GeometryFile,
                colors_to_mappings = default_laser_settings[MAPPINGS],
                focal_height_mm = default_laser_settings[FOCAL_HEIGHT_MM],
                mapping_file=None):

        mapping_file_template = '''<?xml version="1.0" encoding="UTF-8"?>

<de.thomas__oster.visicut.model.mapping.MappingSet serialization="custom" version="0.0.0.0.0">
  <unserializable-parents/>
  <linked-list>
    <default/>
    <int>2</int>
    {mappings}
  </linked-list>
  <de.thomas__oster.visicut.model.mapping.MappingSet>
    <default>
      <description>A new created mapping</description>
      <name>custom FEDT stuff</name>
    </default>
  </de.thomas__oster.visicut.model.mapping.MappingSet>
</de.thomas__oster.visicut.model.mapping.MappingSet>
'''
        single_mapping_template = '''    <mapping>
      <a class="filters" serialization="custom">
        <unserializable-parents/>
        <linked-list>
          <default/>
          <int>1</int>
          <filter>
            <compare>false</compare>
            <inverted>false</inverted>
            <attribute>Color</attribute>
            <value class="awt-color">
              <red>{red}</red>
              <green>{green}</green>
              <blue>{blue}</blue>
              <alpha>255</alpha>
            </value>
          </filter>
        </linked-list>
        <filters>
          <default>
            <multiselectEnabled>false</multiselectEnabled>
          </default>
        </filters>
      </a>
      <b class="vectorProfile">
        <DPI>400.0</DPI>
        <description>This action was generated by FEDT</description>
        <name>{actionname}</name>
        <orderStrategy>INNER_FIRST</orderStrategy>
        <useOutline>false</useOutline>
        <isCut>true</isCut>
        <width>1.0</width>
      </b>
    </mapping>'''
        
        if mapping_file is None:
            temp_mapping_file = "fedt_mappings.xml"
            with open(temp_mapping_file, 'w') as map_file:
                mappings = ''
                for mapping in colors_to_mappings:
                    mappings += single_mapping_template.format(red=mapping[0],
                                                            green=mapping[1],
                                                            blue=mapping[2],
                                                            actionname=colors_to_mappings[mapping])
                map_file.write(mapping_file_template.format(mappings=mappings))
            mapping_file = temp_mapping_file

        instruction(f"ensure that the line colors in your file match the mapping {colors_to_mappings}")
        instruction(f"set the focal height of the laser to {focal_height_mm}")
        instruction("ensure visicut is open")

        # make the svg into the .plf file that they like
        temp_zf = 'spam.zip'
        with ZipFile(temp_zf, 'w') as myzip:
            myzip.write(line_file.file_location)
            myzip.write(mapping_file, "mappings.xml")
            myzip.write("transform.xml")
        temp_plf = temp_zf.replace('.zip','.plf')
        os.rename(temp_zf, temp_plf)
        cut_command = [VISICUT_LOCATION,
                    #'--laserdevice \"' + Laser.default_laser_settings[Laser.LASERDEVICE] + '\"',
                    '--execute',
                    os.path.join(os.getcwd(), temp_plf)]
        try:
            results = subprocess.check_output(cut_command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            # it probably didn't work! incredible. that's likely because we didn't get visicut in here right, or we're running offline.
            print("was not able to call visicut properly")
            print(exc.output)
            raise
        instruction("make sure your file doesn't overlap existing cuts")
        instruction("press 'execute', turn on extraction, and wait for the laser to complete its work")
        os.remove(temp_plf)
        try:
            os.remove(temp_mapping_file)
        except:
            # it might happen that the user supplied a mapping file and we never made a temp... in this case, just ignore it -\_(._.)_/-
            pass

    @staticmethod
    @explicit_checker
    def fab(line_file: GeometryFile,
            config_file: ConfigurationFile|None=None,
            toolpath: CAMFile|None=None, # always none for laser, since we don't generate an explicit CAMFile
            material: str = default_laser_settings[MATERIAL],
            thickness: str = default_laser_settings[THICKNESS],
            cut_speed: int = default_laser_settings[CUT_SPEED],
            cut_power: int = default_laser_settings[CUT_POWER],
            frequency: int = default_laser_settings[CUT_FREQUENCY],
            color_to_setting: SvgColor = SvgColor.GREEN,
            focal_height_mm: int = default_laser_settings[FOCAL_HEIGHT_MM],
            mapping_file: str = None,
            default_settings: dict = {},
            explicit_args = None,
            **kwargs
            ) -> RealWorldObject:

        user_chosen_settings = {}
        user_chosen_settings.update(kwargs)
        user_chosen_settings.update(explicit_args)

        all_settings = dict(Laser.default_laser_settings)
        all_settings.update(default_settings)
        all_settings.update(dict(user_chosen_settings))

        instruction(f"Ensure {all_settings['material']} is in the bed.")

        stored_values = {"line_file": line_file}
        stored_values.update(explicit_args)
        stored_values.update(**kwargs) # they might have arguments that aren't laser arguments

        from control import MODE, Execute
        if isinstance(MODE, Execute):
            # figure out if they set up a mapping request
            colors_to_mappings = Laser.default_laser_settings[Laser.MAPPINGS]
            if config_file is not None and config_file.setting_names:
                desired_setting = config_file.setting_names[Laser.generate_setting_key(default_settings['material'] if 'material' in default_settings else material,
                                                                                        default_settings['thickness'] if 'thickness' in default_settings else thickness,
                                                                                        default_settings['cut_power'] if 'cut_power' in default_settings else cut_power,
                                                                                        default_settings['cut_speed'] if 'cut_speed' in default_settings else cut_speed,
                                                                                        default_settings['frequency'] if 'frequency' in default_settings else frequency)]
                colors_to_mappings[color_to_setting] = desired_setting
            # actually call the laser
            Laser.do_fab(line_file,
                            mapping_file=all_settings['mapping_file'] if 'mapping_file' in all_settings else None,
                            focal_height_mm=all_settings[Laser.FOCAL_HEIGHT_MM])
        else:
            data = None
            if "setting_names" in user_chosen_settings:
                data = user_chosen_settings.pop("setting_names")
            instruction(f"Run the laser cutter and cut file {line_file.file_location} with settings {user_chosen_settings}")
            if data is not None:
                user_chosen_settings["setting_names"] = data


        # note(f"Run the laser cutter and cut file {line_file.file_location} with settings {user_chosen_settings}",
        #             fabbing = True,
        #             latex_details = {SUBJECT: Laser,
        #                                 VERB: 'cut',
        #                                 OBJECT: line_file,
        #                                 SETTINGS: all_settings,
        #                                 FABBED_SOMETHING: True})
        fabbed = fabricate(stored_values)

        if isinstance(MODE, Execute):
            print(f"object number {fabbed.uid} has been fabricated!")

        return fabbed

    @staticmethod    
    def describe():
        setup = '''We used a {machine} with bed size {bedsize} and Visicut. Our default settings were {defaults}.'''.format(
                **{
                    'machine': str(Laser.default_laser_settings[Laser.LASERDEVICE]),
                    'bedsize': str(Laser.default_laser_settings[Laser.LASER_BED_MM]),
                    'defaults': ', '.join([str(x) + ':' + str(y) for x, y in zip(Laser.default_laser_settings.keys(),
                                                                                 Laser.default_laser_settings.values())
                                                                              if x not in [Laser.LASERDEVICE, Laser.LASER_BED_MM]])
                })
        return setup

class SvgEditor(DesignSoftware):

    laser_bed = Laser.default_laser_settings[Laser.LASER_BED_MM]

    @staticmethod
    def design(specification: str=None, vars: dict={}) -> GeometryFile:
        if specification:
            instruction(f"Design an svg file like {specification}",
                    latex_details = {SUBJECT: "Authors",
                                        VERB: 'designed a line file',
                                        SETTINGS: specification})
        elif vars:
            instruction(f"Design an svg file like {vars}",
                    latex_details = {SUBJECT: "Authors",
                                        VERB: 'designed a line file',
                                        SETTINGS: vars})
        else:
            instruction("Get the svg file from the website.",
                    latex_details = {SUBJECT: "Authors",
                                        VERB: 'used a premade SVG'})
        location = "...."
        from control import MODE, Execute
        if isinstance(MODE, Execute):
            location = input("where is the svg?")
        designed = GeometryFile(location)
        designed.metadata.update(vars)
        if specification:
            designed.metadata.update({"specification": specification})
        return designed

    @staticmethod
    def draw_circle(draw, d, CAD_vars):
        radius = 10
        if 'radius' in CAD_vars:
            radius = CAD_vars['radius']
        d.append(draw.Circle(-40, -10, radius,
                fill='none', stroke_width=1, stroke='green'))
    
    @staticmethod
    def draw_line(draw, d, CAD_vars):
        length = 30
        stroke = 'blue'
        if 'length' in CAD_vars:
            length = CAD_vars['length']
        if 'stroke' in CAD_vars:
            stroke = CAD_vars['stroke']
        if 'rotate' in CAD_vars:
            d.append(draw.Line(-40, -10, -40, -10+length,
                    fill='none', stroke_width=1, stroke=stroke))
        else:
            d.append(draw.Line(-40, -10, -40+length, -10,
                    fill='none', stroke_width=1, stroke=stroke))
    
    @staticmethod
    def labelcentre(draw, d, label):
        d.append(draw.Text(x=-20, y=-20, fill='blue', text=label, font_size=10))

    @staticmethod
    @explicit_checker
    def build_geometry(geometry_function=None,
                       label_function=None,
                       label=CURRENT_UID, # FIXME this is hacky?? we should really have
                                          # a good way to find the id of the object without
                                          # assuming that it has the next ID
                       svg_location = "./expt_svgs/",
                       CAD_vars={},
                       explicit_args=None,
                       **kwargs) -> GeometryFile:
        
        svg_fullpath = svg_location
        from control import MODE, Execute
        if isinstance(MODE, Execute):
            import drawsvg as draw

            if geometry_function is None:
                geometry_function = SvgEditor.draw_circle

            d = draw.Drawing(SvgEditor.laser_bed['width'], SvgEditor.laser_bed['height'], origin='center', displayInline=False)
            
            SvgEditor.geometry_function = geometry_function
            geometry_function(draw, d, CAD_vars)
            if label_function is not None:
                label_function(draw, d, label)

            if not os.path.exists(svg_location):
                os.path.makedirs(svg_location)

            svg_fname = "expt_{}.svg".format(label if label else datetime.datetime.now().strftime("%Y%m%d%H%M%S-{}").format(random.randint(0,100)))
            svg_fullpath = os.path.join(svg_location, svg_fname)
            d.save_svg(svg_fullpath)

        stored_values = {}
        if explicit_args:
            for key, arg in explicit_args.items():
                if type(arg) == dict:
                    stored_values.update(arg)
                else:
                    stored_values[key] = arg
        if kwargs:
            for key, arg in kwargs.items():
                if type(arg) == dict:
                    stored_values.update(arg)
                else:
                    stored_values[key] = arg
            #stored_values.update(**kwargs) # they might have arguments that aren't laser arguments

        virtual_object = design(svg_fullpath, GeometryFile, stored_values)

        if isinstance(MODE, Execute):
            print(f"svg has been generated, and is available at {svg_fullpath}")
        else:
            instruction(f"generate svg file with function {geometry_function.__name__} {CAD_vars} {kwargs}",
                            latex_details = {SUBJECT: SvgEditor,
                                                VERB: 'generated a line file',
                                                SETTINGS: stored_values})

        return virtual_object
    
    @staticmethod
    def describe():
        setup = '''We used drawsvg to create our geometries.'''
        return setup

class Slicer(ToolpathSoftware):
    MATERIAL = 'material'
    TEMPERATURE = 'temperature'
    NOZZLE = 'nozzle'
    LAYER_HEIGHT = 'layer_height'
    INFILL_PATTERN = 'infill_pattern'
    INFILL_DENSITY = 'infill_density'
    WALL_THICKNESS = 'wall_thickness'
    SPEED = 'speed'
    BED_HEAT = 'bed_heating'

    default_slicer_settings = {
        MATERIAL: 'PLA',
        TEMPERATURE: '290',
        NOZZLE: '0.4',
        LAYER_HEIGHT: '0.4',
        INFILL_PATTERN: 'stars',
        INFILL_DENSITY: '50%',
        WALL_THICKNESS: '1.2',
        SPEED: '5000',
        BED_HEAT: '60'
    }

    @staticmethod
    def create_toolpath(design: GeometryFile,
                        config: ConfigurationFile|None=None,
                        **kwargs) -> CAMFile:
        
        if config is not None:
            instruction(f"slice {design.file_location} in the slicing software with configuration {config.file_location}")
                    # fabbing = True,
                    # latex_details = {SUBJECT: Slicer,
                    #                     VERB: 'sliced',
                    #                     OBJECT: design,
                    #                     SETTINGS: kwargs,
                    #                     FABBED_SOMETHING: False})
        else:
            instruction(f"slice {design.file_location} in the slicing software with settings {kwargs}")
        from control import MODE, Execute
        gcode_location = ''
        if isinstance(MODE, Execute):
            gcode_location = input("where is the sliced file located? ")
        
        kwargs.update({'config_file':config})
        gcode_file = CAMFile(gcode_location, kwargs)
        return gcode_file

    @staticmethod
    def describe():
        return '''A slicer software'''

class PrusaSlicer(Slicer):
    @staticmethod
    def create_toolpath(volume_file: GeometryFile,
                        config: ConfigurationFile|None=None,
                        temperature: str = Slicer.default_slicer_settings[Slicer.TEMPERATURE],
                        nozzle: str = Slicer.default_slicer_settings[Slicer.NOZZLE],
                        layer_height: str = Slicer.default_slicer_settings[Slicer.LAYER_HEIGHT],
                        infill_pattern: str = Slicer.default_slicer_settings[Slicer.INFILL_PATTERN],
                        infill_density: str = Slicer.default_slicer_settings[Slicer.INFILL_DENSITY],
                        wall_thickness: str = Slicer.default_slicer_settings[Slicer.WALL_THICKNESS],
                        material: str = Slicer.default_slicer_settings[Slicer.MATERIAL],
                        defaults: dict[str, object]={},
                        **kwargs) -> CAMFile:
        gcode_location = ''
        argdict = {
            '--layer-height': layer_height,
            '--nozzle-diameter': nozzle,
            '--temperature': temperature,
            '--fill-pattern': infill_pattern,
            '--fill-density': infill_density,
            '--perimeters': str(math.floor(float(wall_thickness.strip('mm'))/float(nozzle.strip('mm'))))
        }

        from control import MODE, Execute
        if isinstance(MODE, Execute):
            slice_command = [PRUSA_SLICER_LOCATION,
                            '--load', PRUSA_CONFIG_LOCATION]
            for keyval in argdict.items():
                slice_command.extend(list(str(t) for t in keyval))
            slice_command.extend(['--export-gcode', volume_file.file_location])
            slice_command.extend(['--output-filename-format', 'FEDT_[timestamp]_[input_filename_base].gcode'])
            print(slice_command)
            results = subprocess.check_output(slice_command)
        
            # the last line from Prusa Slicer is "Slicing result exported to ..."
            last_line = results.decode('utf-8').strip().split("\n")[-1]
            gcode_location = last_line.split(" exported to ")[1]

        design_bake = {'slicer': 'PrusaSlicer'}
        design_bake.update(argdict)
        gcode = design(gcode_location, CAMFile, design_bake, 'slice the file')

        if isinstance(MODE, Execute):
            print(f"gcode has been generated, and is available at {gcode_location}")

        return gcode

    @staticmethod      
    def describe():
        return '''Prusa Slicer'''

class JankyBambuSlicer(Slicer):
    @staticmethod
    def create_toolpath(volume_file: GeometryFile,
                        config: ConfigurationFile|None=None,
                temperature: str = Slicer.default_slicer_settings[Slicer.TEMPERATURE],
                nozzle: str = Slicer.default_slicer_settings[Slicer.NOZZLE],
                layer_height: str = Slicer.default_slicer_settings[Slicer.LAYER_HEIGHT],
                infill_pattern: str = Slicer.default_slicer_settings[Slicer.INFILL_PATTERN],
                infill_density: str = Slicer.default_slicer_settings[Slicer.INFILL_DENSITY],
                wall_thickness: str = Slicer.default_slicer_settings[Slicer.WALL_THICKNESS],
                material: str = Slicer.default_slicer_settings[Slicer.MATERIAL],
                **kwargs) -> CAMFile:
        gcode_location = ''
        argdict = {
            '--layer-height': layer_height,
            '--nozzle-diameter': nozzle,
            '--temperature': temperature,
            '--fill-pattern': infill_pattern,
            '--fill-density': infill_density,
            '--perimeters': str(math.floor(float(wall_thickness.strip('mm'))/float(nozzle.strip('mm'))))
        }

        from control import MODE, Execute
        if isinstance(MODE, Execute):
            slice_command = [PRUSA_SLICER_LOCATION,
                            '--load', 'bambu.ini']
            for keyval in argdict.items():
                slice_command.extend(list(str(t) for t in keyval))
            slice_command.extend(['--export-gcode', volume_file.file_location])
            slice_command.extend(['--output-filename-format', 'FEDT_[timestamp]_[input_filename_base].gcode'])
            print(slice_command)
            results = subprocess.check_output(slice_command)
        
            # the last line from Prusa Slicer is "Slicing result exported to ..."
            last_line = results.decode('utf-8').strip().split("\n")[-1]
            gcode_location = last_line.split(" exported to ")[1]

        design_bake = {'slicer': 'BambuSlicer'}
        design_bake.update(argdict)
        gcode = design(gcode_location, CAMFile, design_bake, 'slice the file')

        if isinstance(MODE, Execute):
            print(f"gcode has been generated, and is available at {gcode_location}")

        return gcode

    @staticmethod      
    def describe():
        return '''Prusa Slicer imitating Bambu Slicer'''

class BambuSlicer(Slicer):
    @staticmethod
    def create_toolpath(volume_file: GeometryFile,
                        config: ConfigurationFile|None=None,
                temperature: str = Slicer.default_slicer_settings[Slicer.TEMPERATURE], # unused
                nozzle: str = Slicer.default_slicer_settings[Slicer.NOZZLE], # used only in calc of walls
                layer_height: str = Slicer.default_slicer_settings[Slicer.LAYER_HEIGHT],
                infill_pattern: str = Slicer.default_slicer_settings[Slicer.INFILL_PATTERN],
                infill_density: str = Slicer.default_slicer_settings[Slicer.INFILL_DENSITY],
                wall_thickness: str = Slicer.default_slicer_settings[Slicer.WALL_THICKNESS],
                material: str = Slicer.default_slicer_settings[Slicer.MATERIAL], # unused
                **kwargs) -> CAMFile:
        argdict = {}
        gcode_location = ''
        # FIXME bambu studio is a huge pain for actually running on the command line. this... sort of works. but not quite.
        # see: extensive internet complaints.

        from control import MODE, Execute
        if isinstance(MODE, Execute):
            # first read and write all the arguments into the file
            process_json = {}
            with open('process.json') as f:
                process_json = json.loads(''.join(l for l in f.readlines()))
            process_json["infill_density"] = infill_density
            process_json["infill_pattern"] = infill_pattern
            process_json["layer_height"] = layer_height
            process_json["wall_loops"] = str(math.floor(float(wall_thickness)/float(nozzle)))
            generated_process_file = 'fedt_process.json'
            with open(generated_process_file, 'w+') as f:
                f.write(json.dumps(process_json))

            # then call the slicer
            slice_command = [BAMBU_SLICER_LOCATION,
                            f'--load-settings machine.json;{generated_process_file}',
                            '--slice', '2',
                            '--debug', '2',
                            '--export-3mf', 'output.3mf',
                            volume_file.file_location]
            print(' '.join(slice_command))
            gcode_location = subprocess.check_output(slice_command)

        design_bake = {'slicer': 'BambuSlicer'}
        design_bake.update(argdict)
        gcode = design(gcode_location, CAMFile, design_bake, 'slice the file')

        if isinstance(MODE, Execute):
            print(f"gcode has been generated, and is available at {gcode_location}")

        return gcode

    @staticmethod
    def describe():
        return '''Bambu Slicer'''
    
class JankyUltimakerSlicer(Slicer):
    @staticmethod
    def create_toolpath(volume_file: GeometryFile,
                        config: ConfigurationFile|None=None,
                temperature: str = Slicer.default_slicer_settings[Slicer.TEMPERATURE],
                nozzle: str = Slicer.default_slicer_settings[Slicer.NOZZLE],
                layer_height: str = Slicer.default_slicer_settings[Slicer.LAYER_HEIGHT],
                infill_pattern: str = Slicer.default_slicer_settings[Slicer.INFILL_PATTERN],
                infill_density: str = Slicer.default_slicer_settings[Slicer.INFILL_DENSITY],
                wall_thickness: str = Slicer.default_slicer_settings[Slicer.WALL_THICKNESS],
                material: str = Slicer.default_slicer_settings[Slicer.MATERIAL],
                **kwargs) -> CAMFile:
        gcode_location = ''
        argdict = {
            '--layer-height': layer_height,
            '--nozzle-diameter': nozzle,
            '--temperature': temperature,
            '--fill-pattern': infill_pattern,
            '--fill-density': infill_density,
            '--perimeters': str(math.floor(float(wall_thickness.strip('mm'))/float(nozzle.strip('mm'))))
        }

        from control import MODE, Execute
        if isinstance(MODE, Execute):
            slice_command = [PRUSA_SLICER_LOCATION,
                            '--load', 'ultimaker.ini']
            for keyval in argdict.items():
                slice_command.extend(list(str(t) for t in keyval))
            slice_command.extend(['--export-gcode', volume_file.file_location])
            slice_command.extend(['--output-filename-format', 'FEDT_[timestamp]_[input_filename_base].gcode'])
            print(slice_command)
            results = subprocess.check_output(slice_command)
        
            # the last line from Prusa Slicer is "Slicing result exported to ..."
            last_line = results.decode('utf-8').strip().split("\n")[-1]
            gcode_location = last_line.split(" exported to ")[1]

        design_bake = {'slicer': 'UltimakerSlicer'}
        design_bake.update(argdict)
        gcode = design(gcode_location, CAMFile, design_bake, 'slice the file')

        if isinstance(MODE, Execute):
            print(f"gcode has been generated, and is available at {gcode_location}")

        return gcode

    @staticmethod      
    def describe():
        return '''Ultimaker Slicer'''

class Printer(FabricationDevice):
    PRINTER = 'printer'
    SLICER = 'slicer'

    default_printer_settings = {
        PRINTER: 'Ultimaker 3',
        SLICER: PrusaSlicer
    }

    @staticmethod
    def print(gcode: CAMFile) -> RealWorldObject:
        input(f"load {gcode.file_location} onto the printer and hit print. enter when finished.")
    
    @staticmethod
    @explicit_checker
    def fab(input_geometry: GeometryFile|None=None,
            configuration: ConfigurationFile|None=None,
            toolpath: CAMFile|None=None,
            printer: str = default_printer_settings[PRINTER],
            slicer: Slicer = default_printer_settings[SLICER],
            material: str = Slicer.default_slicer_settings[Slicer.MATERIAL],
            temperature: str = Slicer.default_slicer_settings[Slicer.TEMPERATURE],
            nozzle: str = Slicer.default_slicer_settings[Slicer.NOZZLE],
            layer_height: str = Slicer.default_slicer_settings[Slicer.LAYER_HEIGHT],
            infill_pattern: str = Slicer.default_slicer_settings[Slicer.INFILL_PATTERN],
            infill_density: str = Slicer.default_slicer_settings[Slicer.INFILL_DENSITY],
            wall_thickness: str = Slicer.default_slicer_settings[Slicer.WALL_THICKNESS],
            defaults: dict = {},
            explicit_args = None,
            **kwargs
            ) -> RealWorldObject:
        
        if input_geometry is None and toolpath is None:
            raise Exception("You have to provide either a geometry or a CAM file to fab on this machine")

        from control import MODE, Execute

        stored_values = {}
        if explicit_args:
            stored_values.update(explicit_args)
        if kwargs:
            stored_values.update(**kwargs) # they might have arguments that aren't printer arguments
        
        all_values = dict.copy(Slicer.default_slicer_settings)
        all_values.update(Printer.default_printer_settings)
        all_values.update(defaults)
        all_values.update(stored_values)

        # if volume_file.file_location == '':
        #     instruction("Slice the file.",
        #                 latex_details = {SUBJECT: Slicer,
        #                                     VERB: 'sliced',
        #                                     OBJECT: volume_file,
        #                                     SETTINGS: stored_values})

        if toolpath is None:
            # TODO / FIXME : I would like to call this as **all_values, but that throws some kind of error for getting multiple
            # arguments of the same name. I can't figure out where it's coming from.
            toolpath = slicer.create_toolpath(input_geometry, configuration,                        
                                                temperature=all_values['temperature'],
                                                nozzle=all_values['nozzle'],
                                                layer_height=all_values['layer_height'],
                                                infill_pattern=all_values['infill_pattern'],
                                                infill_density=all_values['infill_density'],
                                                wall_thickness=all_values['wall_thickness'],
                                                material=all_values['material'])

        fabbed = fabricate(stored_values, "Run the printer")
        if isinstance(MODE, Execute):
            Printer.print(toolpath)
        # else:
        #     instruction(f"Run the printer, creating object #{fabbed.uid}",
        #             fabbing = True,
        #             latex_details = {SUBJECT: Printer,
        #                                 VERB: 'printed',
        #                                 OBJECT: volume_file,
        #                                 SETTINGS: all_values,
        #                                 FABBED_SOMETHING: True})
        # TODO / FIXME : we should either finish or cut the LaTeX stuff
        
        return fabbed
    
    @staticmethod  
    def describe(default_settings):
        if not 'machine' in default_settings:
            default_settings['machine'] = Printer.default_printer_settings[Printer.PRINTER]
        machine = default_settings.pop('machine')
        setup = '''We used a {machine}. Our default settings were {default_settings}.'''.format(
                **{
                    'machine': machine,
                    'default_settings': ', '.join([str(x) + ':' + str(y) for x, y in zip(default_settings.keys(),
                                                                                         default_settings.values())])
                })
        return setup

class StlEditor(DesignSoftware):

    @staticmethod
    def create_design(features: dict[str, object]) -> GeometryFile:
        if len(features.keys()) == 0:
            instruction("Get the STL file from the website.")
        else:
            instruction(f"Design an STL file with {features}")
        
        file_location = ''

        from control import MODE, Execute
        if isinstance(MODE, Execute):
            file_location = input("where is the stl file?")
        
        return design(file_location, GeometryFile, features)
    
    @staticmethod
    def modify_design(stl: GeometryFile, feature_name: str, feature_value: str) -> GeometryFile:
        instruction(f"Edit {stl.file_location} to set {feature_name} to {feature_value}")
        
        stl.updateVersion(feature_name, feature_value)

        from control import MODE, Execute
        if isinstance(MODE, Execute):
            file_location = input(f"What is the location of the modified stl?")
            stl.file_location = file_location

        return stl

    @staticmethod
    def cube(size: tuple=(1,1,1),
             scale: float=1.) -> GeometryFile:
        # TODO import freecad and all that jazz
        return design("cube.stl",GeometryFile,instr=f"create a cube with size {size}, scale {scale}")
    
    @staticmethod
    def sphere(radius: float=10.) -> GeometryFile:
        # TODO import freecad and all that jazz
        return design("sphere.stl",GeometryFile,instr=f"create a sphere with radius {radius}")

    @staticmethod
    def extract_profile(volume_file: GeometryFile,
                        location: tuple=(0,0,0,0,0,0)) -> GeometryFile:
        instruction(f'extract an svg profile of {volume_file.file_location} at location {location}')
        from control import MODE, Execute
        svg_location = ''
        if isinstance(MODE, Execute):
            svg_location = input("what is the location of the svg profile?")
        return design(svg_location,GeometryFile,{'profile extracted from': volume_file})
    
    @staticmethod
    def rotate(volume_file: GeometryFile,
               angle: float=0) -> GeometryFile:
        instruction(f"Rotate {volume_file.file_location} {angle} degrees")
        from control import MODE, Execute
        if isinstance(MODE, Execute):
            file_location = input(f"What is the location of the modified stl?")
            volume_file.file_location = file_location
        
        volume_file.updateVersion("rotated by", angle)
        return volume_file

    @staticmethod
    def describe():
        setup = '''We used FreeCAD to manipulate our STL files.'''
        return setup

class KnittingMachine(FabricationDevice):

    MACHINE = 'machine'
    YARN = 'yarn'
    TENSION = 'tension'
    MODE = 'knitting mode'
    NUM_COLORS = 'number of yarns/colors'

    default_knitting_settings = {
        MACHINE: 'Shima Seiki',
        YARN: 'tamm pettit',
        TENSION: '5',
        MODE: 'flat',
        NUM_COLORS: '1'
    }

    @staticmethod
    @explicit_checker
    def knit(knitfile: CAMFile,
             defaults: dict = {},
             explicit_args = None,
             **kwargs
             ) -> RealWorldObject:
        stored_values = {'fname':knitfile.file_location}
        if explicit_args:
            stored_values.update(explicit_args)
        if kwargs:
            stored_values.update(**kwargs) # they might have arguments that aren't machine arguments
        
        all_values = {}
        all_values.update(KnittingMachine.default_knitting_settings)
        all_values.update(defaults)
        all_values.update(stored_values)

        instruction(f'cast on the number of stitches required for {knitfile.file_location}')
        instruction(f'set up the machine carriages')

        return fabricate(all_values, f'load up {knitfile.file_location} and start the knitting machine with settings {all_values}')
    
    @staticmethod  
    def describe():
        setup = '''We used a {machine}. Our default settings were {defaults}.'''.format(
                **{
                    'machine': str(KnittingMachine.default_knitting_settings[KnittingMachine.MACHINE]),
                    'defaults': ', '.join([str(x) + ':' + str(y) for x, y in zip(KnittingMachine.default_knitting_settings.keys(),
                                                                                 KnittingMachine.default_knitting_settings.values())])
                })
        return setup

class KnitCompiler(DesignSoftware, ConfigSoftware):

    @staticmethod
    def design(specification: str=None) -> GeometryFile:
        if not specification:
            instruction("Get the knitting design from the website.")
        else:
            instruction(f"Design a knittable file like {specification}")
        
        file_location = ''

        from control import MODE, Execute
        if isinstance(MODE, Execute):
            file_location = input("where is the knitting file?")
        
        designed = GeometryFile(file_location)
        designed.metadata.update({"specification":specification})
        return designed
    
    @staticmethod
    def edit(knitfile: GeometryFile, specification: str) -> GeometryFile:
        instruction(f"Edit {knitfile.file_location} like {specification}")
        file_location = knitfile.file_location
        from control import MODE, Execute
        if isinstance(MODE, Execute):
            file_location = input(f"What is the location of the modified knitfile?")
        
        knitfile.updateVersion('hand-edit', specification)
        knitfile.file_location = file_location

        return knitfile

    @staticmethod
    def modify_feature_by_hand(knitfile:GeometryFile,
                               feature_name: str,
                               feature_value: str|float) -> GeometryFile:
        return KnitCompiler.edit(knitfile, f"set feature {feature_name} to {feature_value}")

    @staticmethod
    def describe():
        setup = '''We used KnitSpeak to manipulate our knitting files.'''
        return setup

class Multimeter:
    resistance = Measurement(
        name="resistance",
        description="The resistance of the object after charring.",
        procedure="""
            Use a multimeter to measure the resistance, with one probe
            at one end of the channel and one at the other.
            """,
        units="ohms",
        feature="1cm along the edge of the shape")
    
    current = Measurement(
        name="current",
        description="The current on the wire.",
        procedure="""
            Use a multimeter to measure the current, with one probe
            at one end of the channel and one at the other.
            """,
        units="amperes",
        feature="whole object")

    @staticmethod
    def measure_resistance(obj: RealWorldObject) -> BatchMeasurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Multimeter.resistance.procedure)
        return BatchMeasurements.single(obj, Multimeter.resistance)
    
    @staticmethod
    def measure_current(obj: RealWorldObject) -> BatchMeasurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Multimeter.current.procedure)
        return BatchMeasurements.single(obj, Multimeter.current)

    @staticmethod
    def lower_resistance(meas1: Measurement, meas2: Measurement):
        return False

class Stopwatch:
    elapsed_time = Measurement(
        name="time elapsed",
        description="The amount of time that elapsed while the thing happened",
        procedure="""
            Start the timer, do {}, stop the timer.
            """,
        units="seconds",
        feature="n/a")

    @staticmethod
    def measure_time(obj: RealWorldObject, instr: str) -> BatchMeasurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Stopwatch.elapsed_time.procedure.format(instr))
        return BatchMeasurements.single(obj, Stopwatch.elapsed_time.set_feature(instr))

class Timestamper:
    timestamp = Measurement(
        name="current time",
        description="What time it is right now",
        procedure="""
            Look at the clock or use a code module to record the current time.
            """,
        units="ms since epoch",
        feature="n/a")

    @staticmethod
    def get_ts(obj: RealWorldObject) -> BatchMeasurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Timestamper.timestamp.procedure)
        return BatchMeasurements.single(obj, Timestamper.timestamp)

class TrueFalser:
    truefalse = Measurement(
        name="true or false",
        description="The answer to a decision",
        procedure="""
            Decide if the answer to "{}" is true or false
            """,
        units="boolean",
        feature="n/a")

    @staticmethod
    def decide_truefalse(obj: RealWorldObject, feature: str=truefalse.procedure) -> BatchMeasurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(TrueFalser.truefalse.procedure.format(feature))
        return BatchMeasurements.single(obj, TrueFalser.truefalse.set_feature(feature))

class Calipers:
    length = Measurement(
        name="size",
        description="The dimension of the object along the given feature.",
        procedure="""
            Align the calipers around the {} of the object,
            then close them around it.
            """,
        units="mm",
        feature="most obvious object feature")

    @staticmethod
    def measure_size(obj: RealWorldObject,
                     dimension: str=length.feature) -> BatchMeasurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Calipers.length.procedure.format(dimension))
        return BatchMeasurements.single(obj, Calipers.length.set_feature(dimension))
    
class Protractor:
    angle = Measurement(
        name="angle",
        description="The angle of the object along the given feature.",
        procedure="""
            Align the protractor around the {} of the object,
            then read off the angle.
            """,
        units="degrees",
        feature="most obvious object feature")

    @staticmethod
    def measure_angle(obj: RealWorldObject,
                      dimension: str=angle.feature) -> BatchMeasurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Protractor.angle.procedure.format(dimension))
        return BatchMeasurements.single(obj, Protractor.angle.set_feature(dimension))

class Scanner:
    geometry_scan = Measurement(
        name="geometry scan",
        description="A full scan of the object's geometry, stored in a file.",
        procedure="""
            Place the object on the scanning table. Open the Einscan software and
            slowly move the scanner around the object. Export the scan file to
            .stl and save it.
            """,
        units="filename",
        feature="full object")

    @staticmethod
    def scan(obj: RealWorldObject) -> BatchMeasurements:
        instruction(f"Scan object #{obj.uid}.", header=True)
        instruction(Scanner.geometry_scan.procedure)
        return BatchMeasurements.single(obj, Scanner.geometry_scan)

class ForceGauge:
    force = Measurement(
        name="force",
        description="The force being exerted on (by?) the object.",
        procedure="""
            Mount the object in the force gauge setup.
            Stick the force gauge probe on top of the object.
            """,
        units="kg",
        feature="n/a")

    @staticmethod
    def measure_force(obj: RealWorldObject, feature: str=force.feature) -> BatchMeasurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(ForceGauge.force.procedure)
        return BatchMeasurements.single(obj, ForceGauge.force)
    
class Anemometer:
    airflow = Measurement(
        name="airspeed",
        description="The speed of airflow through the device.",
        procedure="""
            Hold the anemometer at an outflow of the object and actuate it.
            """,
        units="m/s",
        feature="output outlet")

    @staticmethod
    def measure_airflow(obj: RealWorldObject, feature: str=airflow.feature) -> BatchMeasurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Anemometer.airflow.procedure)
        return BatchMeasurements.single(obj, Anemometer.airflow.set_feature(feature))

class Camera:
    image = Measurement(
        name="photograph",
        description="A photograph of the object.",
        procedure="""
            Take a photo of the object showing {}.
            """,
        units="filename",
        feature="whole object")

    @staticmethod
    def take_picture(obj: RealWorldObject, feature: str=image.feature) -> BatchMeasurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Camera.image.procedure.format(feature))
        return BatchMeasurements.single(obj, Camera.image.set_feature(feature))

class PressureSensor:
    pressure = Measurement(
        name="pressure",
        description="The pressure of air in the device.",
        procedure="""
            Attach the sensor to the device at an air outlet.
            """,
        units="psi",
        feature="output outlet")

    @staticmethod
    def measure_pressure(obj: RealWorldObject, feature: str=pressure.feature) -> BatchMeasurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(PressureSensor.pressure.procedure)
        return BatchMeasurements.single(obj, PressureSensor.pressure.set_feature(feature))

class Scale:
    weight = Measurement(
        name="weight",
        description="The weight of the object.",
        procedure="""
            Set the object on the scale.
            """,
        units="g",
        feature="whole object")

    @staticmethod
    def measure_weight(obj: RealWorldObject, feature: str=weight.feature) -> BatchMeasurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Scale.weight.procedure)
        return BatchMeasurements.single(obj, Scale.weight.set_feature(feature))

class Human:
    # so multifunctional!
    judgement = Measurement(
        name="human judgement",
        description="A human's judgement on a feature of an object.",
        procedure="""
            Judge the object.
            """,
        units="n/a",
        feature="whole object")
    
    @staticmethod
    def judge_something(obj: RealWorldObject, feature: str=judgement.feature) -> BatchMeasurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Human.judgement.procedure + " : " + feature)
        return BatchMeasurements.single(obj, Human.judgement.set_feature(feature))

    @staticmethod
    def do_and_respond(instr: str,
                       question: str):
        instruction(instr)
        from control import MODE, Execute
        if isinstance(MODE, Execute):
            response = input(question)
            return response
        return question

    @staticmethod
    def post_process(obj: RealWorldObject,
                     action: str) -> RealWorldObject:
        obj.updateVersion("post-process", action, f"do {action} to object {obj}")
        return obj
    
    @staticmethod
    def is_reasonable(obj: RealWorldObject):
        answer = Human.do_and_respond(f"check if object #{obj.uid} looks reasonable",
                                        f"does object #{obj.uid} look reasonable [y/n]?")
        obj.metadata.update({"human reasonableness check": (answer == 'y')})
        return obj

    @staticmethod
    def describe():
        setup = '''We manually performed some steps.'''
        return setup

class User:

    @staticmethod
    def do(obj: RealWorldObject, instr: str, user_id: int):
        instr = f"User #{user_id} does {instr}"
        instruction(instr, who=Human)
        USER_DID = f"user did"
        if USER_DID in obj.metadata:
            instr = obj.metadata[USER_DID] + ", then " + instr
        obj.metadata.update({USER_DID: instr})
        return obj

    @staticmethod
    def describe():
        setup = '''Users did some interactions with the object.'''
        return setup

class Environment:
    # this is not the way I would prefer to write this...
    begin_time = date.today()

    @staticmethod
    def wait_up_to_time_multiple(fabbed_objects: List[RealWorldObject],
                                    num_days: int=0,
                                    num_weeks: int=0,
                                    num_months: int=0):

        instruction(f"begin a {num_days} day, {num_weeks} week, {num_months} month count from {Environment.begin_time}")
        from control import MODE, Execute
        if isinstance(MODE, Execute):
            while date.today() < (Environment.begin_time + relativedelta(days=num_days, weeks=num_weeks, months=num_months)):
                pass
            input("Enough time has passed; let's get on with it!")
        instruction(f"a total of {num_days} days, {num_weeks} weeks, {num_months} months has passed!")
        TIME = "time passed"
        for obj in fabbed_objects:
            obj.metadata.update({TIME : date.today() - Environment.begin_time})
        return fabbed_objects
    
    @staticmethod
    def wait_up_to_time_single(fabbed_object: RealWorldObject,
                                num_days: int=0,
                                num_weeks: int=0,
                                num_months: int=0):

        instruction(f"begin a {num_days} day, {num_weeks} week, {num_months} month count from {Environment.begin_time}")
        from control import MODE, Execute
        if isinstance(MODE, Execute):
            while date.today() < (Environment.begin_time + relativedelta(days=num_days, weeks=num_weeks, months=num_months)):
                pass
            input("Enough time has passed; let's get on with it!")
        instruction(f"a total of {num_days} days, {num_weeks} weeks, {num_months} months has passed!")
        TIME = "time passed"
        fabbed_object.metadata.update({TIME : date.today() - Environment.begin_time})
        return fabbed_object

    @staticmethod
    def describe():
        setup = '''We allowed nature to take its course.'''
        return setup