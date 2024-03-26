from config import *
from fedt import *

def build_geometry(geometry_function, label_function=None, label = "L0", CAD_vars=[]):
    print("create geometry which has the following values: {}".format(str(CAD_vars)))
    CAD_file = input("enter the file location of this geometry file:")
    return CAD_file

def prep_cam(CAM_variables):
    return

def do_cam(geom_path, *args, **kwargs):
    print("perform any setup required for your machine to match the following: {} {}".format(str(args), str(kwargs)))
    geom_path = input("enter the file location of this any configuration file that needs to be applied for this:")
    return geom_path

def fabricate(fabrication_file):
    print("fabricate {}".format(fabrication_file))

def post_process(vars_to_labels):
    for vars, label in vars_to_labels.items():
        if len(vars) < 2:
            # no post-process
            pass
        else:
            print("for object {}, {}".format(label,vars[1][1]))

def interact(interaction_variables, vars_to_labels):
    for label in vars_to_labels.values():
        for interaction in interaction_variables:
            for value in interaction[TEST_VALUES]:
                print("For object {}, {}. Then, record in the spreadsheet.".format(label, interaction[INSTRUCTION].format(value)))

def measure(experiment_csv, *args, **kwargs):
    print("now please fill {} with data".format(experiment_csv))