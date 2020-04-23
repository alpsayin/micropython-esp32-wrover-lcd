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

def graph():
    random.seed(time.ticks_cpu() * time.ticks_us())
    graph = Graph(display, 30, 24, x=10, y=50, bg=0, fg=colors.RGB_YELLOW)
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
    txtarea = TextArea(display, 30, 10, x=10, y=10, bg=colors.RGB_WHITE, fg=colors.RGB_PURPLE)
    for i in range(10):
        txtarea.append("test %d" % i)
        txtarea.append("free %d" % gc.mem_free())
        txtarea.paint()

def test():
    import framebuf, gc, micropython
    # direct display access test
    (display.fill(colors.BGR565_WHITE))
    display.fill_rectangle(20, 20, 90, 90, colors.BGR565_RED)
    display.fill_rectangle(200, 20, 90, 90, colors.BGR565_GREEN)
    display.fill_rectangle(114, 130, 90, 90, colors.BGR565_BLUE)
    display.text("test 1 2 3", 20, 20, colors.BGR565_BLACK, colors.BGR565_WHITE)
    # framebuffered access tesst
    rawbuffer = bytearray(display.width*display.height*2)
    fb = framebuf.FrameBuffer(rawbuffer, display.width, display.height, framebuf.RGB565)
    fb.fill(colors.BGR565_RED)
    display.blit_buffer(rawbuffer, 0, 0, display.width, display.height)
    fb.fill(colors.BGR565_GREEN)
    display.blit_buffer(rawbuffer, 0, 0, display.width, display.height)
    fb.fill(colors.BGR565_BLUE)
    display.blit_buffer(rawbuffer, 0, 0, display.width, display.height)
    fb.fill(colors.BGR565_BLACK)
    display.blit_buffer(rawbuffer, 0, 0, display.width, display.height)

    # Higher level access
    text()
    fb.fill(colors.BGR565_BLACK)
    display.blit_buffer(rawbuffer, 0, 0, display.width, display.height)

    display.text("Random plot", 10, 10, colors.BGR565_BLACK, colors.BGR565_WHITE)
    graph()
    micropython.mem_info()
    fb = None
    rawbuffer = None
    gc.collect()
    micropython.mem_info()
