'''
Created on Aug 4, 2014

@author: sushant pradhan
'''
from pymongo import ASCENDING, MongoClient
from src.store.constants import NAME_NODE_ID_KEY, USER_NAME_KEY, NAME_KEY,\
    OBJECT_TYPE_LINK, STRING_POSITION1_LINK, STRING_POSITION2_LINK,\
    STRING_POSITION3_LINK
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
        nameNodes.create_index([(STRING_POSITION1_LINK, ASCENDING),
                                (STRING_POSITION2_LINK, ASCENDING),
                                (STRING_POSITION3_LINK, ASCENDING)], unique=True)
        objNodes = db.objNodes
        objNodes.create_index([(NAME_NODE_ID_KEY, ASCENDING), (OBJECT_TYPE_LINK, ASCENDING)], unique=True)
    def getDatabase(self):
        return self.db
    def dropDatabase(self):
        self.client.drop_database(self.__dbName__)
