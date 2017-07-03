import framebuf
import utime
import ustruct

from framebuf import FrameBuffer
from array import array

RED = const(0xF800)
GREEN = const(0x07E0)
BLUE = const(0x001F)
BLACK = const(0x0000)
WHITE = const(0xFFFF)


def color565(r, g, b):
    return (r & 0xf8) << 8 | (g & 0xfc) << 3 | b >> 3


class DummyPin:
    """A fake gpio pin for when you want to skip pins."""

    OUT = 0
    IN = 0
    PULL_UP = 0
    PULL_DOWN = 0
    OPEN_DRAIN = 0
    ALT = 0
    ALT_OPEN_DRAIN = 0
    LOW_POWER = 0
    MED_POWER = 0
    HIGH_PWER = 0
    IRQ_FALLING = 0
    IRQ_RISING = 0
    IRQ_LOW_LEVEL = 0
    IRQ_HIGH_LEVEL = 0

    def __call__(self, *args, **kwargs):
        return False

    init = __call__
    value = __call__
    out_value = __call__
    toggle = __call__
    high = __call__
    low = __call__
    mode = __call__
    pull = __call__
    drive = __call__
    irq = __call__


class Display:
    _PAGE_SET = None
    _COLUMN_SET = None
    _RAM_WRITE = None
    _RAM_READ = None
    _INIT = ()
    _ENCODE_PIXEL = ">H"
    _ENCODE_POS = ">HH"
    _DECODE_PIXEL = ">BBB"

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self._fg = 0xFFFF
        self._bg = 0x0000
        self.init()

    def init(self):
        """Run the initialization commands."""
        for command, data in self._INIT:
            self._write(command, data)

    def _block(self, x0, y0, x1, y1, data=None):
        """Read or write a block of data."""
        self._write(self._COLUMN_SET, self._encode_pos(x0, x1))
        self._write(self._PAGE_SET, self._encode_pos(y0, y1))
        if data is None:
            size = ustruct.calcsize(self._DECODE_PIXEL)
            return self._read(self._RAM_READ,
                              (x1 - x0 + 1) * (y1 - y0 + 1) * size)
        self._write(self._RAM_WRITE, data)

    def _encode_pos(self, a, b):
        """Encode a postion into bytes."""
        return ustruct.pack(self._ENCODE_POS, a, b)

    def _encode_pixel(self, color):
        """Encode a pixel color into bytes."""
        return ustruct.pack(self._ENCODE_PIXEL, color)

    def _decode_pixel(self, data):
        """Decode bytes into a pixel color."""
        return color565(*ustruct.unpack(self._DECODE_PIXEL, data))

    def pixel(self, x, y, color=None):
        """Read or write a pixel."""
        if color is None:
            return self._decode_pixel(self._block(x, y, x, y))
        if not 0 <= x < self.width or not 0 <= y < self.height:
            return
        self._block(x, y, x, y, self._encode_pixel(color))
        return self

    def rect(self, x, y, width, height, color=None):
        """Draw a filled rectangle."""
        if color is None:
            color = self._fg
        x = min(self.width - 1, max(0, x))
        y = min(self.height - 1, max(0, y))
        w = min(self.width - x, max(1, width))
        h = min(self.height - y, max(1, height))
        self._block(x, y, x + w - 1, y + h - 1, b'')
        chunks, rest = divmod(w * h, 512)
        pixel = self._encode_pixel(color)
        if chunks:
            data = pixel * 512
            for count in range(chunks):
                self._write(None, data)
        self._write(None, pixel * rest)
        self.x = x
        self.y = y
        return self

    def fill(self, color=None):
        """Fill whole screen."""
        if color is not None:
            self._bg = color

        return self.rect(0, 0, self.width, self.height, color)

    def hline(self, x, y, width, color=None):
        """Draw a horizontal line."""
        return self.rect(x, y, width, 1, color)

    def vline(self, x, y, height, color=None):
        """Draw a vertical line."""
        return self.rect(x, y, 1, height, color)

    def move(self, x=None, y=None):
        if x:
            self.x = x
        if y:
            self.y = y
        return self

    def fg(self, color=None):
        if color:
            self._fg = color
            return self
        else:
            return self._fg

    def bg(self, color=None):
        if color:
            self._bg = color
            return self
        else:
            return self._bg

    def text(self, text, x=None, y=None, color=None, background=None):
        if background is None:
            background = self._bg
        if color is None:
            color = self._fg
        if x is None:
            x = self.x
        if y is None:
            y = self.y

        x = min(self.width - 1, max(0, x))
        y = min(self.height - 1, max(0, y))

        lines = text.splitlines()
        longest = 0
        for line in lines:
            longest = max(longest, len(line))

        h = min(self.height - y, 8)

        buffer = bytearray(longest * 8 * 8 * 2)

        fb = framebuf.FrameBuffer(buffer, 8 * longest, 8, framebuf.RGB565)
        for line in lines:
            fb.fill(background)
            fb.text(line, 0, 0, color)
            self.blit_buffer(buffer, x, y, len(line) * 8, h)
            y += 8
            if y >= self.height:
                break

    def blit_buffer(self, buffer, x, y, width, height):
        """Copy pixels from a buffer."""
        if (not 0 <= x < self.width or
            not 0 <= y < self.height or
            not 0 < x + width <= self.width or
                not 0 < y + height <= self.height):
            raise ValueError("out of bounds")

        view = memoryview(buffer)
        onerow = 2 * width
        for row in range(height):
            offset = row * onerow
            self._block(x, y + row, x + width - 1, 1,
                        view[offset:offset + onerow])


class DisplaySPI(Display):

    def __init__(self, spi, dc, cs, rst=None, width=1, height=1):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        if self.rst:
            self.rst.init(self.rst.OUT, value=0)
            self.reset()
        super().__init__(width, height)

    def reset(self):
        self.rst.value(0)
        utime.sleep_ms(50)
        self.rst.value(1)
        utime.sleep_ms(50)

    def _write(self, command=None, data=None):
        self.cs.value(0)

        if command is not None:
            self.dc.value(0)
            self.spi.write(bytearray([command]))
        if data is not None:
            self.dc.value(1)
            self.spi.write(data)

        self.cs.value(1)

    def _read(self, command=None, count=0):
        self.dc.value(0)
        self.cs.value(0)
        if command is not None:
            self.spi.write(bytearray([command]))
        if count:
            data = self.spi.read(count)
        self.cs.value(1)
        return data


class Area(object):

    def __init__(self, display, cols, rows, fg=WHITE, bg=BLACK, border=RED,
                 padding=4, x=0, y=0):
        self.buffer = None
        self.fb = None
        self.display = display
        self.padding = padding
        self.bg = bg
        self.fg = fg
        self.border = border
        self.move(x, y)
        self.resize(cols, rows)
        if hasattr(self, 'init'):
            self.init()

    def initfb(self):
        if self.buffer is None:
            self.buffer = bytearray(self.width * self.height * 2)
        if self.fb is None:
            self.fb = FrameBuffer(self.buffer, self.width, self.height,
                                  framebuf.RGB565)

    def free_fb(self):
        self.buffer = None
        self.fb = None

    def move(self, x, y):
        self.x = x
        self.y = y

    def resize(self, cols, rows):
        pad = 1 + self.padding * 2
        self.rows = rows
        self.cols = cols
        self.width = cols * 8 + pad
        self.height = (rows * 8) + pad
        self.dirty = True

    def paint(self):
        self.initfb()
        self.fb.fill(self.bg)
        self.fb.rect(0, 0, self.width, self.height, self.border)

    def blit(self):
        self.fb = None
        self.display.blit_buffer(
            self.buffer, self.x, self.y, self.width, self.height)
        self.buffer = None


class Point(object):
    x = 0
    y = 0
    v = 0

    def __init__(self, val):
        self.v = val


class Graph(Area):

    def init(self):
        self.scale_x = 8
        self.scale_y = 8
        self.points = array('B', [])

    def point(self, v):
        content_width = len(self.points) * self.scale_x
        window_width = self.width - 2 - self.padding * 2
        if (content_width >= window_width):
            self.points = self.points[1:]

        if v > self.scale_y:
            self.scale_y = int(v) + 1

        self.points.append(v)
        self.dirty = True

    def paint(self):
        if not self.dirty:
            return
        super(Graph, self).paint()
        prev = None
        pad = 1 + self.padding
        x = 0
        for v in self.points:
            point = Point(v)
            point.x = pad + x * self.scale_x
            v = point.v if point.v >= 1 else 1
            point.y = (self.height / self.scale_y) * (self.scale_y / v)
            point.y = round(self.height - point.y)
            point.y += self.padding + 1
            x += 1
            if (prev):
                self.fb.line(prev.x, prev.y, point.x, point.y, self.fg)
            prev = point

        self.blit()
        self.dirty = False


class TextArea(Area):

    def init(self):
        self.lines = []

    def text(self, txt):
        self.lines = txt.splitlines()
        self.dirty = True
        self.paint()

    def append(self, text):
        self.dirty = True
        if isinstance(text, str):
            lines = text.splitlines()
        elif isinstance(text, list):
            lines = text
        else:
            lines = str(text).splitlines()

        for line in lines:
            self.lines.append(line)
        scrollback = self.rows * 2
        if len(self.lines) > scrollback:
            self.lines = self.lines[-scrollback:]

    def paint(self, skip_lines=None):
        if not self.dirty:
            return

        super(TextArea, self).paint()

        pad = 1 + self.padding
        y = pad

        lines = self.lines
        if skip_lines:
            lines = lines[skip_lines - 1:]

        if len(lines) > self.rows:
            lines = lines[-self.rows:]

        for line in lines:
            if len(line) > self.cols:
                line = line[0:self.cols - 1]
            self.fb.text(line, pad, y, self.fg)
            y += 8
        self.blit()
        self.dirty = False
