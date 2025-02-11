import copy
from dataclasses import dataclass
from typing import Callable, Type
from control import MODE, Execute
from instruction import instruction, note

CURRENT_UID = 0
VERSIONS = 'versions'

@dataclass
class VirtualWorldObject:
    uid: int
    version: int
    metadata: dict[str, object]
    file_location: str

    def __init__(self, file_location: str,  metadata: dict[str, object] = {}):
        global CURRENT_UID
        self.uid = CURRENT_UID
        CURRENT_UID += 1
        self.file_location = file_location
        self.metadata = metadata
        self.version = 0
        note("this creates virtual object #{}{}".format(self.uid, " at {}".format(self.file_location) if self.file_location else ''))

    def __hash__(self):
        return self.uid

    def __repr__(self) -> str:
        return "{} {}v{}".format(type(self).__name__, self.uid, self.version)
    
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

@dataclass
class GeometryFile(VirtualWorldObject):

    def __init__(self, file_location: str):
        super().__init__(file_location, {'file_location':file_location})

    def __hash__(self):
        return self.uid

    def __repr__(self) -> str:
        return super(GeometryFile,self).__repr__()

@dataclass
class ConfigurationFile(VirtualWorldObject):

    def __init__(self, file_location: str):
        super().__init__(file_location, {'file_location':file_location})

    def __hash__(self):
        return self.uid

    def __repr__(self) -> str:
        return super(ConfigurationFile,self).__repr__()

@dataclass
class CAMFile(VirtualWorldObject):

    def __init__(self, file_location: str):
        super().__init__(file_location, {'file_location':file_location})

    def __hash__(self):
        return self.uid
    
    def __repr__(self) -> str:
        return super(CAMFile,self).__repr__()

def design(file_location: str,
           filetype=VirtualWorldObject,
           metadata: dict[str, object] = {},
           instr: str | None = None) -> VirtualWorldObject:
    if instr:
        instruction(instr)

    obj = filetype(file_location)
    obj.metadata.update(metadata)

    return obj