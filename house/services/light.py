"""
light.py
under cabinet lighting controls

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

from serial import Serial, SerialException
import time


def open_port(port):
    """
    Open the selected port
    """
    serial = Serial(port, 9600, timeout=1)
    serial.setDTR(False)
    serial.dsrdtr=False
    time.sleep(0.5)  # Wait for initialization

    return serial


def find_port():
    """
    Find the port the Arduino is connected to
    """
    try:
        return open_port("/dev/ttyACM0")
    except SerialException:
        pass

    # Try the other port
    return open_port("/dev/ttyACM1")


def light_on():
    """
    Send message to the light controller to turn the lights on
    """
    find_port().write('ON\n')


def light_off():
    """
    Send message to the light controller to turn the lights off
    """
    find_port().write('OFF\n')


def light_toggle(light_mode):
    """
    Send message to toggle the lights on/off
    """
    if light_mode:
        find_port().write('OFF\n')
        return False
    else:
        find_port().write('ON\n')
        return True


def light_color(zone, red, green, blue):
    """
    Send a color message to the light controller
    """
    find_port().write('COLOR %s%s%s%s\n' % (zone, red, green, blue))