#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import argparse
import commands
import logging
import sys

class DisplayManager(object):
    # Modes
    SINGLE  = 1
    DUAL    = 2

    def __init__(self, args):
        # Logger
        self.log = logging.getLogger('logger')
        self.log.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] %(levelname)-8s : %(message)s")
        handler.setFormatter(formatter)
        self.log.addHandler(handler)

        # Options
        self.mode       = self.SINGLE
        self.internal   = dict()
        self.external   = dict()
        self.verbose    = False
        self.dryrun     = False

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
            self.log.info("Set to single display mode")
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

        # Set laptop monitor to its best resolution.
        self.__syscall('xrandr --output %(name)s --mode %(resolution)s ' + 
            '--rate %(rate)s', self.internal)

        # Set laptop monitor as your primary monitor.
        self.__syscall('xrandr --output %(name)s --primary', self.internal)

        # Put the laptop left, external monitor right
        self.__syscall('xrandr --output %s --right-of %s', \
            (self.external['name'], self.internal['name']))

        # Move LVDS1 to the bottom to make menu available
        external_height = int(self.external['resolution'].split('x')[1])
        internal_height = int(self.internal['resolution'].split('x')[1])
        height_diff = external_height - internal_height
        if external_height > internal_height:
            self.log.debug("Move internal to the bottom by %dpx", height_diff)
            self.__syscall('xrandr --output %s --pos 0x%d', \
                (self.internal['name'],height_diff,))

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
            help="internal display (default); sample format: HDMI1;1920x1080;60")
        parser.add_argument('-e', '--external-output', 
            help="external display; the same format as for internal one")
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
            elif opt == 'dryrun':
                self.dryrun = arg
                if self.dryrun:
                    self.log.info('----- PERFORMING DRY RUN! -----')
            else:
                self.log.debug("Param %s doesn't match!", opt)

if __name__ == "__main__":
    dm = DisplayManager(sys.argv[1:])
    dm.run()