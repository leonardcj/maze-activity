import threading
import subprocess

from gi.repository import GObject

GObject.threads_init()


class Accelerometer():

    ACCELEROMETER_DEVICE = '/sys/devices/platform/lis3lv02d/position'

    def read_position(self):
        """
        return x, y, z values or None if no accelerometer is available
        """
        try:
            fh = open(self.ACCELEROMETER_DEVICE)
            string = fh.read()
            xyz = string[1:-2].split(',')
            fh.close()
            return int(xyz[0]), int(xyz[1]), int(xyz[2])
        except:
            return 0, 0, 0


class EbookModeDetector(GObject.GObject):

    EBOOK_DEVICE = '/dev/input/event4'

    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_FIRST, None, ([bool])), }

    def __init__(self):
        GObject.GObject.__init__(self)
        self._ebook_mode = self._get_initial_value()
        self._start_reading()

    def get_ebook_mode(self):
        return self._ebook_mode

    def _get_initial_value(self):
        try:
            output = subprocess.call(['evtest', '--query', self.EBOOK_DEVICE,
                                      'EV_SW', 'SW_TABLET_MODE'])
            # 10 is ebook_mode, 0 is normal
            return (output == 10)
        except:
            return False

    def _start_reading(self):
        thread = threading.Thread(target=self._read)
        thread.start()

    def _read(self):
        fd = open(self.EBOOK_DEVICE, 'rb')
        for x in range(12):
            fd.read(1)
        value = ord(fd.read(1))
        fd.close()
        self._ebook_mode = (value == 1)
        self.emit('changed', self._ebook_mode)
        # restart
        GObject.idle_add(self._start_reading)

# TODO: Move to tests

import logging
from gi.repository import Gtk


def log_ebook_mode(detector, ebook_mode):
    logging.error('Ebook mode %s', ebook_mode)


def quit(win, detector):
    Gtk.main_quit()


def main():
    win = Gtk.Window()
    win.set_default_size(450, 550)
    label = Gtk.Label('Put your xo in ebook mode nd in notebook mode')
    win.add(label)
    win.show_all()
    ebookdetector = EbookModeDetector()
    ebookdetector.connect('changed', log_ebook_mode)
    win.connect('destroy', quit, ebookdetector)
    Gtk.main()

if __name__ == '__main__':
    main()
