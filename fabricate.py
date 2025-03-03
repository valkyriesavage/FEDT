import abc
import copy
from dataclasses import dataclass
from typing import Callable
from control import MODE, Execute
from instruction import instruction, note
from decorator import explicit_checker
from design import GeometryFile, ConfigurationFile, CAMFile

CURRENT_UID = 0
VERSIONS = 'versions'

@dataclass
class RealWorldObject:
    uid: int
    version: int
    metadata: dict[str, object]

    def __init__(self, metadata: dict[str, object] = {}):
        global CURRENT_UID
        self.uid = CURRENT_UID
        CURRENT_UID += 1
        self.metadata = metadata
        self.version = 0
        note("this creates physical object #{}".format(self.uid))

    def __hash__(self):
        return self.uid

    def __repr__(self) -> str:
        return "RealWorld" + str(self.uid) + 'v' + str(self.version)

    def updateVersion(self, newkey: str, newval: object, instr: str | None = None):
        if instr:
            instruction(instr)
        versions = []
        if VERSIONS in self.metadata:
            versions = self.metadata[VERSIONS]
        versions.append(copy.copy(self))
        self.version += 1
        if newkey in self.metadata:
            self.metadata[newkey] = "{}, {}".format(self.metadata[newkey], newval)
        else:
            self.metadata[newkey] = newval
        self.metadata.update({VERSIONS: versions})
        note("(this creates a new version of #{}: {}v{})".format(self.uid, self.uid, self.version))

def fabricate(metadata: dict[str, object],
              instr: str | None = None) -> RealWorldObject:
    if instr:
        instruction(instr)

    obj = RealWorldObject(metadata)

    return obj


###### this part is a little bit more structurey stuff, which can be used in the library

class FabricationDevice():
    __metaclass__ = abc.ABCMeta

    @staticmethod
    @abc.abstractmethod
    @explicit_checker
    def fab(input_geometry: GeometryFile|None=None,
            configuration: ConfigurationFile|None=None,
            toolpath: CAMFile|None=None,
            default_settings: dict[str, object]|None=None,
            **kwargs) -> RealWorldObject:
        raise NotImplemented

    @staticmethod
    def create_object(non_default_settings: dict[str, object], instr: str|None) -> RealWorldObject:
        return fabricate(non_default_settings, instr)
    
    @staticmethod
    @abc.abstractmethod
    def describe(default_settings):
        raise NotImplemented

    def __repr__(cls):
        return f"{cls.__name__}"

class NameableDevice(type):
    def __repr__(cls):
        return f"{cls.__name__}"

class PostProcessDevice():
    __metaclass__ = abc.ABCMeta

    @staticmethod
    @abc.abstractmethod
    def postprocess_object(feature: str, value: str) -> RealWorldObject:
        raise NotImplemented