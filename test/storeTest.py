'''
Created on Aug 4, 2014

@author: sush
'''
import unittest
from src.store.classStore import ClassStore
from src.store.dbConnection import DBConnection
from src.store.propertyStore import PropertyStore
from src.store.objectStore import ObjectNodeStore
from src.store.nameStore import NameStore

class Test(unittest.TestCase):

    def testClassStore(self):
        dbConn = DBConnection(None)
        cs = ClassStore(dbConn)
        user = cs.createClassNode('user')
        print user
        institution = cs.createClassNode('institution')
        print institution
        place = cs.createClassNode('place')
        print place

        ps = PropertyStore(dbConn)
        location = ps.createPropertyNode('location')
        print str(location)
        ps.addRange(classNode=place, propNode=location)
        ps.addDomain(classNode=institution, propNode=location)
        ps.addDomain(classNode=user, propNode=location)

        print cs.getDomain(user)
        print cs.getDomain(institution)
        print cs.getDomain(place)

        ns = NameStore(dbConn)
        pune = ns.createNameNode('pune')
        os = ObjectNodeStore(dbConn)
        sushant = os.createObjectNode('sushant', user)
        pune = os.createObjectNode('pune', place)
        print "create:%s, get:%s" % (sushant, os.getObjectNode('sushant'))

        ps.createPropertyNode('firstname')
        firstname = ps.getPropertyNode('firstname')
        ps.addDomain(classNode=user, propNode=firstname)
        pradhan = ns.createNameNode('kumar pradhan')
        bhabani = ns.createNameNode('bhabani pradhan')
        bhabani = ns.createNameNode('pradhan mantri')
        os.addObjectProperty(objNode=sushant, propNode=location, valueNode=pune)
        os.addObjectProperty(objNode=sushant, propNode=firstname, valueNode=pradhan)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()