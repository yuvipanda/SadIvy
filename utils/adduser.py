#!/usr/bin/env python
from pymongo.connection import Connection
import sys

conn = Connection("localhost")
db = conn.twitter
users = db.users

user = {'Number': sys.argv[1], 'Username': sys.argv[2], 'Password': sys.argv[3]}

users.insert(user)
