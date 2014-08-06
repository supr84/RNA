'''
Created on Aug 4, 2014

@author: sush
'''
from pymongo import MongoClient
from pymongo import ASCENDING
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
        stringNodes.create_index([("name", ASCENDING)], unique=True)
        
        classNodes = db.classNodes
        classNodes.create_index([("nameNodeId", ASCENDING)], unique=True)
        
        propNodes = db.propNodes
        propNodes.create_index([("nameNodeId", ASCENDING)], unique=True)
        
        userNodes = db.userNodes
        userNodes.create_index([("username", ASCENDING)], unique=True)

        nameNodes = db.nameNodes
        nameNodes.create_index([("pos_1", ASCENDING), ("pos_2", ASCENDING), ("pos_3", ASCENDING)], unique=True)
        
        objNodes = db.objNodes
        objNodes.create_index([("nameNodeId", ASCENDING), ("typeId", ASCENDING)], unique=True)
        
    def getDatabase(self):
        return self.db
    
    def dropDatabase(self):
        self.client.drop_database(self.__dbName__)

if __name__ == '__main__':
    pass

        
        