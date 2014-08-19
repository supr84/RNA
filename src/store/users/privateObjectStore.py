'''
Created on Aug 4, 2014

@author: sushant pradhan
'''
from bson.objectid import ObjectId
from src.store.constants import NAME_NODE_ID_KEY, \
    OWNER_KEY, USER_SECRET_KEY, NAME_NODE_COLLECTION, ID_KEY, \
    OBJECT_NODE_COLLECTION, OBJECT_NAME_KEY,\
    OBJECT_TYPE_LINK
from src.store.nameStore import NameStore
from src.store.users.securityError import SecurityBreachError
from src.store.Exception.storeError import ClassNodeError

class __FACTORY__USER__NAME__PLACE__HOLDER__ObjectStore(object):
    '''
    classdocs
    '''

    def __init__(self, dbConn, userName):
        '''
        Constructor
        '''
        self.USER_NAME = '__FACTORY__USER__NAME__PLACE__HOLDER__'
        self.USER_SECRET = '__FACTORY__USER__SECRET__PLACE__HOLDER__'
        if self.USER_NAME != userName:
            raise SecurityBreachError('sorry you are not allowed to instantiate this class', userName)
        self.objNodes = dbConn.getDatabase()[OBJECT_NODE_COLLECTION]
        self.nameStore = NameStore(dbConn)
        self.nameNodes = dbConn.getDatabase()[NAME_NODE_COLLECTION]
        self.userTypeLink = "%s%s" % (self.USER_SECRET, OBJECT_TYPE_LINK)
        self.userObjNameLink = "%s%s" % (self.USER_SECRET, OBJECT_NAME_KEY)
        self.privateClassStore = None
        self.privatePropStore = None

    def createPrivateObjectNode(self, objName, classNode):
        if None == objName or None == classNode:
            return
        classNode = self.privateClassStore.getPrivateClassNode(classNode[NAME_NODE_ID_KEY],
                                                               classNode.get(ID_KEY))
        if None == classNode:
            raise ClassNodeError('class does not exist', classNode)

        nameNode = self.nameStore.getNameNodeByName(objName)
        if None == nameNode:
            nameNode = self.nameStore.createNameNode(objName)

        objNode = {NAME_NODE_ID_KEY:nameNode[ID_KEY], self.userTypeLink:classNode[ID_KEY], OWNER_KEY: self.USER_SECRET}
        objNodeId =  self.objNodes.insert(objNode)
        objNode[ID_KEY] = ObjectId(objNodeId)
        self.nameStore.addNameLink(nameNodeId=nameNode[ID_KEY], nodeId=objNode[ID_KEY], nameKey=self.userObjNameLink)
        return objNode

    def getPrivateObjectNode(self, objNameNodeId, objNodeId):
        if None == objNameNodeId:
            return None
        query = {ID_KEY:objNameNodeId, self.userObjNameLink : { '$exists': True }}
        nameNode = self.nameNodes.find_one(query, {self.userObjNameLink:1})
        permissibleObject = {NAME_NODE_ID_KEY:1, self.userTypeLink:1, OBJECT_TYPE_LINK :1}
        if None != nameNode:
            return self.objNodes.find_one({ID_KEY:objNodeId}, permissibleObject)
        else:
            return self.objNodes.find_one({ID_KEY:objNodeId, OWNER_KEY: {'$exists':False}}, permissibleObject)

    def sharePrivateObjectNode(self, objNode, userNode):
        isShared = False
        if None == userNode or None == objNode:
            return isShared
        sharedObjectNameKey = "%s%s" % (userNode[USER_SECRET_KEY], OBJECT_NAME_KEY)
        findQuery = {ID_KEY:objNode[ID_KEY], OWNER_KEY: self.USER_SECRET}
        objNode = self.objNodes.find_one(findQuery)
        if None != objNode:
            isShared = self.nameStore.addNameLink(nameNodeId=objNode[NAME_NODE_ID_KEY],
                                                  nodeId=objNode[ID_KEY],
                                                  nameKey=sharedObjectNameKey)
        return isShared
