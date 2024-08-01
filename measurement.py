import csv, time

from design import VirtualWorldObject
from fabricate import RealWorldObject
from dataclasses import dataclass
from typing import Callable
from flowchart import FlowChart
from control import MODE, Execute


@dataclass(eq=True, frozen=True)
class Measurement:
    name: str
    description: str
    procedure: str
    units: str
    feature: str

    def set_feature(self, feature):
        if not feature == self.feature:
            return Measurement(self.name, self.description, self.procedure, self.units, feature)
        return self

    def __repr__(self):
        return self.name + ":" + self.feature
    
    def __hash__(self):
         return hash(self.name + self.feature)
    
    def __eq__(self, other):
         # TODO might make sense here to compare measurement errors or something...
         return (
             self.__class__ == other.__class__ and
             self.name == other.name and
             self.feature == other.feature
         )


@dataclass
class Measurements:
    objects: set[RealWorldObject]
    measurements: set[Measurement]

    @staticmethod
    def single(obj: RealWorldObject, meas: Measurement) -> "Measurements":
        return Measurements(set([obj]), set([meas]))

    @staticmethod
    def empty() -> "Measurements":
        return Measurements(set(), set())

    def __add__(self, other: "Measurements") -> "Measurements":
        return Measurements(self.objects.union(other.objects),
                            self.measurements.union(other.measurements))

    def instruction(self):
        return f"Fill out the measurements for objects {list(self.objects)} and measurements {list(self.measurements)}."

    def get_data(self) -> dict[tuple[Measurement, RealWorldObject], float|str]:
        if isinstance(MODE, Execute):
            experiment_csv = "experiment-{}.csv".format(time.strftime("%Y%m%d-%H%M%S"))

            csv_to_obj = {}
            csv_to_meas = {}

            # first let's set up the columns
            columns = [f"{measurement.name}: {measurement.feature} ({measurement.units})" for measurement in self.measurements]
            csv_to_meas = dict((f"{measurement.name}: {measurement.feature} ({measurement.units})", measurement) for measurement in self.measurements)
            columns = ["Label"] + columns
            rows = [f"{obj.uid}" for obj in self.objects]
            csv_to_obj = dict((obj.uid,obj) for obj in self.objects)

            with open(experiment_csv, 'w') as csvfile:
                spamwriter = csv.writer(csvfile, delimeter=',')
                spamwriter.writerow(columns)
                for obj in rows:
                    spamwriter.writerow([obj] + [',']*(len(columns)-1))

            def walk_metadata(obj: RealWorldObject | VirtualWorldObject, ret_val=False):
                variables = []
                for metakey, metaval in obj.metadata.items():
                    if type(metaval) is RealWorldObject or type(metaval) is VirtualWorldObject:
                        variables.extend(walk_metadata(metaval), ret_val=ret_val)
                    else:
                        if ret_val:
                            variables.extend(metaval)
                        else:
                            variables.extend(metakey)
                return variables

            # now let's make a key csv that actually maps the object UIDs to the things varied in them
            object_variables = walk_metadata(self.objects[0]) # ... all of them should have the same # of vars
            # TODO check if this is true :joy:

            key_csv = experiment_csv.replace('.csv','_key.csv')
            with open(key_csv, 'w') as csvfile:
                spamwriter = csv.writer(csvfile,delimiter=',')
                spamwriter.writerow(['Label'] + list(object_variables))
                for object in self.objects():
                    spamwriter.writerow([object.uid] + walk_metadata(obj))

            # now we have to ask them somehow to actually fill these in?
            # TODO: something else here?
            input(f"add the data in {experiment_csv}. the key, if needed, is in {key_csv}.")
            
            # now we need to strip all the answers back _out_
            recorded_values = {} # dict tuple[Measurement, RealWorldObject], float|str
            with open(experiment_csv, 'r') as csvfile:
                spamreader = csv.DictReader(csvfile, delimiter=',')
                for row in spamreader:
                    for col in row:
                        mobj = None
                        if col == 'Label':
                            mobj = csv_to_obj[row[col]] # it will be the first one
                        else:
                            meas = csv_to_meas[col]
                            value = row[col]
                            recorded_values[(mobj,meas)] = value
            return recorded_values
        else:
            FlowChart().add_instruction(self.instruction())
            return dict()
