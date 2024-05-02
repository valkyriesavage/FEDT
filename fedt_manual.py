from config import *
from fedt import *

class FEDTHuman:
    def __init__(self):
        self.did_CAD = False
        self.did_CAM = False
        self.did_fab = False
        self.did_postprocess = False
        self.did_interact = False
        self.did_measure = False

    def build_geometry(self, label_function=None, label = "L0", CAD_vars=[]):
        print("create geometry which has the following values: {}".format(str(CAD_vars)))
        CAD_file = input("enter the file location of this geometry file:")
        self.did_CAD = True
        return CAD_file

    def prep_cam(self, CAM_variables):
        return

    def do_cam(self, geom_path, *args, **kwargs):
        print("perform any setup required for your machine to match the following: {} {}".format(str(args), str(kwargs)))
        geom_path = input("enter the file location of this any configuration file that needs to be applied for this:")
        self.did_CAM = True
        return geom_path

    def fabricate(self, fabrication_file):
        self.did_fab = True
        print("fabricate {}".format(fabrication_file))

    def post_process(self, vars_to_labels):
        self.did_postprocess = True
        for vars, label in vars_to_labels.items():
            if len(vars) < 2:
                # no post-process
                pass
            else:
                print("for object {}, {}".format(label,vars[1][1]))

    def interact(self, interaction_variables, vars_to_labels):
        self.did_interact = True
        for label in vars_to_labels.values():
            for interaction in interaction_variables:
                for value in interaction[TEST_VALUES]:
                    print("For object {}, {}. Then, record in the spreadsheet.".format(label, interaction[INSTRUCTION].format(value)))

    def measure(self, experiment_csv, *args, **kwargs):
        self.did_measure = True
        print("now please fill {} with data".format(experiment_csv))

    def __str__(self):
        setup = ''
        if self.did_CAD:
            setup += '''We manually edited our CAD models.'''
        if self.did_CAM:
            setup += '''We manually prepared our files for fabrication.'''
        if self.did_fab:
            setup += '''We manually fabricated the objects.'''
        if self.did_postprocess:
            setup += '''We manually post-processed the objects.'''
        if self.did_interact:
            setup += '''We manually interacted with the objects.'''
        if self.did_measure:
            setup += '''We manually measured the objects using a <TOOL>.'''
        return setup