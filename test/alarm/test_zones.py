"""
test_zones.py
Unit test

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


import unittest
from socket import socket, AF_INET, SOCK_STREAM
from threading import Event, Thread
from house.alarm import zones


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.shutdown = Event()
        self.host = "localhost"
        self.port = 8001
        args = (self.host, self.port)
        self.listener = Thread(group=None, target=self.listen, name="listener_test", args=args)
        self.listener.start()

    def tearDown(self):
        self.shutdown.set()
        self.listener.join()

    def test_get_zone_state(self):
        try:
            results = zones.get_zone_status(self.host, self.port)
            result = [item for item in results if item["zone"] == "zone3"][0]
            self.assertEqual(result.get("status"), "closed")
        finally:
            self.shutdown.set()
            self.clear()


    def listen(self, alarm_host, alarm_port):
        s = socket(AF_INET, SOCK_STREAM)
        s.bind((alarm_host, alarm_port))
        s.listen(5)
        while not self.shutdown.is_set():
            (connection, _unused) = s.accept()
            buffer_data = connection.recv(1024)
            return_data = self.process(buffer_data)
            if return_data:
                connection.sendall(return_data)
            connection.close()

        s.close()

    def process(self, buffer_data):
        if "status" in buffer_data:
            return "0:0:1:0:0:0:0:1"
        if "." in buffer_data:
            return None


    def clear(self):
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((self.host, self.port))
        s.sendall(".")

if __name__ == '__main__':
    unittest.main()
