'''
Created on Aug 4, 2014

@author: sush
'''
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from src.store.Exception.storeError import StringNodeError

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
        self.collection.update({'_id':stringNodeId}, { '$addToSet': { positionKey: nameNodeId } })

    def createStringNode(self, string):
        tokens = string.split()
        if len(tokens) != 1:
            raise StringNodeError('string node name should not contain white spaces', string)
        try:
            nodeId =  self.collection.insert({'name':string})
            return {'_id':ObjectId(nodeId)}
        except DuplicateKeyError:
            return self.getStringNode(string)

    def getStringNameById(self, stringNodeId):
        strNode = self.collection.find_one({'_id':stringNodeId})
        if None != strNode:
            return strNode['name']
        return None

    def getStringNode(self, string):
        tokens = string.split()
        if len(tokens) != 1:
            raise StringNodeError('string node name should not contain white spaces', string)
        return self.collection.find_one({'name':string})

if __name__ == '__main__':
    pass
