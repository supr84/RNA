'''
Created on Aug 4, 2014

@author: sush
'''
from bson.objectid import ObjectId
from src.store.Exception.storeError import ClassNodeError
from src.store.constants import DOMAIN_KEY, RANGE_KEY, NAME_NODE_ID_KEY, \
    CLASS_NAME_KEY, OWNER_KEY, UPDATED_EXISTING_KEY
from src.store.nameStore import NameStore

class ClassStore(object):
    '''
    classdocs
    '''

    def __init__(self, dbConn):
        '''
        Constructor
        '''
        self.collection = dbConn.getDatabase().classNodes
        self.nameStore = NameStore(dbConn)
    
    def __getNameNode__(self, className):
        #first letter of class should be capital letters
        name = className.title()
        tokens = name.split()
        if len(tokens) != 1:
            raise ClassNodeError('class node name should not contain white spaces', name)
        nameNode = self.nameStore.getNameNode(name)
        if None == nameNode:
            nameNode = self.nameStore.createNameNode(name)
        return nameNode

    def createClassNode(self, className):
        nameNode = self.__getNameNode__(className)

        classNodeId =  self.collection.insert({NAME_NODE_ID_KEY:nameNode['_id']})
        classNode = {'_id':ObjectId(classNodeId), NAME_NODE_ID_KEY:nameNode['_id']}
        self.nameStore.addNameLink(nameNodeId=nameNode['_id'],
                                   nodeId=classNode['_id'],
                                   nameKey=CLASS_NAME_KEY)
        return classNode
    
    def getClassNode(self, classNodeId):
        if None == classNodeId:
            return None
        return self.collection.find_one({'_id':classNodeId, OWNER_KEY: {'$exists':False}})
    
    #TODO:should we not check if this is indeed a prop_node and a public prop
    def addDomain(self, classNode, propNode, domainKey=DOMAIN_KEY):
        updated = self.collection.update({'_id':classNode['_id'], OWNER_KEY: {'$exists':False}}, { '$addToSet': {  domainKey: propNode['_id'] } })
        return updated[UPDATED_EXISTING_KEY]

    def addRange(self, classNode, propNode, rangeKey=RANGE_KEY):
        updated = self.collection.update({'_id':classNode['_id'], OWNER_KEY: {'$exists':False}}, { '$addToSet': {  rangeKey: propNode['_id'] } })
        return updated[UPDATED_EXISTING_KEY]
