'''
Created on Aug 6, 2014

@author: sush
'''
from pymongo.mongo_client import MongoClient
from src.store.classStore import ClassStore
from src.store.dbConnection import DBConnection
from src.store.propertyStore import PropertyStore
from src.store.userStore import USerStore
import unittest
from src.store.users.prasu05PropStore import Prasu05PropertyStore
from src.store.users.prasu05ClassStore import Prasu05ClassStore
from src.store.users.prasu06ClassStore import Prasu06ClassStore


class PropStoreTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.client = MongoClient('localhost', 27017)
        self.client.drop_database('test')
        self.dbConn = DBConnection('test')
        self.classStore = ClassStore(self.dbConn)
        self.userStore = USerStore(self.dbConn)
        self.propStore = PropertyStore(self.dbConn)
        self.publicDomainClass1 = self.classStore.createClassNode('publicDomainClass1')
        self.publicDomainClass2 = self.classStore.createClassNode('publicDomainClass2')
        self.publicRangeClass1 = self.classStore.createClassNode('publicRangeClass1')
        self.publicRangeClass2 = self.classStore.createClassNode('publicRangeClass2')
        self.user1 = self.userStore.createUserNode("prasu05", "p$5%t")
        self.user2 = self.userStore.createUserNode("prasu06", "^%sf$")
        self.prasu05PropStore = Prasu05PropertyStore(self.dbConn, 'prasu05')
        self.prasu05ClassStore = Prasu05ClassStore(self.dbConn, "prasu05")
        self.prasu06ClassStore = Prasu06ClassStore(self.dbConn, "prasu06")
        self.prasu06DomainClass = self.prasu06ClassStore.createPrivateClassNode("prasuo6PrivateDomainClass")
        self.privateDomainClass = self.prasu05ClassStore.createPrivateClassNode("prasuo5PrivateDomainClass")
        self.privateRangeClass = self.prasu05ClassStore.createPrivateClassNode("prasuo5PrivateRangeClass")
#        self.privateClass1 = self.classStore.createPrivateClassNode('privateClass', self.user1)

    @classmethod
    def tearDownClass(self):
        self.client = MongoClient('localhost', 27017)
#        self.client.drop_database('test')

    def testPropStore(self):
        def testAddDomain(publicPropNodeId, privatePropNodeId):
            #add private property to public class
            self.assertEqual(self.propStore.addDomainToPrivatePropertyNode(privatePropNodeId, self.publicDomainClass2, self.user1), True)
            #add private property to private class
            self.assertEqual(self.propStore.addDomainToPrivatePropertyNode(privatePropNodeId, self.privateClass1, self.user1), True)
            #add public property to public class
            self.assertEqual(self.propStore.addDomain(publicPropNodeId, self.publicDomainClass2), True)
            #add public property to private class
            self.assertEqual(self.propStore.addDomain(publicPropNodeId, self.privateClass1), False)
            self.assertEqual(self.propStore.addDomain(privatePropNodeId, self.privateClass1), False)
            self.assertEqual(self.propStore.addDomain(privatePropNodeId, self.publicDomainClass2), False)
            self.assertEqual(self.propStore.addDomainToPrivatePropertyNode(publicPropNodeId, self.publicDomainClass2, self.user1), False)
            
        
        def testSharePrivatePropertyNode(publicPropNodeId, privatePropNodeId):
            self.assertEqual(self.propStore.sharePrivatePropertyNode(publicPropNodeId, self.user1, self.user2), False)
            self.assertEqual(self.propStore.sharePrivatePropertyNode(publicPropNodeId, self.user2, self.user1), False)
            self.assertEqual(self.propStore.sharePrivatePropertyNode(privatePropNodeId, self.user1, self.user2), True)
            self.assertNotEqual(self.propStore.getPrivatePropertyNode(privatePropNodeId, self.user2), None)

        def testCreatePropNode():
            publicPropNode = self.propStore.createPropertyNode('testProp', self.publicDomainClass1['_id'], self.publicRangeClass1['_id'])
            print publicPropNode
            print self.classStore.getClassNode(self.publicDomainClass1['_id'])
            print self.classStore.getClassNode(self.publicRangeClass1['_id'])
            return publicPropNode

        def testCreatePrivatePropNode():
#            privatePropNode = self.prasu05PropStore.\
#                            createPrivatePropertyNode("testPrivatePropNoed",
#                            self.publicDomainClass1,
#                            self.publicRangeClass1)
            print self.privateDomainClass
            print self.privateRangeClass
            privatePropNode = self.prasu05PropStore.\
                            createPrivatePropertyNode("testPrivatePropNode1",
                            self.prasu06DomainClass,
                            self.privateRangeClass)
            return privatePropNode

        def testGetPropNode(publicPropNodeId):
            self.assertNotEqual(self.propStore.getPropertyNode(publicPropNodeId), None)
            self.assertEqual(self.propStore.getPrivatePropertyNode(publicPropNodeId, self.user1), None)
            self.assertEqual(self.propStore.getPrivatePropertyNode(publicPropNodeId, self.user2), None)
        
        def testGetPrivatePropNode(privatePropNodeId):
            self.assertNotEqual(self.propStore.getPrivatePropertyNode(privatePropNodeId, self.user1), None)
            self.assertEqual(self.propStore.getPrivatePropertyNode(privatePropNodeId, self.user2), None)
            self.assertEqual(self.propStore.getPropertyNode(privatePropNodeId), None)

#        publicPropNodeId = testCreatePropNode()
        privatePropNodeId = testCreatePrivatePropNode()
#        testGetPropNode(publicPropNodeId)
#        testGetPrivatePropNode(privatePropNodeId)
#        testSharePrivatePropertyNode(publicPropNodeId, privatePropNodeId)
#        testAddDomain(publicPropNodeId, privatePropNodeId)
        
    
    
    def testAddValLink(self):
        pass

if __name__ == "__main__":
    unittest.main()