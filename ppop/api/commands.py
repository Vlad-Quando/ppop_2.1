import socket
import json
import struct


# IP = '192.168.0.0'  # Station's address to connect to
# PORT = 24           # Station's port to connect to
IP: str = '80.87.106.12'
PORT: int = 28026


HEADER_TEMPLATE: dict = { # Template of packet's header
    'type': None,
    'info': None,
    'size': None,
}
START_TEMPLATE: dict = {  # Template of imit-start packet's body
    'movement': None,
    'power': None,
    'reserved': None,
}
POINT_TEMPLATE: dict = {  # Template of load-route element packet's body
    'time': None,
    'lat': None,
    'lon': None,
    'alt': None,
}
SYSPAR_TEMPLATE: dict = { # Template of get-params and set-params packet's body
    'ip4_addr': None,
    'ip4_mask': None,
    'ip4_gateway': None,
    'systime': None,
    'postname': None,
}


def start(movement: str, power: str, reserved: str):
    '''Send start command to station'''

    sct = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Creating socket object

    try:
        sct.connect((IP, PORT)) # Attempt to establish connection
    except ConnectionRefusedError:
        return {
            'error': 'ConnectionRefusedError',
            'info': 'station is not active'
            }
    
    # Counting params quantity to know if some params were missed
    params_quantity = sum(map(lambda x: x != None, [movement, power, reserved]))
    if params_quantity == 0: # If no params were passed
        header = [10, 0, 0] # Creating header
        body = None # Edmpty body - no params
    elif 0 < params_quantity < 3:   # If only some params were passed but not all - error
        sct.close()
        return {
            'error': 'Incorrect params',
            'info': 'You didn\'t pass correct values of params or didn\'t specify each of them.',
        }
    elif params_quantity == 3: # If all params were passed 
        header = [10, 0, 3] # Creating header

        try:
            body = [ # Creating body
                int(movement),
                int(power),
                int(reserved),
            ]
        except Exception as e: # If some params have incorrect value or datatype
            return {
                'error': 'Failed to parse passed params',
                'info': f'Exception was reaised: {e}'
            }

    byte_header = struct.pack('iii', *header) # Encoding header

    try:
        sct.sendall(byte_header) # Sending header
    except Exception as e:
        return {
            'error': 'Failed to send command',
            'info': f'Exception was reaised: {e}'
        }


    if body != None: # If there are body with params
        byte_body = struct.pack('iii', *body) # Encoding body

        try:
            sct.sendall(byte_body) # Sending body
        except Exception as e:
            sct.close()
            return {
                'error': 'Failed to send command',
                'info': f'Exception was reaised: {e}'
            }
    
    sct.close() # Closing connection

    return 'No responce' 


def stop():
    '''Send stop command to station'''

    sct = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Creating socket object

    try:
        sct.connect((IP, PORT)) # Attempt to establish connection
    except ConnectionRefusedError:
        return {
            'error': 'ConnectionRefusedError',
            'info': 'station is not active',
            }
    
    # Creating header of packet
    header = [5, 0, 0] # type - info - size

    # Serializing header and encoding it to bytes
    byte_header: bytes = struct.pack('iii', *header)

    try:
        sct.sendall(byte_header)    # Sending header to the station
        data = 'No responce'
    except Exception as e:
        sct.close()
        return {
            'error': 'Failed to send command',
            'info': f'Exception was reaised: {e}'
        }

    sct.close() # Closing the connection

    return data


def get_params():
    '''Send get-params command to station'''

    sct = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Creating socket object

    try:
        sct.connect((IP, PORT)) # Attempt to establish connection
    except ConnectionRefusedError:
        return {
            'error': 'ConnectionRefusedError',
            'info': 'station is not active',
            }
    
    PARAMS_LENGTH: int = 148 # Length of awaiting params bytes array, not final value
    
    header = [2, 0, 0]  # Creating header
    byte_header = struct.pack('iii', *header)   # Encoding header

    try:
        sct.sendall(byte_header)    # Sending header to the station
    except Exception as e:
        sct.close()
        return {
            'error': 'Failed to send command',
            'info': f'Exception was reaised: {e}'
        }

    responce = sct.recv(PARAMS_LENGTH) # Recieving responce with params

    time = struct.unpack('i', responce[16:20])[0] # Extracting time
    
    post_name = ''  # String for storing post name
    for i in range(20, 148):    # Extracting post name
        if responce[i] == 0:
            break
        post_name += chr(responce[i])
    
    sct.close() # Closing the connection
    
    return {
        'time': time,
        'post_name': post_name
    }


def set_params(addr: int|None, mask: int|None, gateway: int|None, systime: int|None, postname: str|None):
    '''Send set-params command to station'''

    # Check if all params were passed
    if addr != None and mask != None and gateway != None and systime != None and postname != None:
        sct = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Creating socket object
        sct.settimeout(5) # Setting max time of waiting for responce

        try:
            sct.connect((IP, PORT)) # Attempt to establish connection
        except ConnectionRefusedError:
            return {
                'error': 'ConnectionRefusedError',
                'info': 'station is not active',
                }
    
        body = [        # Creating body with passed params to be set
            int(addr),
            int(mask),
            int(gateway),
            int(systime),
            postname.encode('utf-8'),
        ]
        # Encoding body to bytes array
        byte_body = struct.pack(f"iiii{len(body[-1])}s", *body[:-1], body[-1])

        header = [2, 0, len(byte_body)]     # Creating header
        byte_header = struct.pack('iii', *header)   # Encoding header

        try:
            sct.sendall(byte_header)    # Sending header
            sct.sendall(byte_body)      # Sending body
        except Exception as e:
            sct.close()
            return {
                'error': 'Failed to send command',
                'info': f'Exception was reaised: {e}'
            }

        sct.close() # Closing connection

        return 'No responce'

    return {
            'error': 'Incorrect params',
            'info': 'You didn\'t pass correct values of params or didn\'t specify each of them.',
        }


def get_track(points: list = []):
    '''Send get-track command to station'''

    sct = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Creating socket object

    try:
        sct.connect((IP, PORT)) # Attempt to establish connection
    except ConnectionRefusedError:
        return {
            'error': 'ConnectionRefusedError',
            'info': 'station is not active',
            }
    
    header = [15, 0, 0] # Creating body
    byte_header: bytes = struct.pack('iii', *header) # Encoding header

    try:
        sct.sendall(byte_header) # Sending header
    except Exception as e:
        sct.close()
        return {
            'error': 'Failed to send command',
            'info': f'Exception was reaised: {e}'
        }

    responce: bytes = sct.recv(340) # Revieving current track (340 - is not final value)
    points = [] # Array for storing recieved points

    for i in range(8, len(responce[8:]), 16): # Parsing recieved points
        cur_point = {}
        try:
            cur_point['lat'] = struct.unpack('f', responce[i:i+4])[0]
            cur_point['lon'] = struct.unpack('f', responce[i+4:i+8])[0]
            cur_point['alt'] = struct.unpack('f', responce[i+8:i+12])[0]
            cur_point['time'] = struct.unpack('i', responce[i+12:i+16])[0]
            points.append(cur_point)

        except Exception: # If some point does not have some value to be specified correctly
            points.append(cur_point)
            sct.close() # Closing connection

            return {
                'error': 'Error occured while trying to parse recieved points array',
                'points': points
            }

    sct.close()     # Closing connection

    return points


def set_track(points):
    '''Send set-track command to station'''

    sct = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Creating socket object
    sct.settimeout(5) # Setting max time of waiting for responce

    try:
        sct.connect((IP, PORT)) # Attempt to establish connection
    except ConnectionRefusedError:
        return {
            'error': 'ConnectionRefusedError',
            'info': 'station is not active',
            }

    body = b''  # Bytes array for storing passed track
    if not points:
        sct.close() # Closing connection and returning error message if no points passed
        return {
            'error': 'Failed to extract points data',
            'info': 'You didn\'t pass points array.'
        }
    
    for point in points: # Packing points to bytes array
        try:
            cur_point = struct.pack('fffi', point['lat'], point['lon'], point['alt'], point['time'])
            body += cur_point

        except Exception as e: # If some point was specified incorrectly
            sct.close()
            return {
                'error': 'Failed to pack points data',
                'info': f'Wrong format or datatype: {e}'
            }
    
    header = [15, 0, len(body)] # Creating header
    byte_header = struct.pack('iii', *header) # Encoding header

    try:
        sct.sendall(byte_header)    # Sending header
        sct.sendall(body)           # Sending track
    except Exception as e:
        sct.close()
        return {
            'error': 'Failed to send command',
            'info': f'Exception was reaised: {e}'
        }
    
    responce = sct.recv(340)    # Resieving station responce (340 - is not final value)

    points = [] # Array for storing gotten points
    for i in range(8, len(responce[8:]), 16): # Extracting points from gotten bytes array
        cur_point = {}
        try:
            cur_point['lat'] = struct.unpack('f', responce[i:i+4])[0]
            cur_point['lon'] = struct.unpack('f', responce[i+4:i+8])[0]
            cur_point['alt'] = struct.unpack('f', responce[i+8:i+12])[0]
            cur_point['time'] = struct.unpack('i', responce[i+12:i+16])[0]
            points.append(cur_point)
        except Exception: # If some point does not have some value to be specified correctly
            points.append(cur_point)
            sct.close() # Closing connection

            return {
                'error': 'Error occured while trying to parse recieved points array',
                'points': points
            }

    sct.close() # Closing connection

    return points



# ---------------------------------------------------------------------
status_keys = [ # Array of params names that station returns
	'num_gps',
	'num_glo',
	'state',
	'hw_ready',
	'imit_ready',
	'bg_collection',
	'nav_fix',
	'version',
	'fwversion',
	'task_time',
	'oper_time',
	'work_time',
	'nav_hacc',
	'nav_ngps',
	'nav_nglo',
	'time_sync',
	'track_loaded',
	'reserved',
]

def status():
    sct = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Creating socket object

    try:
        sct.connect((IP, PORT)) # Attempt to establish connection
    except ConnectionRefusedError:
        return {
            'error': 'ConnectionRefusedError',
            'info': 'station is not active',
            }
    
    header = [1, 0, 0] # type - info - size Creating header
    byte_header = struct.pack('iii', *header)   # Encoding header to bytes
    
    try:
        sct.sendall(byte_header)    # Sending header to the station
    except Exception as e:
        sct.close()
        return {
            'error': 'Failed to send command',
            'info': f'Exception was reaised: {e}'
        }

    responce = sct.recv(24) # Recieving responce from station

    data = {} # Dict for storing responce
    for i in range(0, len(responce) - 6): # Extracting data from gotten bytes array
        data[status_keys[i]] = responce[i]

    sct.close() # Closing connection

    return data
