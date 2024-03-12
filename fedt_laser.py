from config import *

import os
import subprocess
import time
from zipfile import ZipFile
import drawsvg as draw

laser_bed = {
    'width': 24 * 2.54 * 10, # in mm
    'height': 18 * 2.54 * 10 # in mm
}

def build_geometry(geometry_function, label_function=None, label = "L0", label_location = (0,0), svg_location = "./"):
    d = draw.Drawing(laser_bed['width'], laser_bed['height'], origin='center', displayInline=False)
    
    geometry_function(d)
    if label_function is not None:
        label_function(d, label)

    svg_location = os.path.join(svg_location, "expt_" + label + '.svg')
    d.save_svg(svg_location)
    #d.savePng('example.png')
    return svg_location

def prep_cam(cut_powers=[100], cut_speeds=[100], frequencies=[5000], materials=["Acrylic"], thicknesses=["3.0mm"]):
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