'''
Created on Aug 4, 2014

@author: sush
'''
from src.store.Exception.storeError import PropertyNodeError
from bson.objectid import ObjectId
from src.store.nameStore import NameStore
from src.store.classStore import ClassStore
from src.store.constants import DOMAIN_KEY, RANGE_KEY, NAME_KEY, IS_PRIVATE_KEY,\
    VIEWERS_KEY, OWNER_KEY, NAME_NODE_ID_KEY, USER_NAME_KEY, PROP_NAME_KEY,\
    UPDATED_EXISTING_KEY
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

    def __getNameNode__(self, propName):
        name = propName.lower()
        tokens = name.split()
        if len(tokens) != 1:
            raise PropertyNodeError('class node name should not contain white spaces', name)
        nameNode = self.nameStore.getNameNode(name)
        if None == nameNode:
            nameNode = self.nameStore.createNameNode(name)
        return nameNode

    def __getPropNodeStructure__(self, domainClassNode, rangeClassNode, nameNode):
        propertyNode = {NAME_NODE_ID_KEY:nameNode['_id'],
                        RANGE_KEY:rangeClassNode['_id'],
                        DOMAIN_KEY:[domainClassNode['_id'],]}
        return propertyNode

    def __storePropertyNode__(self, propName, nameNode, propertyNode):
        propertyNode['_id'] = self.collection.insert(propertyNode)
        propertyNode[NAME_KEY]  = propName
        self.nameStore.addNameLink(nameNode=nameNode, node=propertyNode, nameKey=PROP_NAME_KEY)
        return propertyNode

    def createPropertyNode(self, propName, domainClassNode, rangeClassNode):
        if None == propName or None == domainClassNode or None == rangeClassNode:
            return None
        nameNode = self.__getNameNode__(propName)
        propNode = self.__getPropNodeStructure__(domainClassNode, rangeClassNode, nameNode)
        propNode = self.__storePropertyNode__(propName, nameNode, propNode)
        self.classStore.addDomain(domainClassNode, propNode)
        self.classStore.addRange(rangeClassNode, propNode)
        return nameNode['_id']

    def createPrivatePropertyNode(self, propName, domainClassNode, rangeClassNode, userNode):
        if None == propName or None == userNode or None == domainClassNode or None == rangeClassNode:
            return
        nameNode = self.__getNameNode__(propName)
        propNode = self.__getPropNodeStructure__(domainClassNode, rangeClassNode, nameNode)
        propNode[OWNER_KEY] = userNode['_id']
        propNode[VIEWERS_KEY] = [userNode[USER_NAME_KEY],]
        propNode[IS_PRIVATE_KEY] = True
        propNode = self.__storePropertyNode__(propName, nameNode, propNode)
        self.classStore.addDomain(classNode=domainClassNode,
                                  propNode=propNode,
                                  userNode=userNode)
        self.classStore.addRange(classNode=rangeClassNode,
                                 propNode=propNode,
                                 userNode=userNode)
        return nameNode['_id']

    def getPrivatePropertyNode(self, nameNodeId, userNode):
        if None == userNode:
            return
        nameNode = self.nameStore.getNameNodeById(nameNodeId)
        if None == nameNode:
            return
        names = nameNode[PROP_NAME_KEY]
        for name in names:
            propertyNode = self.collection.find_one({'_id':name,
                                                     IS_PRIVATE_KEY:True,
                                                     VIEWERS_KEY:{'$in': [userNode[USER_NAME_KEY],]}})
            if None != propertyNode:
                return propertyNode

    def getPropertyNode(self, nameNodeId):
        nameNode = self.nameStore.getNameNodeById(nameNodeId)
        if None == nameNode:
            return None
        names = nameNode[PROP_NAME_KEY]
        for name in names:
            propertyNode = self.collection.find_one({'_id':name, IS_PRIVATE_KEY: {'$exists':False}})
            if None != propertyNode:
                return propertyNode

    def sharePrivatePropertyNode(self, nameNodeId, ownerUserNode, shareWithUserNode):
        if None == ownerUserNode or None == shareWithUserNode:
            return False
        nameNode = self.nameStore.getNameNodeById(nameNodeId)
        if None == nameNode:
            return False
        names = nameNode[PROP_NAME_KEY]
        for name in names:
            propertyNode = self.collection.find_one({'_id':name,
                                                     IS_PRIVATE_KEY:True,
                                                     OWNER_KEY:ownerUserNode['_id']
                                                     })
            if None != propertyNode:
                self.collection.update({'_id':name,
                                          IS_PRIVATE_KEY:True,
                                          OWNER_KEY:ownerUserNode['_id']
                                          },{ '$addToSet': { VIEWERS_KEY: shareWithUserNode[USER_NAME_KEY] } })
                for domain in propertyNode[DOMAIN_KEY]:
                    classNode = {'_id':domain}
                    self.classStore.addDomain(classNode=classNode,
                                              propNode=propertyNode,
                                              userNode=shareWithUserNode)
                range = {'_id':propertyNode[RANGE_KEY]}
                self.classStore.addRange(classNode=range,
                                          propNode=propertyNode,
                                          userNode=shareWithUserNode)
                return True
        return False

    def addValLink(self, nameNodeId, valNodeId):
        nameNode = self.nameStore.getNameNodeById(nameNodeId)
        if None == nameNode:
            return False
        names = nameNode[PROP_NAME_KEY]
        for name in names:
            propNode = self.collection.find_one({'_id':name})
            if None != propNode:
                self.collection.update({'_id':propNode['_id']}, { '$addToSet': { 'val':valNodeId } })
                return True

    def addDomain(self, nameNodeId, classNode):
        nameNode = self.nameStore.getNameNodeById(nameNodeId)
        if None == nameNode:
            return False
        names = nameNode[PROP_NAME_KEY]
        for name in names:
            propNode = self.collection.find_one({'_id':name})
            if None != propNode:
                updated = self.collection.update({'_id':propNode['_id'], IS_PRIVATE_KEY: { '$exists': False }}, { '$addToSet': { DOMAIN_KEY: classNode['_id'] } })
                if updated[UPDATED_EXISTING_KEY]:
                    self.classStore.addDomain(classNode=classNode, propNode=propNode)
                return updated[UPDATED_EXISTING_KEY]

    def addDomainToPrivatePropertyNode(self, nameNodeId, classNode, ownerUserNode):
        isAdded = False
        if None == ownerUserNode:
            return isAdded

        nameNode = self.nameStore.getNameNodeById(nameNodeId)
        if None == nameNode:
            return isAdded
        names = nameNode[PROP_NAME_KEY]
        for name in names:
             propNode = self.collection.find_one({'_id':name,
                                                     IS_PRIVATE_KEY:True,
                                                     OWNER_KEY:ownerUserNode['_id']
                                                     })
             if None != propNode:
                updated = self.collection.update({'_id':propNode['_id'], OWNER_KEY: ownerUserNode['_id']}, { '$addToSet': { DOMAIN_KEY: classNode['_id'] } })
                if updated[UPDATED_EXISTING_KEY]:
                    for viewer in propNode[VIEWERS_KEY]:
                        userNode = {USER_NAME_KEY:viewer}
                        self.classStore.addDomain(classNode=classNode, propNode=propNode, userNode=userNode)
                isAdded = updated[UPDATED_EXISTING_KEY]
        return isAdded

if __name__ == '__main__':
    pass
