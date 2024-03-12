from config import *

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
          "Users will perform {} interactions.\n".format(number_of_user_interactions) +
          "{} total measurements will be recorded.".format(number_of_recorded_values))