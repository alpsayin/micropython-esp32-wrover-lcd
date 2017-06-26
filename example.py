import machine
import ili9341
from machine import Pin

RED = ili9341.color565(255, 0, 0)

spi = machine.SPI(2,
                  baudrate=20000000,
                  mosi=Pin(23, Pin.OUT),
                  miso=Pin(25, Pin.IN),
                  sck=Pin(19, Pin.OUT))

display = ili9341.ILI9341(
            spi,
            cs=Pin(22, Pin.OUT),
            dc=Pin(21, Pin.OUT),
            rst=Pin(18, Pin.OUT),
            width=320,
            height=240)

bl = Pin(5, Pin.OUT)
bl.value(0)
display.fill(RED)
