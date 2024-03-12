import csv
import time

def create_experiment_csv(vars_to_labels, measurement_variables, measurement_repetitions):
    experiment_csv = "experiment-{}.csv".format(time.strftime("%Y%m%d-%H%M%S"))

    with open(experiment_csv, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile)
        spamwriter.writerow(['Labelled Object'] + measurement_variables + ["ID"])
        for rep in range(measurement_repetitions):
            for config in vars_to_labels.keys():
                spamwriter.writerow(vars_to_labels[config] + []*len(measurement_variables) + [config.split('//')[0]])

    return experiment_csv