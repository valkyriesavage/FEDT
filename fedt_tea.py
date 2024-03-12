import tea

def do_experiment(measurement_variables, hypothesis, experiment_csv,
                  CAD_variables =[],
                  CAM_variables=[],
                  post_process_variables=[],
                  interaction_variables=[]):
    variables_tea = CAD_variables +\
                    CAM_variables +\
                    post_process_variables +\
                    interaction_variables +\
                    measurement_variables
    
    for variable in variables_tea:
        # munge it to have the right stuff. we name things a little differently
        if variable["data type"] == "nominal":
            variable["categories"] = variable["test_values"]
        # anything else we want to do? we could add "values" to the ratio ones
        # or do anything else we like

    study_design = {
        'study type': 'experiment',
        'independent variables': [var['name'] for var in CAD_variables +
                                                        CAM_variables +
                                                        post_process_variables +
                                                        interaction_variables],
        'dependent variables': [var['name'] for var in measurement_variables]
    }
    tea.data(experiment_csv, key='ID') # TODO: determine if this is the right key
    tea.define_variables(variables_tea)
    tea.define_study_design(study_design)
    return tea.hypothesize(hypothesis[0],hypothesis[1])