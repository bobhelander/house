"""
recorder.py
Inserts the data points in the database

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

from datetime import datetime
from house.environment.external import read_weather, CIMMARON_HILLS, temperature 
from house.environment.external import wind_speed, humidity, current_rain
from house.environment.nest import Nest
from house.irrigation.sprinkler import sprinkler_state
from house.alarm.zones import get_zone_state
from house.data.service_data import update_history, retrieve_history


def record_data(nest_user, nest_password, weather_station):
    """
    Collect the data and send it to the database
    """
    
    weather = read_weather(weather_station)
    nest = Nest(nest_user, nest_password)
    nest.login()
    nest.read_status()
    
    irrigation_state = sprinkler_state()
    alarm_zones = get_zone_state()

    data = {"entryDate": datetime.now(),
            "irrigation_zone1": irrigation_state["zone1"],
            "irrigation_zone2": irrigation_state["zone2"],
            "irrigation_zone3": irrigation_state["zone3"],
            "irrigation_zone4": irrigation_state["zone4"],
            "alarm_zone1": alarm_zones["zone1"],
            "alarm_zone2": alarm_zones["zone2"],
            "alarm_zone3": alarm_zones["zone3"],
            "alarm_zone4": alarm_zones["zone4"],
            "alarm_zone5": alarm_zones["zone5"],
            "alarm_zone6": alarm_zones["zone6"],
            "alarm_zone7": alarm_zones["zone7"],
            "alarm_zone8": alarm_zones["zone8"],
            "alarm_zone9": alarm_zones["zone9"],
            "outside_temp": temperature(weather),
            "outside_humidity": humidity(weather),
            "rainfall": current_rain(weather),
            "wind_speed": wind_speed(weather)}

    data.update(nest.history_states())
    update_history(data)


def retrieve_data():
    """
    Return all history
    """
    return retrieve_history()