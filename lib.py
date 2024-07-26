import drawsvg as draw
import os
import subprocess
import time
from zipfile import ZipFile

from instruction import instruction
from measurement import Measurement, Measurements
from fabricate import fabricate, RealWorldObject
from dataclasses import dataclass

from config import *


@dataclass
class LineFile:
    svg_location = ''

    def __init__(self, svg_location):
        self.svg_location = svg_location

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

class Laser:
    CUT_POWER = "cut power"
    CUT_SPEED = "speed"
    CUT_FREQUENCY = "frequency"
    MATERIAL = "material"
    THICKNESS = "thickness"
    FOCAL_HEIGHT_MM = "focal height mm"
    LASERDEVICE = "laser device"
    LASER_BED = "laser bed size in mm"

    LASERVARS = [CUT_POWER,CUT_SPEED,CUT_FREQUENCY,MATERIAL,THICKNESS,FOCAL_HEIGHT_MM]

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
        }
    }

    generated_setting_names = {}

    def __init__(self, default_laser_settings = default_laser_settings):
        self.default_laser_settings = default_laser_settings

    @staticmethod
    def generate_setting_key(material,thickness,cut_power,cut_speed,frequency):
        return "{}.{}.{}.{}.{}".format(material,thickness,cut_power,cut_speed,frequency)

    def prep_cam(self, CAM_variables):
        cut_powers=[self.default_laser_settings[Laser.CUT_POWER]]
        cut_speeds=[self.default_laser_settings[Laser.CUT_SPEED]]
        frequencies=[self.default_laser_settings[Laser.CUT_FREQUENCY]]
        materials=[self.default_laser_settings[Laser.MATERIAL]]
        thicknesses=[self.default_laser_settings[Laser.THICKNESS]]

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
                        self.generated_setting_names[Laser.generate_setting_key(material,thickness,cut_power,cut_speed,frequency)] = cut_setting_fname
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

        return
        

    def fab(self, line_file: LineFile,
                    colors_to_mappings = {RED: "cut", BLUE: "mark"},
                    specific_color = GREEN,
                    specific_cut_power = default_laser_settings[CUT_POWER],
                    specific_cut_speed = default_laser_settings[CUT_SPEED],
                    specific_cut_frequency = default_laser_settings[CUT_FREQUENCY],
                    material = default_laser_settings[MATERIAL],
                    thickness = default_laser_settings[THICKNESS],
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
                try:
                    mappings += single_mapping_template.format(red=specific_color[0],
                                                            green=specific_color[1],
                                                            blue=specific_color[2],
                                                            actionname=self.generated_setting_names[Laser.generate_setting_key(material,
                                                                                                                                thickness,
                                                                                                                                specific_cut_power,
                                                                                                                                specific_cut_speed,
                                                                                                                                specific_cut_frequency)])
                except:
                    # if they didn't actually generate custom settings, pass!
                    pass
                map_file.write(mapping_file_template.format(mappings=mappings))
            mapping_file = temp_mapping_file

        instruction("ensure that the line colors in your file match the line colors defined in {}".format(mapping_file))
        instruction("set the focal height of the laser to {}".format(focal_height_mm))

        # make the svg into the .plf file that they like
        temp_zf = 'spam.zip'
        with ZipFile(temp_zf, 'w') as myzip:
            myzip.write(line_file)
            myzip.write(mapping_file, "mappings.xml")
            myzip.write("transform.xml")
        temp_plf = temp_zf.replace('.zip','.plf')
        os.rename(temp_zf, temp_plf)
        cut_command = [VISICUT_LOCATION,
                    '--laserdevice ' + self.default_laser_settings[Laser.LASERDEVICE],
                    '--execute',
                    temp_plf]
        try:
            results = subprocess.check_output(cut_command)
        except:
            # it probably didn't work! incredible. that's likely because we didn't get visicut in here right.
            print("was not able to call visicut properly")
        os.remove(temp_plf)
        try:
            os.remove(temp_mapping_file)
        except:
            # it might happen that the user supplied a mapping file and we never made a temp... in this case, just ignore it -\_(._.)_/-
            pass

    def circ_wood_fab(self,
                      line_file: LineFile,
                      focal_height_mm: int) -> RealWorldObject:
    
        from control import MODE, Execute
        if isinstance(MODE, Execute):
            pass
        instruction("Run the laser cutter.")

        self.fab(line_file.svg_location, focal_height_mm=focal_height_mm)

        return fabricate({"line_file": line_file,
                          "focal_height_mm": focal_height_mm,})
    
    def __str__(self):
        setup = '''We used a {machine} with bed size {bedsize} and Visicut. Our default settings were {defaults}.'''.format(
                **{
                    'machine': str(self.default_laser_settings[Laser.LASERDEVICE]),
                    'bedsize': str(self.default_laser_settings[Laser.LASER_BED]),
                    'defaults': ', '.join([str(x) + ':' + str(y) for x, y in zip(self.default_laser_settings.keys(), self.default_laser_settings.values()) if x not in [Laser.LASERDEVICE, Laser.LASER_BED]])
                })
        return setup

    def __repr__(self):
        return str(self)


class SvgEditor:
    laser_bed = Laser.default_laser_settings[Laser.LASER_BED]

    @staticmethod
    def design() -> LineFile:
        instruction("Get the line file from the website.")
        return LineFile()

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
    def build_geometry(geometry_function=None, label_function=None, label = "L0", svg_location = "./expt_svgs/", CAD_vars={}) -> LineFile:
        if geometry_function is None:
            geometry_function = SvgEditor.draw_circle

        d = draw.Drawing(SvgEditor.laser_bed['width'], SvgEditor.laser_bed['height'], origin='center', displayInline=False)
        
        SvgEditor.geometry_function = geometry_function
        geometry_function(draw, d, CAD_vars)
        if label_function is not None:
            label_function(draw, d, label)

        if not os.path.exists(svg_location):
            os.path.makedirs(svg_location)

        svg_fname = "expt_" + label + ".svg"
        svg_fullpath = os.path.join(svg_location, svg_fname)
        d.save_svg(svg_fullpath)
        #d.savePng('example.png')
        return LineFile(svg_fullpath)
    
    @staticmethod
    def __str__():
        setup = '''We used drawsvg to create our geometries.'''
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
        units="ohms")

    @staticmethod
    def measure_resistance(obj: RealWorldObject) -> Measurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Multimeter.resistance.procedure)
        return Measurements.single(obj, Multimeter.resistance)
