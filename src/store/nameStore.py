'''
Created on Aug 4, 2014

@author: sush
'''
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
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
        self.collection = dbConn.getDatabase().nameNodes
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
        return self.collection.find_one({'_id':nameNodeId})

    def getNameNode(self, name):
        query = self.__getquery__(name)
        return self.collection.find_one(query)
    
    def addNameLink(self, nameNode, node):
        self.collection.update({'_id':nameNode['_id']}, { '$addToSet': { 'name': node['_id'] } } )

if __name__ == '__main__':
    pass
