'''
Created on Aug 4, 2014

@author: sush
'''
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from src.store.Exception.storeError import UserNodeError

class USerStore(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        dbConn = params
        self.collection = dbConn.getDatabase().userNodes

    def getUserNodeCollection(self):
        return self.collection

    def createUserNode(self, username):
        name = username.lower()
        tokens = name.split()
        if len(tokens) != 1:
            raise UserNodeError('user node name should not contain white spaces', name)
        try:
            nodeId =  self.getUserNodeCollection().insert({'username':name})
            return self.getUserNodeCollection().find_one({'_id':ObjectId(nodeId)}, {'username':1})
        except DuplicateKeyError:
            return self.getUserNode(username)

    def getUserNode(self, username):
        name = username.lower()
        tokens = name.split()
        if len(tokens) != 1:
            raise UserNodeError('user node name should not contain white spaces', name)
        return self.getUserNodeCollection().find_one({'username':name}, {'username':1})

if __name__ == '__main__':
    pass
