'''
Created on Aug 4, 2014

@author: sush
'''
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from src.store.constants import CLASS_NAME_KEY, PROP_NAME_KEY, OBJECT_NAME_KEY, \
    UPDATED_EXISTING_KEY, NAME_NODE_COLLECTION
from src.store.stringStore import StringStore

class NameStore(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        dbConn = params
        self.collection = dbConn.getDatabase()[NAME_NODE_COLLECTION]
        self.stringStore = StringStore(dbConn)

    def __getquery__(self, name, createMissingTokens = False):
        tokens = name.split()
        #TODO: parallelize it
        pos = 0;
        query = {}
        for token in tokens:
            if createMissingTokens:
                stringNode = self.stringStore.createStringNode(token)
            else:
                stringNode = self.stringStore.getStringNode(token)
            if stringNode == None:
                return {'_id':'-1'}
            else:
                pos += 1
                query["pos_%s"%(pos)] = stringNode['_id']
            query['length'] = pos
        return query

    def createNameNode(self, name):
        query = self.__getquery__(name, True)
        try:
            nodeId =  self.collection.insert(query)
            nameNode = {'_id':ObjectId(nodeId)}
            query.pop('length')
            for key in query.keys():
                stringNodeId = query[key]
                self.stringStore.addPosLinkToStringNode(stringNodeId=stringNodeId,
                                                        nameNodeId=ObjectId(nodeId),
                                                        positionKey=key)
            return nameNode
        except DuplicateKeyError:
            return self.getNameNode(name)

    def getNameById(self, nameNodeId):
        nameNode = self.collection.find_one({'_id':nameNodeId})
        if None == nameNode:
            return None
        length = nameNode['length']
        name = ""
        for i in range(0, length):
            name += self.stringStore.getStringNameById(nameNode["pos_%s" % (i + 1)]) + " "
        return name.strip()

    def getNameNodeById(self, nameNodeId):
        return self.collection.find_one({'_id':nameNodeId},
                                        {CLASS_NAME_KEY:1, PROP_NAME_KEY:1, OBJECT_NAME_KEY:1})

    def getNameNode(self, name):
        query = self.__getquery__(name)
        return self.collection.find_one(query,
                                        {CLASS_NAME_KEY:1, PROP_NAME_KEY:1, OBJECT_NAME_KEY:1})

    def addNameLink(self, nameNodeId, nodeId, nameKey):
        if None == nameKey or None == nameNodeId or None == nodeId:
            return
        updated = self.collection.update({'_id':nameNodeId}, { '$addToSet': { nameKey: nodeId } } )
        return updated[UPDATED_EXISTING_KEY]
