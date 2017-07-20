#-------------------------------------------------------------------------------
# Name:        /faraday/classes/helper.py
# Purpose:      Provides helper functions to make faraday software easier
#
# Author:      Bryce Salmi
#
# Created:     7/19/2017
# Licence:     GPLv3
#-------------------------------------------------------------------------------
import os
import logging
import sys
import ConfigParser

class Helper:
    """
    test
    """

    def __init__(self, name):
        """
        """
        # Class variables
        self.path = ''

        # Local variables
        self._name = name
        self._logger = ''


    def getLogger(self):
        """
        Get logger configuration and create instance of a logger
        """
        # Known paths where loggingConfig.ini can exist
        relpath1 = os.path.join('etc', 'faraday')
        relpath2 = os.path.join('..', 'etc', 'faraday')
        setuppath = os.path.join(sys.prefix, 'etc', 'faraday')
        userpath = os.path.join(os.path.expanduser('~'), '.faraday')
        self.path = ''

        # Check all directories until first instance of loggingConfig.ini
        for location in os.curdir, relpath1, relpath2, setuppath, userpath:
            try:
                logging.config.fileConfig(os.path.join(location, "loggingConfig.ini"))
                self.path = location
                break
            except ConfigParser.NoSectionError:
                pass

        self._logger = logging.getLogger(self._name)
        return self._logger
