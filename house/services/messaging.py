"""
messaging.py
Email message methods

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

import smtplib
from email.mime.text import MIMEText


def send_smtp_message(data, destination, source_user, source_pwd, source_server, source_port):
    """
    Send a message to an eMail address
    """
    msg = MIMEText(data, 'plain')
    msg['Subject'] = "House Message"
    msg['From'] = source_user
    msg['To'] = destination

    server = smtplib.SMTP_SSL(source_server, source_port)
    server.login(source_user, source_pwd)
    server.sendmail(source_user, destination, msg.as_string())