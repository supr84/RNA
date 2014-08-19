'''
Created on Aug 4, 2014

@author: sushant pradhan
'''
from bson.objectid import ObjectId
from src.store.Exception.storeError import ClassNodeError, \
    ObjectNodeError, PropertyNodeError, ValueNodeError
from src.store.constants import OBJECT_NAME_KEY, ID_KEY, NAME_NODE_ID_KEY, \
    RANGE_KEY, DOMAIN_KEY, OBJECT_TYPE_LINK, OBJECT_NODE_COLLECTION, OWNER_KEY,\
    NAME_NODE_COLLECTION, NAME_KEY, UPDATED_EXISTING_KEY
from src.store.nameStore import NameStore

class ObjectStore(object):
    '''
    classdocs
    '''
    def __init__(self, dbConn):
        '''
        Constructor
        '''
        self.objNodes = dbConn.getDatabase()[OBJECT_NODE_COLLECTION]
        self.nameStore = NameStore(dbConn)
        self.nameNodes = dbConn.getDatabase()[NAME_NODE_COLLECTION]
        self.publicClassStore = None
        self.publicPropStore = None

    def createObjectNode(self, objName, classNode):
        if None == objName or None == classNode:
            return
        classNode = self.publicClassStore.getClassNode(classNode.get(ID_KEY))
        nameNode = self.nameStore.getNameNodeByName(objName)
        if None == nameNode:
            nameNode = self.nameStore.createNameNode(objName)
        if None == classNode:
            raise ClassNodeError('class does not exist', classNode)
        objNode = {NAME_NODE_ID_KEY:nameNode[ID_KEY], OBJECT_TYPE_LINK:classNode[ID_KEY]}
        objNodeId = self.objNodes.insert(objNode)
        objNode[ID_KEY] = ObjectId(objNodeId)
        self.nameStore.addNameLink(nameNodeId=nameNode[ID_KEY], nodeId=objNode[ID_KEY], nameKey=OBJECT_NAME_KEY)
        return objNode

    def getObjectNode(self, objNodeId):
        findQuery = {ID_KEY:objNodeId, OWNER_KEY: {'$exists':False}}
        permissibleFields = {NAME_NODE_ID_KEY:1, OBJECT_TYPE_LINK:1}
        if None != objNodeId:
            return self.objNodes.find_one(findQuery, permissibleFields)
        else:
            return None

    def addPublicProperty(self, objNode, propNode, valueNode):
        objNode = self.getObjectNode(objNode[ID_KEY])
        if None == objNode:
            raise ObjectNodeError('object does not exist', objNode)

        objType = self.publicClassStore.getClassNode(objNode[OBJECT_TYPE_LINK])
        if None == objType:
            raise ClassNodeError(message='class does not exist', objNode=objNode[OBJECT_TYPE_LINK])

        prop = self.publicPropStore.getPropertyNode(propNode[ID_KEY])
        if None == prop:
            raise PropertyNodeError('property does not exist', propNode)

        if objType[ID_KEY] not in prop[DOMAIN_KEY]:
            raise ClassNodeError("object's objType does not have the mentioned property", objType)
        # check propRange
        if not prop.has_key(RANGE_KEY):
            val = self.nameNodes.find_one({ID_KEY:valueNode[ID_KEY]})
            if None == val:
                raise ValueNodeError(message='value does not exist', objNode=valueNode)
            linkName = self.nameStore.getNameNodeById(prop[NAME_NODE_ID_KEY])[NAME_KEY]
            updated = self.objNodes.update({ID_KEY:objNode[ID_KEY]}, { '$addToSet': { linkName:val[ID_KEY] } })
            if updated[UPDATED_EXISTING_KEY]:
                return self.publicPropStore.addValLink(prop, val)
            else:
                return False
        else:
            propRange = prop[RANGE_KEY]
            val = self.getObjectNode(valueNode[ID_KEY])
            if None == val:
                raise ValueNodeError(message='value does not exist', objNode=valueNode)
            elif propRange != val[OBJECT_TYPE_LINK]:
                raise ValueNodeError(message="value is not compatible with property's range", objNode=propRange)
            linkName = self.nameStore.getNameNodeById(prop[NAME_NODE_ID_KEY])[NAME_KEY]
            updated = self.objNodes.update({ID_KEY:objNode[ID_KEY]}, { '$addToSet': { linkName:val[ID_KEY] } })
            if updated[UPDATED_EXISTING_KEY]:
                return self.publicPropStore.addValLink(prop, val)
            else:
                return False
