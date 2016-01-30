"""
alarm_monitor.py
alarm controller methods

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

from house.alarm.zones import get_zone_state, ZONE_DEFINITIONS, ZONE_STATE_TEXT
import time


class Monitor(object):
    """
    Alarm monitoring class that watches for state changes in the alarm controller.
    If a change occurs the callback handlers are called.
    """

    def __init__(self):
        self.handlers = list()
        self.enabled = True
        self.state = None
        
    def enable(self, enabled=True):
        """
        Turn on/off callback handlers.  begin() must be called again after re-enabling
        """
        self.enabled = enabled
        
    def add_handler(self, handler):
        """
        Add a callback handler
        callback(changed_zone[])
        """
        self.handlers.append(handler)
        
    def begin(self):
        """
        Begin the alarm monitor loop
        """

        # Read baseline
        self.state = get_zone_state()

        while self.enabled:
            # Read state
            new_state = get_zone_state()

            # Create a list of changed zones since the last call
            changed = [{"key": key, 
                        "name": ZONE_DEFINITIONS[key],
                        "state": value, 
                        "state_text": ZONE_STATE_TEXT[key][int(value)]}
                       for key, value in new_state.iteritems()
                       if value != self.state[key]]

            # This is now our state
            self.state = new_state

            # call the handlers
            if changed:
                for handler in self.handlers:
                    handler(changed)
                    
            time.sleep(.2)