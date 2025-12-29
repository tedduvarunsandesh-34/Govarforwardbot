from keep_alive import start
start()   # start web server for Render & UptimeRobot

from bot import Bot

app = Bot()
app.run()
