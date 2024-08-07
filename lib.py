from datetime import date
from typing import List
import datetime
from dateutil.relativedelta import relativedelta
import drawsvg as draw
import os
import random
import subprocess
import time
from zipfile import ZipFile

from decision import decision
from instruction import instruction
from measurement import Measurement, Measurements
from fabricate import fabricate, RealWorldObject
from design import design, VirtualWorldObject, LineFile, VolumeFile, GCodeFile
from decorator import explicit_checker

from config import *


NAME = "name"
TEST_VALUES = "test_values"
INSTRUCTION = "instruction"
DATA_TYPE = 'data type'
ARGNAME = 'argname'
VERSIONS = 'versions'

CAD = 'CAD'
CAM = 'CAM'
FAB = 'fab'
POST_PROCESS = 'post-process'
INTERACTION = 'interaction'
TIME = 'time'

class Laser:
    CUT_POWER = "cut power"
    CUT_SPEED = "speed"
    CUT_FREQUENCY = "frequency"
    MATERIAL = "material"
    THICKNESS = "thickness"
    FOCAL_HEIGHT_MM = "focal height mm"
    LASERDEVICE = "laser device"
    LASER_BED = "laser bed size in mm"
    MAPPINGS = "mappings from colors to cut lines"

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
        LASER_BED: {
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
    def prep_cam(CAM_variables):
        cut_powers=[Laser.default_laser_settings[Laser.CUT_POWER]]
        cut_speeds=[Laser.default_laser_settings[Laser.CUT_SPEED]]
        frequencies=[Laser.default_laser_settings[Laser.CUT_FREQUENCY]]
        materials=[Laser.default_laser_settings[Laser.MATERIAL]]
        thicknesses=[Laser.default_laser_settings[Laser.THICKNESS]]

        for variable in CAM_variables:
            if variable[NAME] == Laser.CUT_POWER:
                cut_powers = variable[TEST_VALUES]
            if variable[NAME] == Laser.CUT_SPEED:
                cut_speeds = variable[TEST_VALUES]
            if variable[NAME] == Laser.CUT_FREQUENCY:
                frequencies = variable[TEST_VALUES]
            if variable[NAME] == Laser.MATERIAL:
                materials = variable[TEST_VALUES]
            if variable[NAME] == Laser.THICKNESS:
                thicknesses = variable[TEST_VALUES]

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

        return generated_setting_names
        
    @staticmethod
    def do_fab(line_file: LineFile,
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

        instruction(f"ensure that the line colors in your file match the line colors defined in {mapping_file}")
        instruction(f"set the focal height of the laser to {focal_height_mm}")

        # make the svg into the .plf file that they like
        temp_zf = 'spam.zip'
        with ZipFile(temp_zf, 'w') as myzip:
            myzip.write(line_file.svg_location)
            myzip.write(mapping_file, "mappings.xml")
            myzip.write("transform.xml")
        temp_plf = temp_zf.replace('.zip','.plf')
        os.rename(temp_zf, temp_plf)
        cut_command = [VISICUT_LOCATION,
                    '--laserdevice ' + Laser.default_laser_settings[Laser.LASERDEVICE],
                    '--execute',
                    temp_plf]
        try:
            results = subprocess.check_output(cut_command)
        except:
            # it probably didn't work! incredible. that's likely because we didn't get visicut in here right, or we're running offline.
            print("was not able to call visicut properly")
        os.remove(temp_plf)
        try:
            os.remove(temp_mapping_file)
        except:
            # it might happen that the user supplied a mapping file and we never made a temp... in this case, just ignore it -\_(._.)_/-
            pass

    @staticmethod
    @explicit_checker
    def fab(line_file: LineFile,
            setting_names: dict = {},
            material: str = default_laser_settings[MATERIAL],
            thickness: str = default_laser_settings[THICKNESS],
            cut_speed: int = default_laser_settings[CUT_SPEED],
            cut_power: int = default_laser_settings[CUT_POWER],
            frequency: int = default_laser_settings[CUT_FREQUENCY],
            color_to_setting: SvgColor = SvgColor.GREEN,
            focal_height_mm: int = default_laser_settings[FOCAL_HEIGHT_MM],
            mapping_file: str = None,
            explicit_args = None,
            **kwargs
            ) -> RealWorldObject:
    
        from control import MODE, Execute
        if isinstance(MODE, Execute):
            # figure out if they set up a mapping request
            colors_to_mappings = Laser.default_laser_settings[Laser.MAPPINGS]
            if setting_names:
                desired_setting = setting_names[Laser.generate_setting_key(material, thickness, cut_power, cut_speed, frequency)]
                colors_to_mappings[color_to_setting] = desired_setting
            # actually call the laser
            Laser.do_fab(line_file,
                            mapping_file=mapping_file,
                            focal_height_mm=focal_height_mm)
        instruction("Run the laser cutter.")

        stored_values = {"line_file": line_file}
        if explicit_args:
            stored_values.update(explicit_args)
        if kwargs:
            stored_values.update(**kwargs) # they might have arguments that aren't laser arguments

        fabbed = fabricate(stored_values)

        if isinstance(MODE, Execute):
            print(f"object number {fabbed.uid} has been fabricated!")

        return fabbed
    
    def __str__():
        setup = '''We used a {machine} with bed size {bedsize} and Visicut. Our default settings were {defaults}.'''.format(
                **{
                    'machine': str(Laser.default_laser_settings[Laser.LASERDEVICE]),
                    'bedsize': str(Laser.default_laser_settings[Laser.LASER_BED]),
                    'defaults': ', '.join([str(x) + ':' + str(y) for x, y in zip(Laser.default_laser_settings.keys(),
                                                                                 Laser.default_laser_settings.values())
                                                                              if x not in [Laser.LASERDEVICE, Laser.LASER_BED]])
                })
        return setup

    def __repr__(self):
        return str(self)

class SvgEditor:
    laser_bed = Laser.default_laser_settings[Laser.LASER_BED]

    @staticmethod
    def design(specification: str=None, vars: dict=None) -> LineFile:
        if specification:
            instruction(f"Design an svg file like {specification}")
        elif vars:
            instruction(f"Design an svg file like {vars}")
        else:
            instruction("Get the svg file from the website.")
        location = "...."
        from control import MODE, Execute
        if isinstance(MODE, Execute):
            location = input("where is the svg?")
        designed = LineFile(location)
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
    def labelcentre(draw, d, label):
        d.append(draw.Text(x=-20, y=-20, fill='blue', text=label, font_size=10))

    @staticmethod
    @explicit_checker
    def build_geometry(geometry_function=None,
                       label_function=None,
                       label=None,
                       svg_location = "./expt_svgs/",
                       CAD_vars={},
                       explicit_args=None,
                       **kwargs) -> LineFile:
        
        svg_fullpath = svg_location
        from control import MODE, Execute
        if isinstance(MODE, Execute):
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

        stored_values = {LineFile.LINE_FILE: svg_fullpath}
        if explicit_args:
            stored_values.update(explicit_args)
        if kwargs:
            stored_values.update(**kwargs) # they might have arguments that aren't printer arguments

        virtual_object = LineFile(stored_values)
        virtual_object.svg_location = svg_fullpath

        if isinstance(MODE, Execute):
            print(f"svg has been generated, and is available at {svg_location}")

        return virtual_object
    
    @staticmethod
    def __str__():
        setup = '''We used drawsvg to create our geometries.'''
        return setup

    def __repr__(self):
        return str(self)

class Slicer:
    MATERIAL = 'material'
    TEMPERATURE = 'temperature'
    NOZZLE = 'nozzle'
    LAYER_HEIGHT = 'layer height'
    INFILL_PATTERN = 'infill pattern'
    INFILL_DENSITY = 'infill density'
    WALL_THICKNESS = 'wall thickness'
    SPEED = 'speed'
    BED_HEAT = 'bed heating'

    default_slicer_settings = {
        MATERIAL: 'PLA',
        TEMPERATURE: '290 C',
        NOZZLE: '0.4mm',
        LAYER_HEIGHT: '0.4mm',
        INFILL_PATTERN: 'checkerboard',
        INFILL_DENSITY: '50%',
        WALL_THICKNESS: '1.2mm',
        SPEED: '5000',
        BED_HEAT: '60'
    }

    @staticmethod
    def slice(volume_file: VolumeFile,
              **kwargs) -> GCodeFile:

        instruction(f"slice {volume_file.stl_location} in the slicing software with settings {kwargs}")
        from control import MODE, Execute
        gcode_location = ''
        if isinstance(MODE, Execute):
            gcode_location = input("where is the sliced file located? ")
        
        gcode_file = design({VolumeFile.VOLUME_FILE: volume_file})
        gcode_file.metadata.update(kwargs)
        gcode_file.gcode_location = gcode_location
        return gcode_file

    class PrusaSlicer:
        @staticmethod
        def slice(volume_file: VolumeFile) -> GCodeFile:
            instruction(f"slice {volume_file.stl_location} in the slicing software")
            gcode_location = ''
            # TODO : map argdict into real commandline calls for prusa, add function args for this
            argdict = {}

            from control import MODE, Execute
            if isinstance(MODE, Execute):
                slice_command = [PRUSA_SLICER_LOCATION,
                                '--load', PRUSA_CONFIG_LOCATION]
                for keyval in argdict.items():
                    slice_command.extend(list(keyval))
                slice_command.extend(['--export-gcode', volume_file])
                results = subprocess.check_output(slice_command)
            
                # the last line from Prusa Slicer is "Slicing result exported to ..."
                last_line = results.decode('utf-8').strip().split("\n")[-1]
                gcode_location = last_line.split(" exported to ")[1]

            design_bake = {VolumeFile.VOLUME_FILE: volume_file}
            design_bake.update(argdict)
            gcode = design(design_bake)
            gcode.gcode_location = gcode_location

            if isinstance(MODE, Execute):
                print(f"gcode has been generated, and is available at {gcode_location}")

            return gcode
        
        def __str__():
            setup = '''We used Prusa Slicer'''

    class BambuSlicer:
        @staticmethod
        def slice(volume_file: VolumeFile) -> GCodeFile:
            argdict = {}
            gcode_location = ''
            # TODO prep_cam(argdict)
            # there is some kind of processing that needs to happen here to encode the arguments into files
            # because Bambu does not take commandline arguments

            from control import MODE, Execute
            if isinstance(MODE, Execute):
                slice_command = [BAMBU_SLICER_LOCATION,
                                '--debug 2',
                                '--load-settings "{BAMBU_MACHINE_SETTINGS_LOCATION};{BAMBU_PROCESS_SETTINGS_LOCATION}"',
                                volume_file]
                gcode_location = subprocess.check_output(slice_command)

            design_bake = {VolumeFile.VOLUME_FILE: volume_file}
            design_bake.update(argdict)
            gcode = design(design_bake)
            gcode.gcode_location = gcode_location

            if isinstance(MODE, Execute):
                print(f"gcode has been generated, and is available at {gcode_location}")

            return gcode
        
        def __str__():
            setup = '''We used Bambu Slicer'''
        
    def __str__():
        setup = '''We used a slicer software'''

    def __repr__(self):
        return str(self)

class Printer:
    PRINTER = 'printer'
    SLICER = 'slicer'

    default_printer_settings = {
        PRINTER: 'Ultimaker 3',
        SLICER: Slicer.PrusaSlicer
    }

    @staticmethod
    def print(gcode: GCodeFile) -> RealWorldObject:
        # TODO implement me!
        obj = fabricate(gcode.metadata, "print the object")
        return obj
    
    @staticmethod
    @explicit_checker
    def slice_and_print(volume_file: VolumeFile,
                        printer: str = default_printer_settings[PRINTER],
                        material: str = Slicer.default_slicer_settings[Slicer.MATERIAL],
                        temperature: str = Slicer.default_slicer_settings[Slicer.TEMPERATURE],
                        nozzle: str = Slicer.default_slicer_settings[Slicer.NOZZLE],
                        layer_height: str = Slicer.default_slicer_settings[Slicer.LAYER_HEIGHT],
                        infill_pattern: str = Slicer.default_slicer_settings[Slicer.INFILL_PATTERN],
                        infill_density: str = Slicer.default_slicer_settings[Slicer.INFILL_DENSITY],
                        wall_thickness: str = Slicer.default_slicer_settings[Slicer.WALL_THICKNESS],
                        slicer: Slicer = default_printer_settings[SLICER],
                        explicit_args = None,
                        **kwargs
                        ) -> RealWorldObject:

        from control import MODE, Execute

        gcode = slicer.slice(volume_file)
        if isinstance(MODE, Execute):
            # actually call the printer
            Printer.print(gcode)
        instruction("Slice the file.")
        instruction("Run the printer.")

        stored_values = {GCodeFile.GCODE_FILE: gcode}
        if explicit_args:
            stored_values.update(explicit_args)
        if kwargs:
            stored_values.update(**kwargs) # they might have arguments that aren't printer arguments

        fabbed =  fabricate(stored_values)

        if isinstance(MODE, Execute):
            print(f"object #{fabbed.uid} has been fabricated!")
        
        return fabbed
    
    def __str__():
        setup = '''We used a {machine}, which we controlled through {slicer}. Our default settings were {defaults}.'''.format(
                **{
                    'machine': str(Printer.default_printer_settings[Printer.PRINTER]),
                    'bedsize': str(Printer.default_printer_settings[Printer.SLICER]),
                    'defaults': ', '.join([str(x) + ':' + str(y) for x, y in zip(Slicer.default_slicer_settings.keys(),
                                                                                 Slicer.default_slicer_settings.values())])
                })
        return setup

    def __repr__(self):
        return str(self)

class StlEditor:

    @staticmethod
    def design(specification: str=None) -> VolumeFile:
        if not specification:
            instruction("Get the stl file from the website.")
        else:
            instruction(f"Design an STL file like {specification}")
        
        stl_location = ''

        from control import MODE, Execute
        if isinstance(MODE, Execute):
            stl_location = input("where is the stl file?")
        
        designed = VolumeFile(stl_location)
        designed.metadata.update({"specification":specification})
        return designed
    
    @staticmethod
    def edit(stl: VolumeFile, specification: str) -> VolumeFile:
        instruction(f"Edit {stl.stl_location} like {specification}")
        stl_location = stl.stl_location
        from control import MODE, Execute
        if isinstance(MODE, Execute):
            stl_location = input(f"What is the location of the modified stl?")
        HAND_EDIT = "hand-edited"
        if HAND_EDIT in stl.metadata:
            specification = stl.metadata[HAND_EDIT] + ", then " + specification

        versions = []
        if VERSIONS in stl.metadata:
            versions = stl.metadata[VERSIONS]
            versions.append(stl)
        new_obj = design(stl.metadata)
        new_obj.stl_location = stl_location
        new_obj.metadata.update({VERSIONS: versions, HAND_EDIT: specification})

        return new_obj

    @staticmethod
    def cube(size: tuple=(1,1,1),
             scale: float=1.) -> VolumeFile:
        # TODO import freecad and all that jazz
        return VolumeFile("")
    
    @staticmethod
    def sphere(radius: float=10.) -> VolumeFile:
        # TODO import freecad and all that jazz
        return VolumeFile("")

    @staticmethod
    def extract_profile(volume_file: VolumeFile,
                        location: tuple=(0,0,0,0,0,0)) -> LineFile:
        instruction(f'extract an svg profile of {volume_file.stl_location} at location {location}')
        from control import MODE, Execute
        svg_location = ''
        if isinstance(MODE, Execute):
            print(f'extract an svg profile of {volume_file.stl_location} at location {location}')
            svg_location = input("what is the location of the svg profile?")
        return LineFile(svg_location)
    
    @staticmethod
    def rotate(volume_file: VolumeFile,
               angle: float=0) -> VolumeFile:
        instruction(f'rotate the object {volume_file.stl_location} {angle} degrees')
        from control import MODE, Execute
        stl_location = volume_file.stl_location
        if isinstance(MODE, Execute):
            stl_location = input("what is the location of the rotated stl?")
            volume_file.stl_location = stl_location
        volume_file.metadata.update({'rotation angle':angle})
        return volume_file
            
    @staticmethod
    def add_bent_path(volume_file: VolumeFile,
                        bend_radius: float=0) -> VolumeFile:
        instruction(f'add a bent path of radius {bend_radius} to the object {volume_file.stl_location}')
        from control import MODE, Execute
        stl_location = volume_file.stl_location
        if isinstance(MODE, Execute):
            stl_location = input("what is the location of the stl with the bent path added?")
            volume_file.stl_location = stl_location
        volume_file.metadata.update({'input bend radius':bend_radius})
        return volume_file

    @staticmethod
    def modify_feature_by_hand(volume_file:VolumeFile,
                               feature_name: str,
                               feature_value: str|float) -> VolumeFile:
        instruction(f'modify the file {volume_file.stl_location} to have feature {feature_name} with value {feature_value}')
        from control import MODE, Execute
        stl_location = volume_file.stl_location
        if isinstance(MODE, Execute):
            stl_location = input(f"what is the location of the modified stl with {feature_name} value {feature_value}?")
            volume_file.stl_location = stl_location
        volume_file.metadata.update({feature_name: feature_value})
        return volume_file
    
    @staticmethod
    def sample_convex(volume_file: VolumeFile) -> LineFile:
        instruction(f'extract an svg profile of the convex parts of {volume_file.stl_location}')
        from control import MODE, Execute
        svg_location = ''
        if isinstance(MODE, Execute):
            svg_location = input("what is the location of the svg profile?")
        return LineFile(svg_location)
    
    @staticmethod
    def sample_concave(volume_file: VolumeFile) -> LineFile:
        instruction(f'extract an svg profile of the concave parts of {volume_file.stl_location}')
        from control import MODE, Execute
        svg_location = ''
        if isinstance(MODE, Execute):
            svg_location = input("what is the location of the svg profile?")
        return LineFile(svg_location)

    @staticmethod
    def __str__():
        setup = '''We used FreeCAD to manipulate our STL files.'''
        return setup

    def __repr__(self):
        return str(self)

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
    def measure_resistance(obj: RealWorldObject) -> Measurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Multimeter.resistance.procedure)
        return Measurements.single(obj, Multimeter.resistance)
    
    @staticmethod
    def measure_current(obj: RealWorldObject) -> Measurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Multimeter.current.procedure)
        return Measurements.single(obj, Multimeter.current)

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
        units="s",
        feature="n/a")

    @staticmethod
    def measure_time(obj: RealWorldObject, instr: str) -> Measurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Stopwatch.elapsed_time.procedure.format(instr))
        return Measurements.single(obj, Stopwatch.elapsed_time)

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
                     dimension: str=length.feature) -> Measurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Calipers.length.procedure.format(dimension))
        measurement = Calipers.length
        if measurement.feature != dimension:
            measurement = measurement.set_feature(dimension)
        return Measurements.single(obj, measurement)
    
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
                      dimension: str=angle.feature) -> Measurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Protractor.angle.procedure.format(dimension))
        measurement = Protractor.angle
        if measurement.feature != dimension:
            measurement = measurement.set_feature(dimension)
        return Measurements.single(obj, measurement)

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
    def scan(obj: RealWorldObject) -> Measurements:
        instruction(f"Scan object #{obj.uid}.", header=True)
        instruction(Scanner.geometry_scan.procedure)
        return Measurements.single(obj, Scanner.geometry_scan)

class ForceGauge:
    force = Measurement(
        name="force",
        description="The force being exerted on (by?) the object.",
        procedure="""
            Mount the object in the force gauge cage.
            Stick the force gauge probe on top of the object.
            """,
        units="kg",
        feature="n/a")

    @staticmethod
    def measure_force(obj: RealWorldObject) -> Measurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(ForceGauge.force.procedure)
        return Measurements.single(obj, ForceGauge.force)
    
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
    def measure_airflow(obj: RealWorldObject, feature: str=airflow.feature) -> Measurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Anemometer.airflow.procedure)
        return Measurements.single(obj, Anemometer.airflow.set_feature(feature))

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
    def take_picture(obj: RealWorldObject, feature: str=image.feature) -> Measurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Camera.image.procedure.format(feature))
        return Measurements.single(obj, Camera.image.set_feature(feature))

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
    def measure_pressure(obj: RealWorldObject, feature: str=pressure.feature) -> Measurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(PressureSensor.pressure.procedure)
        return Measurements.single(obj, PressureSensor.pressure.set_feature(feature))

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
    def measure_weight(obj: RealWorldObject, feature: str=weight.feature) -> Measurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Scale.weight.procedure)
        return Measurements.single(obj, Scale.weight.set_feature(feature))

class Human:
    # so multifunctional!

    @staticmethod
    def do_and_respond(instr: str,
                       question: str):
        instruction(instr)
        from control import MODE, Execute
        if isinstance(MODE, Execute):
            return input(question)
        return question

    @staticmethod
    def post_process(obj: RealWorldObject,
                     action: str) -> RealWorldObject:
        instruction("do " + action + f" to object #{obj.uid}")
        versions = []
        if VERSIONS in obj.metadata:
            versions = obj.metadata[VERSIONS]
            versions.append(obj)
        new_obj = fabricate(obj.metadata)
        new_obj.metadata.update({VERSIONS: versions, "post-process": action})
        return new_obj
    
    @staticmethod
    def mould_mycomaterial(obj: RealWorldObject,
                            type: str) -> RealWorldObject:
        instruction(f"mould {type} mycomaterial from mould #{obj.uid}")
        obj.metadata.update({"mycomaterial":type})
        return obj
    
    @staticmethod
    def is_reasonable(obj: RealWorldObject):
        if decision(f"does object #{obj.uid} look reasonable?"):
            obj.metadata.update({"human reasonableness check": True}) # TODO no idea how to encode this
        else:
            obj.metadata.update({"human reasonableness check": False})
        return obj

    @staticmethod
    def __str__():
        # TODO how to track which ones?
        setup = '''We manually performed some steps. ???? HOW TO TRACK WHICH ONES ????'''
        return setup

    def __repr__(self):
        return str(self)

class User:

    @staticmethod
    def do(obj: RealWorldObject, instr: str, user_id: int):
        instruction(instr)
        USER_DID = f"user {user_id} did"
        if USER_DID in obj.metadata:
            instr = obj.metadata[USER_DID] + ", then " + instr
        obj.metadata.update({USER_DID: instr})
        return obj

    @staticmethod
    def __str__():
        setup = '''Users did some interactions with the object.'''
        return setup

    def __repr__(self):
        return str(self)

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
    def __str__():
        setup = '''We allowed nature to take its course.'''
        return setup

    def __repr__(self):
        return str(self)