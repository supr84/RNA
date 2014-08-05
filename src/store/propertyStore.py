'''
Created on Aug 4, 2014

@author: sush
'''
from src.store.Exception.storeError import PropertyNodeError
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from src.store.nameStore import NameStore
from src.store.classStore import ClassStore

class PropertyStore(object):
    '''
    classdocs
    '''
    def __init__(self, params):
        '''
        Constructor
        '''
        dbConn = params
        self.collection = dbConn.getDatabase().propNodes
        self.nameStore = NameStore(dbConn)
        self.classStore = ClassStore(dbConn)

    def createPropertyNode(self, propName):
        name = propName.lower()
        tokens = name.split()
        if len(tokens) != 1:
            raise PropertyNodeError('class node name should not contain white spaces', name)

        nameNode = self.nameStore.getNameNode(name)
        if None == nameNode:
            nameNode = self.nameStore.createNameNode(name)

        try:
            propertyNodeId = self.collection.insert({'nameNodeId':nameNode['_id']})
            propNode = {'_id':ObjectId(propertyNodeId), 'name':propName}
            self.nameStore.addNameLink(nameNode=nameNode,
                                       node=propNode)
            return propNode
        except DuplicateKeyError:
            return self.getPropertyNode(name)

    def getPropertyNodeByNode(self, propNode):
        if None != propNode:
            return self.collection.find_one({'_id':propNode['_id']}, {})
        else:
            return None

    def getPropertyNameById(self, propNodeId):
        propNode = self.collection.find_one({'_id':propNodeId}, {'nameNodeId':1})
        if None != propNode:
            return self.nameStore.getNameById(propNode['nameNodeId'])
        else:
            return None

    def addValNode(self, propNodeId, valNodeId):
        self.collection.update({'_id':propNodeId}, { '$addToSet': { 'val':valNodeId } })

    def getPropertyNode(self, propName):
        name = propName.lower()
        tokens = name.split()
        if len(tokens) != 1:
            raise PropertyNodeError('class node name should not contain white spaces', name)

        nameNode = self.nameStore.getNameNode(name)
        if None == nameNode:
            return None
        propNode = self.collection.find_one({'nameNodeId':nameNode['_id']}, {})
        propNode['name'] = nameNode['name']
        return propNode

    def addRange(self, classNode, propNode):
        self.collection.update({'_id':propNode['_id']}, { '$set': { 'range': classNode['_id'] } })
        self.classStore.addRange(classNode=classNode, propNode=propNode)

    def addDomain(self, classNode, propNode):
        self.collection.update({'_id':propNode['_id']}, { '$addToSet': { 'domain': classNode['_id'] } })
        self.classStore.addDomain(classNode=classNode, propNode=propNode)

    def getRange(self, propNode):
        return self.collection.find_one({'_id':propNode['_id']}, {'range':1})

    def getDomain(self, propNode):
        return self.collection.find_one({'_id':propNode['_id']}, {'domain':1})

if __name__ == '__main__':
    pass
