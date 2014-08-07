'''
Created on Aug 4, 2014

@author: sush
'''
from bson.objectid import ObjectId
from src.store.Exception.storeError import PropertyNodeError
from src.store.classStore import ClassStore
from src.store.constants import DOMAIN_KEY, RANGE_KEY, IS_PRIVATE_KEY, \
    NAME_NODE_ID_KEY, PROP_NAME_KEY, UPDATED_EXISTING_KEY, OWNER_KEY, \
    PROPERTY_NODE_COLLECTION, CLASS_NODE_COLLECTION
from src.store.nameStore import NameStore
class PropertyStore(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        dbConn = params
        self.propNodes = dbConn.getDatabase()[PROPERTY_NODE_COLLECTION]
        self.classNodes = dbConn.getDatabase()[CLASS_NODE_COLLECTION]
        self.nameStore = NameStore(dbConn)
        self.classStore = ClassStore(dbConn)

    def __getNameNode__(self, propName):
        name = propName.lower()
        tokens = name.split()
        if len(tokens) != 1:
            raise PropertyNodeError('class node name should not contain white spaces', name)
        nameNode = self.nameStore.getNameNode(name)
        if None == nameNode:
            nameNode = self.nameStore.createNameNode(name)
        return nameNode

    def __updateClassLinks__(self, classNodeId, propNodeId):
        domainUpdated = self.classNodes.update({'_id':classNodeId, OWNER_KEY: {'$exists':False}}, { '$addToSet': {  DOMAIN_KEY: propNodeId } })
        if domainUpdated[UPDATED_EXISTING_KEY]:
            rangeUpdated = self.classNodes.update({'_id':classNodeId, OWNER_KEY: {'$exists':False}}, { '$addToSet': {  RANGE_KEY: propNodeId } })
            return rangeUpdated[UPDATED_EXISTING_KEY]
        return False

    def createPropertyNode(self, propName, domainClassNodeId, rangeClassNodeId):
        domainClassNode = self.classStore.getClassNode(domainClassNodeId)
        rangeClassNode = self.classStore.getClassNode(rangeClassNodeId)
        if None == domainClassNode or None == rangeClassNode:
            return
        nameNode = self.__getNameNode__(propName)
        propertyNode = {NAME_NODE_ID_KEY:nameNode['_id'],
                        RANGE_KEY:rangeClassNode['_id'],
                        DOMAIN_KEY:[domainClassNode['_id'],]}
        propNodeId = self.propNodes.insert(propertyNode)
        propertyNode['_id'] = ObjectId(propNodeId)
        
        self.__updateClassLinks__(classNodeId=domainClassNode['_id'],
                             propNodeId=propertyNode['_id'])

        return propertyNode

    def getPropertyNode(self, propNodeId):
        if None == propNodeId:
            return None
        return self.propNodes.find_one({'_id':propNodeId, OWNER_KEY: {'$exists':False}})

    def addDomain(self, propNodeId, domainClassNodeId):
        domainClassNode = self.classStore.getClassNode(domainClassNodeId)
        if None == domainClassNode:
            return False
        updated = self.propNodes.update({'_id':propNodeId, OWNER_KEY: {'$exists':False}}, { '$addToSet': { DOMAIN_KEY: domainClassNodeId } })
        return updated[UPDATED_EXISTING_KEY]
    
    def addValLink(self, nameNodeId, valNodeId):
        nameNode = self.nameStore.getNameNodeById(nameNodeId)
        if None == nameNode:
            return False
        names = nameNode[PROP_NAME_KEY]
        for name in names:
            propNode = self.propNodes.find_one({'_id':name})
            if None != propNode:
                self.propNodes.update({'_id':propNode['_id']}, { '$addToSet': { 'val':valNodeId } })
                return True
if __name__ == '__main__':
    pass
