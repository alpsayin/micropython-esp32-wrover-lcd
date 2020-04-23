from micropython import const

ONES5 = const((1<<5)-1)
ONES6 = const((1<<6)-1)
ONES8 = const((1<<8)-1)

BGR565_BLUE = const(0xF800)
BGR565_GREEN = const(0x07E0)
BGR565_RED = const(0x001F)
BGR565_BLACK = const(0x0000)
BGR565_WHITE = const(0xFFFF)

RGB_YELLOW = const(0xFF7F07)  #YELLOW
RGB_GREEN = const(0x00FF00)  #GREEN
RGB_RED = const(0xFF0000)  #RED
RGB_BLUE = const(0x0000FF) #BLUE
RGB_PURPLE = const(0xFF0FF0) #PURPLE
RGB_ORANGE = const(0x770F00) #I WANTED ORANGE, IT GAVE ME LEMON-LIME
RGB_WHITE = const(0xFFFFFF) #WHITE
RGB_BLACK = const(0x000000) #HAVE A GUESS
RGB_OFF = const(0x000000) #HAVE A GUESS

def BGR565toRGB(color16):
    blue = ((color16>>11) & ONES5)<<3
    green = ((color16>>6) & ONES6)<<2
    red = ((color16) & ONES5)<<3
    return (red<<16) | (green<<8) | blue

def RGBtoBGR565(color24):
    red = ((color24>>16) & ONES8)>>3
    green = ((color24>>8) & ONES8)>>2
    blue = ((color24) & ONES8)>>3
    return (blue<<11) | (green<<5) | red