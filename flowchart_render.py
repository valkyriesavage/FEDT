import inspect
import io
from contextlib import redirect_stdout
import math
import os
import textwrap

from graphviz import Digraph
from PIL import Image
import xml.etree.ElementTree as ET

indent = 0
shutup = True
DEFAULT = -1234567890

id_counter = 0
def next_id():
    global id_counter
    id_counter += 1
    return f"node{id_counter}"

def create_styled_node(dot, label, parent=None, is_header=False, block_type=None, invisible=False, max_char_width=150):
    global indent
    if not shutup:
        print(' '*(indent+4) + f'making a node: {label}, with parent {parent}')

    # this is something weird coming from having ''' '''-type multiline literals :shrug:
    label = label.replace("\\n', '",'').strip()

    if len(label) > max_char_width:
        # let's make some newlines, awwwwwww yeahhhhhhhh
        label = textwrap.fill(label, max_char_width)

    # Set node attributes based on type and whether it's a header
    #label = '<<b>{}</b>>'.format(label) if is_header else label # sadly we can't make this work with textwrap
    style = 'invis' if invisible else 'filled'
    shape = 'rectangle'
    width = '2'
    
    color = 'white' if is_header else 'lightgrey'
    # if block_type == 'fabricate':
    #     color = 'lightblue'
    # elif block_type == 'measure':
    #     color = 'lightgreen'
    # elif block_type == 'converge':
    #     color = 'orange'

    new_id = next_id()
    dot.node(new_id, label, style=style, shape=shape, fillcolor=color, width=width)
    if parent:
        dot.edge(parent, new_id)
        if not shutup:
            print(' '*(indent+4) + f'\tmaking parent edge from {new_id} to {parent}')
    if not shutup:
        print(' '*(indent+4) + f'\tnew node id is {new_id}')
    return new_id

def generate_fake_node(node_list, item_type="par"):
    class FakeNode:
        def __init__(self, text, item_type="par"):
            self.text = text
            self.item_type = item_type
            # is this the best way to do it? probably not. but that's fine.
            self.node = ET.ElementTree(ET.fromstring(f'''<{item_type}-item>
<header>Repeat for {text}</header></{item_type}-item>
''')).getroot()

    def summarize_nodes(node_list):
        # we want to just look at the headers
        summarize = []
        for node in node_list:
            summarize.append(node.find('header').text.split("Loop for ")[-1])
        summary = ", ".join(summarize) + "..."
        is_numerical_sequence = True
        last = DEFAULT
        num = DEFAULT
        step = DEFAULT
        mult = DEFAULT
        for tag in summarize:
            try:
                num = float(tag)
            except:
                # whoops, not a number
                is_numerical_sequence = False
                break
            if last == DEFAULT: # first loop, set the 'last'
                last = num
                continue
            if step == DEFAULT: # second loop, find the 'step'/'mult'
                step = num - last
                mult = num / last
                last = num
                continue
            this_step = num - last
            try:
                this_mult = num/last
            except ZeroDivisionError:
                this_mult = 0
            if not (math.isclose(this_step, step) or math.isclose(this_mult, mult)): # future loops, check the step/mult
                is_numerical_sequence = False
                break
            last = num
        if is_numerical_sequence and len(summarize) > 3:
            summary = "{}, {}, ... {}".format(summarize[0], summarize[1], summarize[-1])
        return summary

    fakenode = FakeNode(summarize_nodes(node_list), item_type).node
    return fakenode

def process_in_series(dot, parent, series_node, pare_down=True):
    global indent
    if not shutup:
        print(' '*indent + f'making series nodes for parent {parent}')
    last_node_created = parent
    nodes = series_node.findall('series-item')

    if pare_down and len(nodes) > 4:
        # note that the -2th node is the last "real" node. the -1th node is just the "</par-item>" thing, for some reason.
        summary_node = generate_fake_node(nodes[2:-1], item_type="series")
        nodes = [nodes[0], nodes[1], summary_node, nodes[-1]]

    for series_item in nodes:
        if not len([child for child in series_item]):
            continue # some bug

        indent += 4
        tmp = build_flowchart_recursive(dot, series_item, last_node_created, pare_down=pare_down)
        indent -= 4

        last_node_created = tmp

    return last_node_created

def process_in_parallel(dot, parent, parallel_node, pare_down=True):
    global indent
    if not shutup:
        print(' '*indent + f'making parallel nodes for parent {parallel_node.tag}')

    nodes = parallel_node.findall('par-item')

    if pare_down and len(nodes) > 4:
        # note that the -2th node is the last "real" node. the -1th node is just the "</par-item>" thing, for some reason.
        summary_node = generate_fake_node(nodes[2:-1], item_type="par")
        nodes = [nodes[0], nodes[1], summary_node, nodes[-1]]
    
    parallel_end_nodes = []
    for par_item in nodes:
        if not len([child for child in par_item]):
            continue # some bug

        indent += 4
        last_node_created = build_flowchart_recursive(dot, par_item, parent, pare_down=pare_down)
        indent -= 4

        parallel_end_nodes.append(last_node_created)

    converge_node_id = create_styled_node(dot, 'Converge', block_type='converge')
    for end_node in parallel_end_nodes:
        if not shutup:
            print(' '*indent + f'making a parent edge from {last_node_created} to {converge_node_id} (converge)')
        dot.edge(end_node, converge_node_id)

    return converge_node_id

def process_while(dot, parent, while_node, pare_down=True):
    global indent
    if not shutup:
        print(' '*indent + f'making while nodes for parent {while_node.tag}')
    parallel_end_nodes = []
    # add a condition node
    condition_node = create_styled_node(dot, 'do while ' + while_node.attrib.get('condition'), parent=parent)

    last_node_created = condition_node
    for loop_item in while_node.findall('loop-item'):
        if not len([child for child in loop_item]):
            continue # some bug

        indent += 4
        last_node_created = build_flowchart_recursive(dot, loop_item, last_node_created, pare_down=pare_down)
        indent -= 4

    # loop back up to the condition
    if not shutup:
        print(' '*indent + f'making a parent edge from {last_node_created} to {condition_node}')
    dot.edge(last_node_created, condition_node)

    return last_node_created

def build_flowchart_recursive(dot, node, current_parent, pare_down=True):
    last_id = current_parent
    global indent
    if not shutup:
        print(' '*indent + f'exploring {node.tag}: {node.text.strip() if node.text else ""} ; parent: {current_parent}')

    # process the node
    if node.tag in ['instruction','note','header']:
        last_id = create_styled_node(dot, node.text, is_header=node.tag=='header', parent=current_parent) # TODO some weird artefact text generated in some places, not sure why
    elif node.tag == 'in-series':
        last_id = process_in_series(dot, current_parent, node, pare_down=pare_down)
    elif node.tag == 'in-parallel':
        last_id = process_in_parallel(dot, current_parent, node, pare_down=pare_down)
    elif node.tag == 'loop':
        last_id = process_while(dot, current_parent, node, pare_down=pare_down)
    elif node.tag in ['par-item','series-item']:
        if not shutup:
            print(' ' * indent + f'keeping parent: {current_parent}')
        last_id = current_parent
    else:
        if not shutup:
            print(' ' * indent + f'unknown tag: {node.tag}, keeping parent: {current_parent}')
        last_id = current_parent

    # process sequential children
    if not node.tag in ['in-series','in-parallel','loop']:
        if not shutup:
            print(' '*indent + f'now looking at children of {node.tag}: {node.text.strip() if node.text else ""}')
        for item in node:
            indent += 4
            tmp = build_flowchart_recursive(dot, item, last_id, pare_down=pare_down)
            indent -= 4
            # dot.edge(tmp, last_id)
            last_id = tmp

    return last_id

def build_flowchart(xml_root, pare_down=True):
    dot = Digraph(comment='Flowchart')
    dot.attr(rankdir='TB')  # Top-to-Bottom flow direction
    
    # Add "experiment start" block
    start_node_id = create_styled_node(dot, 'Experiment Start', block_type='start')
    current_parent = start_node_id
    
    current_parent = build_flowchart_recursive(dot, xml_root, current_parent, pare_down=pare_down) 

    # Add "experiment end" block
    end_node_id = create_styled_node(dot, 'Experiment End', parent=current_parent, block_type='end')
    
    return dot


def render_flowchart(capture_function, pdf=False, remove=True, pare_down=True):

    f = io.StringIO()
    with redirect_stdout(f):                 
        print(capture_function())
    xml_location = f.getvalue().split(' to ')[-1].split('\n')[0]
    xml_content = ''
    with open(xml_location) as f:
        xml_content = f.readlines()
    if remove:
        os.remove(xml_location)
    xml_content = f"<data>{xml_content}</data>"

    # Parse the XML
    xml_root = ET.fromstring(xml_content)

    # Build the flowchart
    flowchart = build_flowchart(xml_root, pare_down=pare_down)

    # Save the flowchart
    if pdf:
        fname = f'expt_flowcharts/{capture_function.__name__}_flowchart'
        flowchart.render(fname, format='pdf', cleanup=True)

        from pdf2image import convert_from_path
        # Display the flowchart
        im=convert_from_path(fname + '.pdf')[0]
        im.show()
    else:
        fname = f'expt_flowcharts/{capture_function.__name__}_flowchart'
        flowchart.render(fname, format='png', cleanup=True)

        # Display the flowchart
        im=Image.open(fname + '.png')
        im.show()