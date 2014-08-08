'''
Created on Aug 4, 2014

@author: sushant pradhan
'''
from bson.objectid import ObjectId
from src.store.Exception.storeError import ClassNodeError
from src.store.constants import DOMAIN_KEY, RANGE_KEY, NAME_NODE_ID_KEY, \
    CLASS_NAME_KEY, OWNER_KEY, UPDATED_EXISTING_KEY, ID_KEY
from src.store.nameStore import NameStore

class ClassStore(object):
    '''
    Use StoreFactory to get instance of this class, bypassing that might result in unpredictable results.
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

        classNodeId =  self.collection.insert({NAME_NODE_ID_KEY:nameNode[ID_KEY]})
        classNode = {ID_KEY:ObjectId(classNodeId), NAME_NODE_ID_KEY:nameNode[ID_KEY]}
        self.nameStore.addNameLink(nameNodeId=nameNode[ID_KEY],
                                   nodeId=classNode[ID_KEY],
                                   nameKey=CLASS_NAME_KEY)
        return classNode

    def getClassNode(self, classNodeId):
        if None == classNodeId:
            return None
        return self.collection.find_one({ID_KEY:classNodeId, OWNER_KEY: {'$exists':False}},
                                        {NAME_NODE_ID_KEY:1,
                                         DOMAIN_KEY:1,
                                         RANGE_KEY:1})

    def addDomain(self, classNode, propNode):
        propNode = self.publicPropStore.getPropertyNode(propNode[ID_KEY])
        if None == propNode:
            return False
        updated = self.collection.update({ID_KEY:classNode[ID_KEY],
                                          OWNER_KEY: {'$exists':False}},
                                         { '$addToSet': {  DOMAIN_KEY: propNode[ID_KEY] } })
        return updated[UPDATED_EXISTING_KEY]

    def addRange(self, classNode, propNode):
        propNode = self.publicPropStore.getPropertyNode(propNode[ID_KEY])
        if None == propNode:
            return False
        updated = self.collection.update({ID_KEY:classNode[ID_KEY],
                                          OWNER_KEY: {'$exists':False}},
                                         { '$addToSet': {  RANGE_KEY: propNode[ID_KEY] } })
        return updated[UPDATED_EXISTING_KEY]
