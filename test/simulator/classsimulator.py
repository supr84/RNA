'''
Created on Aug 4, 2014

@author: sushant pradhan


'''

from src.store.dbConnection import DBConnection
from src.store.classStore import ClassStore
from src.store.propertyStore import PropertyStore
from random import randint

def populateClassesAndProperties(cs, ps):
    classNodes = []
    propNodes = []
    classNode = cs.createClassNode("class%s" % 0)
    classNodes.append(classNode)
    for j in range(0, 10):
        propNode = ps.createPropertyNode("prop%s|%s" % (0, j))
        propNodes.append(propNode)
        ps.addDomain(classNode=classNode, propNode=propNode)

    for i in range(1, 100):
        classNode = cs.createClassNode("class%s" % i)
        classNodes.append(classNode)
        for j in range(0, 10):
            propNode = ps.createPropertyNode("prop%s|%s" % (i, j))
            propNodes.append(propNode)
            ps.addDomain(classNode=classNode, propNode=propNode)
            ps.addRange(classNode=classNodes[randint(0, i)], propNode=propNode)

def getDBConn():
    return DBConnection(None)

def getStores():
    dbConn = getDBConn()
    cs = ClassStore(dbConn)
    ps = PropertyStore(dbConn)
    return (cs, ps)

if __name__ == '__main__':
    (cs, ps) = getStores()
    populateClassesAndProperties(cs, ps)
