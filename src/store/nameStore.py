'''
Created on Aug 4, 2014

@author: sushant pradhan
'''
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from src.store.constants import CLASS_NAME_KEY, PROP_NAME_KEY, OBJECT_NAME_KEY, \
    UPDATED_EXISTING_KEY, NAME_NODE_COLLECTION, ID_KEY, NAME_KEY,\
    NAME_LENGTH_KEY
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
        self.permissibleObj = {"pos_1":1,
                               "pos_2":1,
                               "pos_3":1,
                               "pos_4":1,
                               "pos_5":1,
                               "pos_6":1,
                               "pos_7":1,
                               "pos_8":1,
                               CLASS_NAME_KEY:1,
                               PROP_NAME_KEY:1,
                               OBJECT_NAME_KEY:1,
                               NAME_LENGTH_KEY:1
                               }

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
                return {ID_KEY:'-1'}
            else:
                pos += 1
                query["pos_%s"%(pos)] = stringNode[ID_KEY]
            query[NAME_LENGTH_KEY] = pos
        return query

    def createNameNode(self, name):
        query = self.__getquery__(name, True)
        try:
            nodeId =  self.collection.insert(query)
            nameNode = {ID_KEY:ObjectId(nodeId)}
            query.pop(NAME_LENGTH_KEY)
            for key in query.keys():
                stringNodeId = query[key]
                self.stringStore.addPosLinkToStringNode(stringNodeId=stringNodeId,
                                                        nameNodeId=ObjectId(nodeId),
                                                        positionKey=key)
            return nameNode
        except DuplicateKeyError:
            return self.getNameNodeByName(name)

    def getNameNodeById(self, nameNodeId):
        nn = self.collection.find_one({ID_KEY:nameNodeId}, self.permissibleObj)
        if None != nn:
            nn[NAME_KEY] = self.__getName__(nn)
        return nn

    def getNameNodeByName(self, name):
        query = self.__getquery__(name)
        nn = self.collection.find_one(query, self.permissibleObj)
        if None != nn:
            nn[NAME_KEY] = self.__getName__(nn)
        return nn

    def addNameLink(self, nameNodeId, nodeId, nameKey):
        if None == nameKey or None == nameNodeId or None == nodeId:
            return
        updated = self.collection.update({ID_KEY:nameNodeId}, { '$addToSet': { nameKey: nodeId } } )
        return updated[UPDATED_EXISTING_KEY]

    def __getName__(self, nameNode):
        if None == nameNode:
            return None
        length = nameNode[NAME_LENGTH_KEY]
        name = ""
        for i in range(0, length):
            name += self.stringStore.getStringNameById(nameNode["pos_%s" % (i + 1)]) + " "
        return name.strip()
