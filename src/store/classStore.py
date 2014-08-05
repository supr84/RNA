'''
Created on Aug 4, 2014

@author: sush
'''
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from src.store.Exception.storeError import ClassNodeError
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
    
    def createClassNode(self, className):
        #first letter of class should be capital letters
        name = className.title()
        tokens = name.split()
        if len(tokens) != 1:
            raise ClassNodeError('class node name should not contain white spaces', name)
        
        nameNode = self.nameStore.getNameNode(name)
        if None == nameNode:
            nameNode = self.nameStore.createNameNode(name)

        try:
            classNodeId =  self.collection.insert({'nameNodeId':nameNode['_id']})
            classNode = {'_id':ObjectId(classNodeId)}
            self.nameStore.addNameLink(nameNode=nameNode,
                                       node=classNode)
            return classNode
        except DuplicateKeyError:
            return self.getClassNode(name)
    
    def getClassNodeByNode(self, classNode):
        if None != classNode:
            return self.collection.find_one({'_id':classNode['_id']}, {})
        else:
            return None

    def getClassNode(self, className):
        name = className.title()
        tokens = name.split()
        if len(tokens) != 1:
            raise ClassNodeError('class node name should not contain white spaces', name)

        nameNode = self.nameStore.getNameNode(name)
        if None == nameNode:
            return None
        return self.collection.find_one({'nameNodeId':nameNode['_id']}, {})

    def hasDomain(self, propNode, classNode):
        self.collection.find_one({'_id':classNode['_id']}, { 'domain': 1 } )

    def getDomain(self, classNode):
        return self.collection.find_one({'_id':classNode['_id']}, { 'domain': 1 } )
    
    def getRange(self, classNode):
        return self.collection.find_one({'_id':classNode['_id']}, { 'range': 1 } )
    
    def addDomain(self, classNode, propNode):
        self.collection.update({'_id':classNode['_id']}, { '$addToSet': { 'domain': propNode['_id'] } })
    
    def addRange(self, classNode, propNode):
        self.collection.update({'_id':classNode['_id']}, { '$addToSet': { 'range': propNode['_id'] } })

if __name__ == '__main__':
    pass
