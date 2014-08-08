'''
Created on Aug 4, 2014

@author: sushant pradhan
'''
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from src.store.Exception.storeError import StringNodeError
from src.store.constants import NAME_KEY, ID_KEY

class StringStore(object):
    '''
    classdocs
    '''
    def __init__(self, params):
        '''
        Constructor
        '''
        dbConn = params
        self.collection = dbConn.getDatabase().stringNodes

    def addPosLinkToStringNode(self, stringNodeId, nameNodeId, positionKey):
        self.collection.update({ID_KEY:stringNodeId}, { '$addToSet': { positionKey: nameNodeId } })

    def createStringNode(self, string):
        tokens = string.split()
        if len(tokens) != 1:
            raise StringNodeError('string node name should not contain white spaces', string)
        try:
            nodeId =  self.collection.insert({NAME_KEY:string})
            return {ID_KEY:ObjectId(nodeId)}
        except DuplicateKeyError:
            return self.getStringNode(string)

    def getStringNameById(self, stringNodeId):
        strNode = self.collection.find_one({ID_KEY:stringNodeId})
        if None != strNode:
            return strNode[NAME_KEY]
        return None

    def getStringNode(self, string):
        tokens = string.split()
        if len(tokens) != 1:
            raise StringNodeError('string node name should not contain white spaces', string)
        return self.collection.find_one({NAME_KEY:string})
