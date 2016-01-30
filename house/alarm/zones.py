"""
zones.py
Provides the alarm system status

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

# Setup of the house sensors
ZONES = ["zone%s" % zone_number for zone_number in range(1, 10)]

ZONE_DESCRIPTIONS = ["Back Door", "Garage Exterior", "Garage Internal", "Front Door",
                     "unassigned", "unassigned", "unassigned", "unassigned", "Garage Door"]

ZONE_DEFINITIONS = dict(zip(ZONES, ZONE_DESCRIPTIONS))

# Zones 1-8: Zero = Open, Zone9: Zero = closed
ZONE_STATE_DESCRIPTIONS = [("open", "closed") for _ in range(8)] + [("closed", "open")]

ZONE_STATE_TEXT = dict(zip(ZONES, ZONE_STATE_DESCRIPTIONS))


def get_zone_state(alarm_host, alarm_port):
    """
    Read the alarm data from the arduino
    """

    s = socket(AF_INET, SOCK_STREAM)
    s.connect((alarm_host, alarm_port))
    s.sendall("status")

    data_buffer = ""

    # Receive the response
    while True:
        data = s.recv(2048)
        if not data:
            break
        data_buffer += data

    s.close()

    # Data from the arduino is returned in this format "0:0:1:0:0:0:0:1"
    # Create a dictionary with the zone names as the key
    return dict(zip(ZONES, data_buffer.strip().split(":")))


def get_zone_status(alarm_host, alarm_port):
    """
    Returns current status of the alarm system
    """
    return [{"zone": zone_key,
             "description": ZONE_DEFINITIONS.get(zone_key, "unknown"),
             "status": ZONE_STATE_TEXT[zone_key][int(status)]}
            for zone_key, status in get_zone_state(alarm_host, alarm_port).items()]