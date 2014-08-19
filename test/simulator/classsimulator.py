'''
Created on Aug 4, 2014

@author: sushant pradhan


'''

from pymongo.mongo_client import MongoClient
from random import randint
from src.store.StoreFactory import StoreFactory
from src.store.classStore import ClassStore
from src.store.dbConnection import DBConnection
from src.store.propertyStore import PropertyStore

def populateClassesAndProperties(cs, ps):
    classNodes = []
    propNodes = []
    classNode0 = cs.createClassNode("class%s" % 0)
    classNode1 = cs.createClassNode("class%s" % 1)

    classNodes.append(classNode1)
    classNodes.append(classNode0)
    for j in range(0, 10):
        propNode = ps.createPropertyNode("prop%s|%s" % (0, j), classNode0, classNode1)
        propNodes.append(propNode)

    for i in range(2, 10000):
        classNode = cs.createClassNode("class%s" % i)
        classNodes.append(classNode)
        for j in range(0, 1):
            propNode = ps.createPropertyNode("prop%s|%s" % (i, j), classNodes[randint(0, i)], classNodes[randint(0, i)])
            propNodes.append(propNode)

def getDBConn():
    client = MongoClient('localhost', 27017)
    client.drop_database('simulator')
    return DBConnection('simulator')

def getStores():
    dbConn = getDBConn()
    storeFactory = StoreFactory(dbConn, '/TalenticaWorkspace/TLabs/graphite-python/RNA/src/store/users')
    cs = storeFactory.publicClassStore
    ps = storeFactory.publicPropertyStore
    return (cs, ps)

if __name__ == '__main__':
    (cs, ps) = getStores()
    populateClassesAndProperties(cs, ps)
