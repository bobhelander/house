"""
irrigation_service.py
irrigation service methods

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

from time import sleep
from house.data.service_data import check_schedule, get_cycle_durations, add_cycle, update_status
from datetime import datetime
from house.irrigation.sprinkler import sprinkler_state, sprinkler_end_cycle
from house.irrigation.sprinkler import sprinkler_control, sprinkler_start_cycle
from house.environment.external import read_weather, wind_speed, humidity, current_rain
from house.data.recorder import record_data
import logging
import logging.handlers
from ConfigParser import ConfigParser
import os


log = logging.getLogger()
log.setLevel(logging.DEBUG)
log.addHandler(logging.handlers.SysLogHandler(address='/dev/log'))

LAST_STATUS = "No Status"

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "settings.conf")
SETTINGS = ConfigParser()
SETTINGS.read(SETTINGS_FILE)

def in_schedule():
    """
    Return if there is a cycle in the scheduled window now
    """
    date = datetime.now()
    schedule_id = check_schedule(date)
    if schedule_id is not None:
        return schedule_id[0], get_cycle_durations(schedule_id[0])
    
    return None, None


def update_from_weather(cycle_id, cycle_durations, station_number, api_key):
    """
    Check the current weather conditions.  Update status if a weather event should stop
    the cycle.
    """

    # Get current weather
    weather = read_weather(station_number, api_key)
    
    # Turn off if too windy
    if wind_speed(weather) > 10:
        update_status("Canceled: Wind")
        logging.info("Skipping Cycle: %s Too Windy: %s MPH", cycle_id, wind_speed(weather))
        return [0 for unused in cycle_durations]
    
    # Turn off if humidity is too high
    if humidity(weather) > 90:
        update_status("Canceled: Humidity")
        logging.info("Skipping Cycle: %s Humidity too high: %s", cycle_id, humidity(weather))
        return [0 for unused in cycle_durations]

    # Reduce if rainfall in last 24 hours
    if current_rain(weather) > 0:
        update_status("Canceled: Rain")
        logging.info("Skipping Cycle: %s 3 hour rainfall: %s", cycle_id, current_rain(weather))
        return [0 for unused in cycle_durations]    
    
    return cycle_durations


def start_cycle(cycle_id, cycle_durations):
    """
    Opens a irrigation value for the cycle duration
    """
    update_status("Running Cycle")
    logging.debug("Starting Cycle: %s", cycle_id)
    date = datetime.now()
    add_cycle(cycle_id, date, str(cycle_durations))
    zone = 1
    for duration in cycle_durations:
        run_cycle(zone, duration)
        zone += 1
    
    # Be sure all zones are closed
    sprinkler_end_cycle()
    update_status("Finished Cycle")
    logging.debug("Finished Cycle: %s", cycle_id)


def wait_for_cycle():
    """
    A cycle is running.  Loop while we are in that cycle.
    """
    # Check cycle_milliseconds
    while int(sprinkler_state()["cycle_milliseconds"]) > 0:
        sleep(15)


def run_cycle(zone, duration):
    """
    Calls the start_cycle method and waits for completion
    """
    logging.debug("Starting Zone: %s Duration: %s", zone, duration)
    # Waiting for finish
    wait_for_cycle()
    # Shutdown all
    sprinkler_end_cycle()
    # Open zone valve
    if duration > 0:
        # Start cycle counter.  Do this before turning
        # on the zone.  This will prevent runaway watering.
        sprinkler_start_cycle(duration*1000*60)
        # Turn the zone on
        sprinkler_control(zone, "on")
        logging.debug("Zone On")        
    
    # Waiting for finish
    wait_for_cycle()
    logging.debug("Finished Zone: %s", zone)


def service():
    """
    Main loop waiting for a cycle_window to become valid
    """
    logging.debug('Service Started')
    while True:
        try:
            logging.debug("Service woke up")
            cycle_id, cycle_durations = in_schedule()
            if cycle_id:
                cycle_durations = update_from_weather(cycle_id, cycle_durations,
                                                      station_number=SETTINGS.get("weather", "station"),
                                                      api_key=SETTINGS.get("weather", "api_key"))
                
                logging.debug("Cycle Id: %s Duration: %s", cycle_id, cycle_durations)
                start_cycle(cycle_id, cycle_durations)
            else:
                record_data()
                sleep(60*15)  # 15 minutes
                
        except Exception, ex:
            logging.exception(ex)
                 
    logging.debug('Service Ended')


if __name__ == '__main__':
    service()