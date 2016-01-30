"""
rest_service.py
web.py REST service

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

import web
from house.environment.nest import Nest
from house.environment import external
from house.alarm import zones
from house.irrigation import sprinkler
from house.data.service_data import get_status
from house.data.recorder import record_data, retrieve_data
from house.services.messaging import send_smtp_message
from house.services.light import light_off, light_on, light_toggle, light_color
import json
from ConfigParser import ConfigParser
import os

urls = (
    '/api/environment/inside', 'EnvironmentInside',
    '/api/environment/inside/TempHumidity', 'EnvironmentInsideTempHumidity',
    '/api/environment/inside/status', 'EnvironmentInsideStatus',
    '/api/environment/inside/running', 'EnvironmentInsideRunning',
    '/api/environment/inside/fan', 'EnvironmentInsideFan',
    '/api/environment/inside/fan/(on|auto)', 'EnvironmentInsideFan',
    '/api/environment/inside/away', 'EnvironmentInsideAway',
    '/api/environment/inside/away/(true|false)', 'EnvironmentInsideAway',
    '/api/environment/outside', 'EnvironmentOutside',
    '/api/environment/outside/KCOS', 'EnvironmentOutsideKCOS',
    '/api/environment/outside/TempHumidity', 'EnvironmentOutsideTempHumidity',
    '/api/environment/outside/wind', 'EnvironmentOutsideWind',
    '/api/environment/outside/rain', 'EnvironmentOutsideRainfall',
    '/api/alarm/status', 'AlarmStatus',
    '/api/irrigation/state', 'IrrigationState',
    '/api/irrigation/status', 'IrrigationStatus',
    '/api/irrigation/zone/([1-4])/(on|off)', 'Irrigation',
    '/api/irrigation/cycle/(\d{1,7})', 'IrrigationCycle',
    '/api/irrigation/cycle/status', 'IrrigationCycleStatus',
    '/api/history', 'History',
    '/api/message', 'Message',
    '/api/status', 'Status',
    '/api/light', 'Light',
    '/api/light/color/([A-Fa-f0-9]{2})/([A-Fa-f0-9]{2})/([A-Fa-f0-9]{2})/([A-Fa-f0-9]{2})', 'LightColor'
)

web.config.debug = False
app = web.application(urls, globals())

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "settings.conf")
SETTINGS = ConfigParser()
SETTINGS.read(SETTINGS_FILE)


class Status:
    """
    If the caller receives this response the service is working
    """

    def GET(self, zone, state):
        return json.dumps({"status": "ONLINE"})


class Irrigation:
    """
    REST Controller to open/close irrigation values
    """

    def PUT(self, zone, state):
        return json.dumps(sprinkler.sprinkler_control(zone=zone,
                                                      state=state,
                                                      host=SETTINGS.get("irrigation", "irrigation_host"),
                                                      port=SETTINGS.get("irrigation", "irrigation_port")))


class IrrigationState:
    """
    REST Controller to return the irrigation state
    """

    def GET(self):
        return json.dumps(sprinkler.sprinkler_state(host=SETTINGS.get("irrigation", "irrigation_host"),
                                                    port=SETTINGS.get("irrigation", "irrigation_port")))


class IrrigationStatus:
    """
    REST Controller to return the irrigation status
    """

    def GET(self):
        return json.dumps(sprinkler.sprinkler_status(host=SETTINGS.get("irrigation", "irrigation_host"),
                                                     port=SETTINGS.get("irrigation", "irrigation_port")))


class IrrigationCycle:
    """
    REST Controller to start/stop irrigation cycles
    """

    def PUT(self, milliseconds):
        return json.dumps(sprinkler.sprinkler_start_cycle(milliseconds=milliseconds,
                                                          host=SETTINGS.get("irrigation", "irrigation_host"),
                                                          port=SETTINGS.get("irrigation", "irrigation_port")))
    
    def DELETE(self, milliseconds):
        return json.dumps(sprinkler.sprinkler_end_cycle(host=SETTINGS.get("irrigation", "irrigation_host"),
                                                        port=SETTINGS.get("irrigation", "irrigation_port")))


class IrrigationCycleStatus:
    """
    REST Controller to return the irrigation cycle status
    """

    def GET(self):
        return json.dumps(get_status())


class AlarmStatus:
    """
    REST Controller to return the alarm system state
    """

    def GET(self):
        return json.dumps(zones.get_zone_status(alarm_host=SETTINGS.get("alarm", "alarm_host"),
                                                alarm_port=SETTINGS.get("alarm", "alarm_port")))


class EnvironmentInside:
    """
    REST Controller to return current environment shared status inside the house
    """

    def GET(self):
        nest = Nest(username=SETTINGS.get("nest", "user"),
                    password=SETTINGS.get("nest", "pwd"))
        nest.login()
        nest.read_status()
        return json.dumps(nest.status["shared"])


class EnvironmentInsideStatus:
    """
    REST Controller to return current environment status inside the house
    """

    def GET(self):
        nest = Nest(username=SETTINGS.get("nest", "user"),
                    password=SETTINGS.get("nest", "pwd"))
        nest.login()
        nest.read_status()
        return json.dumps(nest.status)


class EnvironmentInsideTemperature:
    """
    REST Controller to return current temperature inside the house
    """

    def GET(self):
        nest = Nest(username=SETTINGS.get("nest", "user"),
                    password=SETTINGS.get("nest", "pwd"))
        nest.login()
        nest.read_status()
        #nest.status["shared"].itervalues().next()
        return json.dumps(nest.status["shared"].itervalues().next())


class EnvironmentInsideTempHumidity:
    """
    REST Controller to return current humidity inside the house
    """

    def GET(self):
        nest = Nest(username=SETTINGS.get("nest", "user"),
                    password=SETTINGS.get("nest", "pwd"))
        nest.login()
        nest.read_status()        
        temperature = nest.status["shared"].itervalues().next()["current_temperature"]
        humidity = nest.status["device"].itervalues().next()["current_humidity"]
        return json.dumps({"temperature": external.convert_to_fahrenheit(temperature), "humidity": humidity})


class EnvironmentInsideRunning:
    """
    REST Controller to return current status of HVAC heating/cooling
    """

    def GET(self):
        nest = Nest(username=SETTINGS.get("nest", "user"),
                    password=SETTINGS.get("nest", "pwd"))
        nest.login()
        nest.read_status()        
        return json.dumps(nest.heat_cool_states())


class EnvironmentInsideFan:
    """
    REST Controller to return current of the HVAC fan on/off
    REST Controller to turn the HVAC fan on/off
    """

    def GET(self):
        nest = Nest(username=SETTINGS.get("nest", "user"),
                    password=SETTINGS.get("nest", "pwd"))
        nest.login()
        nest.read_status()        
        return json.dumps(nest.fan())
    
    def PUT(self, state):
        nest = Nest(username=SETTINGS.get("nest", "user"),
                    password=SETTINGS.get("nest", "pwd"))
        nest.login()
        nest.read_status()
        nest.set_fan(state)


class EnvironmentInsideAway:
    """
    REST Controller to return if the Nest device is set to "Away" mode
    REST Controller to set the Nest device to "Away" mode  on/off
    """
    def GET(self):
        nest = Nest(username=SETTINGS.get("nest", "user"),
                    password=SETTINGS.get("nest", "pwd"))
        nest.login()
        nest.read_status()        
        return json.dumps(nest.away())
    
    def PUT(self, state):
        nest = Nest(username=SETTINGS.get("nest", "user"),
                    password=SETTINGS.get("nest", "pwd"))
        nest.login()
        nest.read_status()
        nest.set_away(state)


class EnvironmentOutside:
    """
    Return weather data from the station
    """

    def GET(self):
        return json.dumps(external.read_weather(station_number=SETTINGS.get("weather", "station"),
                                                api_key=SETTINGS.get("weather", "api_key")))


class EnvironmentOutsideKCOS:

    def GET(self):
        return json.dumps(external.read_weather_station(external.KCOS,
                                                        api_key=SETTINGS.get("weather", "api_key")))


class EnvironmentOutsideTempHumidity:
    """
    Return temperature and humidity from the weather station
    """

    def GET(self):
        weather = external.read_weather(station_number=SETTINGS.get("weather", "station"),
                                        api_key=SETTINGS.get("weather", "api_key"))
        temperature = external.convert_to_fahrenheit(external.convert_from_kelvin(weather["main"]["temp"]))
        humidity = weather["main"]["humidity"]
        return json.dumps({"temperature": temperature, "humidity": humidity})


class EnvironmentOutsideWind:
    """
    Return wind data from the weather station
    """

    def GET(self):
        weather = external.read_weather(station_number=SETTINGS.get("weather", "station"),
                                        api_key=SETTINGS.get("weather", "api_key"))
        wind_speed = external.wind_speed(weather)
        return json.dumps({ "wind": wind_speed })


class EnvironmentOutsideRainfall:
    """
    Return rainfall data from the weather station
    """

    def GET(self):
        weather = external.read_weather(station_number=SETTINGS.get("weather", "station"),
                                        api_key=SETTINGS.get("weather", "api_key"))
        rainfall = external.current_rain(weather)
        return json.dumps({"3h": rainfall})


class History:
    """
    Add or retrieve history data
    """

    def PUT(self):
        record_data(nest_user=SETTINGS.get("nest", "user"),
                    nest_password=SETTINGS.get("nest", "pwd"),
                    weather_station=SETTINGS.get("weather", "station"))
 
    def GET(self):
        return json.dumps(retrieve_data())


class Message:
    """
    Send a message to the configured destination
    """

    def PUT(self):
        send_smtp_message(data=web.data(),
                          destination=SETTINGS.get("messaging", "destination"),
                          source_user=SETTINGS.get("messaging", "source_user"),
                          source_pwd=SETTINGS.get("messaging", "source_pwd"),
                          source_server=SETTINGS.get("messaging", "source_server"),
                          source_port=SETTINGS.get("messaging", "source_port"))


class Light:
    """
    Under cabinet light controls
    """
    light_mode = False
    
    def PUT(self):
        light_on()
        
    def DELETE(self):
        light_off()
        
    def GET(self):
        Light.light_mode = light_toggle(Light.light_mode)


class LightColor:
    """
    Under cabinet light color methods
    """
    
    def PUT(self, zone, red, green, blue):
        light_color(zone, red, green, blue)        
            

if __name__ == "__main__":
    app.run()