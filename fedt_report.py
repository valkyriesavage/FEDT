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

    return '''{tea_results} was the outcome of {tea_hypothesis} and {CAD_variables} and also {CAM_variables} we did {fab_repetitions} with our {post_process_variables} and {post_process_repetitions} {interaction_variables} {measurement_variables} {measurement_repetitions}'''.format(
            {
                tea_results: str(tea_results),
                tea_hypothesis: str(tea_hypothesis),
                CAD_variables: str(CAD_variables),
                CAM_variables: str(CAM_variables),
                fab_repetitions: str(fab_repetitions),
                post_process_variables: str(post_process_variables),
                post_process_repetitions: str(post_process_repetitions),
                interaction_variables: str(interaction_variables),
                measurement_variables: str(measurement_variables),
                measurement_repetitions: str(measurement_repetitions)
            })