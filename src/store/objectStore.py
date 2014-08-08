'''
Created on Aug 4, 2014

@author: sush
'''
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from src.store.Exception.storeError import ClassNodeError, NameNodeError, \
    ObjectNodeError, PropertyNodeError, ValueNodeError
from src.store.classStore import ClassStore
from src.store.constants import OBJECT_NAME_KEY, ID_KEY, NAME_NODE_ID_KEY,\
    RANGE_KEY, DOMAIN_KEY, OBJECT_TYPE_LINK
from src.store.nameStore import NameStore
from src.store.propertyStore import PropertyStore

class ObjectNodeStore(object):
    '''
    classdocs
    '''
    def __init__(self, dbConn):
        '''
        Constructor
        '''
        self.collection = dbConn.getDatabase().objectNodes
        self.nameStore = NameStore(dbConn)
        self.classStore = ClassStore(dbConn)
        self.propStore = PropertyStore(dbConn)

    def createObjectNode(self, objName, classNode):
        nameNode = self.nameStore.getNameNode(objName)
        if None == nameNode:
            nameNode = self.nameStore.createNameNode(objName)

        classNode = self.classStore.getClassNodeByNode(classNode = classNode)
        if None == classNode:
            raise ClassNodeError('class does not exist', classNode)

        try:
            objNodeId =  self.collection.insert({NAME_NODE_ID_KEY:nameNode[ID_KEY], OBJECT_TYPE_LINK:classNode[ID_KEY]})
            objNode = {ID_KEY:ObjectId(objNodeId), OBJECT_TYPE_LINK:classNode[ID_KEY]}
            self.nameStore.addNameLink(nameNode=nameNode, node=objNode, OBJECT_NAME_KEY)
            return objNode
        except DuplicateKeyError:
            return self.getClassNode(objName)

    def getObjectNodeByNode(self, objNode):
        if None != objNode:
            return self.collection.find_one({ID_KEY:objNode[ID_KEY]}, {ID_KEY:1, OBJECT_TYPE_LINK:1})
        else:
            return None

    def getObjectNode(self, objName):
        nameNode = self.nameStore.getNameNode(objName)
        if None == nameNode:
            raise NameNodeError('name node does not exist', objName)
        return self.collection.find_one({NAME_NODE_ID_KEY:nameNode[ID_KEY]}, {ID_KEY:1, OBJECT_TYPE_LINK:1})

    def addObjectProperty(self, objNode, propNode, valueNode):
        obj = self.getObjectNodeByNode(objNode)
        if None == obj:
            raise ObjectNodeError('object does not exist', objNode)

        type = self.classStore.getClassNodeByNode({ID_KEY:obj[OBJECT_TYPE_LINK]})
        if None == type:
            raise ClassNodeError(message='class does not exist', objNode=obj[OBJECT_TYPE_LINK])

        prop = self.propStore.getPropertyNodeByNode(propNode)
        if None == prop:
            raise PropertyNodeError('property does not exist', propNode)

        #object's type should have the property being added to the object
        domain = self.classStore.getDomain(classNode=type)
        if None == domain:
            raise ClassNodeError("object's type does not exist", type)
        elif propNode[ID_KEY] not in domain[DOMAIN_KEY]:
            raise ClassNodeError("object's type does not have the mentioned property", type)
        #check range
        range = self.propStore.getRange(propNode)
        if not range.has_key(RANGE_KEY):
            val = self.nameStore.getNameNodeById(valueNode[ID_KEY])
            if None == val:
                raise ValueNodeError(message='value does not exist', objNode=valueNode)
            linkName = self.propStore.getPropertyNameById(propNode[ID_KEY])
            self.collection.update({ID_KEY:objNode[ID_KEY]}, { '$addToSet': { linkName:val[ID_KEY] } })
            self.propStore.addValNode(propNode[ID_KEY], val[ID_KEY])
        else:
            val = self.getObjectNodeByNode(valueNode)
            if None == val:
                raise ValueNodeError(message='value does not exist', objNode=valueNode)
            elif range[RANGE_KEY] != val[OBJECT_TYPE_LINK]:
                raise ValueNodeError(message='value is not compatible with range', objNode=range)
            linkName = self.propStore.getPropertyNameById(propNode[ID_KEY])
            self.collection.update({ID_KEY:objNode[ID_KEY]}, { '$addToSet': { linkName:val[ID_KEY] } })
            self.propStore.addValNode(propNode[ID_KEY], val[ID_KEY])
