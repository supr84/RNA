'''
Created on Aug 4, 2014

@author: sush
'''
from src.store.nameStore import NameStore
from pymongo.errors import DuplicateKeyError
from src.store.classStore import ClassStore
from bson.objectid import ObjectId
from src.store.Exception.storeError import ClassNodeError, NameNodeError,\
    ObjectNodeError, PropertyNodeError, ValueNodeError
from src.store.propertyStore import PropertyStore
from src.store.constants import OBJECT_NAME_KEY

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
            objNodeId =  self.collection.insert({'nameNodeId':nameNode['_id'], 'typeId':classNode['_id']})
            objNode = {'_id':ObjectId(objNodeId), 'typeId':classNode['_id']}
            self.nameStore.addNameLink(nameNode=nameNode, node=objNode, OBJECT_NAME_KEY)
            return objNode
        except DuplicateKeyError:
            return self.getClassNode(objName)

    def getObjectNodeByNode(self, objNode):
        if None != objNode:
            return self.collection.find_one({'_id':objNode['_id']}, {'_id':1, 'typeId':1})
        else:
            return None
        
    def getObjectNode(self, objName):
        nameNode = self.nameStore.getNameNode(objName)
        if None == nameNode:
            raise NameNodeError('name node does not exist', objName)
        return self.collection.find_one({'nameNodeId':nameNode['_id']}, {'_id':1, 'typeId':1})
    
    def addObjectProperty(self, objNode, propNode, valueNode):
        obj = self.getObjectNodeByNode(objNode)
        if None == obj:
            raise ObjectNodeError('object does not exist', objNode)
        
        type = self.classStore.getClassNodeByNode({'_id':obj['typeId']})
        if None == type:
            raise ClassNodeError(message='class does not exist', objNode=obj['typeId'])
        
        prop = self.propStore.getPropertyNodeByNode(propNode)
        if None == prop:
            raise PropertyNodeError('property does not exist', propNode)

        #object's type should have the property being added to the object
        domain = self.classStore.getDomain(classNode=type)
        if None == domain:
            raise ClassNodeError("object's type does not exist", type)
        elif propNode['_id'] not in domain['domain']:
            raise ClassNodeError("object's type does not have the mentioned property", type)
        
        #check range
        range = self.propStore.getRange(propNode)
        if not range.has_key('range'):
            val = self.nameStore.getNameNodeById(valueNode['_id'])
            if None == val:
                raise ValueNodeError(message='value does not exist', objNode=valueNode)
            linkName = self.propStore.getPropertyNameById(propNode['_id'])
            self.collection.update({'_id':objNode['_id']}, { '$addToSet': { linkName:val['_id'] } })
            self.propStore.addValNode(propNode['_id'], val['_id'])
        else:
            val = self.getObjectNodeByNode(valueNode)
            if None == val:
                raise ValueNodeError(message='value does not exist', objNode=valueNode)
            elif range['range'] != val['typeId']:
                raise ValueNodeError(message='value is not compatible with range', objNode=range)
            linkName = self.propStore.getPropertyNameById(propNode['_id'])
            self.collection.update({'_id':objNode['_id']}, { '$addToSet': { linkName:val['_id'] } })
            self.propStore.addValNode(propNode['_id'], val['_id'])
    
if __name__ == '__main__':
    pass

    