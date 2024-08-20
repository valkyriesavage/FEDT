import inspect
import io
from contextlib import redirect_stdout

from graphviz import Digraph
from PIL import Image
import xml.etree.ElementTree as ET

indent = 0
shutup = True

id_counter = 0
def next_id():
    global id_counter
    id_counter += 1
    return f"node{id_counter}"

def parse_xml(file):
    tree = ET.parse(file)
    root = tree.getroot()
    return root

def create_styled_node(dot, label, parent=None, is_header=False, block_type=None):
    global indent
    if not shutup:
        print(' '*(indent+4) + f'making a node: {label}, with parent {parent}')
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

    new_id = next_id()
    dot.node(new_id, label, style=style, shape=shape, fillcolor=color, width=width)
    if parent:
        dot.edge(parent, new_id)
    if not shutup:
        print(' '*(indent+4) + f'\tnew node id is {new_id}')
    return new_id

def process_in_series(dot, parent, series_node):
    global indent
    if not shutup:
        print(' '*indent + f'making series nodes for parent {series_node}')
    last_node_created = parent
    for series_item in series_node.findall('series-item'):
        if not len([child for child in series_item]):
            continue # some bug

        indent += 4
        tmp = build_flowchart_recursive(dot, series_item, last_node_created)
        indent -= 4
        dot.edge(tmp, last_node_created)
        last_node_created = tmp

    return last_node_created

def process_in_parallel(dot, parent, parallel_node):
    global indent
    if not shutup:
        print(' '*indent + f'making parallel nodes for parent {parallel_node.tag}')
    parallel_end_nodes = []
    for par_item in parallel_node.findall('par-item'):
        if not len([child for child in par_item]):
            continue # some bug

        indent += 4
        last_node_created = build_flowchart_recursive(dot, par_item, parent)
        indent -= 4

        parallel_end_nodes.append(last_node_created)

    converge_node_id = create_styled_node(dot, 'Converge', block_type='converge')
    for end_node in parallel_end_nodes:
        dot.edge(end_node, converge_node_id)

    return converge_node_id

def build_flowchart_recursive(dot, node, current_parent):
    last_id = None
    global indent
    if not shutup:
        print(' '*indent + f'exploring {node.tag}: {node.text}')

    # process the node
    if node.tag in ['instruction','note','header']:
        last_id = create_styled_node(dot, node.text.strip(), parent=current_parent)
    elif node.tag == 'in-series':
        last_id = process_in_series(dot, current_parent, node)
    elif node.tag == 'in-parallel':
        last_id = process_in_parallel(dot, current_parent, node)
    elif node.tag in ['par-item','series-item']:
        last_id = current_parent
    else:
        if not shutup:
            print(f'{node.tag}')
        last_id = current_parent

    # process sequential children
    if not node.tag in ['in-series','in-parallel']:
        for item in node:
            if not shutup:
                print(' '*indent + f'now looking at children of {node.tag}: {node.text}')
            indent += 4
            tmp = build_flowchart_recursive(dot, item, last_id)
            indent -= 4
            # dot.edge(tmp, last_id)
            last_id = tmp

    return last_id

def build_flowchart(xml_root):
    dot = Digraph(comment='Flowchart')
    dot.attr(rankdir='TB')  # Top-to-Bottom flow direction
    
    # Add "experiment start" block
    start_node_id = create_styled_node(dot, 'Experiment Start', block_type='start')
    current_parent = start_node_id
    
    current_parent = build_flowchart_recursive(dot, xml_root, current_parent) 

    # Add "experiment end" block
    end_node_id = create_styled_node(dot, 'Experiment End', parent=current_parent, block_type='end')
    
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

sample_simple = '''
<in-parallel>
    <par-item>
        <header>Loop for concentric</header>
        <in-parallel>
            <par-item>
                <header>Loop for 0</header>
                <instruction>Slice expt_stls/cube.stl.</instruction>
                <instruction>Run the printer, creating object #0</instruction>
            </par-item>
            <par-item>
                <header>Loop for 1</header>
                <instruction>Slice expt_stls/cube.stl.</instruction>
                <instruction>Run the printer, creating object #1</instruction>
            </par-item>
        </in-parallel>
    </par-item>
    <par-item>
        <header>Loop for line</header>
        <in-parallel>
            <par-item>
                <header>Loop for 0</header>
                <instruction>Slice expt_stls/cube.stl.</instruction>
                <instruction>Run the printer, creating object #2</instruction>
            </par-item>
            <par-item>
                <header>Loop for 1</header>
                <instruction>Slice expt_stls/cube.stl.</instruction>
                <instruction>Run the printer, creating object #3</instruction>
            </par-item>
        </in-parallel>
    </par-item>
</in-parallel>
<instruction>Fill out the csv for 0 objects ([]) and 0 measurements ([]) (0 datapoints).</instruction>
'''