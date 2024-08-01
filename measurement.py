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
        return Measurement(self.name, self.description, self.procedure, self.units, feature)

    def __repr__(self):
        return self.name
    
    def __hash__(self):
         return hash(self.name + self.feature)
    
    def __eq__(self, other):
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

    def get_data(self) -> dict[tuple[Measurement, RealWorldObject], float]:
        if isinstance(MODE, Execute):
            # Have user fill spreadsheet
            # Actually do analysis
            return dict()
        else:
            FlowChart().add_instruction(self.instruction())
            return dict()
