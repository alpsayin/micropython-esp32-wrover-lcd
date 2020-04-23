import machine
import random
import ili9341
import time
import gc
import colors
from machine import Pin
from widgets import TextArea
from widgets import Graph


# use VSPI (ID=2) at 80mhz
spi = machine.SPI(2,
                  baudrate=32000000,
                  mosi=Pin(23, Pin.OUT),  # mosi = 23
                  miso=Pin(25, Pin.IN),   # miso = 25
                  sck=Pin(19, Pin.OUT))   # sclk = 19

display = ili9341.ILI9341(
    spi,
    cs=Pin(22, Pin.OUT),          # cs   = 22
    dc=Pin(21, Pin.OUT),          # dc   = 21
    rst=Pin(18, Pin.OUT),         # rst  = 18
    width=240,
    height=320)

# turn on the backlight
bl = Pin(5, Pin.OUT)
bl.value(0)

# fill the screen with some colored boxes
(display.fill(colors.WHITE))

#        .rect(20, 20, 90, 90, RED)
#        .rect(200, 20, 90, 90, GREEN)
#        .rect(114, 130, 90, 90, BLUE)
#        .text("test 1 2 3", 125, 125, BLACK))

random.seed(time.ticks_cpu() * time.ticks_us())


def graph():
    graph = Graph(display, 30, 8, x=10, y=150)
    graph.point(10)
    for i in range(50):
        v = random.randint(0, 10)
        graph.point(v)
        graph.paint()
        # time.sleep(0.1)

    graph.free_fb()
    gc.collect()


def text():
    gc.collect()
    txtarea = TextArea(display, 30, 10, x=10, y=10)
    for i in range(10):
        txtarea.append("test %d" % i)
        txtarea.append("free %d" % gc.mem_free())
        txtarea.paint()

graph()
text()
