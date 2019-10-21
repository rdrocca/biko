from datetime import datetime
from pymongo import MongoClient


class Dbconn:
    def __init__(self):
        self.dbuser = "admin"
        self.dbpass = "bikoadmin1"
        self.dbnode = 'ds040017.mlab.com:40017/bikodb'
        self.db = None
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = MongoClient('mongodb://' + self.dbuser + ':' + self.dbpass + '@' + self.dbnode)
        except TimeoutError:
            exit("Error: Unable to connect to the database")
        self.db = self.connection['bikodb']

    def get_collection(self, collection_name):
        if self.db is None:
            self.connect()
        return self.db[collection_name]

    def add_booking(self, new_booking):
        if self.db is None:
            self.connect()
        collection = self.db['bookings']
        booking_id = collection.insert_one(new_booking[1]).inserted_id
        return True if booking_id is not None else False

    def get_booking(self, user_id):
        if self.db is None:
            self.connect()
        collection = self.db['bookings']
        record = collection.find_one({"user": user_id})
        return True if record is not None else False
