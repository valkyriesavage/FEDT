# FEDT
Fabrication Experimentation Design Tool

## running the demos in the folder

To run the demos in this folder, install PIL and graphviz. The best example to look at first is demo_studies.py : this file has the samples that we shared with our user study participants. The file can be run with `python demo_studies.py` on the command line.

To change which sample study is being run, edit the `if __name__ == '__main__'` block in the code, commenting out anything you do not wish to run, and uncommenting anything you do wish to run.

Calling a study with `render_flowchart(study_function)` will render a flowchart of the experiment. Calling a function bare as `study_function()` will render the flowchart XML to the commandline.

Execute mode is triggered with `control.MODE = Execute()`.

## dependencies

* PIL (for flowchart visualization)
* graphviz (for flowchart visualization)
* drawsvg (for doing svg authoring, only if you use those modules)
* freecad (for doing stl authoring, only if you use those modules)
