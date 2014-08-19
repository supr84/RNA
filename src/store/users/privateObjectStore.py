'''
Created on Aug 4, 2014

@author: sushant pradhan
'''
from bson.objectid import ObjectId
from src.store.constants import NAME_NODE_ID_KEY, \
    OWNER_KEY, USER_SECRET_KEY, NAME_NODE_COLLECTION, ID_KEY, \
    OBJECT_NODE_COLLECTION, OBJECT_NAME_KEY,\
    OBJECT_TYPE_LINK, DOMAIN_KEY, RANGE_KEY, UPDATED_EXISTING_KEY, NAME_KEY
from src.store.nameStore import NameStore
from src.store.users.securityError import SecurityBreachError
from src.store.Exception.storeError import ClassNodeError, ObjectNodeError,\
    PropertyNodeError, ValueNodeError

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
        self.userDomainLink = "%s%s" % (self.USER_SECRET, DOMAIN_KEY)
        self.userRangeLink = "%s%s" % (self.USER_SECRET, RANGE_KEY)
        self.privateClassStore = None
        self.privatePropStore = None

    def createPrivateObjectNode(self, objName, classNode):
        if None == objName or None == classNode:
            return
        classNode = self.privateClassStore.getPrivateClassNode(classNode.get(ID_KEY))
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

    def getPrivateObjectNode(self, objNodeId):
        permissibleObject = {NAME_NODE_ID_KEY:1, self.userTypeLink:1, OBJECT_TYPE_LINK :1}
        on = self.objNodes.find_one({ID_KEY: objNodeId}, permissibleObject)
        if None == on:
            return None
        query = {ID_KEY:on[NAME_NODE_ID_KEY], self.userObjNameLink : on[ID_KEY]}
        nameNode = self.nameNodes.find_one(query, {self.userObjNameLink:1})
        if None != nameNode:
            return on
        else:
            return self.objNodes.find_one({ID_KEY:objNodeId, OWNER_KEY: {'$exists':False}},
                                            permissibleObject)

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

    def addPrivateProperty(self, objNode, propNode, valueNode):
        objNode = self.getPrivateObjectNode(objNode[ID_KEY])
        if None == objNode:
            raise ObjectNodeError('object does not exist', objNode)

        objType = self.privateClassStore.getPrivateClassNode(objNode[self.userTypeLink])
        if None == objType:
            raise ClassNodeError(message='class does not exist', objNode=objNode[self.userTypeLink])

        prop = self.privatePropStore.getPrivatePropertyNode(propNode[ID_KEY])
        if None == prop:
            raise PropertyNodeError('property does not exist', propNode)

        if objType[ID_KEY] not in prop[DOMAIN_KEY] or objType[ID_KEY] not in prop[self.userDomainLink]:
            raise ClassNodeError("object's type does not have the mentioned property", objType)
        # check propRange
        if not prop.has_key(RANGE_KEY) and prop.has_key(self.userRangeLink):
            val = self.nameNodes.find_one({ID_KEY:valueNode[ID_KEY]})
            if None == val:
                raise ValueNodeError(message='value does not exist', objNode=valueNode)
            linkName = "%s%s" % (self.USER_SECRET, self.nameStore.getNameNodeById(prop[NAME_NODE_ID_KEY])[NAME_KEY])
            updated = self.objNodes.update({ID_KEY:objNode[ID_KEY]}, { '$addToSet': { linkName:val[ID_KEY] } })
            if updated[UPDATED_EXISTING_KEY]:
                return self.privatePropStore.addPrivateValLink(prop, val)
            else:
                return False
        else:
            propRange = prop[RANGE_KEY]
            if None == propRange:
                propRange = prop[self.userRangeLink]
            if propRange != val[OBJECT_TYPE_LINK]:
                raise ValueNodeError(message="value is not compatible with property's range", objNode=propRange)
            val = self.getObjectNode(valueNode[ID_KEY])
            if None == val:
                raise ValueNodeError(message='value does not exist', objNode=valueNode)
            linkName = "%s%s" % (self.USER_SECRET, self.nameStore.getNameNodeById(prop[NAME_NODE_ID_KEY])[NAME_KEY])
            updated = self.objNodes.update({ID_KEY:objNode[ID_KEY]}, { '$addToSet': { linkName:val[ID_KEY] } })
            if updated[UPDATED_EXISTING_KEY]:
                return self.privatePropStore.addPrivateValLink(prop, val)
            else:
                return False