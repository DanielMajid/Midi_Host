# Libraries
import time
import mido

# Defining dictionaries, sets, and time constants
open_inputs = {}
open_outputs = {}

known_inputs = set()
known_outputs = set()

scan_interval = 1.0
last_scan = 0.0

# Identifies if recognized port is an internal (ignored) or external port
def is_internal_port(name):
    return (
        name.startswith("RtMidiIn Client:")
        or name.startswith("RtMidiOut Client:")
    )

# opens all available inputs
def open_input(device):
    print("Opening input:", device)

    try:
        port = mido.open_input(device)
        open_inputs[device] = port

    except Exception as error:
        print("Failed to open input:", device)
        print("Error:", error)

#opens all available outputs 
def open_output(device):
    print("Opening output:", device)

    try:
        port = mido.open_output(device)
        open_outputs[device] = port

    except Exception as error:
        print("Failed to open output:", device)
        print("Error:", error)

#closes all available inputs and deletes name from dictionary
def close_input(device):
    print("Closing input:", device)

    port = open_inputs.get(device)

    if port is not None:
        try:
            port.close()

        except Exception as error:
            print("Error closing input:", device)
            print("Error:", error)

        del open_inputs[device]

#closes all available outputs an deletes name from dictionary
def close_output(device):
    print("Closing output:", device)

    port = open_outputs.get(device)

    if port is not None:
        try:
            port.close()

        except Exception as error:
            print("Error closing output:", device)
            print("Error:", error)

        del open_outputs[device]

def scan_devices():
    global known_inputs
    global known_outputs

# adds names of current inputs and outputs to "current" set
    current_inputs = {
        name
        for name in mido.get_input_names()
        if not is_internal_port(name)
    }

    current_outputs = {
        name
        for name in mido.get_output_names()
        if not is_internal_port(name)
    }

    added_inputs = current_inputs - known_outputs
    removed_inputs = known_inputs - current_inputs

    added_outputs = current_outputs - known_outputs
    removed_outputs = known_outputs - current_outputs

    for device in added_inputs:
        open_input(device)

    for device in removed_inputs:
        close_input(device)

    for device in added_outputs:
        open_output(device)

    for device in removed_outputs:
        close_output(device)

    known_inputs = current_inputs
    known_outputs = current_outputs


def route_messages():
    for input_name in list(open_inputs):
        input_port = open_inputs[input_name]

        try:
            messages = list(input_port.iter_pending())

        except Exception as error:
            print("Read error:", input_name)
            print("Error:", error)
            continue

        for message in messages:
            print(input_name, "->", message)

            for output_name in list(open_outputs):
                if output_name == input_name:
                    continue

                output_port = open_outputs[output_name]

                try:
                    output_port.send(message)

                except Exception as error:
                    print("Send error:", output_name)
                    print("Error:", error)

def close_all_ports():

    for device in list(open_inputs):
        close_input(device)

    for device in list(open_outputs):
        close_output(device)

print("MIDI router running...")
print("Press Ctrl-C to stop.")

try:
    while True:

        now = time.monotonic()

        if now - last_scan >= scan_interval:
            scan_devices()
            last_scan = now

        route_messages()

        time.sleep(0.001)

except KeyboardInterrupt:
    print("Stopping.")

finally:
    close_all_ports()
    print("All MIDI ports closed.")
