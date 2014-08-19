'''
Created on Aug 4, 2014

@author: sushant pradhan
'''
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from src.store.Exception.storeError import UserNodeError
from src.store.constants import USER_NAME_KEY, USER_SECRET_KEY

class UserStore(object):
    '''
    classdocs
    '''

    def __init__(self, dbConn):
        '''
        Constructor
        '''
        self.collection = dbConn.getDatabase().userNodes

    def getUserNodeCollection(self):
        return self.collection

    def createUserNode(self, username, secret):
        name = username.lower()
        tokens = name.split()
        if len(tokens) != 1:
            raise UserNodeError('user node name should not contain white spaces', name)
        try:
            nodeId =  self.getUserNodeCollection().insert({USER_NAME_KEY:name, USER_SECRET_KEY:secret})
            return self.getUserNodeCollection().find_one({'_id':ObjectId(nodeId)},
                                                         {USER_NAME_KEY:1,
                                                          USER_SECRET_KEY:1})
        except DuplicateKeyError:
            return self.getUserNode(username)

    def getUserNode(self, username):
        name = username.lower()
        tokens = name.split()
        if len(tokens) != 1:
            raise UserNodeError('user node name should not contain white spaces', name)
        return self.getUserNodeCollection().find_one({USER_NAME_KEY: name}, {USER_NAME_KEY:1, USER_SECRET_KEY:1})
