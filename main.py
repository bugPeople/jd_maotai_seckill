#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Usage:
#     ./main.py -d -v subtest -a 1 --arg2 2
#

"""Python script contains logging setup and argparse"""

import argparse
import logging
import os
import sys

from maotai.jd_spider_requests import JdSeckill

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
SCRIPT_NAME = os.path.basename(__file__)


def log_init(root_path, name="app", debug=False, verbose=False):
    """Set up global logs"""
    log_format = "%(asctime)s %(process)s %(levelname)s [-] %(message)s"
    log_level = logging.INFO
    log_path = os.path.join(root_path, "log")
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    if debug:
        log_level = logging.DEBUG
        log_file = os.path.join(log_path, "%s.debug.log" % name)
    else:
        log_file = os.path.join(log_path, "%s.log" % name)

    if verbose:
        logging.basicConfig(
                format=log_format,
                level=log_level)
    else:
        logging.basicConfig(
                format=log_format,
                level=log_level,
                filename=log_file)


def parse_sys_args(argv):
    """Parses commaond-line arguments"""
    parser = argparse.ArgumentParser(
        description="Parser arguments")
    parser.add_argument(
        "-d", "--debug", action="store_true", dest="debug",
        default=False, help="Enable debug message.")
    parser.add_argument(
        "-v", "--verbose", action="store_true", dest="verbose",
        default=False, help="Show message in standard output.")
    parser.add_argument(
        "-a", "--all", action="store_true",
        dest="all", required=False,
        default=False, help="Reserve and second kill product.")
    parser.add_argument(
        "--run-once", action="store_true",
        dest="run_once", required=False,
        default=False, help="Run action once.")

    return parser.parse_args(argv[1:]), parser


def main():
    args, parser = parse_sys_args(sys.argv)
    log_init(CURRENT_PATH, SCRIPT_NAME, args.debug, args.verbose)

    if not args.all:
        parser.print_help()
        sys.exit(1)

    jd_seckill = JdSeckill(run_once=args.run_once)

    if args.all:
        jd_seckill.reserve_and_seckill()


if __name__ == "__main__":
    main()
