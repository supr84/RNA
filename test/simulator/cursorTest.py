'''
Created on Aug 5, 2014

@author: sushant pradhan
'''
import time
from src.store.dbConnection import DBConnection

if __name__ == '__main__':
    dbConn = DBConnection(None)
    strNodes = dbConn.getDatabase().stringNodes.find()
    before = time.clock()
    for strNode in strNodes:
        print strNode
    after = time.clock()
    print after - before