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
        self.publicClassStore = None

    def __getNameNode__(self, propName):
        name = propName.lower()
        tokens = name.split()
        if len(tokens) != 1:
            raise PropertyNodeError('class node name should not contain white spaces', name)
        nameNode = self.nameStore.getNameNodeByName(name)
        if None == nameNode:
            nameNode = self.nameStore.createNameNode(name)
        return nameNode

    def createPropertyNode(self, propName, domainClassNode, rangeClassNode=None):
        if None == propName or None == domainClassNode:
            return None
        dcn = self.publicClassStore.getClassNode(domainClassNode.get(ID_KEY))
        if None == dcn:
            return None
        hasRange = False
        nameNode = self.__getNameNode__(propName)
        propertyNode = {NAME_NODE_ID_KEY:nameNode[ID_KEY],
                        DOMAIN_KEY:[dcn[ID_KEY], ]}
        if None != rangeClassNode:
            rcn = self.publicClassStore.getClassNode(rangeClassNode.get(ID_KEY))
            if None == rcn:
                return None
            propertyNode[RANGE_KEY] = rcn[ID_KEY]
            hasRange = True

        propNodeId = self.propNodes.insert(propertyNode)
        propertyNode[ID_KEY] = ObjectId(propNodeId)
        self.publicClassStore.addDomain(dcn, propertyNode)
        if hasRange:
            self.publicClassStore.addRange(rcn, propertyNode)
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

    def addValLink(self, propNode, valNode):
        if None == propNode or None == valNode:
            return False
        pn = self.getPropertyNode(propNode[ID_KEY])
        if None == pn:
            return False
        updated = self.propNodes.update({ID_KEY:pn[ID_KEY]}, { '$addToSet': { PROP_VALUE_KEY: valNode[ID_KEY] } })
        return updated[UPDATED_EXISTING_KEY]
