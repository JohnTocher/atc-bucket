import socket
import subprocess

def get_device_info():
    """ Retrieve device info returns a dictionary 
    
    """

    device_info = dict()
    device_info["OK"] = False

    try:
        local_hn = socket.gethostname()
        device_info["hostname"] = local_hn
    except Exception as e:
        print(f"Failed getting device info:\n{str(e)}")
        return device_info

    device_info["OK"] = True    # OK if we get to here!
    return device_info

def show_device_info():
    """ Prints some device info 
    
    
    """
    local_info = get_device_info()
    print("Local device info:")
    print(f"Hostname: {local_info['hostname']}")

def wookie_default_utility():
    """ Run prompts for default setup
    
    """

    show_device_info()

if __name__ == "__main__":
    wookie_default_utility()
