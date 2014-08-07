'''
Created on Aug 6, 2014

@author: sush
'''
from pymongo.mongo_client import MongoClient
from src.store.classStore import ClassStore
from src.store.dbConnection import DBConnection
from src.store.userStore import USerStore
import unittest
from src.store.users.prasu05ClassStore import Prasu05ClassStore
from src.store.users.prasu06ClassStore import Prasu06ClassStore
from src.store.constants import NAME_NODE_ID_KEY


class CLassStoreTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.client = MongoClient('localhost', 27017)
        self.client.drop_database('test')
    
    def setUp(self):
        self.dbConn = DBConnection('test')
        self.classStore = ClassStore(self.dbConn)
        self.userStore = USerStore(self.dbConn)
        self.user1 = self.userStore.createUserNode("prasu05", "p$5%t")
        self.user2 = self.userStore.createUserNode("prasu06", "^%sf$")
        self.prasu05ClassStore = Prasu05ClassStore(self.dbConn, "prasu05")
        self.prasu06ClassStore = Prasu06ClassStore(self.dbConn, "prasu06")

    @classmethod
    def tearDownClass(self):
        self.client = MongoClient('localhost', 27017)
#        self.client.drop_database('test')

    def testCLassStore(self):
        def testCreateClassNode():
            publicClass = self.classStore.createClassNode("publicClass")
            return publicClass

        def testCreatePrivateClassNode():
            return self.prasu05ClassStore.createPrivateClassNode("privateClass")
        
        def testGetClassNode(publicClass, privateClass):
            self.assertNotEqual(self.classStore.getClassNode(publicClass['_id']), None)
            self.assertEqual(self.classStore.getClassNode(privateClass['_id']), None)
        
        def testGetPrivateClassNode(publicClass, privateClass):
            privateClass1 = self.prasu05ClassStore.getPrivateClassNode(classNameNodeId=privateClass[NAME_NODE_ID_KEY],
                                                                           classNodeId=privateClass['_id'])
            print privateClass1
            self.assertNotEqual(privateClass, None)
            self.assertEqual(self.prasu05ClassStore.getPrivateClassNode(classNameNodeId=publicClass[NAME_NODE_ID_KEY],
                                                                           classNodeId=publicClass['_id']), None)
            self.assertEqual(self.prasu06ClassStore.getPrivateClassNode(classNameNodeId=publicClass[NAME_NODE_ID_KEY],
                                                                           classNodeId=publicClass['_id']), None)
            self.assertEqual(self.prasu06ClassStore.getPrivateClassNode(classNameNodeId=privateClass[NAME_NODE_ID_KEY],
                                                                           classNodeId=privateClass['_id']), None)
        
        def testSharePrivateClassNode(publicClass, privateClass):
            self.assertEqual(self.prasu05ClassStore.sharePrivateClassNode(publicClass, self.user2), False)
            self.assertEqual(self.prasu05ClassStore.sharePrivateClassNode(privateClass, self.user2), True)
            self.assertNotEqual(self.prasu06ClassStore.getPrivateClassNode(classNameNodeId=privateClass[NAME_NODE_ID_KEY],
                                                                           classNodeId=privateClass['_id']), None)

        publicClass = testCreateClassNode()
        privateClass = testCreatePrivateClassNode()
        print privateClass
        testGetClassNode(publicClass, privateClass)
        testGetPrivateClassNode(publicClass, privateClass)
        testSharePrivateClassNode(publicClass, privateClass)
    
    def testAddValLink(self):
        pass

if __name__ == "__main__":
    unittest.main()