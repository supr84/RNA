'''
Created on Aug 4, 2014

@author: sushant pradhan
'''
from bson.objectid import ObjectId
from src.store.Exception.storeError import ClassNodeError
from src.store.constants import DOMAIN_KEY, RANGE_KEY, NAME_NODE_ID_KEY, \
    CLASS_NAME_KEY, OWNER_KEY, UPDATED_EXISTING_KEY, CLASS_NODE_COLLECTION, \
    USER_SECRET_KEY, NAME_NODE_COLLECTION, ID_KEY
from src.store.nameStore import NameStore
from src.store.users.securityError import SecurityBreachError

class __FACTORY__USER__NAME__PLACE__HOLDER__ClassStore(object):
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
        self.classNodes = dbConn.getDatabase()[CLASS_NODE_COLLECTION]
        self.nameStore = NameStore(dbConn)
        self.nameNodes = dbConn.getDatabase()[NAME_NODE_COLLECTION]
        self.userDomainLink = "%s%s" % (self.USER_SECRET, DOMAIN_KEY)
        self.userRangeLink = "%s%s" % (self.USER_SECRET, RANGE_KEY)
        self.userClassNameLink = "%s%s" % (self.USER_SECRET, CLASS_NAME_KEY)

    def __getPrivateLinks__(self, classNode, linkName):
        findQuery = {ID_KEY: classNode.get(ID_KEY),
                     linkName: { '$exists': True }}
        links = self.classNodes.find_one(findQuery, {linkName:1})
        if None != links:
            return links[linkName]
        else:
            return []

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

    def createPrivateClassNode(self, className):
        nameNode = self.__getNameNode__(className)
        classNodeId =  self.classNodes.insert({NAME_NODE_ID_KEY:nameNode[ID_KEY], OWNER_KEY: self.USER_SECRET})
        classNode = {ID_KEY:ObjectId(classNodeId), NAME_NODE_ID_KEY:nameNode[ID_KEY]}
        self.nameStore.addNameLink(nameNodeId=nameNode[ID_KEY],
                                   nodeId=classNode[ID_KEY],
                                   nameKey="%s%s" % (self.USER_SECRET, CLASS_NAME_KEY))
        return classNode


    def getPrivateClassNode(self, classNameNodeId, classNodeId):
        if None == classNameNodeId:
            return None
        query = {ID_KEY:classNameNodeId, self.userClassNameLink : { '$exists': True }}
        nameNode = self.nameNodes.find_one(query, {self.userClassNameLink:1})
        if None != nameNode:
            return self.classNodes.find_one({ID_KEY:classNodeId},
                                                        {NAME_NODE_ID_KEY:1,
                                                         DOMAIN_KEY:1,
                                                         RANGE_KEY:1,
                                                         self.userRangeLink:1,
                                                         self.userDomainLink:1})
        else:
            return self.classNodes.find_one({ID_KEY:classNodeId, OWNER_KEY: {'$exists':False}},
                                                        {NAME_NODE_ID_KEY:1,
                                                         self.userRangeLink:1,
                                                         self.userDomainLink:1
                                                         })

    def sharePrivateClassNode(self, classNode, userNode):
        isShared = False
        if None == userNode or None == classNode:
            return isShared
        sharedClassNameKey = "%s%s" % (userNode[USER_SECRET_KEY], CLASS_NAME_KEY)
        findQuery = {ID_KEY:classNode[ID_KEY], OWNER_KEY: self.USER_SECRET}
        classNode = self.classNodes.find_one(findQuery)
        if None != classNode:
            isShared = self.nameStore.addNameLink(nameNodeId=classNode[NAME_NODE_ID_KEY],
                                                  nodeId=classNode,
                                                  nameKey=sharedClassNameKey)
            if isShared:
                sharedDomainNameKey = "%s%s" % (userNode[USER_SECRET_KEY], DOMAIN_KEY)
                sharedRangeNameKey = "%s%s" % (userNode[USER_SECRET_KEY], RANGE_KEY)

                self.classNodes.update(findQuery,
                                       {'$addToSet':
                                            {sharedDomainNameKey:
                                                {'$each':self.__getPrivateLinks__(classNode, self.userDomainLink)}
                                            }
                                        })
                self.classNodes.update(findQuery,
                                       {'$addToSet':
                                            {sharedRangeNameKey:
                                                {'$each': self.__getPrivateLinks__(classNode, self.userRangeLink)}
                                            }
                                        })
        return isShared

    def addPrivateDomain(self, classNode, propNode):
        return self.__addLink__(classNode, propNode, self.userDomainLink)

    def addPrivateRange(self, classNode, propNode):
        return self.__addLink__(classNode, propNode, self.userRangeLink)

    def __addLink__(self, classNode, propNode, key):
        privateClassNode = self.getPrivateClassNode(classNameNodeId=classNode[NAME_NODE_ID_KEY],
                                                    classNodeId=classNode[ID_KEY])
        if None != privateClassNode:
            propNode = self.privatePropStore.getPrivatePropertyNode(propNameNodeId=propNode.get(NAME_NODE_ID_KEY),
                                                                propNodeId=propNode[ID_KEY])
            if None == propNode:
                return False
            updated = self.classNodes.update({ID_KEY:classNode[ID_KEY]},
                                             { '$addToSet': {  key: propNode[ID_KEY] } })
            return updated[UPDATED_EXISTING_KEY]
        return False
