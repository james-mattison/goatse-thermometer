import Adafruit_DHT
import time
from datetime import datetime
import curses
import flask
from flask import url_for
import threading
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

PIN = 18
DHT_SENSOR = Adafruit_DHT.DHT11


app = flask.Flask(__name__, static_url_path = "/root/static")

dts = lambda : datetime.now().strftime("%H:%M:%S")

screen = curses.initscr()

screen.border(0)
box = curses.newwin(6, 60, 3, 2)
box.box()
box.addstr(3, 25, "Monitor Starting")
box.border(1)
box.refresh()

class Sensor:

    humidity = None
    temperature = None
    writing = False


def run_sensor():
    i = 0
    while True:
        i += 1
        time.sleep(2)
        h, t = Adafruit_DHT.read(DHT_SENSOR, PIN) 
        box.clear()
        #try:
        if h is None or t is None:
            box.addstr(2, 4, f"[READ FAILED]")
            box.addstr(3, 4, f"H: {h} T: {t}")
            box.border(1)
            box.refresh()
            continue
        t = float(t)
        h = float(h)
        Sensor.temperature = t
        Sensor.humidity = h


        t = (9/5) * t + 32
        s = f"Temperature: {t:2.2f}F Humidity: {h:2.2f}%\n{dts()}"
        box.border(1)
        box.addstr(2, 4, f"[READ-OK {i}]")
        box.addstr(3, 4, s)
        box.border(1)
        box.refresh()
        if i % 5 == 0:
            Sensor.writing = True
            img = Image.open("/root/hello.jpg")
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("LiberationSans-Bold.ttf", size = 24)
            draw.text((20, 20), s, font = font)
            img.save("/root/static/temperature.png", optimize = True, quality = 50)
            print("{dts()}: Wrote temperature.png")
            Sensor.writing = False



thread = threading.Thread(target = run_sensor, daemon = True)
thread.start()

app = flask.Flask(__name__)

@app.route("/", methods = [ "GET", "POST" ])
def index():
    while Sensor.writing:
        time.sleep(0.1)
        print(f"Image file being written!")
    return flask.render_template("index.html")


if __name__ == "__main__":
    app.run("0.0.0.0", port = 80)
