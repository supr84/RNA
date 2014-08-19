'''
Created on Aug 4, 2014

@author: sushant pradhan
'''
from bson.objectid import ObjectId
from src.store.constants import DOMAIN_KEY, NAME_NODE_ID_KEY, \
    OWNER_KEY, USER_SECRET_KEY, NAME_NODE_COLLECTION, ID_KEY, FORM_KEY, FORM_NAME_KEY, \
    FORM_NODE_COLLECTION
from src.store.nameStore import NameStore
from src.store.users.securityError import SecurityBreachError
from src.store.Exception.storeError import FormNodeError

class __FACTORY__USER__NAME__PLACE__HOLDER__FormStore(object):
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
        self.formNodes = dbConn.getDatabase()[FORM_NODE_COLLECTION]
        self.nameStore = NameStore(dbConn)
        self.nameNodes = dbConn.getDatabase()[NAME_NODE_COLLECTION]
        self.userDomainLink = "%s%s" % (self.USER_SECRET, DOMAIN_KEY)
        self.userFormLink = "%s%s" % (self.USER_SECRET, FORM_KEY)
        self.userFormNameLink = "%s%s" % (self.USER_SECRET, FORM_NAME_KEY)
        self.privateClassStore = None

    def __getNameNode__(self, formURI):
        # TODO: add proper URL validation
        name = formURI
        tokens = name.split()
        if len(tokens) > 1000:
            raise FormNodeError('form node name should not contain white spaces', name)
        nameNode = self.nameStore.getNameNodeByName(name)
        if None == nameNode:
            nameNode = self.nameStore.createNameNode(name)
        return nameNode

    def createPrivateFormNode(self, formURI):
        nameNode = self.__getNameNode__(formURI)
        formNode = {NAME_NODE_ID_KEY:nameNode[ID_KEY], OWNER_KEY: self.USER_SECRET}
        formNodeId = self.formNodes.insert(formNode)
        formNode[ID_KEY] = ObjectId(formNodeId)
        self.nameStore.addNameLink(nameNodeId=nameNode[ID_KEY],
                                   nodeId=formNode[ID_KEY],
                                   nameKey="%s%s" % (self.USER_SECRET, FORM_NAME_KEY))
        return formNode

    def getPrivateFormNode(self, formNameNodeId, formNodeId):
        if None == formNameNodeId:
            return None
        query = {ID_KEY:formNameNodeId, self.userFormNameLink : { '$exists': True }}
        nameNode = self.nameNodes.find_one(query, {self.userFormNameLink:1})
        if None != nameNode:
            return self.formNodes.find_one({ID_KEY:formNodeId})
        else:
            return self.formNodes.find_one({ID_KEY:formNodeId, OWNER_KEY: {'$exists':False}})

    def sharePrivateFormNode(self, formNode, userNode):
        isShared = False
        if None == userNode or None == formNode:
            return isShared
        sharedFormNameKey = "%s%s" % (userNode[USER_SECRET_KEY], FORM_NAME_KEY)
        findQuery = {ID_KEY:formNode[ID_KEY], OWNER_KEY: self.USER_SECRET}
        formNode = self.formNodes.find_one(findQuery)
        if None != formNode:
            isShared = self.nameStore.addNameLink(nameNodeId=formNode[NAME_NODE_ID_KEY],
                                                  nodeId=formNode[ID_KEY],
                                                  nameKey=sharedFormNameKey)
        return isShared
