"""
sprinkler.py
Irrigation control methods

Copyright (C) 2013-2016  Bob Helander

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from socket import socket, AF_INET, SOCK_STREAM
from time import sleep
import logging


ZONE_KEYS = ["zone1", "zone2", "zone3", "zone4"]
ZONE_NAMES = ["ZONE 1", "ZONE 2", "ZONE 3", "ZONE 4"]
ZONE_DEFINITIONS = dict(zip(ZONE_KEYS + ["cycle_milliseconds"], ZONE_NAMES + ["cycle_time"]))
ZONE_STATE_TEXT = dict(zip(ZONE_KEYS, [("off", "on") for _ in range(len(ZONE_KEYS))]))


def send_message(message, host, port):
    """
    Send the message to the irrigation controller retry if the message fails
    """
    # Retry up to 3 times if an error occurs
    retry_count = 3
    
    while retry_count > 0:
        try:
            retry_count -= 1
            return _send_message(message, host, port)
        except Exception, ex:
            logging.exception(ex)
            if retry_count <= 0:
                raise
            sleep(2)
            

def _send_message(message, host, port):
    """
    Send a message to the irrigation controller
    """
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((host, port))
    data_buffer = ""
    try:
        s.sendall(message)

        while True:
            data = s.recv(2048)
            if not data:
                break
            data_buffer += data
    finally:
        s.close()
    
    return data_buffer.strip()


def sprinkler_state(host, port):
    """
    Read the current irrigation controller state
    """
    return state_data(send_message("status", host, port))


def sprinkler_status(host, port):
    """
    Return the cycle milliseconds left if the cycle
    """
    return status_data(sprinkler_state(host, port))


def state_data(status_message):
    """
    Format and return the status data from the irrigation controller
    """
    # Controller data is returned in this format 0:1:0:0:12345
    return dict(zip(ZONE_KEYS + ["cycle_milliseconds"], status_message.split(":")))


def status_data(state_data):
    """
    Return the formatted status data
    """
    return {"cycle_milliseconds": state_data["cycle_milliseconds"],
            "zones": [{"zone": zone,
                       "description": ZONE_DEFINITIONS.get(zone, "unknown"),
                       "status": ZONE_STATE_TEXT[zone][int(status)]}
                      for zone, status in state_data.items() if zone in ZONE_KEYS]}


def sprinkler_control(zone, state, host, port):
    """
    Turn a zone on or off
    """
    send_message("zone0%s-%s" % (str(zone), state), host, port)
    return sprinkler_status(host, port)


def sprinkler_start_cycle(milliseconds, host, port):
    """
    Set the irrigation controller shutoff timer
    """
    return status_data(state_data(send_message("startcycle-%s" % str(milliseconds, host, port))))


def sprinkler_end_cycle(host, port):
    """
    Interrupt a cycle
    """
    return status_data(state_data(send_message("endcycle", host, port)))