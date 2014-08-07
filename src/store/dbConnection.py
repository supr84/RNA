'''
Created on Aug 4, 2014

@author: sush
'''
from pymongo import ASCENDING, MongoClient
from src.store.constants import IS_PRIVATE_KEY, NAME_NODE_ID_KEY, USER_NAME_KEY, \
    NAME_KEY, OWNER_KEY
class DBConnection(object):
    '''
    classdocs
    '''
    def __init__(self, dbName):
        '''
        Constructor
        '''
        self.__dbName__ = dbName
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[dbName]
        self.__ensureIndex__(self.db)

    def __ensureIndex__(self, db):
        stringNodes = db.stringNodes
        stringNodes.create_index([(NAME_KEY, ASCENDING)], unique=True)
        
        classNodes = db.classNodes
        classNodes.create_index([(NAME_NODE_ID_KEY, ASCENDING)], unique=True)
        
        propNodes = db.propNodes
        propNodes.create_index([(NAME_NODE_ID_KEY, ASCENDING)], unique=True)
        
        userNodes = db.userNodes
        userNodes.create_index([(USER_NAME_KEY, ASCENDING)], unique=True)

        nameNodes = db.nameNodes
        nameNodes.create_index([("pos_1", ASCENDING), ("pos_2", ASCENDING), ("pos_3", ASCENDING)], unique=True)
        
        objNodes = db.objNodes
        objNodes.create_index([(NAME_NODE_ID_KEY, ASCENDING), ("typeId", ASCENDING)], unique=True)
        
    def getDatabase(self):
        return self.db
    
    def dropDatabase(self):
        self.client.drop_database(self.__dbName__)

if __name__ == '__main__':
    pass

        
        