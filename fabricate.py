import copy
from dataclasses import dataclass
from typing import Callable
from control import MODE, Execute
from instruction import instruction, note

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

    obj = RealWorldObject(dict(metadata))

    return obj