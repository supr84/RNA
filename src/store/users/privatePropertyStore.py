'''
Created on Aug 4, 2014

@author: sushant pradhan
'''
from bson.objectid import ObjectId
from src.store.Exception.storeError import ClassNodeError
from src.store.constants import DOMAIN_KEY, RANGE_KEY, NAME_NODE_ID_KEY, \
    OWNER_KEY, UPDATED_EXISTING_KEY, PROPERTY_NODE_COLLECTION, PROP_NAME_KEY, ID_KEY, \
    USER_SECRET_KEY, NAME_NODE_COLLECTION, PROP_VALUE_KEY
from src.store.nameStore import NameStore
from src.store.users.securityError import SecurityBreachError

class __FACTORY__USER__NAME__PLACE__HOLDER__PropertyStore(object):
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
        self.propNodes = dbConn.getDatabase()[PROPERTY_NODE_COLLECTION]
        self.nameNodes = dbConn.getDatabase()[NAME_NODE_COLLECTION]
        self.nameStore = NameStore(dbConn)
        self.userDomainLink = "%s%s" % (self.USER_SECRET, DOMAIN_KEY)
        self.userRangeLink = "%s%s" % (self.USER_SECRET, RANGE_KEY)
        self.userPropNameLink = "%s%s" % (self.USER_SECRET, PROP_NAME_KEY)

    def __getPrivateLinks__(self, propNode, linkName):
        findQuery = {ID_KEY: propNode.get(ID_KEY),
                     linkName: { '$exists': True }}
        links = self.propNodes.find_one(findQuery, {linkName:1})
        if None != links:
            return links[linkName]
        else:
            return []

    def __getNameNode__(self, formURI):
        #first letter of class should be capital letters
        name = formURI.title()
        tokens = name.split()
        if len(tokens) != 1:
            raise ClassNodeError('class node name should not contain white spaces', name)
        nameNode = self.nameStore.getNameNodeByName(name)
        if None == nameNode:
            nameNode = self.nameStore.createNameNode(name)
        return nameNode

    def createPrivatePropertyNode(self, propName, domainClassNode, rangeClassNode):
        privateRangeClass = None
        privateDomainClass = self.privateClassStore.getPrivateClassNode(classNodeId=domainClassNode.get(ID_KEY))
        if None != privateDomainClass:
            privateRangeClass = self.privateClassStore.getPrivateClassNode(classNodeId=rangeClassNode.get(ID_KEY))
            if None == privateRangeClass:
                return None

        nameNode = self.__getNameNode__(propName)
        propertyNode = {NAME_NODE_ID_KEY:nameNode[ID_KEY],
                        OWNER_KEY: self.USER_SECRET,
                        self.userDomainLink: [privateDomainClass.get(ID_KEY),],
                        self.userRangeLink: [privateRangeClass.get(ID_KEY),]
                        }
        propNodeId = self.propNodes.insert(propertyNode)
        propertyNode[ID_KEY] = ObjectId(propNodeId)
        self.nameStore.addNameLink(nameNodeId=nameNode[ID_KEY],
                                   nodeId=propertyNode[ID_KEY],
                                   nameKey=self.userPropNameLink)
        self.privateClassStore.addPrivateDomain(classNode=privateDomainClass,
                                                propNode=propertyNode)
        self.privateClassStore.addPrivateRange(classNode=privateRangeClass,
                                                propNode=propertyNode)
        propertyNode.pop(OWNER_KEY)
        return propertyNode

    def getPrivatePropertyNode(self, propNodeId):
        permissibleObject = {NAME_NODE_ID_KEY:1,
                             DOMAIN_KEY:1,
                             RANGE_KEY:1,
                             self.userRangeLink:1,
                             self.userDomainLink:1}
        pn = self.propNodes.find_one({ID_KEY: propNodeId}, permissibleObject)
        if None == pn:
            return None
        query = {ID_KEY:pn[NAME_NODE_ID_KEY], self.userPropNameLink : pn[ID_KEY]}
        nameNode = self.nameNodes.find_one(query, {self.userPropNameLink:1})
        if None != nameNode:
            return pn
        else:
            return self.propNodes.find_one({ID_KEY:propNodeId, OWNER_KEY: {'$exists':False}},
                                            permissibleObject)

    def sharePrivatePropertyNode(self, propNode, userNode):
        isShared = False
        if None == userNode or None == propNode:
            return isShared
        sharedPropNameKey = "%s%s" % (userNode[USER_SECRET_KEY], PROP_NAME_KEY)
        findQuery = {ID_KEY:propNode.get(ID_KEY), OWNER_KEY: self.USER_SECRET}
        propNode = self.propNodes.find_one(findQuery)
        if None != propNode:
            isShared = self.nameStore.addNameLink(nameNodeId=propNode[NAME_NODE_ID_KEY],
                                                  nodeId=propNode.get(ID_KEY),
                                                  nameKey=sharedPropNameKey)
            if isShared:
                sharedDomainNameKey = "%s%s" % (userNode[USER_SECRET_KEY], DOMAIN_KEY)
                sharedRangeNameKey = "%s%s" % (userNode[USER_SECRET_KEY], RANGE_KEY)

                self.propNodes.update(findQuery,
                                       {'$addToSet':
                                            {sharedDomainNameKey:
                                                {'$each':self.__getPrivateLinks__(propNode, self.userDomainLink)}
                                            }
                                        })
                self.propNodes.update(findQuery,
                                       {'$addToSet':
                                            {sharedRangeNameKey:
                                                {'$each': self.__getPrivateLinks__(propNode, self.userRangeLink)}
                                            }
                                        })
        return isShared

    def addPrivateDomain(self, propNode, domainClassNode):
        privateDomainClass = self.privateClassStore.\
            getPrivateClassNode(classNodeId=domainClassNode.get(ID_KEY))
        if None != privateDomainClass:
            privatePropNode = self.getPrivatePropertyNode(propNodeId=propNode[ID_KEY])
            if None == privatePropNode:
                return False
            updated = self.propNodes.update({ID_KEY:propNode.get(ID_KEY)},
                                            { '$addToSet': {  self.userDomainLink: privateDomainClass.get(ID_KEY) } })
            return updated[UPDATED_EXISTING_KEY]
        return False

    def addPrivateValLink(self, propNode, valNode):
        if None == propNode or None == valNode:
            return False
        pn = self.getPrivatePropertyNode(propNode[ID_KEY])
        if None == pn:
            return False
        privateValKey = "%s%s" % (self.USER_SECRET, PROP_VALUE_KEY)
        updated = self.propNodes.update({ID_KEY:pn[ID_KEY]}, { '$addToSet': { privateValKey: valNode[ID_KEY] } })
        return updated[UPDATED_EXISTING_KEY]
