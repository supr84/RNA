'''
Created on Aug 4, 2014

@author: sush
'''
class NameNodeError(Exception):
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



class UserNodeError(Exception):
    '''
    classdocs
    '''
    def __init__(self, message, userName):
        '''
        Constructor
        '''
        self.msg = message
        self.val = userName

    def __str__(self):
        return "{msg:'%s', val:'%s'}" % (self.msg, self.val)

class StringNodeError(Exception):
    '''
    classdocs
    '''
    def __init__(self, message, stringName):
        '''
        Constructor
        '''
        self.msg = message
        self.val = stringName

    def __str__(self):
        return "{msg:'%s', val:'%s'}" % (self.msg, self.val)

class PropertyNodeError(Exception):
    '''
    classdocs
    '''
    def __init__(self, message, propertyName):
        '''
        Constructor
        '''
        self.msg = message
        self.val = propertyName

    def __str__(self):
        return "{msg:'%s', val:'%s'}" % (self.msg, self.val)

class ObjectNodeError(Exception):
    '''
    classdocs
    '''
    def __init__(self, message, objNode):
        '''
        Constructor
        '''
        self.msg = message
        self.val = objNode

    def __str__(self):
        return "{msg:'%s', val:'%s'}" % (self.msg, self.val)

class ValueNodeError(ObjectNodeError):
    def __init__(self, message, objNode):
        ObjectNodeError(message=message, objNode=objNode)

class ClassNodeError(ObjectNodeError):
    def __init__(self, message, objNode):
        ObjectNodeError(message=message, objNode=objNode)
