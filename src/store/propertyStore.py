'''
Created on Aug 4, 2014

@author: sushant pradhan
'''
from bson.objectid import ObjectId
from src.store.Exception.storeError import PropertyNodeError
from src.store.constants import DOMAIN_KEY, RANGE_KEY, NAME_NODE_ID_KEY, \
    PROP_NAME_KEY, UPDATED_EXISTING_KEY, OWNER_KEY, PROPERTY_NODE_COLLECTION, \
    CLASS_NODE_COLLECTION, ID_KEY, PROP_VALUE_KEY
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

    def __getNameNode__(self, propName):
        name = propName.lower()
        tokens = name.split()
        if len(tokens) != 1:
            raise PropertyNodeError('class node name should not contain white spaces', name)
        nameNode = self.nameStore.getNameNode(name)
        if None == nameNode:
            nameNode = self.nameStore.createNameNode(name)
        return nameNode

    def createPropertyNode(self, propName, domainClassNode, rangeClassNode):
        domainClassNode = self.publicClassStore.getClassNode(domainClassNode.get(ID_KEY))
        rangeClassNode = self.publicClassStore.getClassNode(rangeClassNode.get(ID_KEY))
        if None == domainClassNode or None == rangeClassNode:
            return None
        nameNode = self.__getNameNode__(propName)
        propertyNode = {NAME_NODE_ID_KEY:nameNode[ID_KEY],
                        RANGE_KEY:rangeClassNode[ID_KEY],
                        DOMAIN_KEY:[domainClassNode[ID_KEY], ]}
        propNodeId = self.propNodes.insert(propertyNode)
        propertyNode[ID_KEY] = ObjectId(propNodeId)
        self.publicClassStore.addDomain(domainClassNode, propertyNode)
        self.publicClassStore.addRange(rangeClassNode, propertyNode)
        return propertyNode

    def getPropertyNode(self, propNodeId):
        if None == propNodeId:
            return None
        return self.propNodes.find_one({ID_KEY:propNodeId, OWNER_KEY: {'$exists':False}})

    def addDomain(self, propNode, domainClassNode):
        if None == propNode or None == domainClassNode:
            return False
        domainClassNode = self.publicClassStore.getClassNode(domainClassNode[ID_KEY])
        if None == domainClassNode:
            return False
        updated = self.propNodes.update({ID_KEY:propNode[ID_KEY],
                                         OWNER_KEY: {'$exists':False}},
                                        { '$addToSet': { DOMAIN_KEY: domainClassNode[ID_KEY] } })
        return updated[UPDATED_EXISTING_KEY]

    def addValLink(self, nameNodeId, valNodeId):
        nameNode = self.nameStore.getNameNodeById(nameNodeId)
        if None == nameNode:
            return False
        names = nameNode[PROP_NAME_KEY]
        for name in names:
            propNode = self.propNodes.find_one({ID_KEY:name})
            if None != propNode:
                self.propNodes.update({ID_KEY:propNode[ID_KEY]}, { '$addToSet': { PROP_VALUE_KEY: valNodeId } })
                return True
