#!/usr/bin/env python3
"""Entry point for LavaCLI - run with: python -m lavacli"""
import sys

from lavacli.app import run

if __name__ == '__main__':
    run(sys.argv[1:])
