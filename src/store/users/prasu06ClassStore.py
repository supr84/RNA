'''
Created on Aug 4, 2014

@author: sush
'''
from bson.objectid import ObjectId
from src.store.Exception.storeError import ClassNodeError
from src.store.constants import IS_PRIVATE_KEY, DOMAIN_KEY, USER_NAME_KEY, \
    RANGE_KEY, NAME_NODE_ID_KEY, CLASS_NAME_KEY, OWNER_KEY, UPDATED_EXISTING_KEY, \
    CLASS_NODE_COLLECTION, USER_SECRET_KEY, NAME_NODE_COLLECTION
from src.store.nameStore import NameStore
from src.store.userStore import USerStore
from src.store.users.securityError import SecurityBreachError

class Prasu06ClassStore(object):
    '''
    classdocs
    '''

    def __init__(self, dbConn, userName):
        '''
        Constructor
        '''
        USER_NAME = 'prasu06'
        if USER_NAME != userName:
            raise SecurityBreachError('sorry you are not allowed to instantiate this class', userName)
        self.userStore = USerStore(dbConn)
        self.nameStore = NameStore(dbConn)
        self.userNode = self.userStore.getUserNode(USER_NAME)
        self.collection = dbConn.getDatabase()[CLASS_NODE_COLLECTION]
        self.nameNodes = dbConn.getDatabase()[NAME_NODE_COLLECTION]
        self.userDomainLink = "%s%s" % (self.userNode[USER_SECRET_KEY], DOMAIN_KEY)
        self.userRangeLink = "%s%s" % (self.userNode[USER_SECRET_KEY], RANGE_KEY) 
        self.userClassNameLink = "%s%s" % (self.userNode[USER_SECRET_KEY], CLASS_NAME_KEY)
    
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

    def createPrivateClassNode(self, className):
        nameNode = self.__getNameNode__(className)
        classNodeId =  self.collection.insert({NAME_NODE_ID_KEY:nameNode['_id'], OWNER_KEY: self.userNode[USER_NAME_KEY]})
        classNode = {'_id':ObjectId(classNodeId), NAME_NODE_ID_KEY:nameNode['_id']}
        self.nameStore.addNameLink(nameNodeId=nameNode['_id'],
                                   nodeId=classNode['_id'],
                                   nameKey="%s%s" % (self.userNode[USER_SECRET_KEY], CLASS_NAME_KEY))
        return classNode

    def getPrivateClassNode(self, classNameNodeId, classNodeId):
        if None == classNameNodeId:
            return None
        query = {'_id':classNameNodeId, self.userClassNameLink : { '$exists': True }}
        nameNode = self.nameNodes.find_one(query, {self.userClassNameLink:1})
        if None != nameNode:
            return self.collection.find_one({'_id':classNodeId}, {NAME_NODE_ID_KEY:1,
                                                                  DOMAIN_KEY:1,
                                                                  RANGE_KEY:1,
                                                                  self.userRangeLink:1,
                                                                  self.userDomainLink:1
                                                                  })

    def sharePrivateClassNode(self, classNodeId, shareWithUserNode):
        isShared = False
        if None == shareWithUserNode:
            return isShared
        
        classNode = self.collection.find_one({'_id':classNodeId['_id'], OWNER_KEY: self.userNode[USER_NAME_KEY]})
        if None != classNode:
            isShared = self.nameStore.addNameLink(nameNodeId=classNode[NAME_NODE_ID_KEY],
                                       nodeId=classNodeId,
                                       nameKey="%s%s" % (shareWithUserNode[USER_SECRET_KEY], CLASS_NAME_KEY))
        return isShared
    
    def addPrivateDomain(self, classNodeId, propNodeId):
        updated = self.collection.update({'_id':classNodeId, OWNER_KEY: self.userNode[USER_NAME_KEY]}, { '$addToSet': {  self.userDomainLink: propNodeId } })
        return updated[UPDATED_EXISTING_KEY]

    def addPrivateRange(self, classNodeId, propNodeId):
        updated = self.collection.update({'_id':classNodeId, OWNER_KEY: self.userNode[USER_NAME_KEY]}, { '$addToSet': {  self.userRangeLink: propNodeId } })
        return updated[UPDATED_EXISTING_KEY]
