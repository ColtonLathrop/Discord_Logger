import json
import websockets
import asyncio
import time
from datetime import date, datetime, timedelta
import db_con

class Disbot():
    authurl = 'https://discordapp.com/api/oauth2/authorize'
    tokenurl = 'https://discordapp.com/api/v6/oauth2/token'
    REDIRECT_URI = 'https://nicememe.website'
    code = ''
    gateway = 'wss://gateway.discord.gg/?v=6&encoding=json'

    def __init__(self, token):
        #initialize some of the starting variables
        self.heartbeatinterval = None
        self.lastheartbeat = datetime.utcnow()
        self.nextheartbeat = None
        self.heartbeattracker = 1
        self.token = token
        self.callinject = False
        self.isauthed = False
        self.current_status = None
        self.queue = 0


    def resetconnection(self):
        #used to reset the auth flag on retry to force the logic to reauth on exception
        # probably could do something better - but hey it works
        self.isauthed = False
        return

    def loopcontrol(self):
        #sleep to minimize cpu usage (running this on azure vm with low specs)
        time.sleep(2)
        return

    async def connect(self):
        #creates the websocket object and associates it with the connection class
        async with websockets.connect(self.gateway) as self.websocket:
            #pull initial heartbeat
            recv = await self.websocket.recv()
            recvjson = json.loads(recv)
            #primary request handling logic - terrible code, but works well due to simple requirements.
            while 1:
                zz = []
                time.sleep(2)
                #cheeky logic to prevent haning the async on waiting for a request and never sending heartbeat
                self.queue = self.websocket.messages.qsize()
                #I don't believe I am using asyncio right, but this works well in pulling only pending messages
                if self.websocket.messages.qsize() > 0:
                    updates = []
                    for i in range(self.queue):
                        activity = await self.websocket.recv()
                        updates.append(json.loads(activity))
                    self.store_db(updates)
                if self.handleheartbeat(recvjson) == True:
                    await self.websocket.send(bytes('{"op": 1, "d":%s}' % str(self.heartbeattracker), 'utf-8'))
                    recv = await self.websocket.recv()
                    recvjson = json.loads(recv)
                    zz.append(recvjson)
                    #due to async nature, sometimes updates we actually want to pull are recv() and not just to heartbeat opcode 0
                    #always try to store this.
                    self.store_db(zz)
                #simple check to see if auth flag is set - if not make auth happen
                if self.isauthed == False:
                    #send the generated auth request bytes over socket
                    await self.websocket.send(self.authrequest())
                    print('Request Payload:' + str(self.authrequest()))
                    recv = await self.websocket.recv()
                    recvjson = json.loads(recv)
                    print('response payload: ' + str(recvjson))
                    if recvjson.get('t') == 'READY':
                        print('Client Now Authed')
                        self.isauthed = True
                    if self.current_status == None:
                        recv = await self.websocket.recv()
                        recvjson = json.loads(recv)
                        self.current_status = recvjson


    def store_db(self, json):
        x = db_con.Dbconnection(json)
        x.go()
        print('Uploaded to DB.')
        return

    def authrequest(self):
        #basic dict for auth request - converted to bytes encoded utf-8
        #bot token is also passed
        auth = {"op":2, "d":{"token":self.token,
        "properties":
        {"$os":"Windows", "$browser":"Python", "$device":"SurfaceBook"},
        "compress":False,"large_threshold":250, "shard":[0,1],
        "presence":{"game":{"name":"Python","type":0},
        "status":"online","since": None,"afk":False}}}
        x = json.dumps(auth, ensure_ascii=True)
        return bytes(x, 'utf-8')


    def handleheartbeat(self, jsonx):
        #Handles initializing the heartbeattracker, True if send heartbeat
        #questionable logic, but works well in handling whether it's time to beat
        NoneType = type(None)
        try:
            if self.nextheartbeat is not None:
                if self.nextheartbeat < (datetime.utcnow() + timedelta(seconds=2)):
                    #-5 seconds to ensure we don't get dropped right at 45 (untested)
                    self.nextheartbeat = datetime.utcnow() + timedelta(seconds=(self.heartbeatinterval/1000)-5)
                    self.heartbeattracker += 1
                    print('Repeating Heartbeat: #' + str(self.heartbeattracker))
                    return True
                else:
                    return False
            else:
                pass
            # shoudln't hit this code on non-initial connection create
            if 'heartbeat_interval' in jsonx.get('d'):
                self.heartbeatinterval = jsonx['d']['heartbeat_interval']
                self.nextheartbeat = self.lastheartbeat + timedelta(seconds=(self.heartbeatinterval/1000)-5)
                print('Initialized Heartbeat.')
                return True
            else:
                return False
        except:
            # Really only expcetion that can hit is the get('d'), but data field is always in discord gateway json responses
            print('Error Handling Heartbeat Logic.')
            return False


    def async(self):
        #start out event loop until compelte (won't complete due to loop)
        #always running implementation so no need for any other logic here
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.connect())
