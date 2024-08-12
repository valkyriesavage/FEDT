import inspect
import io
from contextlib import redirect_stdout

from graphviz import Digraph
from PIL import Image
import xml.etree.ElementTree as ET

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


def render_flowchart(capture_function = None):

    f = io.StringIO()
    with redirect_stdout(f):                 
        print(capture_function())
    xml_content = f.getvalue()
    xml_content = f"<data>{xml_content}</data>"

    print(xml_content)

    # Parse the XML
    xml_root = ET.fromstring(xml_content)

    # Build the flowchart
    flowchart = build_flowchart(xml_root)

    # Save the flowchart
    fname = f'expt_flowcharts/{capture_function.__name__}_flowchart'
    flowchart.render(fname, format='png', cleanup=True)

    # Display the flowchart
    im=Image.open(fname + '.png')
    im.show()