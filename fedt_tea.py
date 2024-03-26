import tea

def do_experiment(hypothesis, fedt_experiment):
    variables_tea = fedt_experiment.CAD_variables +\
                    fedt_experiment.CAM_variables +\
                    fedt_experiment.post_process_variables +\
                    fedt_experiment.interaction_variables +\
                    fedt_experiment.measurement_variables
    
    for variable in variables_tea:
        # munge it to have the right stuff. we name things a little differently
        if variable["data type"] == "nominal":
            variable["categories"] = variable["test_values"]
        # anything else we want to do? we could add "values" to the ratio ones
        # or do anything else we like

    study_design = {
        'study type': 'experiment',
        'independent variables': [var['name'] for var in fedt_experiment.CAD_variables +
                                                        fedt_experiment.CAM_variables +
                                                        fedt_experiment.post_process_variables +
                                                        fedt_experiment.interaction_variables],
        'dependent variables': [var['name'] for var in fedt_experiment.measurement_variables]
    }
    tea.data(fedt_experiment.experiment_csv, key='ID') # TODO: determine if this is the right key
    tea.define_variables(variables_tea)
    tea.define_study_design(study_design)
    return tea.hypothesize(hypothesis[0],hypothesis[1])