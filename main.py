import disbot

x = disbot.Disbot(token='')

#always on app - simple logic for simple function
while 1:
    x.loopcontrol()
    try:
        x.resetconnection()
        x.async()
    except:
        pass
