from instruction import instruction
from measurement import Measurement, Measurements
from fabricate import fabricate, RealWorldObject
from dataclasses import dataclass


@dataclass
class LineFile:
    pass


class SvgEditor:

    @staticmethod
    def design() -> LineFile:
        instruction("Get the line file from the website.")
        return LineFile()


class LaserSlicer:

    @staticmethod
    def cam_and_fab(line_file: LineFile,
                    focal_offset_height_mm: int) -> RealWorldObject:

        def cam():
            # TODO Actually set up settings
            instruction("Add the settings to Visicut.")

        # @fedt_fabricate(instruction="Run the laser cutter.")
        def fab():
            from control import MODE, Execute
            if isinstance(MODE, Execute):
                pass
            instruction("Run the laser cutter.")
            return fabricate({
                "line_file": line_file,
                "focal_offset_height_mm": focal_offset_height_mm
            })

        cam()
        return fab()


class Multimeter:
    resistance = Measurement(
        name="resistance",
        description="The resistance of the object after charring.",
        procedure="""
            Use a multimeter to measure the resistance, with one probe
            at one end of the channel and one at the other.
            """,
        units="ohms")

    @staticmethod
    def measure_resistance(obj: RealWorldObject) -> Measurements:
        instruction(f"Measure object #{obj.uid}.", header=True)
        instruction(Multimeter.resistance.procedure)
        return Measurements.single(obj, Multimeter.resistance)
