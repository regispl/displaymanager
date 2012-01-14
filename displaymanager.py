#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import argparse
import commands
import logging
import sys

class DisplayManager(object):
    # Modes
    SINGLE  = 101
    DUAL    = 102

    # Type
    INTERNAL    = 201
    EXTERNAL    = 202

    # Positions
    INTERNAL_EXTERNAL   = 301
    EXTERNAL_INTERNAL   = 302

    def __init__(self, args):
        # Logger
        self.log = logging.getLogger('logger')
        self.log.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] %(levelname)-8s : %(message)s")
        handler.setFormatter(formatter)
        self.log.addHandler(handler)

        # Options
        self.mode           = self.SINGLE
        self.internal       = dict()
        self.external       = dict()
        self.primary        = self.INTERNAL
        self.order          = self.INTERNAL_EXTERNAL
        self.verbose        = False
        self.dryrun         = False

        # Parse args and process options
        self.__process_opts(self.__parse_args(args))

    def set_verbose(self):
        self.verbose = True
        self.log.setLevel(logging.DEBUG)
        self.log.info('Set verbosity to DEBUG')

    def run(self):
        if self.mode == self.SINGLE:
            self.log.info("Set to single display mode")
            self.__set_single()
        else:
            self.log.info("Set to dual display mode")
            self.__set_dual()
        self.log.info('Done!')

    def __set_single(self):
        # Turn off external monitor
        self.__syscall('xrandr --output %(name)s --off', self.external)

        # Set external monitor to its best resolution.
        self.__syscall('xrandr --output %(name)s --mode %(resolution)s ' + 
            '--rate %(rate)s', self.internal)

        # Reset positon
        self.__syscall('xrandr --output %(name)s --pos 0x0', self.internal)

        # Set Screen0 size
        self.__syscall('xrandr --screen 0 --fb %(resolution)s', self.internal)

    def __set_dual(self):
        # Set external monitor to its best resolution.
        self.__syscall('xrandr --output %(name)s --mode %(resolution)s ' + 
            '--rate %(rate)s', self.external)

        # Set internal monitor to its best resolution.
        self.__syscall('xrandr --output %(name)s --mode %(resolution)s ' + 
            '--rate %(rate)s', self.internal)

        # Set primary monitor.
        primary = self.primary if self.primary else self.internal['name']
        self.__syscall('xrandr --output %s --primary', (primary,))

        # Decide which goes to the left or right
        params = tuple()
        if self.order == self.INTERNAL_EXTERNAL:
            params = (self.external['name'], self.internal['name'])
        else:
            params = (self.internal['name'], self.external['name'])
        self.__syscall('xrandr --output %s --right-of %s', params)

        # Displays' position
        horizontal_offset = 0
        vertical_offset = 0

        # Move internal to the bottom to make menu available if external height
        # is bigger than internal
        external_height = int(self.external['resolution'].split('x')[1])
        internal_height = int(self.internal['resolution'].split('x')[1])
        if external_height > internal_height:
            vertical_offset = external_height - internal_height
            self.log.debug("Move internal display to the bottom by %dpx", \
                vertical_offset)

        # Move internal to the right if it's the rightmost display
        if self.order == self.EXTERNAL_INTERNAL:
            horizontal_offset = int(self.external['resolution'].split('x')[0])
            self.log.debug("Move internal display to the right by %dpx", \
                horizontal_offset)
        self.__syscall('xrandr --output %s --pos %dx%d', \
            (self.internal['name'], horizontal_offset, vertical_offset,))

    def __syscall(self, cmd, args = None):
        args = args if args else tuple()
        output = None
        to_call = cmd % args
        self.log.debug("calling: %s", to_call)
        if not self.dryrun:
            pass
            output = commands.getstatusoutput(to_call)
        return output

    def __parse_args(self, args):
        # Parse options
        parser = argparse.ArgumentParser(
            description="Easily extend Xubuntu desktop to external display " + 
                "with xrandr.")
        parser.add_argument('-m', '--mode', default=self.SINGLE,
            help="display configuration: single or dual")
        parser.add_argument('-i', '--internal-output', 
            help="internal display (default); format is: \"HDMI1;1920x1080;60\"")
        parser.add_argument('-e', '--external-output', 
            help="external display; the same format as for internal one")
        parser.add_argument('-p', '--primary', default=None,
            help="define primary display using it's name, i.e. --primary \"HDMI1\"")
        parser.add_argument('-o', '--order', default=None,
            help="define display order: \"IE\" if internal on the left, " + 
                "\"EI\" otherwise")
        parser.add_argument('-v', '--verbose', action='store_true', default=False,
            help="verbose")
        parser.add_argument('--dryrun', action='store_true', default=False,
            help="make a dry run - without applying changes")
        options = vars(parser.parse_args())
        return options

    def __process_opts(self, options):
        # Verbosity first
        if options['verbose']:
            self.set_verbose()

        # Retrieve parsed options
        for opt, arg in options.items():
            self.log.debug("Parsed option: %s %s", opt, arg)
            if opt == 'mode' and arg.lower() in ('single', 'dual'):
                self.mode = self.SINGLE if arg.lower() == 'single' \
                    else self.DUAL
            elif opt == 'internal_output':
                params = arg.split(';')
                self.internal['name'] = params[0]
                self.internal['resolution'] = params[1]
                self.internal['rate'] = params[2]
            elif opt == 'external_output':
                params = arg.split(';')
                self.external['name'] = params[0]
                if len(params) > 1:
                    self.log.debug('External output fully specified')
                    self.external['resolution'] = params[1]
                    self.external['rate'] = params[2]
            elif opt == 'primary':
                self.primary = arg
            elif opt == 'order' and arg and arg.lower() in ('ie', 'ei'):
                self.order = self.INTERNAL_EXTERNAL if arg.lower() == 'ie' \
                    else self.EXTERNAL_INTERNAL
            elif opt == 'dryrun':
                self.dryrun = arg
                if self.dryrun:
                    self.log.info('----- PERFORMING DRY RUN! -----')
            else:
                self.log.debug("Param %s doesn't match!", opt)

if __name__ == "__main__":
    dm = DisplayManager(sys.argv[1:])
    dm.run()