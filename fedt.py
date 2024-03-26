import csv
import itertools
import os
import time

from config import *
import fedt_manual

NAME = "name"
TEST_VALUES = "test_values"
INSTRUCTION = "instruction"

THREED_PRINTING = "3D printing"
LASERCUTTING = "lasercutting"

label_i = 0
def incrementing_labels(*args, **kwargs):
    global label_i
    label_str = "L"+str(label_i)
    label_i = label_i + 1
    return label_str

def hash_labels(*args, **kwargs):
    label_str = "L" + str(hash(str(args)))
    return label_str

def raw_labels(*args, **kwargs):
    label_str = str(args)
    return label_str

class FEDTExperiment:
    ''' a class to instantiate an experiment, with variables and needed functions '''
    CAD_variables = []
    CAM_variables = []
    fab_repetitions = 1
    post_process_variables = []
    post_process_repetitions = 1
    interaction_variables = []

    measurement_variables = []
    measurement_repetitions = 1

    tea_hypothesis = None
    tea_results = None

    experiment_csv = ''
    key_csv = ''

    geometry_function = None
    label_function = None
    label_gen_function = None
    cad_function = fedt_manual.build_geometry
    prep_cam_function = fedt_manual.prep_cam
    fabricate_function = fedt_manual.fabricate
    post_process_function = fedt_manual.post_process
    interaction_function = fedt_manual.interact
    measurement_function = fedt_manual.measure

    cad_tool = None
    machine = None
    fab_type = None
    configuration_base_file = None

    def experiment_size(self):
        ''' report the size of the specified experiment '''
        number_of_fabbed_objects = 1
        for var in self.CAD_variables + self.CAM_variables + self.post_process_variables:
            number_of_fabbed_objects = number_of_fabbed_objects * len(var['test_values'])
        self.number_of_fabbed_objects = number_of_fabbed_objects * self.fab_repetitions * self.post_process_repetitions

        number_of_user_interactions = number_of_fabbed_objects
        for var in self.interaction_variables:
            number_of_user_interactions = number_of_user_interactions * len(var['test_values'])
        self.number_of_user_interactions = number_of_user_interactions * self.measurement_repetitions

        self.number_of_recorded_values = number_of_user_interactions * len(self.measurement_variables)

        print("This experiment will require fabricating {} unique objects.\n".format(self.number_of_fabbed_objects) + 
            ("Users will perform {} interactions.\n".format(self.number_of_user_interactions) if len(self.interaction_variables) > 0 else "") +
            "{} total measurements will be recorded.".format(self.number_of_recorded_values))
    
    def label_all_conditions(self, label_gen_function=incrementing_labels):
        self.label_gen_function=label_gen_function

        expanded_CAD = []
        for var in self.CAD_variables:
            expanded_CAD.append([('CAD', var['argname'], val) for val in var['test_values']])

        expanded_CAM = []
        for var in self.CAM_variables:
            expanded_CAM.append([('CAM', var['argname'], val) for val in var['test_values']])

        exploded_fab = list(itertools.product(*expanded_CAD,*expanded_CAM))*self.fab_repetitions

        expanded_PP = []
        for var in self.post_process_variables:
            expanded_PP.append([('PP', var['description'].format(val)) for val in var['test_values']])
        expanded_PP = expanded_PP*self.post_process_repetitions

        exploded_vars = itertools.product(exploded_fab,*expanded_PP)

        vars_to_labels = {}
        for exploded in exploded_vars:
            condition_label = label_gen_function(exploded)
            vars_to_labels[exploded] = condition_label
        
        self.vars_to_labels = vars_to_labels
        
        return vars_to_labels

    def create_experiment_csv(self, experiment_csv="experiment-{}.csv"):
        if not self.vars_to_labels:
            self.label_all_conditions(label_gen_function=raw_labels)

        experiment_csv = experiment_csv.format(time.strftime("%Y%m%d-%H%M%S"))

        if len(self.interaction_variables) > 0:
            #... we get to explode _those_ now
            expanded_ixn = []
            for var in self.interaction_variables:
                expanded_ixn.append([(var['instruction'].format(val)) for val in var['test_values']])
            exploded_ixn = list(itertools.product(*expanded_ixn))

            with open(experiment_csv, 'w', newline='') as csvfile:
                spamwriter = csv.writer(csvfile,delimiter='\t')
                spamwriter.writerow(['Labelled Object','User Interaction'] + [var['name'] for var in self.measurement_variables])
                for _ in range(self.measurement_repetitions):
                    for _, label in self.vars_to_labels.items():
                        for ixn in exploded_ixn:
                            spamwriter.writerow([label,str(ixn)] + []*len(self.measurement_variables))

        else:
            with open(experiment_csv, 'w', newline='') as csvfile:
                spamwriter = csv.writer(csvfile,delimiter='\t')
                spamwriter.writerow(['Labelled Object'] + [var['name'] for var in self.measurement_variables])
                for _ in range(self.measurement_repetitions):
                    for config, label in self.vars_to_labels.items():
                        spamwriter.writerow([label] + []*len(self.measurement_variables))

        key_csv = experiment_csv.replace('.csv','_key.csv')
        with open(key_csv, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile)
            spamwriter.writerow(['Label','Configuration'])
            for config, label in self.vars_to_labels.items():
                spamwriter.writerow([self.vars_to_labels[config], config])

        self.experiment_csv = experiment_csv
        self.key_csv = key_csv

        return experiment_csv, key_csv
    
    def configure_for_freecad(self):
        import fedt_3D_geom
        self.cad_function = fedt_3D_geom.build_geometry
        self.cad_tool = "FreeCAD"
    
    def configure_for_printing(self, machine=PRUSA, cam_tool=PRUSA_SLICER_LOCATION, base_config=PRUSA_CONFIG_LOCATION):
        import fedt_print
        self.machine = machine
        self.fab_type = THREED_PRINTING
        self.cam_tool = cam_tool
        self.configuration_base_file = base_config
        self.prep_cam_function = fedt_print.prep_cam
        self.cam_function = fedt_print.do_cam
        self.fabricate_function = fedt_print.fabricate

    def configure_for_drawsvg(self):
        import fedt_2D_geom
        self.cad_function = fedt_2D_geom.build_geometry
        self.cad_tool = "drawsvg"

    def configure_for_lasercutting(self, machine="Epilog Helix", cam_tool=VISICUT_LOCATION, base_config="mappings.xml"):
        import fedt_laser
        self.machine = machine
        self.fab_type = LASERCUTTING
        self.cam_tool = VISICUT_LOCATION
        self.prep_cam_function = fedt_laser.prep_cam
        self.cam_function = fedt_laser.do_cam
        self.fabricate_function = fedt_laser.fabricate

    def fabricate(self):
        self.prep_cam_function(self.CAM_variables)

        CAM_paths = []

        CAD_to = 0
        for pos,var in enumerate(self.vars_to_labels[list(self.vars_to_labels.keys())[0]][0]):
            if var[0] == 'CAD':
                CAD_to = pos+1
            else:
                break

        for vars, label in self.vars_to_labels.items():
            # separate variables
            CAD_vars = vars[0][:CAD_to]
            CAM_vars = vars[0][CAD_to:]
            post_process_vars = vars[1] # honestly don't need this rn

            geom_file = self.cad_function(self.geometry_function, self.label_function, label, CAD_vars=CAD_vars)
            CAM_path = self.cam_function(geom_file, CAM_vars)
            CAM_paths.append(CAM_path)
        
        self.CAM_paths = CAM_paths
        for path in CAM_paths:
            self.fabricate(path)

    def post_process(self):
        self.post_process_function(self.vars_to_labels)

    def interact(self):
        self.interaction_function(self.interaction_variables, self.vars_to_labels)
    
    def measure(self):
        self.measurement_function(self.experiment_csv)

    @staticmethod
    def stringify_variable_list(variable_list):
        human_string = ""
        for variable in variable_list:
            if variable['test_values']: # should catch all independent variables
                human_string += "{} (values {})".format(variable['name'], variable['test_values'])
            elif variable['name']: # should catch dependent variables
                human_string += " " + str(variable['name'])
        return human_string

    def report_latex(self):
        ''' render a string of LaTeX that describes what has been done on this experiment '''

        setup = '''We used {cad_tool} to generate objects varying along the following dimensions: {CAD_variables}.
        We then used {cam_tool} to generate different CAM settings: {CAM_variables}.
        We fabricated objects of each configuration {fab_repetitions} times on our {machine}.
        In all, we fabricated {num_fabbed_objects} objects.
        After fabrication, we performed post-processing, processing {post_process_repetitions} objects with each of the following values: {post_process_variables}.
        Users then interacted with our objects, doing {interaction_variables} {measurement_repetitions} times on every object ({num_user_ixns} total interactions).
        We recorded {measurement_variables} for each ({num_recorded_values} total measurements).'''.format(
                **{
                    'cad_tool': str(self.cad_tool),
                    'CAD_variables': self.stringify_variable_list(self.CAD_variables),
                    'cam_tool': str(os.path.split(self.cam_tool)[-1]),
                    'CAM_variables': self.stringify_variable_list(self.CAM_variables),
                    'fab_repetitions': str(self.fab_repetitions*self.post_process_repetitions),
                    'post_process_variables': self.stringify_variable_list(self.post_process_variables),
                    'post_process_repetitions': str(self.post_process_repetitions),
                    'interaction_variables': self.stringify_variable_list(self.interaction_variables),
                    'measurement_variables': self.stringify_variable_list(self.measurement_variables),
                    'measurement_repetitions': str(self.measurement_repetitions),
                    'machine': str(self.machine),
                    'num_fabbed_objects': str(self.number_of_fabbed_objects),
                    'num_recorded_values': str(self.number_of_recorded_values),
                    'num_user_ixns': str(self.number_of_user_interactions),
                })

        if self.tea_results is not None:
            setup += '''{tea_results} was the outcome of {tea_hypothesis}'''.format({
                        'tea_results': str(self.tea_results),
                        'tea_hypothesis': str(self.tea_hypothesis)
                    })
        
        return setup