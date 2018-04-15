import pyodbc
import json
from datetime import datetime

class Dbconnection():

    def __init__(self, fetches):
        self.fetches = fetches
        #sql server name
        self.server = ''
        #database name
        self.database = ''
        #sql login username - make sure sql login is enabled in sql server
        self.username = ''
        #sql lopgin password
        self.password = ''
        #driver version - search for SQL 2016 odbc driver if missing
        self.driver= '{ODBC Driver 13 for SQL Server}'
        #connection string is built
        self.connectionstring = 'DRIVER='+self.driver+';SERVER='+self.server+';PORT=1443;DATABASE='+self.database+';UID='+self.username+';PWD='+ self.password
        #connection is made - try block could be implemented, but as always on app - retry logic is in main.py
        self.connection = pyodbc.connect(self.connectionstring)
        #passes the fetches to parse method to pull out PRESENCE_UPDATE and MESSAGE_CREATE
        self.parse_fetch(self.fetches)

    def parse_fetch(self, fetch):
        #Used to convert fetch to the db query object
        self.insert = []
        print(fetch)
        for i in fetch:
            print(i)
            j = i
            if j.get('t') == 'PRESENCE_UPDATE':
                #needed to mitigate
                #horrible formatting issues - future refactor would implement format class
                x = []
                x.append('PRESENCE_UPDATE')
                d = j.get('d')
                x.append("""'""" + str(datetime.now()) + """'""")
                x.append(d.get('user').get('id'))
                temp = str(d.get('status'))
                temp = temp.replace("""'""", '')
                x.append("""'"""+temp+"""'""")
                temp = str(d.get('roles'))
                temp = temp.replace("""'""", '')
                x.append("""'""" + temp + """'""")
                x.append(d.get('guild_id'))
                temp = str(d.get('game'))
                temp = temp.replace("""'""", '')
                x.append("""'"""+ str(temp) + """'""")
                self.insert.append(x)
            if j.get('t') == 'MESSAGE_CREATE':
                #needed to mitigate
                #horrible formatting issues with the insert and single quotes (json)- future refactor would implement format class
                x = []
                x.append('MESSAGE_CREATE')
                d = j.get('d')
                x.append("""'""" + str(datetime.now()) + """'""")
                x.append(d.get('author').get('id'))
                x.append('Null')
                x.append('Null')
                x.append("""'""" + str(d.get('content')) + """'""")
                x.append(d.get('guild_id'))
                self.insert.append(x)



    def go(self):
        #inserts into the database
        for i in self.insert:
            print('INSERT INTO ' + str(i[0]) + ' VALUES (' + str(i[1]) +  ', ' + str(i[2]) + ', ' + str(i[3]) + ', '+  str(i[4]) + ', ' + str(i[5]) + ', ' + str(i[6]) + ');')
            self.connection.execute('INSERT INTO ' + str(i[0]) + ' VALUES (' + str(i[1]) +', ' + str(i[2]) + ', ' + str(i[3]) + ', '+  str(i[4]) + ', ' + str(i[5]) + ', ' + str(i[6]) + '); ')
            #without commit out execute wouldn't save and the process left open unhandled.
            self.connection.commit()
