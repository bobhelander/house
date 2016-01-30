"""
cache.py
Class that holds the cached weather data

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


class WeatherCache(object):
    """
    WeatherCache holds the last received set of data from the weather site.
    """

    def __init__(self):
        self.cache = None

    def get(self):
        """
        Get the cached data
        """
        return self.cache
    
    def set(self, cache):
        """
        Set the cached data
        """
        self.cache = cache
