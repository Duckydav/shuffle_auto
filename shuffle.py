
# ----------------------------------------------------------------------------------------------------------
# Shuffle auto v1.0
# Author: David Francois
# Copyright (c) 2024, David Francois




# ----------------------------------------------------------------------------------------------------------
# modules
# ----------------------------------------------------------------------------------------------------------


import nuke
from PySide2.QtCore import QTimer

# Define the timer and double-click state
click_timer = QTimer()
click_timer.setSingleShot(True)  # Ensure the timer is in singleShot mode
is_double_click = False
knob_callback_short = None  # Callback for single-click updates
knob_callback_long = None   # Callback for double-click updates

# Connect to the timer for single-click
click_timer.timeout.connect(lambda: single_click())

# ----------------------------------------------------------------------------------------------------------

def setup_short_callback(node):
    """
    Set up a callback on the Shuffle2 node to dynamically update the label
    using to_label_short whenever the node's inputs or mappings change.
    """
    global knob_callback_short

    def knob_changed_callback_short():
        # Update the label dynamically using to_label_short for single-click
        to_label_short(node)

    # Remove existing short callback if any, and add new one
    remove_short_callback(node)
    knob_callback_short = knob_changed_callback_short
    nuke.addKnobChanged(knob_callback_short, node=node)

def setup_long_callback(node):
    """
    Set up a callback on the Shuffle2 node to dynamically update the label
    using to_label whenever the node's inputs or mappings change (double-click).
    """
    global knob_callback_long

    def knob_changed_callback_long():
        # Update the label dynamically using to_label for double-click
        to_label(node)

    # Remove existing long callback if any, and add new one
    remove_long_callback(node)
    knob_callback_long = knob_changed_callback_long
    nuke.addKnobChanged(knob_callback_long, node=node)

def remove_short_callback(node):
    """
    Remove the callback for the single-click action (to_label_short).
    """
    global knob_callback_short
    if knob_callback_short:
        nuke.removeKnobChanged(knob_callback_short, node=node)
        knob_callback_short = None

def remove_long_callback(node):
    """
    Remove the callback for the double-click action (to_label).
    """
    global knob_callback_long
    if knob_callback_long:
        nuke.removeKnobChanged(knob_callback_long, node=node)
        knob_callback_long = None

def get():
    """
    This function is called on a double-click and applies the long label.
    """
    try:
        node = nuke.selectedNode()
    except:
        nuke.message("Please select a Shuffle2")
        return

    if node.Class() != "Shuffle2":
        nuke.error("Please select a Shuffle2")
        return

    # Ensure the short callback is removed, and apply long label
    remove_short_callback(node)
    to_label(node)  # Call to_label on double-click
    setup_long_callback(node)  # Setup long callback if needed for double-click

def get_short():
    """
    This function is called on a single-click and applies the short label.
    """
    try:
        node = nuke.selectedNode()
    except:
        nuke.message("Please select a Shuffle2")
        return

    if node.Class() != "Shuffle2":
        nuke.error("Please select a Shuffle2")
        return

    # Ensure the long callback is removed, and apply short label
    remove_long_callback(node)
    to_label_short(node)  # Call to_label_short on single-click
    setup_short_callback(node)  # Setup short callback for dynamic updates on single-click

def single_click():
    """
    Function to handle single click, calling the short label function.
    """
    global is_double_click
    print("single_click() called")
    print(f"is_double_click: {is_double_click}")
    if not is_double_click:
        print("Calling get_short() from single_click()")
        get_short()  # Call get_short on single-click
    is_double_click = False

def double_click():
    """
    Function to handle double-click, calling the long label function.
    """
    global is_double_click
    print("double_click() called")
    print("Calling get() from double_click()")

    get()  # Call get on double-click
    is_double_click = False
    print(f"is_double_click set to: {is_double_click}")

def run():
    """
    Entry point function that handles both single and double clicks.
    """
    global is_double_click
    if click_timer.isActive():  # If the timer is already running, it means this is a double-click
        is_double_click = True
        click_timer.stop()
        double_click()
    else:
        click_timer.start(500)  # Start the timer and wait for a possible double-click

def to_label(node):
    mappings = node["mappings"].value()
    label = ""
    input = ['A', 'B']

    def index(value):
        if "{" in value and "}" in value:
            return int(value.split("{")[1].split("}")[0])
        return 0

    fromInput1 = input[1 - index(node['fromInput1'].value())]
    fromInput2 = input[1 - index(node['fromInput2'].value())]

    channel_shortcuts = {
        "red": "r",
        "green": "g",
        "blue": "b",
        "alpha": "a",
        "X": "x",
        "Y": "y",
        "Z": "z",
        "u": "u",
        "v": "v"
    }

    connections = {"A": {}, "B": {}}
    for mapping in mappings:
        if mapping[0] == -1 and mapping[1] == 'black':
            continue

        for channel in channel_shortcuts:
            if mapping[1].endswith(f".{channel}"):
                in_channel = channel_shortcuts[channel]
                input_key = fromInput1 if mapping[0] == 0 else fromInput2
                input_layer = mapping[1].split('.')[0]
                out_channel = channel_shortcuts[mapping[2].split('.')[-1]]
                output_layer = mapping[2].split('.')[0]

                if input_layer not in connections[input_key]:
                    connections[input_key][input_layer] = {"in_channels": "", "out_channels": {}}
                connections[input_key][input_layer]["in_channels"] += in_channel
                if output_layer not in connections[input_key][input_layer]["out_channels"]:
                    connections[input_key][input_layer]["out_channels"][output_layer] = ""
                connections[input_key][input_layer]["out_channels"][output_layer] += out_channel

    if fromInput1 == 'B' and fromInput2 == 'B' and node['in2'].value() == 'none':
        for input_key, layers in connections.items():
            for input_layer, details in layers.items():
                in_channels = details["in_channels"]
                for output_layer, out_channels in details["out_channels"].items():
                    input_display = input_layer if input_layer != "rgba" else in_channels
                    output_display = out_channels if output_layer == "rgba" else output_layer
                    label += f"{input_layer}.{in_channels} = {output_layer}.{out_channels}\n"
    else:
        for input_key in ["B", "A"]:
            layers = connections[input_key]
            for input_layer, details in layers.items():
                in_channels = details["in_channels"]
                for output_layer, out_channels in details["out_channels"].items():
                    input_display = input_layer if input_layer != "rgba" else in_channels
                    output_display = out_channels if output_layer == "rgba" else output_layer
                    label += f"{input_key}➞{input_layer}.{in_channels} = {output_layer}.{out_channels}\n"

    max_length_per_line = 50
    lines = label.split('\n')
    wrapped_label = ""
    for line in lines:
        while len(line) > max_length_per_line:
            wrapped_label += line[:max_length_per_line] + "\n"
            line = line[max_length_per_line:]
        wrapped_label += line + "\n"

    # Print the generated label for debugging
    print("Generated label in to_label:\n", wrapped_label.strip())


    node['label'].setValue(wrapped_label.strip())

def to_label_short(node):
    mappings = node["mappings"].value()
    # print(f"mappings: {mappings}")
    label = ""
    input = ['A', 'B']

    def index(value):
        if "{" in value and "}" in value:
            return int(value.split("{")[1].split("}")[0])
        return 0

    fromInput1 = input[1 - index(node['fromInput1'].value())]
    fromInput2 = input[1 - index(node['fromInput2'].value())]

    channel_shortcuts = {
        "red": "r",
        "green": "g",
        "blue": "b",
        "alpha": "a",
        "X": "x",
        "Y": "y",
        "Z": "z",
        "u": "u",
        "v": "v",
        "front": "front",
        "back": "back"
    }

    connections = {"A": {}, "B": {}}
    for mapping in mappings:
        if mapping[0] == -1 and mapping[1] == 'black':
            continue

        for channel in channel_shortcuts:
            if mapping[1].endswith(f".{channel}"):
                input_key = fromInput1 if mapping[0] == 0 else fromInput2
                input_layer = mapping[1].split('.')[0]
                in_channel = channel_shortcuts[channel]
                output_layer = mapping[2].split('.')[0]
                out_channel = channel_shortcuts[mapping[2].split('.')[-1]]

                if input_layer not in connections[input_key]:
                    connections[input_key][input_layer] = {"in_channels": "", "out_channels": {}}
                connections[input_key][input_layer]["in_channels"] += in_channel
                if output_layer not in connections[input_key][input_layer]["out_channels"]:
                    connections[input_key][input_layer]["out_channels"][output_layer] = ""
                connections[input_key][input_layer]["out_channels"][output_layer] += out_channel

    if fromInput1 == 'B' and fromInput2 == 'B' and node['in2'].value() == 'none':
        for input_key, layers in connections.items():
            for input_layer, details in layers.items():
                in_channels = details["in_channels"]
                for output_layer, out_channels in details["out_channels"].items():
                    input_display = input_layer if input_layer != "rgba" else in_channels
                    output_display = out_channels if output_layer == "rgba" else output_layer
                    label += f"{input_display} = {output_display}\n"
    else:
        for input_key in ["B", "A"]:
            layers = connections[input_key]
            for input_layer, details in layers.items():
                in_channels = details["in_channels"]
                for output_layer, out_channels in details["out_channels"].items():
                    input_display = input_layer if input_layer != "rgba" else in_channels
                    output_display = out_channels if output_layer == "rgba" else output_layer
                    label += f"{input_key}➞{input_display} = {output_display}\n"

    max_length_per_line = 50
    lines = label.split('\n')
    wrapped_label = ""
    for line in lines:
        while len(line) > max_length_per_line:
            wrapped_label += line[:max_length_per_line] + "\n"
            line = line[max_length_per_line:]
        wrapped_label += line + "\n"

    # Print the generated label for debugging
    print("Generated label in to_label_short:\n", wrapped_label.strip())


    node['label'].setValue(wrapped_label.strip())
