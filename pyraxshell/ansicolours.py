'''
Created on 20 Oct 2013

@author: Simone Soldateschi
'''
import logging

from singleton import Singleton


@Singleton
class ANSIColours(object):
    '''
    ANSI colours facility
    '''


    def __init__(self):
        '''
        Constructor
        '''
        # supported ANSI colours
        self._colours = ['black', 'red', 'green', 'yellow', 'blue', 'magenta',
                         'cyan', 'white']
        
        # reset all ANSI attributes escape string
        self._endc = '\033[0m'
    
    @property
    def colours(self):
        '''
        list supported ANSI colours
        '''
        return self._colours
    
    @property
    def endc(self):
        '''
        reset all ANSI attributes escape string
        '''
        return self._endc
    
    def get(self, colour, bright = False):
        '''
        return ANSI escape string which represents 'colour'
        
        @param colour    name of the colour to translate to ANSI code
        @param bright    True for bright color, False for normal
        @return    ANSI colour escape string
        '''
        try:
            index = self._colours.index(colour)
            offset = 90 if not bright else 100
            return '\033[%dm' % (offset + index)
        except ValueError:
            logging.warn('colour \'%s\' not in \'%s\'' %
                         (colour, ', '.join([c for c in self._colours])))
            return None
