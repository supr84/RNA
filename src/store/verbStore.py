'''
Created on Aug 4, 2014

@author: sushant pradhan
'''
from bson.objectid import ObjectId

from src.store.Exception.storeError import VerbNodeError
from src.store.constants import DOMAIN_KEY, NAME_NODE_ID_KEY, \
    OWNER_KEY, ID_KEY, \
    VERB_NODE_COLLECTION, FORM_KEY, UPDATED_EXISTING_KEY,\
    VERB_NAME_KEY
from src.store.nameStore import NameStore


class VerbStore(object):
    '''
    Use StoreFactory to get instance of this class, bypassing that might result in unpredictable results.
    '''

    def __init__(self, dbConn):
        '''
        Constructor
        '''
        self.verbs = dbConn.getDatabase()[VERB_NODE_COLLECTION]
        self.nameStore = NameStore(dbConn)
        self.publicClassStore = None
        self.publicFormStore = None

    def __getNameNode__(self, verbName):
        # first letter of class should be capital letters
        name = verbName.lower()
        tokens = name.split()
        if len(tokens) != 1:
            raise VerbNodeError('verb node name should not contain white spaces', name)
        nameNode = self.nameStore.getNameNodeByName(name)
        if None == nameNode:
            nameNode = self.nameStore.createNameNode(name)
        return nameNode

    def createVerbNode(self, verbName, domainNode):
        nameNode = self.__getNameNode__(verbName)
        verbNode = {NAME_NODE_ID_KEY:nameNode[ID_KEY],
                    DOMAIN_KEY:[domainNode[ID_KEY], ]
                    }
        verbNodeId = self.verbs.insert(verbNode)
        verbNode[ID_KEY] = ObjectId(verbNodeId)
        self.nameStore.addNameLink(nameNodeId=nameNode[ID_KEY],
                                   nodeId=verbNode[ID_KEY],
                                   nameKey=VERB_NAME_KEY)
        return verbNode

    def getVerbNode(self, verbNodeId):
        if None == verbNodeId:
            return None
        permissibleObject = {NAME_NODE_ID_KEY:1,
                             DOMAIN_KEY:1,
                             FORM_KEY:1
                             }
        query = {ID_KEY:verbNodeId, OWNER_KEY: {'$exists':False}}

        return self.verbs.find_one(query,
                                   permissibleObject)

    def addDomain(self, verbNode, classNode):
        classNode = self.publicClassStore.getClassNode(classNode[ID_KEY])
        if None == classNode:
            return False
        updated = self.verbs.update({ID_KEY:verbNode[ID_KEY],
                                     OWNER_KEY: {'$exists':False}},
                                    { '$addToSet': {  DOMAIN_KEY: classNode[ID_KEY] } })
        return updated[UPDATED_EXISTING_KEY]
    
    def addForm(self, verbNode, formNode):
        formNode = self.publicFormStore.getFormNode(formNode[ID_KEY])
        if None == formNode:
            return False
        updated = self.verbs.update({ID_KEY:verbNode[ID_KEY],
                                     OWNER_KEY: {'$exists':False}},
                                    { '$addToSet': {  FORM_KEY: formNode[ID_KEY] } })
        return updated[UPDATED_EXISTING_KEY]
        
