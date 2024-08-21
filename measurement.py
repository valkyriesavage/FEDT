import csv, os, time

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
        return self.name + ":" + self.feature + " (" + self.units + ")"
    
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
class BatchMeasurements:
    objects: set[RealWorldObject]
    measurements: set[Measurement]

    @staticmethod
    def single(obj: RealWorldObject, meas: Measurement) -> "BatchMeasurements":
        return BatchMeasurements(set([obj]), set([meas]))
    
    @staticmethod
    def multiple(obj: RealWorldObject, meases: set[Measurement]) -> "BatchMeasurements":
        return BatchMeasurements(set([obj]), meases)

    @staticmethod
    def empty() -> "BatchMeasurements":
        return BatchMeasurements(set(), set())

    def __add__(self, other: "BatchMeasurements") -> "BatchMeasurements":
        return BatchMeasurements(self.objects.union(other.objects),
                            self.measurements.union(other.measurements))

    def instruction(self):
        return f"Fill out the csv for {len(list(self.objects))} objects ({list(self.objects)}) and {len(list(self.measurements))} measurements ({list(self.measurements)}) ({self.how_many()} datapoints)."

    def get_all_data(self) -> dict[tuple[Measurement, RealWorldObject], float|str]:
        from control import MODE, Execute
        if isinstance(MODE, Execute):
            print("now it's time to get data!")
            experiment_csv = os.path.join("expt_csvs","experiment-{}.csv".format(time.strftime("%Y%m%d-%H%M%S")))

            csv_to_obj = {}
            csv_to_meas = {}

            # first let's set up the columns
            columns = [f"{measurement.name}: {measurement.feature} ({measurement.units})" for measurement in self.measurements]
            csv_to_meas = dict((f"{measurement.name}: {measurement.feature} ({measurement.units})", measurement) for measurement in self.measurements)
            columns = ["Label"] + columns
            rows = [f"{obj.uid}" for obj in self.objects]
            csv_to_obj = dict((str(obj.uid),obj) for obj in self.objects)

            with open(experiment_csv, 'w') as csvfile:
                spamwriter = csv.writer(csvfile)
                spamwriter.writerow(columns)
                for obj in rows:
                    spamwriter.writerow([obj] + ['']*(len(columns)-1))

            def walk_metadata(obj: RealWorldObject | VirtualWorldObject, ret_val=False):
                variables = []
                print(type(metaval))
                for metakey, metaval in obj.metadata.items():
                    if type(metaval) in [RealWorldObject, VirtualWorldObject] or \
                        issubclass(type(metaval), VirtualWorldObject) or \
                        issubclass(type(metaval), RealWorldObject):
                        variables.extend(walk_metadata(metaval, ret_val=ret_val))
                    else:
                        if ret_val:
                            variables.append(metaval)
                        else:
                            variables.append(metakey)
                return variables

            # now let's make a key csv that actually maps the object UIDs to the things varied in them

            object_variables = walk_metadata(list(self.objects)[-1]) # TODO : deal with what happens if they don't have the same # of vars?

            key_csv = experiment_csv.replace('.csv','_key.csv')
            with open(key_csv, 'w') as csvfile:
                spamwriter = csv.writer(csvfile,delimiter=',')
                spamwriter.writerow(['Label'] + list(object_variables))
                for obj in self.objects:
                    spamwriter.writerow([obj.uid] + walk_metadata(obj, ret_val=True))

            # now we have to ask them somehow to actually fill these in?
            input(f"Add the data in {experiment_csv}. The key, if needed, is in {key_csv}. Enter when finished.")
            
            # now we need to strip all the answers back _out_ LOL
            recorded_values = {} # dict tuple[Measurement, RealWorldObject], float|str
            with open(experiment_csv, 'r') as csvfile:
                spamreader = csv.DictReader(csvfile, delimiter=',')
                for row in spamreader:
                    for col in row:
                        mobj = None
                        if col == 'Label':
                            mobj = csv_to_obj[row[col]]
                        else:
                            meas = csv_to_meas[col]
                            value = row[col]
                            recorded_values[(mobj,meas)] = value
            return recorded_values
        else:
            FlowChart().add_instruction(self.instruction())
            return dict()
    
    def how_many(self) -> int:
        return len(self.objects) * len(self.measurements)

class ImmediateMeasurements:
    objects: list[RealWorldObject] = [] # rows
    measurements: list[Measurement] = [] # cols
    csv: str = None
    data_points: dict[RealWorldObject,dict[Measurement,float|str]] = {}

    @staticmethod
    def empty() -> "ImmediateMeasurements":
        return ImmediateMeasurements()

    def set_up_csv(self):
        self.csv = os.path.join("expt_csvs","experiment-{}.csv".format(time.strftime("%Y%m%d-%H%M%S")))
    
    def dump_to_csv(self):
        if not self.csv:
            self.set_up_csv()
        from control import MODE, Execute
        if not isinstance(MODE, Execute):
            FlowChart().add_note("the collected data will be exported to a csv. the 'key' csv linking labels to features will also be written.")
            return

        with open(self.csv, 'w+') as csvfile:
            spamwriter = csv.DictWriter(csvfile, fieldnames=['Label'] + self.measurements)
            spamwriter.writeheader()
            spamwriter.writerows(self.data_points.values())

        def walk_metadata(obj: RealWorldObject | VirtualWorldObject, ret_val=False):
            variables = []
            for metakey, metaval in obj.metadata.items():
                if type(metaval) in [RealWorldObject, VirtualWorldObject] or \
                        issubclass(type(metaval), VirtualWorldObject) or \
                        issubclass(type(metaval), RealWorldObject):
                    variables.extend(walk_metadata(metaval, ret_val=ret_val))
                else:
                    if ret_val:
                        variables.append(metaval)
                    else:
                        variables.append(metakey)
            return variables

        # now let's make a key csv that actually maps the object UIDs to the things varied in them
        object_variables = walk_metadata(self.objects[0]) # TODO : deal with what happens if they don't have the same # of vars?

        key_csv = self.csv.replace('.csv','_key.csv')
        with open(key_csv, 'w+') as csvfile:
            spamwriter = csv.writer(csvfile,delimiter=',')
            spamwriter.writerow(['Label'] + list(object_variables))
            for obj in self.objects:
                spamwriter.writerow([obj.uid] + walk_metadata(obj, ret_val=True))

        print(f"all the data are in {self.csv}. the key for labelled objects is in {key_csv}.")
        FlowChart().add_note(f"working with ({self.how_many()} data points)")

    def do_measure(self, obj: RealWorldObject, meas: Measurement) -> "ImmediateMeasurements":
        if not meas in self.measurements:
            self.measurements.append(meas)
            for row in self.data_points.values():
                row.update({meas: ''})
                
        if not obj in self.data_points.keys():
            self.objects.append(obj)
            obj_blank_dict = {"Label":obj.uid}
            obj_blank_dict.update(dict([(meas,'') for meas in self.measurements]))
            self.data_points[obj] = obj_blank_dict
        
        measured = ''
        from control import MODE, Execute
        if isinstance(MODE, Execute):
            measured = input(f"what is the value of {meas} for object #{obj.uid}?")
            self.data_points[obj][meas] = measured
        else:
            FlowChart().add_instruction(f"measure {meas} for object #{obj.uid}")
        return measured

    def __add__(self, other: "BatchMeasurements") -> "ImmediateMeasurements":
        self.do_measure(other.objects.pop(), other.measurements.pop()) # TODO I.... don't like this :joy:
        return self

    def get_all_data(self) -> dict[tuple[Measurement, RealWorldObject], float|str]:
        FlowChart().add_note(f"working with ({self.how_many()} data points)")
        return self.data_points
    
    def how_many(self) -> int:
        # note that we subtract one from each row because we store the label in there, too
        return sum([len(self.data_points[rwo].keys()) - 1 for rwo in self.data_points])