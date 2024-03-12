from config import *

def latex(tea_results,
            tea_hypothesis,
            CAD_variables,
            CAM_variables,
            print_repetitions,
            post_process_variables,
            post_process_repetitions,
            interaction_variables,
            measurement_variables,
            measurement_repetitions):
    
    # uh oh, do we need state variables to track what kind of printing and stuff we called?

    return '''{} was the outcome of {} and {} and also {} we did {} with our {} and {} {} {} {} {}'''.format(
            tea_results,
            tea_hypothesis,
            CAD_variables,
            CAM_variables,
            print_repetitions,
            post_process_variables,
            post_process_repetitions,
            interaction_variables,
            measurement_variables,
            measurement_repetitions)