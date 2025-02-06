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

    def __hash__(self):
        return self.uid

    def __repr__(self) -> str:
        return "RealWorld" + str(self.uid) + 'v' + str(self.version)
    
    def updateVersion(self, newkey, newval):
        versions = []
        if VERSIONS in self.metadata:
            versions = self.metadata[VERSIONS]
        versions.append(copy.deepcopy(self))
        self.version += 1
        self.metadata.update({VERSIONS: versions, newkey: newval})
        note("(this creates a new version of #{}, which we call {})".format(self.uid, str(self)))

def fabricate(metadata: dict[str, object],
              instr: str | None = None) -> RealWorldObject:
    if instr:
        instruction(instr)

    global CURRENT_UID
    obj = RealWorldObject(CURRENT_UID, 0, dict(metadata))
    CURRENT_UID += 1
    note("this creates object #{}".format(obj.uid))

    return obj