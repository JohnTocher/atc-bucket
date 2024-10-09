""" Serial debugguing utility for simple testing at ATC

    Updated by John Tocher
    01/06/2018

    If you're using the anaconda python distro and dont have pyserial, use:
    conda install -c anaconda pyserial

    Version 0.1.3
    No strict API / specifications at 1.x release!

"""
import serial
import sys
import io
import string
import datetime
import time

VER_MAJOR = 0
VER_MINOR = 1
VER_PATCH = 3

MAX_READ_SIZE = 100 # Maximum number of characters to read in a single operation
QUIT_MESSAGE = "!QUIT"  # The string that will stop the passive receive operation
RETURN_MSG_EOL = "\r\n" # MIg be \n of \r\n depending on your requirement
CHALLENGE_RESPONSE_TIMEOUT = 10 # The default time to wait for a respnse in C&R mode

# Dictionary of canned commands to save typing
CANNED_RESPONSES = {
        "01" : "Test",
        "02" : "AT+COPS?",
        "03" : "Command 03",
        "04" : "Command 04",
        "05" : "Command 05",
        "06" : "Command 06",
        "07" : "Command 07",
        "08" : "Command 08",
        "09" : "Command 09",
        "10" : "Command 10",
}


def lookup_response(input_string):
    """ Returns a particule response to definied input strings """

    response = ""
    if input_string == "time?":
        response = datetime.datetime.today().strftime("%H:%M:%S\n")
    elif input_string == "date?":
        response = datetime.datetime.today().strftime("%Y-%m-%d\n")
    elif len(input_string) > 5 and input_string[0:5] == "echo:":
        response = input_string[5:]
    else:
        print(f"Ignored command [{input_string}]")
    return response

def setup_port(port_name, baudrate, port_bits=8, port_parity="N", stop_bits=1):
    """ Configure the port """

    if port_parity == "N":
        use_parity = serial.PARITY_NONE
    elif port_parity == "O":
        use_parity = serial.PARITY_ODD
    elif port_parity == "E":
        use_parity = serial.PARITY_EVEN
    else:
        pass
        # error here
    
 
    # ToDo - handle XON/XOFF and DSRR/DTR Properly
    this_port = serial.Serial(port_name, baudrate, timeout=0, parity=use_parity)

    return this_port

def listen_and_show_codes(which_port):
    """ Opens the supplied port, prints recevied characters in various formats """

    done_debugging = False
    rx_buffer = ""
    char_count = 0

    while not done_debugging:
        this_input = which_port.read(MAX_READ_SIZE)
        if len(this_input) > 0:
            for each_char in this_input:
                char_count += 1
                if each_char in (13, 10):
                    if rx_buffer == QUIT_MESSAGE:
                        done_debugging = True
                    else:
                        response = lookup_response(rx_buffer)
                        if len(response) > 0:
                            which_port.write(response.encode())
                            which_port.write(RETURN_MSG_EOL.encode())
                            #for each_byte in response:
                            #    which_port.writelines(which_port)
                    sys.stdout.flush()
                    rx_buffer = ""
                else:
                    rx_buffer += chr(each_char)
                    if chr(each_char) in string.printable:
                        char_string = chr(each_char)
                    else:
                        char_string = "-"
                    if len(rx_buffer) > MAX_READ_SIZE:
                        rx_buffer = rx_buffer[-MAX_READ_SIZE:]
                    print("{0:04} {1:03} {1:02x} {1:08b} {2}".format(char_count, each_char, char_string))
                    sys.stdout.flush()
            
def listen_and_display_lines(which_port):
    """ Opens the supplied port, prints recevied characters in various formats """

    done_debugging = False
    rx_buffer = ""

    while not done_debugging:
        this_input = which_port.read(MAX_READ_SIZE)
        if len(this_input) > 0:
            for each_char in this_input:
                if each_char in (13, 10):
                    if rx_buffer == QUIT_MESSAGE:
                        done_debugging = True
                    print(f"RX: {rx_buffer}")
                    sys.stdout.flush()
                    rx_buffer = ""
                else:
                    rx_buffer += chr(each_char)

def simple_challenge_response(which_port):
    """ Asks the user for input, sends it and waits for a response """

    done_debugging = False
    rx_buffer = ""
    last_command = ""

    print("Enter the command to send")
    print("Enter '!!' to repeat last command, '!nn' for canned strings")
    print(f"Will wait for a response for {CHALLENGE_RESPONSE_TIMEOUT} seconds max, and display any response ")
    print(f"Enter '{QUIT_MESSAGE}' to end\n")
        
    while not done_debugging:
        
        user_input = input("Enter your command: ")
        input_len = len(user_input)
        if user_input == QUIT_MESSAGE:
            done_debugging = True
            break
        elif (input_len > 1) and user_input[0:2] == "!!":
            user_output = last_command
            which_port.write(RETURN_MSG_EOL.encode())   # Add the EOL constant
        elif (input_len > 2) and user_input[0:1] == "!":
            canned_key = user_input[1:3]
            canned_response = CANNED_RESPONSES.get(canned_key, "Unknown")
            user_output = canned_response
        else:
            user_output = user_input

        print(f"Sending: {user_input}")
        which_port.write(user_output.encode())
        which_port.write(RETURN_MSG_EOL.encode())   # Add the EOL constant
        last_command = user_output
        rx_buffer = ""
        
        serial_timer = 0
        while serial_timer < CHALLENGE_RESPONSE_TIMEOUT:
            this_input = which_port.read(MAX_READ_SIZE)
            if len(this_input) > 0:
                for each_char in this_input:
                    if each_char in (13, 10):
                        print(f"RX: {rx_buffer}")
                        sys.stdout.flush()
                        rx_buffer = ""
                        serial_timer = CHALLENGE_RESPONSE_TIMEOUT
                    else:
                        rx_buffer += chr(each_char)
            serial_timer += 1
            time.sleep(1)
    
    print("\nAll done\n")

        
def serial_debugger():
    """ Perform serial test operations here """
    print("Starting serial port")
    #port_1 = setup_port(port_name = "COM4", baudrate="9600", port_bits=8)
    port_1 = setup_port(port_name="/dev/ttyUSB3", baudrate="9600", port_bits=8)


    # Choose a mod that suits your curent requirements by uncommenting one of the options below.
    # Or extend one for job/specific testing

    #listen_and_display(port_1) # Simple displays text on screen as recevied
    #listen_and_show_codes(port_1)   # Displays received data in a variety of formats
    simple_challenge_response(port_1)   # Simple challange and response

if __name__ == "__main__":
    serial_debugger()
else:
    # Called from elsehwre
    pass
