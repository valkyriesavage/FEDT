import csv
import itertools
import time

from config import *

NAME = "name"
TEST_VALUES = "test_values"

CUT_POWER = "cut power"
CUT_SPEED = "speed"
CUT_FREQUENCY = "frequency"
MATERIAL = "material"
THICKNESS = "thickness"

def experiment_size(CAD_variables=[], CAM_variables=[], fab_repetitions=1,
                    post_process_variables=[], post_process_repetitions=1,
                    interaction_variables=[],
                    measurement_variables=[], measurement_repetitions=1):
    number_of_fabbed_objects = 1
    for var in CAD_variables + CAM_variables + post_process_variables:
        number_of_fabbed_objects = number_of_fabbed_objects * len(var['test_values'])
    number_of_fabbed_objects = number_of_fabbed_objects * fab_repetitions * post_process_repetitions

    number_of_user_interactions = number_of_fabbed_objects
    for var in interaction_variables:
        number_of_user_interactions = number_of_user_interactions * len(var['test_values'])
    number_of_user_interactions = number_of_user_interactions * measurement_repetitions

    number_of_recorded_values = number_of_user_interactions * len(measurement_variables)

    print("This experiment will require fabricating {} unique objects.\n".format(number_of_fabbed_objects) + 
          ("Users will perform {} interactions.\n".format(number_of_user_interactions) if len(interaction_variables) > 0 else "") +
          "{} total measurements will be recorded.".format(number_of_recorded_values))

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

def label_all_conditions(CAD_variables=[], CAM_variables=[], fab_repetitions=1,
                    post_process_variables=[], post_process_repetitions=1, label_gen_function=incrementing_labels):
    expanded_CAD = []
    for var in CAD_variables:
        expanded_CAD.append([('CAD', var['argname'], val) for val in var['test_values']])

    expanded_CAM = []
    for var in CAM_variables:
        expanded_CAM.append([('CAM', var['argname'], val) for val in var['test_values']])

    exploded_fab = list(itertools.product(*expanded_CAD,*expanded_CAM))*fab_repetitions

    expanded_PP = []
    for var in post_process_variables:
        expanded_PP.append([('PP', var['description'].format(val)) for val in var['test_values']])
    expanded_PP = expanded_PP*post_process_repetitions

    exploded_vars = itertools.product(exploded_fab,*expanded_PP)

    vars_to_labels = {}
    for exploded in exploded_vars:
        condition_label = label_gen_function(exploded)
        vars_to_labels[exploded] = condition_label
    
    return vars_to_labels
    

def create_experiment_csv(vars_to_labels, interaction_variables, measurement_variables, measurement_repetitions, experiment_csv="experiment-{}.csv"):

    experiment_csv = experiment_csv.format(time.strftime("%Y%m%d-%H%M%S"))

    if len(interaction_variables) > 0:
        #... we get to explode _those_ now
        expanded_ixn = []
        for var in interaction_variables:
            expanded_ixn.append([(var['instruction'].format(val)) for val in var['test_values']])
        exploded_ixn = list(itertools.product(*expanded_ixn))

        with open(experiment_csv, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile,delimiter='\t')
            spamwriter.writerow(['Labelled Object','User Interaction'] + [var['name'] for var in measurement_variables])
            for _ in range(measurement_repetitions):
                for _, label in vars_to_labels.items():
                    for ixn in exploded_ixn:
                        spamwriter.writerow([label,str(ixn)] + []*len(measurement_variables))

    else:
        with open(experiment_csv, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile,delimiter='\t')
            spamwriter.writerow(['Labelled Object'] + [var['name'] for var in measurement_variables])
            for _ in range(measurement_repetitions):
                for config, label in vars_to_labels.items():
                    spamwriter.writerow([label] + []*len(measurement_variables))

    key_csv = experiment_csv.replace('.csv','_key.csv')
    with open(key_csv, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile)
        spamwriter.writerow(['Label','Configuration'])
        for config, label in vars_to_labels.items():
            spamwriter.writerow([vars_to_labels[config], config])

    return experiment_csv, key_csv

def request_postprocess(vars_to_labels):
    for vars, label in vars_to_labels.items():
        if len(vars) < 2:
            # no post-process
            pass
        else:
            print("for object {}, {}".format(label,vars[1][1]))