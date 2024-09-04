from dataclasses import dataclass
from typing import Callable
from control import MODE, Execute
from instruction import instruction

CURRENT_UID = 0


@dataclass
class RealWorldObject:
    uid: int
    version: int
    metadata: dict[str, object]

    def __hash__(self):
        return self.uid

    def __repr__(self) -> str:
        return "RealWorld" + str(self.uid) + 'v' + str(self.version)


def fabricate(metadata: dict[str, object],
              instr: str | None = None) -> RealWorldObject:
    if instr:
        instruction(instr)

    global CURRENT_UID
    obj = RealWorldObject(CURRENT_UID, 0, dict(metadata))
    CURRENT_UID += 1

    return obj