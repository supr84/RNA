'''
Created on Aug 11, 2014

@author: sushanta pradhan
'''
from src.store.constants import FORM_NODE_COLLECTION, ID_KEY, NAME_NODE_ID_KEY,\
    FORM_NAME_KEY, OWNER_KEY, UPDATED_EXISTING_KEY, FORM_FIELD_QUERY_CLASS,\
    FORM_FIELD_CARDINALITY, FORM_PUBLIC_FIELD
from src.store.nameStore import NameStore
from src.store.Exception.storeError import VerbNodeError
from bson.objectid import ObjectId

class FormStore(object):
    '''
    classdocs
    '''
    def __init__(self, dbConn):
        self.forms = dbConn.getDatabase()[FORM_NODE_COLLECTION]
        self.nameStore = NameStore(dbConn)
        self.publicClassStore = None

    def __getNameNode__(self, formURI):
        #TODO: add proper URL validation
        name = formURI
        tokens = name.split()
        if len(tokens) > 1000:
            raise VerbNodeError('class node name should not contain white spaces', name)
        nameNode = self.nameStore.getNameNodeByName(name)
        if None == nameNode:
            nameNode = self.nameStore.createNameNode(name)
        return nameNode

    def createFormNode(self, formURI):
        nameNode = self.__getNameNode__(formURI)
        formNode = {NAME_NODE_ID_KEY:nameNode[ID_KEY]}
        formNodeId = self.forms.insert(formNode)
        formNode[ID_KEY] = ObjectId(formNodeId)
        self.nameStore.addNameLink(nameNodeId=nameNode[ID_KEY],
                                   nodeId=formNode[ID_KEY],
                                   nameKey=FORM_NAME_KEY)
        return formNode

    def getFormNode(self, formNodeId):
        if None == formNodeId:
            return None
        permissibleObject = {FORM_PUBLIC_FIELD:1}
        query = {ID_KEY:formNodeId, OWNER_KEY: {'$exists':False}}
        return self.forms.find_one(query, permissibleObject)

    def addField(self, formNode, fieldName, fieldClassNode, cardinality=1):
        fn = self.getFormNode(formNode.get(ID_KEY))
        if None == fn:
            return False
        fcn = self.publicClassStore.getClassNode(fieldClassNode.get(ID_KEY))
        if None == fcn:
            return False
        findQuery = {ID_KEY:fn[ID_KEY], OWNER_KEY: {'$exists':False}}
        fieldObj = {FORM_FIELD_QUERY_CLASS: fcn[ID_KEY], FORM_FIELD_CARDINALITY:cardinality}
        updated = self.forms.update(findQuery,{'$set' : { fieldName: fieldObj} })
        if updated[UPDATED_EXISTING_KEY]:
            updated = self.forms.update(findQuery,{'$addToSet': {  FORM_PUBLIC_FIELD: fieldName }})
            return updated[UPDATED_EXISTING_KEY]
