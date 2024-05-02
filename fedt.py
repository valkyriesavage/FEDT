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

    def __init__(self,
                 cad_executor=fedt_manual.FEDTHuman(),
                 cam_executor=fedt_manual.FEDTHuman(),
                 fabricate_executor=fedt_manual.FEDTHuman(),
                 post_process_executor=fedt_manual.FEDTHuman(),
                 interaction_executor=fedt_manual.FEDTHuman(),
                 measure_executor=fedt_manual.FEDTHuman(),
                 label_gen_function=raw_labels):
        self.cad_executor = cad_executor
        self.cam_executor = cam_executor
        self.fabricate_executor = fabricate_executor
        self.post_process_executor = post_process_executor
        self.interaction_executor = interaction_executor
        self.measure_executor = measure_executor
        self.label_gen_function = label_gen_function

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
    
    def label_all_conditions(self):

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
            condition_label = self.label_gen_function(exploded)
            vars_to_labels[exploded] = condition_label
        
        self.vars_to_labels = vars_to_labels
        
        return vars_to_labels

    def create_experiment_csv(self, experiment_csv="experiment-{}.csv"):
        if not hasattr(self, 'vars_to_labels'):
            self.label_all_conditions()

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
        self.cad_executor = fedt_3D_geom.FEDTFreeCAD()
    
    def configure_for_printing(self):
        import fedt_print
        self.cam_executor = fedt_print.FEDTPrinter()
        self.fabricate_executor = fedt_print.FEDTPrinter()

    def configure_for_drawsvg(self):
        import fedt_2D_geom
        self.cad_executor = fedt_2D_geom.FEDTdrawsvg()

    def configure_for_lasercutting(self):
        import fedt_laser
        self.cam_executor = fedt_laser.FEDTLaser()
        self.fabricate_executor = fedt_laser.FEDTLaser()

    def prep_cam(self):
        self.cam_executor.prep_cam(self.CAM_variables)

    def fabricate(self):
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
            post_process_vars = []
            if len(vars) > 1:
                post_process_vars = vars[1] # honestly don't need this rn

            geom_file = self.cad_executor.build_geometry(geometry_function=self.geometry_function, label_function=self.label_function, label=label, CAD_vars=CAD_vars)
            CAM_path = self.cam_executor.do_cam(geom_file, CAM_vars)
            CAM_paths.append(CAM_path)
        
        self.CAM_paths = CAM_paths
        for path in CAM_paths:
            self.fabricate_executor.fabricate(path)

    def post_process(self):
        self.post_process_executor.post_process(self.vars_to_labels)

    def interact(self):
        self.interaction_executor.interact(self.interaction_variables, self.vars_to_labels)
    
    def measure(self):
        self.measure_executor.measure(self.experiment_csv)

    @staticmethod
    def stringify_variable_list(begin_string, variable_list):
        human_string = ""
        for variable in variable_list:
            if 'test_values' in variable.keys(): # should catch all independent variables
                human_string += "{} (values {})".format(variable['name'], variable['test_values'])
            elif 'name' in variable.keys(): # should catch dependent variables
                human_string += " " + str(variable['name'])
        if len(human_string) > 0:
            human_string = begin_string + human_string + '.'

        return human_string

    def report_latex(self):
        ''' render a string of LaTeX that describes what has been done on this experiment '''

        post_process_string = ''
        if len(self.post_process_variables) > 0:
            post_process_string = '''After fabrication, we post-processed {post_process_repetitions} objects with each of the following values: {post_process_variables}. {post_process_executor}'''.format(
                **{
                    'post_process_variables': self.stringify_variable_list(self.post_process_variables),
                    'post_process_repetitions': str(self.post_process_repetitions),
                    'post_process_executor': str(self.post_process_executor)
                })
        interaction_string = ''
        if len(self.interaction_variables) > 0:
            interaction_string = '''{interaction_executor} Users did {interaction_variables} {measurement_repetitions} times on every object ({num_user_ixns} total interactions).'''.format(
                **{
                    'interaction_variables': self.stringify_variable_list(self.interaction_variables),
                    'interaction_executor': str(self.interaction_executor),
                    'num_user_ixns': str(self.number_of_user_interactions)
                })

        setup = '''{CAD_executor} {CAD_variables}
        {CAM_executor} {CAM_variables}
        We fabricated objects of each configuration {fab_repetitions} times. {fab_executor}
        In all, we fabricated {num_fabbed_objects} objects.
        {post_process_string}
        {interaction_string}
        {measurement_executor} We recorded {measurement_variables} for each ({num_recorded_values} total measurements).'''.format(
                **{
                    'CAD_executor': str(self.cad_executor),
                    'CAD_variables': self.stringify_variable_list('We generated objects varying along the following dimensions: ',self.CAD_variables),
                    'CAM_executor': str(self.cam_executor),
                    'CAM_variables': self.stringify_variable_list('We generated different CAM settings:',self.CAM_variables),
                    'fab_repetitions': str(self.fab_repetitions*self.post_process_repetitions),
                    'fab_executor': str(self.fabricate_executor),
                    'post_process_string': post_process_string,
                    'interaction_string': interaction_string,
                    'measurement_variables': self.stringify_variable_list('', self.measurement_variables),
                    'measurement_repetitions': str(self.measurement_repetitions),
                    'measurement_executor': str(self.measure_executor),
                    'num_fabbed_objects': str(self.number_of_fabbed_objects),
                    'num_recorded_values': str(self.number_of_recorded_values)
                })

        if self.tea_results is not None:
            setup += '''{tea_results} was the outcome of {tea_hypothesis}'''.format({
                        'tea_results': str(self.tea_results),
                        'tea_hypothesis': str(self.tea_hypothesis)
                    })
        
        return setup