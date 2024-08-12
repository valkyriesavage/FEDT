import xml.etree.ElementTree as ET
from graphviz import Digraph

def parse_xml(file):
    tree = ET.parse(file)
    root = tree.getroot()
    return root

def style_node(dot, node_id, label, is_header=False, block_type=None):
    # Set node attributes based on type and whether it's a header
    style = 'filled,bold' if is_header else 'filled'
    shape = 'rectangle'
    width = '2'
    
    color = 'lightgrey'
    if block_type == 'fabricate':
        color = 'lightblue'
    elif block_type == 'measure':
        color = 'lightgreen'
    elif block_type == 'converge':
        color = 'orange'
    
    dot.node(node_id, label, style=style, shape=shape, fillcolor=color, width=width)

def process_instruction(dot, parent, instruction, node_id, block_type=None):
    style_node(dot, node_id, instruction, block_type=block_type)
    if parent:
        dot.edge(parent, node_id)

def process_in_series(dot, parent, series_node, id_counter):
    current_parent = parent
    for series_item in series_node.findall('series-item'):
        for child in series_item:
            if child.tag == 'header':
                node_id = f'node{id_counter}'
                id_counter += 1
                style_node(dot, node_id, child.text.strip(), is_header=True)
                if current_parent:
                    dot.edge(current_parent, node_id)
                current_parent = node_id
            elif child.tag == 'instruction':
                node_id = f'node{id_counter}'
                id_counter += 1
                process_instruction(dot, current_parent, child.text.strip(), node_id, block_type='measure')
                current_parent = node_id
    return id_counter, current_parent

def process_in_parallel(dot, parent, parallel_node, id_counter):
    parallel_end_nodes = []
    for par_item in parallel_node.findall('par-item'):
        current_parent = parent
        for child in par_item:
            if child.tag == 'header':
                node_id = f'node{id_counter}'
                id_counter += 1
                style_node(dot, node_id, child.text.strip(), is_header=True)
                if current_parent:
                    dot.edge(current_parent, node_id)
                current_parent = node_id
            elif child.tag == 'instruction':
                node_id = f'node{id_counter}'
                id_counter += 1
                process_instruction(dot, current_parent, child.text.strip(), node_id, block_type='fabricate')
                current_parent = node_id
        parallel_end_nodes.append(current_parent)

    # Create a converging node after parallel branches
    converge_node_id = f'node{id_counter}'
    style_node(dot, converge_node_id, 'Converge', block_type='converge')
    for end_node in parallel_end_nodes:
        dot.edge(end_node, converge_node_id)
    id_counter += 1

    return id_counter, converge_node_id

def build_flowchart(xml_root):
    dot = Digraph(comment='Flowchart')
    dot.attr(rankdir='TB')  # Top-to-Bottom flow direction
    id_counter = 0
    
    # Add "experiment start" block
    start_node_id = f'node{id_counter}'
    style_node(dot, start_node_id, 'Experiment Start', block_type='start')
    parent = start_node_id
    id_counter += 1
    
    for element in xml_root:
        if element.tag == 'instruction':
            node_id = f'node{id_counter}'
            id_counter += 1
            process_instruction(dot, parent, element.text.strip(), node_id)
            parent = node_id  # Set the current node as parent for the next instruction
        elif element.tag == 'in-series':
            id_counter, parent = process_in_series(dot, parent, element, id_counter)
        elif element.tag == 'in-parallel':
            id_counter, parent = process_in_parallel(dot, parent, element, id_counter)

    # Add "experiment end" block
    end_node_id = f'node{id_counter}'
    style_node(dot, end_node_id, 'Experiment End', block_type='end')
    dot.edge(parent, end_node_id)
    
    return dot

# Put the xml between the <data> header

xml_content = """
<data>
<in-parallel><par-item>
<header>Loop for TODO</header>
<instruction>slice large obj from thingiverse.stl in the slicing software</instruction>
<instruction>Slice the file.</instruction>
<instruction>Run the printer.</instruction>
<instruction>do hold a light above the object to object #0</instruction>
<header>Measure object #1.</header>
<instruction>
            Take a photo of the object showing bottom.
            </instruction></par-item><par-item>
<header>Loop for TODO</header>
<instruction>slice large obj from thingiverse.stl in the slicing software</instruction>
<instruction>Slice the file.</instruction>
<instruction>Run the printer.</instruction>
<instruction>do hold a light above the object to object #2</instruction>
<header>Measure object #3.</header>
<instruction>
            Take a photo of the object showing bottom.
            </instruction></par-item><par-item>
<header>Loop for TODO</header>
<instruction>slice large obj from thingiverse.stl in the slicing software</instruction>
<instruction>Slice the file.</instruction>
<instruction>Run the printer.</instruction>
<instruction>do hold a light above the object to object #4</instruction>
<header>Measure object #5.</header>
<instruction>
            Take a photo of the object showing bottom.
            </instruction></par-item><par-item>
<header>Loop for TODO</header>
<instruction>slice large obj from thingiverse.stl in the slicing software</instruction>
<instruction>Slice the file.</instruction>
<instruction>Run the printer.</instruction>
<instruction>do hold a light above the object to object #6</instruction>
<header>Measure object #7.</header>
<instruction>
            Take a photo of the object showing bottom.
            </instruction></par-item><par-item>
<header>Loop for TODO</header>
<instruction>slice large obj from thingiverse.stl in the slicing software</instruction>
<instruction>Slice the file.</instruction>
<instruction>Run the printer.</instruction>
<instruction>do hold a light above the object to object #8</instruction>
<header>Measure object #9.</header>
<instruction>
            Take a photo of the object showing bottom.
            </instruction></par-item><par-item>
<header>Loop for TODO</header>
<instruction>slice large obj from thingiverse.stl in the slicing software</instruction>
<instruction>Slice the file.</instruction>
<instruction>Run the printer.</instruction>
<instruction>do hold a light above the object to object #10</instruction>
<header>Measure object #11.</header>
<instruction>
            Take a photo of the object showing bottom.
            </instruction></par-item><par-item>
<header>Loop for TODO</header>
<instruction>slice large obj from thingiverse.stl in the slicing software</instruction>
<instruction>Slice the file.</instruction>
<instruction>Run the printer.</instruction>
<instruction>do hold a light above the object to object #12</instruction>
<header>Measure object #13.</header>
<instruction>
            Take a photo of the object showing bottom.
            </instruction></par-item><par-item>
<header>Loop for TODO</header>
<instruction>slice large obj from thingiverse.stl in the slicing software</instruction>
<instruction>Slice the file.</instruction>
<instruction>Run the printer.</instruction>
<instruction>do hold a light above the object to object #14</instruction>
<header>Measure object #15.</header>
<instruction>
            Take a photo of the object showing bottom.
            </instruction></par-item><par-item>
<header>Loop for TODO</header>
<instruction>slice large obj from thingiverse.stl in the slicing software</instruction>
<instruction>Slice the file.</instruction>
<instruction>Run the printer.</instruction>
<instruction>do hold a light above the object to object #16</instruction>
<header>Measure object #17.</header>
<instruction>
            Take a photo of the object showing bottom.
            </instruction></par-item><par-item>
<header>Loop for TODO</header>
<instruction>slice large obj from thingiverse.stl in the slicing software</instruction>
<instruction>Slice the file.</instruction>
<instruction>Run the printer.</instruction>
<instruction>do hold a light above the object to object #18</instruction>
<header>Measure object #19.</header>
<instruction>
            Take a photo of the object showing bottom.
            </instruction></par-item><par-item>
<header>Loop for TODO</header>
<instruction>slice medium obj from thingiverse.stl in the slicing software</instruction>
<instruction>Slice the file.</instruction>
<instruction>Run the printer.</instruction>
<instruction>do hold a light above the object to object #20</instruction>
<header>Measure object #21.</header>
<instruction>
            Take a photo of the object showing bottom.
            </instruction></par-item><par-item>
<header>Loop for TODO</header>
<instruction>slice medium obj from thingiverse.stl in the slicing software</instruction>
<instruction>Slice the file.</instruction>
<instruction>Run the printer.</instruction>
<instruction>do hold a light above the object to object #22</instruction>
<header>Measure object #23.</header>
<instruction>
            Take a photo of the object showing bottom.
            </instruction></par-item><par-item>
<header>Loop for TODO</header>
<instruction>slice medium obj from thingiverse.stl in the slicing software</instruction>
<instruction>Slice the file.</instruction>
<instruction>Run the printer.</instruction>
<instruction>do hold a light above the object to object #24</instruction>
<header>Measure object #25.</header>
<instruction>
            Take a photo of the object showing bottom.
            </instruction></par-item><par-item>
<header>Loop for TODO</header>
<instruction>slice medium obj from thingiverse.stl in the slicing software</instruction>
<instruction>Slice the file.</instruction>
<instruction>Run the printer.</instruction>
<instruction>do hold a light above the object to object #26</instruction>
<header>Measure object #27.</header>
<instruction>
            Take a photo of the object showing bottom.
            </instruction></par-item><par-item>
<header>Loop for TODO</header>
<instruction>slice medium obj from thingiverse.stl in the slicing software</instruction>
<instruction>Slice the file.</instruction>
<instruction>Run the printer.</instruction>
<instruction>do hold a light above the object to object #28</instruction>
<header>Measure object #29.</header>
<instruction>
            Take a photo of the object showing bottom.
            </instruction></par-item><par-item>
<header>Loop for TODO</header>
<instruction>slice medium obj from thingiverse.stl in the slicing software</instruction>
<instruction>Slice the file.</instruction>
<instruction>Run the printer.</instruction>
<instruction>do hold a light above the object to object #30</instruction>
<header>Measure object #31.</header>
<instruction>
            Take a photo of the object showing bottom.
            </instruction></par-item></in-parallel>
<instruction>Fill out the measurements for objects [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31] and measurements [photograph:bottom].</instruction>    
</data>
"""

# Parse the XML
xml_root = ET.fromstring(xml_content)

# Build the flowchart
flowchart = build_flowchart(xml_root)

# Save and display the flowchart, it saves in the same directory in normal quality
# flowchart.render('flowchart-output', format='png', cleanup=True)

# If wanted a higher resolution chart use this
# Render the graph with higher resolution
output_path = 'flowchart_hd.png'  # Save to the current directory
flowchart.attr(dpi='1200')  # Set the DPI for higher resolution
flowchart.render(output_path, format='png', cleanup=True)

# Added a print statement after done
print(f"Flow chart generated and saved as '{output_path}' with higher quality")
