
"""
Primary command line hook.
"""

from twisted.conch.stdio import runWithProtocol

from invective.tui import CommandLineUserInterface

def main():
    runWithProtocol(CommandLineUserInterface)
