"""
service_data.py
Database queries

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

import sqlite3
from datetime import datetime


def create_database():
    """"
    Create the database tables and add some default data
    """

    conn = sqlite3.connect("house.db")
 
    cursor = conn.cursor()
 
    cursor.execute("""CREATE TABLE cycle_status ('status' VARCHAR(128), 'status_date' DATETIME)""")
    
    cursor.execute("""CREATE TABLE schedule ( 'id' INTEGER PRIMARY KEY, 'day' INTEGER, 'start' INTEGER, 'end' INTEGER,
                      'zone1' INTEGER, 'zone2' INTEGER, 'zone3' INTEGER, 'zone4' INTEGER)""")

    cursor.execute("""CREATE TABLE cycles ( 'id' INTEGER PRIMARY KEY, 'schedule_id' INTEGER,
                      'cycledate' VARCHAR(10), 'cycletime' DATETIME,
                      'zone1' INTEGER, 'zone2' INTEGER, 'zone3' INTEGER, 'zone4' INTEGER)""")

    cursor.execute("""CREATE TABLE history (
                      'id' INTEGER PRIMARY KEY, 
                      'entryDate' DATETIME,
                      'fan_state' INTEGER, 
                      'cool_state' INTEGER, 
                      'heat_state' INTEGER,
                      'irrigation_zone1' INTEGER, 
                      'irrigation_zone2' INTEGER,
                      'irrigation_zone3' INTEGER, 
                      'irrigation_zone4' INTEGER,
                      'alarm_zone1' INTEGER, 
                      'alarm_zone2' INTEGER,
                      'alarm_zone3' INTEGER, 
                      'alarm_zone4' INTEGER,
                      'alarm_zone5' INTEGER, 
                      'alarm_zone6' INTEGER,
                      'alarm_zone7' INTEGER, 
                      'alarm_zone8' INTEGER,
                      'alarm_zone9' INTEGER, 
                      'inside_temp' DECIMAL,
                      'inside_humidity' INTEGER, 
                      'outside_temp' DECIMAL,
                      'outside_humidity' INTEGER,
                      'rainfall' DECIMAL,
                      'wind_speed' DECIMAL)""")    

    # Day of the week : hour of the day : hour to end the window : zone minutes
    cursor.execute("INSERT INTO schedule (day, start, end, zone1, zone2, zone3, zone4) VALUES (6,4,6,30,30,0,0)")
    cursor.execute("INSERT INTO schedule (day, start, end, zone1, zone2, zone3, zone4) VALUES (6,21,23,30,30,0,0)")
    cursor.execute("INSERT INTO schedule (day, start, end, zone1, zone2, zone3, zone4) VALUES (2,4,6,30,30,0,0)")
    cursor.execute("INSERT INTO schedule (day, start, end, zone1, zone2, zone3, zone4) VALUES (2,21,23,30,30,0,0)")
    #cursor.execute("INSERT INTO schedule (day, start, end, zone1, zone2, zone3, zone4) VALUES (2,0,24,1,1,1,1)")
    
    conn.commit()


SCHEDULE_SQL = """
SELECT id FROM schedule WHERE day = :day_of_week AND start <= :hour_of_day 
AND end > :hour_of_day AND id NOT IN 
(SELECT schedule_id FROM cycles WHERE cycledate = :date)
"""


def check_schedule(check_date):
    """
    Return the identifier of the schedule entry if its schedule window is active now
    """
    data = {"day_of_week": check_date.weekday(),
            "hour_of_day": check_date.hour,
            "date": check_date.strftime("%Y-%m-%d")}
    
    conn = sqlite3.connect("house.db")
    cursor = conn.cursor()
    cursor.execute(SCHEDULE_SQL, data)
    return cursor.fetchone()


CYCLE_SQL = "SELECT zone1, zone2, zone3, zone4 FROM schedule WHERE id = :id"


def get_cycle_durations(cycle_id):
    """
    Read the duration of each zone for the selected schedule entry
    """
    data = {"id": cycle_id}
    
    conn = sqlite3.connect("house.db")
    cursor = conn.cursor()
    cursor.execute(CYCLE_SQL, data)
    return cursor.fetchone()


ADD_CYCLE_SQL = "INSERT INTO cycles (schedule_id, cycledate, cycletime) VALUES (:cycle_id, :date, :cycle_times)"


def add_cycle(cycle_id, date, cycle_times):
    """
    Add an entry to the schedule
    """
    data = {"cycle_id": cycle_id,
            "date": date.strftime("%Y-%m-%d"),
            "cycle_times": cycle_times}
    
    conn = sqlite3.connect("house.db")
    cursor = conn.cursor()
    cursor.execute(ADD_CYCLE_SQL, data)
    conn.commit()


CLEAR_STATUS_SQL = "DELETE FROM cycle_status"
ADD_STATUS_SQL = "INSERT INTO cycle_status (status, status_date) VALUES (:status, :date)"


def update_status(status):
    """
    Update a status record in the cycle_status table
    """
    data = {"status": status,
            "date": datetime.now()}
    
    conn = sqlite3.connect("house.db")
    cursor = conn.cursor()
    cursor.execute(CLEAR_STATUS_SQL)
    cursor.execute(ADD_STATUS_SQL, data)
    conn.commit()


STATUS_SQL = "SELECT status, status_date FROM cycle_status"


def get_status():
    """
    Get the status row from the cycle_status table
    """
    conn = sqlite3.connect("house.db")
    cursor = conn.cursor()
    cursor.execute(STATUS_SQL)
    return cursor.fetchone()


HISTORY_UPDATE_SQL = """INSERT INTO history ('entryDate','fan_state','cool_state',
                        'heat_state', 'irrigation_zone1', 'irrigation_zone2',
                        'irrigation_zone3', 'irrigation_zone4',
                        'alarm_zone1', 'alarm_zone2',
                        'alarm_zone3', 'alarm_zone4',
                        'alarm_zone5', 'alarm_zone6',
                        'alarm_zone7', 'alarm_zone8',
                        'alarm_zone9', 'inside_temp',
                        'inside_humidity', 'outside_temp',
                        'outside_humdity', 'rainfall',
                        'wind_speed') VALUES (:entryDate, :fan_state, :cool_state,
                        :heat_state, :irrigation_zone1, :irrigation_zone2,
                        :irrigation_zone3, :irrigation_zone4, :alarm_zone1,
                        :alarm_zone2, :alarm_zone3, :alarm_zone4, :alarm_zone5,
                        :alarm_zone6, :alarm_zone7, :alarm_zone8, :alarm_zone9,
                        :inside_temp, :inside_humidity, :outside_temp, :outside_humdity,
                        :rainfall, :wind_speed)"""
                        

def update_history(data):
    """
    Add a history data record to the history table
    """
    conn = sqlite3.connect("house.db")
    cursor = conn.cursor()
    try:
        cursor.execute(HISTORY_UPDATE_SQL, data)
        conn.commit()
    except Exception as e:
        print e


HISTORY_SQL = """SELECT CAST(strftime('%s', entryDate) as INTEGER) as dt,
                        fan_state,cool_state,
                        heat_state, irrigation_zone1, irrigation_zone2,
                        irrigation_zone3, irrigation_zone4,
                        alarm_zone1, alarm_zone2,
                        alarm_zone3, alarm_zone4,
                        alarm_zone5, alarm_zone6,
                        alarm_zone7, alarm_zone8,
                        alarm_zone9, inside_temp,
                        inside_humidity, outside_temp,
                        outside_humdity, rainfall,
                        wind_speed FROM history 
                        WHERE entryDate > date('now', '-12 hours')
                        ORDER BY entryDate ASC"""


def dict_factory(cursor, row):
    """
    Create a dictionary of column names and their values
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def retrieve_history():
    """
    Get all the data from the history table
    """
    conn = sqlite3.connect("house.db")
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    try:
        cursor.execute(HISTORY_SQL)
        return cursor.fetchall()
    except Exception as e:
        print e
