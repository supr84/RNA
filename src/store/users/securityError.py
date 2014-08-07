'''
Created on Aug 4, 2014

@author: sush
'''
class SecurityBreachError(Exception):
    '''
    classdocs
    '''
    def __init__(self, message, name):
        '''
        Constructor
        '''
        self.msg = message
        self.val = name

    def __str__(self):
        return "{msg:'%s', val:'%s'}" % (self.msg, self.val)
