import os
import subprocess
import time
from zipfile import ZipFile
import drawsvg as draw

from config import *
from fedt import *

laser_bed = {
    'width': 24 * 2.54 * 10, # in mm
    'height': 18 * 2.54 * 10 # in mm
}

default_laser_settings = {
    CUT_POWER: 100,
    CUT_SPEED: 100,
    CUT_FREQUENCY: 5000,
    MATERIAL: "Acrylic",
    THICKNESS: "3.0mm"
}

def build_geometry(geometry_function, label_function=None, label = "L0", svg_location = "./expt_svgs/", CAD_vars=[]):
    d = draw.Drawing(laser_bed['width'], laser_bed['height'], origin='center', displayInline=False)
    
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

def prep_cam(CAM_variables):
    cut_powers=[default_laser_settings[CUT_POWER]]
    cut_speeds=[default_laser_settings[CUT_SPEED]]
    frequencies=[default_laser_settings[CUT_FREQUENCY]]
    materials=[default_laser_settings[MATERIAL]]
    thicknesses=[default_laser_settings[THICKNESS]]

    for variable in CAM_variables:
        if variable[NAME] == CUT_POWER:
            cut_powers = variable[TEST_VALUES]
        if variable[NAME] == CUT_SPEED:
            cut_speeds = variable[TEST_VALUES]
        if variable[NAME] == CUT_FREQUENCY:
            frequencies = variable[TEST_VALUES]
        if variable[NAME] == MATERIAL:
            materials = variable[TEST_VALUES]
        if variable[NAME] == THICKNESS:
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
                    cut_setting_fname = "fedt_generated_{}.xml".format(time.strftime("%Y%m%d-%H%M%S%f"))
                    with open(cut_setting_fname, "w+") as f:
                        f.write(xmlstr)
                    myzip.write(cut_setting_fname, "profiles/{}".format(cut_setting_fname))            
                    for material in materials:
                        for thickness in thicknesses:
                            myzip.write(cut_setting_fname, "laserprofiles/Epilog_32_Helix/{}/{}/{}".format(material,thickness,cut_setting_fname))
                    os.remove(cut_setting_fname)
        
    temp_vcsettings = temp_zf.replace('.zip','.vcsettings')
    os.rename(temp_zf, temp_vcsettings)

    print("please open Visicut and Options > Import Settings > " + temp_vcsettings)

    return

def do_cam(*args, **kwargs):
    # do nothing
    return

def prep_all_for_fab(vars_to_labels, geometry_function, label_function):
    CAM_paths = []

    CAD_to = 0
    for pos,var in enumerate(vars_to_labels[list(vars_to_labels.keys())[0]][0]):
        if var[0] == 'CAD':
            CAD_to = pos+1
        else:
            break

    for vars, label in vars_to_labels.items():
        # separate variables
        CAD_vars = vars[0][:CAD_to]
        CAM_vars = vars[0][CAD_to:]
        post_process_vars = vars[1] # honestly don't need this rn

        geom_file = build_geometry(geometry_function, label_function, label, CAD_vars=CAD_vars)
        CAM_path = do_cam(geom_file, CAM_vars)
        CAM_paths.append(CAM_path)
    
    return CAM_paths

def fabricate(cut_file, laserdevice="Epilog Helix", mapping_file="mappings.xml"):
    # make the svg into the .plf file that they like
    temp_zf = 'spam.zip'
    with ZipFile(temp_zf, 'w') as myzip:
        myzip.write(cut_file)
        myzip.write(mapping_file)
        myzip.write("transform.xml")
    temp_plf = temp_zf.replace('.zip','.plf')
    os.rename(temp_zf, temp_plf)
    cut_command = [VISICUT_LOCATION,
                   '--laserdevice ' + laserdevice,
                   '--execute',
                   temp_plf]
    results = subprocess.check_output(cut_command)
    os.remove(temp_plf)
    return results