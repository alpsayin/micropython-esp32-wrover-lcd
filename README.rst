ESP32-WROVER LCD Display Driver for MicroPython
===============================================
This is a fork of the fork of the Adafruit Display drivers for MicroPython. Only a couple
of minor changes were made to adapt the Adafruit driver to work with the LCD
on the Espressif ESP32-WROVER kit (v3). And I've made some other changes to make it 
work with v4.1. Things like display being in portrait mode and color setting being in BGR
rather than RGB. And most notably a bugfix that prevented writing row blocks.

Original fork here: https://github.com/20after4/micropython-esp32-wrover-lcd

Example code is included in example.py.

Tested with MicroPython esp32spiram-idf4-20200422-v1.12-388-g388d419ba.bin. 
Get the latest firmware from http://micropython.org/download#esp32

Read the docs (probaly the original docs of the Adafruit driver)
=============
Documentation -partially- available at http://micropython-rgb.readthedocs.io/
