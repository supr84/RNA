'''
Created on Aug 4, 2014

@author: sush
'''
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from src.store.Exception.storeError import ClassNodeError
from src.store.nameStore import NameStore
from src.store.constants import IS_PRIVATE_KEY, DOMAIN_KEY, USER_NAME_KEY,\
    VIEWERS_KEY, RANGE_KEY, NAME_NODE_ID_KEY, CLASS_NAME_KEY, OWNER_KEY,\
    UPDATED_EXISTING_KEY

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

    def __updateClassNode__(self, propNode, classNode, field, userNode=None):
        isUpdated = False
        if propNode.has_key(IS_PRIVATE_KEY):
            if None == userNode:
                return isUpdated
            privateField = "%s%s" % (userNode[USER_NAME_KEY], field)
            updated = self.collection.update({'_id':classNode['_id']}, { '$addToSet': {  privateField: propNode['_id'] } })
            isUpdated = updated[UPDATED_EXISTING_KEY]
        else:
            updated = self.collection.update({'_id':classNode['_id']}, { '$addToSet': { field: propNode['_id'] } })
            isUpdated = updated[UPDATED_EXISTING_KEY]
        return isUpdated

    def createPrivateClassNode(self, className, userNode):
        nameNode = self.__getNameNode__(className)
        classNodeId =  self.collection.insert({NAME_NODE_ID_KEY:nameNode['_id'],
                                               OWNER_KEY : userNode['_id'],
                                               VIEWERS_KEY : [userNode[USER_NAME_KEY],],
                                               IS_PRIVATE_KEY : True})
        classNode = {'_id':ObjectId(classNodeId)}
        self.nameStore.addNameLink(nameNode=nameNode,
                                   node=classNode,
                                   nameKey=CLASS_NAME_KEY)
        return classNode

    def getPrivateClassNode(self, classNodeId, userNode):
        if None == userNode:
            return
        return self.collection.find_one({'_id':classNodeId['_id'],
                                                 IS_PRIVATE_KEY:True,
                                                 VIEWERS_KEY:{'$in': [userNode[USER_NAME_KEY],]}})
    def createClassNode(self, className):
        nameNode = self.__getNameNode__(className)

        classNodeId =  self.collection.insert({NAME_NODE_ID_KEY:nameNode['_id']})
        classNode = {'_id':ObjectId(classNodeId)}
        self.nameStore.addNameLink(nameNode=nameNode,
                                   node=classNode,
                                   nameKey=CLASS_NAME_KEY)
        return classNode
    
    def getClassNode(self, classNodeId):
        if None == classNodeId:
            return None
        return self.collection.find_one({'_id':classNodeId, IS_PRIVATE_KEY: {'$exists':False}})
    
    def sharePrivateClassNode(self, classNodeId, ownerUserNode, shareWithUserNode):
        isShared = False
        if None == ownerUserNode or None == shareWithUserNode:
            return isShared
        classNode = self.collection.find_one({'_id':classNodeId['_id'],
                                                 IS_PRIVATE_KEY:True,
                                                 OWNER_KEY:ownerUserNode['_id']
                                                 })
        if None != classNode:
            updated = self.collection.update({'_id':classNodeId['_id'],
                                              IS_PRIVATE_KEY:True,
                                              OWNER_KEY:ownerUserNode['_id']
                                              },{ '$addToSet': { VIEWERS_KEY: shareWithUserNode[USER_NAME_KEY] } })
            isShared = updated[UPDATED_EXISTING_KEY]
        return isShared
    
    def addDomain(self, classNode, propNode, userNode=None):
        return self.__updateClassNode__(propNode=propNode, classNode=classNode, userNode=userNode, field=DOMAIN_KEY)

    def addRange(self, classNode, propNode, userNode=None):
        return self.__updateClassNode__(propNode=propNode, classNode=classNode, userNode=userNode, field=RANGE_KEY)

if __name__ == '__main__':
    pass
