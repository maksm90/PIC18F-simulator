"""
Run all minipic core tests
"""

from unittest import defaultTestLoader, TextTestRunner
import os
import sys

def runTests(testDir):
    import piclog
    piclog.logger.disabled = True
    testSuite = defaultTestLoader.discover(testDir)
    TextTestRunner(verbosity=1).run(testSuite)
    piclog.logger.disabled = False


if __name__ == '__main__':
    thisdir = os.path.dirname(os.path.realpath(__file__))
    parentdir = os.path.dirname(thisdir)
    sys.path.append(parentdir)

    runTests(thisdir)
