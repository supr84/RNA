'''
Created on Aug 4, 2014

@author: sush
'''
from bson.objectid import ObjectId
from src.store.Exception.storeError import ClassNodeError
from src.store.classStore import ClassStore
from src.store.constants import DOMAIN_KEY, USER_NAME_KEY, RANGE_KEY, \
    NAME_NODE_ID_KEY, CLASS_NAME_KEY, OWNER_KEY, UPDATED_EXISTING_KEY, \
    USER_SECRET_KEY, OBJECT_NODE_COLLECTION, PROPERTY_NODE_COLLECTION, PROP_NAME_KEY
from src.store.nameStore import NameStore
from src.store.userStore import USerStore
from src.store.users.prasu05ClassStore import Prasu05ClassStore
from src.store.users.securityError import SecurityBreachError

class Prasu05PropertyStore(object):
    '''
    classdocs
    '''

    def __init__(self, dbConn, userName):
        '''
        Constructor
        '''
        self.USER_NAME = 'prasu05'
        if self.USER_NAME != userName:
            raise SecurityBreachError('sorry you are not allowed to instantiate this class', userName)
        self.propNodes = dbConn.getDatabase()[PROPERTY_NODE_COLLECTION]
        self.privateClassStore = Prasu05ClassStore(dbConn, self.USER_NAME)
        self.classStore = ClassStore(dbConn)
        self.userStore = USerStore(dbConn)
        self.nameStore = NameStore(dbConn)
        self.userNode = self.userStore.getUserNode(self.USER_NAME)
        self.collection = dbConn.getDatabase()[OBJECT_NODE_COLLECTION]
        self.userDomainLink = "%s%s" % (self.userNode[USER_SECRET_KEY], DOMAIN_KEY)
        self.userRangeLink = "%s%s" % (self.userNode[USER_SECRET_KEY], RANGE_KEY)
        self.userPropNameLink = "%s%s" % (self.userNode[USER_SECRET_KEY], PROP_NAME_KEY)
    
    def __getNameNode__(self, className):
        #first letter of class should be capital letters
        name = className.title()
        tokens = name.split()
        if len(tokens) != 1:
            raise ClassNodeError('class node name should not contain white spaces', name)
        nameNode = self.nameStore.getNameNode(name)
        if None == nameNode:
            nameNode = self.nameStore.createNameNode(name)
        return nameNode

    def createPrivatePropertyNode(self, propName, domainClassNode, rangeClassNode):
        nameNode = self.__getNameNode__(propName)
        propertyNode = {NAME_NODE_ID_KEY:nameNode['_id'],
                        OWNER_KEY:self.USER_NAME}
        propNodeId = self.propNodes.insert(propertyNode)
        propertyNode['_id'] = ObjectId(propNodeId)
        self.nameStore.addNameLink(nameNodeId=nameNode['_id'],
                                   nodeId=propertyNode['_id'],
                                   nameKey=self.userPropNameLink)
        isDomainUpdated = False
        isRangeUpdated = False
        publicDomainClass = self.classStore.getClassNode(domainClassNode['_id'])
        if None != publicDomainClass:
            self.classStore.addDomain(publicDomainClass, propertyNode, self.userDomainLink)
            self.propNodes.update(propertyNode, { '$addToSet': {  DOMAIN_KEY: propertyNode['_id'] } })
            isDomainUpdated = True
        publicRangeClass = self.classStore.getClassNode(rangeClassNode['_id'])
        if None != publicRangeClass:
            self.classStore.addRange(publicRangeClass, propertyNode, self.userRangeLink)
            self.propNodes.update(propertyNode, { '$addToSet': {  RANGE_KEY: propertyNode['_id'] } })
            isRangeUpdated = True

        if not isDomainUpdated:
            privateDomainClassNode = self.privateClassStore.getPrivateClassNode(classNameNodeId=domainClassNode[NAME_NODE_ID_KEY],
                                                                         classNodeId=domainClassNode['_id'])
            if None != privateDomainClassNode:
                self.privateClassStore.addPrivateDomain(privateDomainClassNode['_id'], propertyNode['_id'])
                self.propNodes.update(propertyNode, { '$addToSet': {  self.userDomainLink: propertyNode['_id'] } })

        if not isRangeUpdated:
            privateRangeClassNode = self.privateClassStore.getPrivateClassNode(classNameNodeId=rangeClassNode[NAME_NODE_ID_KEY],
                                                                         classNodeId=rangeClassNode['_id'])
            if None != privateRangeClassNode:
                self.privateClassStore.addPrivateRange(privateRangeClassNode['_id'], propertyNode['_id'])
                self.propNodes.update(propertyNode, { '$addToSet': {  self.userRangeLink: propertyNode['_id'] } })
            else:
                #TODO: remove this floating property node
                pass
        return propertyNode

    def getPrivatePropertyNode(self, propNameNodeId, propNodeId):
        pass

    def sharePrivatePropertyNode(self, classNodeId, shareWithUserNode):
        isShared = False
        if None == shareWithUserNode:
            return isShared
        
        classNode = self.collection.find_one({'_id':classNodeId['_id'], OWNER_KEY: self.userNode[USER_NAME_KEY]})
        if None != classNode:
            isShared = self.nameStore.addNameLink(nameNodeId=classNode[NAME_NODE_ID_KEY],
                                       nodeId=classNodeId,
                                       nameKey="%s%s" % (shareWithUserNode[USER_SECRET_KEY], CLASS_NAME_KEY))
        return isShared
    
    def addPrivateDomain(self, propNodeId, domainClassNameNodeId, domainClassNodeId):
        domainClassNode = self.privateClassStore.getPrivateClassNode(domainClassNameNodeId, domainClassNodeId)
        if None == domainClassNode:
            return False
        updated = self.collection.update({'_id':propNodeId, OWNER_KEY: self.userNode[USER_NAME_KEY]}, { '$addToSet': {  self.userDomainLink: domainClassNode['_id'] } })
        return updated[UPDATED_EXISTING_KEY]