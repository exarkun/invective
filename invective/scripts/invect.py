
"""
Primary command line hook.
"""

from twisted.conch.stdio import runWithProtocol
from twisted.python.log import startLogging

from invective.tui import CommandLineUserInterface

def main():
    startLogging(file('invective.log', 'w'))
    runWithProtocol(CommandLineUserInterface)
