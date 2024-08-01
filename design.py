from dataclasses import dataclass
from typing import Callable
from control import MODE, Execute
from instruction import instruction

CURRENT_UID = 0


@dataclass
class VirtualWorldObject:
    uid: int
    metadata: dict[str, object]

    def __init__(self, metadata):
        global CURRENT_UID
        self.uid = CURRENT_UID
        CURRENT_UID += 1
        self.metadata = metadata

    def __hash__(self):
        return self.uid

    def __repr__(self) -> str:
        return str(self.uid)
    
@dataclass
class LineFile(VirtualWorldObject):
    LINE_FILE = 'line file'
    svg_location = ''

    def __init__(self, svg_location):
        super().__init__({'svg_location':svg_location})
        self.svg_location = svg_location

@dataclass
class VolumeFile(VirtualWorldObject):
    VOLUME_FILE = 'volume file'
    stl_location = ''

    def __init__(self, stl_location):
        super().__init__({'stl_location':stl_location})
        self.stl_location = stl_location

@dataclass
class GCodeFile(VirtualWorldObject):
    GCODE_FILE = 'gcode file'
    gcode_location = ''

    def __init__(self, gcode_location):
        super().__init__({'gcode_location':gcode_location})
        self.gcode_location = gcode_location


def design(metadata: dict[str, object],
              instr: str | None = None) -> VirtualWorldObject:
    if instr:
        instruction(instr)

    obj = VirtualWorldObject(metadata)

    return obj