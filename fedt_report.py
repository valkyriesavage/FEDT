from config import *

def latex(CAD_variables=[],
            CAM_variables=[],
            fab_repetitions=1,
            post_process_variables=[],
            post_process_repetitions=1,
            interaction_variables=[],
            measurement_variables=[],
            measurement_repetitions=1,
            tea_results='',
            tea_hypothesis=''):
    
    # uh oh, do we need state variables to track what kind of printing and stuff we called?

    return '''{} was the outcome of {} and {} and also {} we did {} with our {} and {} {} {} {}'''.format(
            str(tea_results),
            str(tea_hypothesis),
            str(CAD_variables),
            str(CAM_variables),
            str(fab_repetitions),
            str(post_process_variables),
            str(post_process_repetitions),
            str(interaction_variables),
            str(measurement_variables),
            str(measurement_repetitions))