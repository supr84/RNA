'''
Created on Aug 4, 2014

@author: sushant pradhan
'''
from bson.objectid import ObjectId
from src.store.constants import DOMAIN_KEY, RANGE_KEY, NAME_NODE_ID_KEY, \
    OWNER_KEY, UPDATED_EXISTING_KEY, \
    USER_SECRET_KEY, NAME_NODE_COLLECTION, ID_KEY, FORM_KEY, \
    VERB_NODE_COLLECTION, VERB_NAME_KEY, VERB_KEY
from src.store.nameStore import NameStore
from src.store.users.securityError import SecurityBreachError
from src.store.Exception.storeError import VerbNodeError

class __FACTORY__USER__NAME__PLACE__HOLDER__VerbStore(object):
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
        self.verbNodes = dbConn.getDatabase()[VERB_NODE_COLLECTION]
        self.nameStore = NameStore(dbConn)
        self.nameNodes = dbConn.getDatabase()[NAME_NODE_COLLECTION]
        self.userDomainLink = "%s%s" % (self.USER_SECRET, DOMAIN_KEY)
        self.userFormLink = "%s%s" % (self.USER_SECRET, FORM_KEY)
        self.userVerbNameLink = "%s%s" % (self.USER_SECRET, VERB_NAME_KEY)
        self.privateClassStore = None
        self.privateFormStore = None

    def __getPrivateLinks__(self, verbNode, linkName):
        findQuery = {ID_KEY: verbNode.get(ID_KEY),
                     linkName: { '$exists': True }}
        links = self.verbNodes.find_one(findQuery, {linkName:1})
        if None != links:
            return links[linkName]
        else:
            return []

    def __getNameNode__(self, formURI):
        # first letter of class should be capital letters
        name = formURI.lower()
        tokens = name.split()
        if len(tokens) != 1:
            raise VerbNodeError('verb node name should not contain white spaces', name)
        nameNode = self.nameStore.getNameNodeByName(name)
        if None == nameNode:
            nameNode = self.nameStore.createNameNode(name)
        return nameNode

    def createPrivateVerbNode(self, verbName):
        nameNode = self.__getNameNode__(verbName)
        verbNode = {NAME_NODE_ID_KEY:nameNode[ID_KEY], OWNER_KEY: self.USER_SECRET}
        verbNodeId = self.verbNodes.insert(verbNode)
        verbNode[ID_KEY] = ObjectId(verbNodeId)
        self.nameStore.addNameLink(nameNodeId=nameNode[ID_KEY],
                                   nodeId=verbNode[ID_KEY],
                                   nameKey="%s%s" % (self.USER_SECRET, VERB_NAME_KEY))
        return verbNode


    def getPrivateVerbNode(self, verbNameNodeId, verbNodeId):
        if None == verbNameNodeId:
            return None
        query = {ID_KEY:verbNameNodeId, self.userVerbNameLink : { '$exists': True }}
        nameNode = self.nameNodes.find_one(query, {self.userVerbNameLink:1})
        permisibleObject = {NAME_NODE_ID_KEY:1,
                            DOMAIN_KEY:1,
                            RANGE_KEY:1,
                            self.userDomainLink:1,
                            self.userFormLink:1}
        if None != nameNode:
            return self.verbNodes.find_one({ID_KEY:verbNodeId},
                                           permisibleObject)
        else:
            return self.verbNodes.find_one({ID_KEY:verbNodeId, OWNER_KEY: {'$exists':False}},
                                           permisibleObject)

    def sharePrivateVerbNode(self, verbNode, userNode):
        isShared = False
        if None == userNode or None == verbNode:
            return isShared
        sharedVerbNameKey = "%s%s" % (userNode[USER_SECRET_KEY], VERB_NAME_KEY)
        findQuery = {ID_KEY:verbNode[ID_KEY], OWNER_KEY: self.USER_SECRET}
        verbNode = self.verbNodes.find_one(findQuery)
        if None != verbNode:
            isShared = self.nameStore.addNameLink(nameNodeId=verbNode[NAME_NODE_ID_KEY],
                                                  nodeId=verbNode[ID_KEY],
                                                  nameKey=sharedVerbNameKey)
            if isShared:
                sharedDomainNameKey = "%s%s" % (userNode[USER_SECRET_KEY], DOMAIN_KEY)
                sharedFormNameKey = "%s%s" % (userNode[USER_SECRET_KEY], FORM_KEY)

                self.verbNodes.update(findQuery,
                                       {'$addToSet':
                                            {sharedDomainNameKey:
                                                {'$each':self.__getPrivateLinks__(verbNode, self.userDomainLink)}
                                            }
                                        })
                self.verbNodes.update(findQuery,
                                       {'$addToSet':
                                            {sharedFormNameKey:
                                                {'$each': self.__getPrivateLinks__(verbNode, self.userFormLink)}
                                            }
                                        })
        return isShared

    def addPrivateDomain(self, verbNode, classNode):
        key = self.userDomainLink
        privateVerbNode = self.getPrivateVerbNode(verbNameNodeId=verbNode[NAME_NODE_ID_KEY],
                                                  verbNodeId=verbNode[ID_KEY])
        if None != privateVerbNode:
            classNode = self.privateClassStore.getPrivateClassNode(classNameNodeId=classNode.get(NAME_NODE_ID_KEY),
                                                                classNodeId=classNode[ID_KEY])
            if None == classNode:
                return False
            updated = self.verbNodes.update({ID_KEY:verbNode[ID_KEY]},
                                             { '$addToSet': {  key: classNode[ID_KEY] } })
            return updated[UPDATED_EXISTING_KEY]
        return False

    def addPrivateForm(self, verbNode, formNode):
        key = self.userFormLink
        privateVerbNode = self.getPrivateVerbNode(verbNameNodeId=verbNode[NAME_NODE_ID_KEY],
                                                    verbNodeId=verbNode[ID_KEY])
        if None != privateVerbNode:
            classNode = self.privateFormStore.getPrivateFormNode(formNameNodeId=formNode.get(NAME_NODE_ID_KEY),
                                                                 formNodeId=formNode[ID_KEY])
            if None == classNode:
                return False
            updated = self.verbNodes.update({ID_KEY:verbNode[ID_KEY]},
                                             { '$addToSet': {  key: classNode[ID_KEY] } })
            return updated[UPDATED_EXISTING_KEY]
        return False
