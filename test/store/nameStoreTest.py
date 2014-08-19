'''
Created on Aug 6, 2014

@author: sushant pradhan
'''
from pymongo.mongo_client import MongoClient
from src.store.dbConnection import DBConnection
from src.store.nameStore import NameStore
import unittest
from src.store.constants import NAME_KEY, ID_KEY


class NameStoreTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.client = MongoClient('localhost', 27017)
        self.client.drop_database('test')
    
    def setUp(self):
        self.dbConn = DBConnection('test')
        self.nameStore = NameStore(self.dbConn)

    @classmethod
    def tearDownClass(self):
        self.client = MongoClient('localhost', 27017)
#        self.client.drop_database('test')
    def testGetName(self):
        name = "test name Node"
        nameNode = self.nameStore.createNameNode(name)
        nn = self.nameStore.getNameNodeByName(name)
        self.assertEqual(nn[NAME_KEY], name)
        nn = self.nameStore.getNameNodeById(nameNode[ID_KEY])
        self.assertEqual(nn[NAME_KEY], name)

    def testCLassStore(self):
        def testCreateNameNode():
            nameNode1 = self.nameStore.createNameNode("test name Node")
            print nameNode1
            print self.nameStore.createNameNode("test name Node")

        def testCreatePrivateClassNode():
            return self.prasu05ClassStore.createPrivateClassNode("privateClass")
        
        def testGetClassNode(publicClassId, privateClassId):
            self.assertNotEqual(self.classStore.getClassNode(publicClassId['_id']), None)
            self.assertEqual(self.classStore.getClassNode(privateClassId['_id']), None)
        
        def testGetPrivateClassNode(publicClassId, privateClassId):
            self.assertNotEqual(self.classStore.getPrivateClassNode(privateClassId, self.user1), None)
            self.assertEqual(self.classStore.getPrivateClassNode(privateClassId, self.user2), None)
            self.assertEqual(self.classStore.getPrivateClassNode(publicClassId, self.user1), None)
        
        def testSharePrivateClassNode(publicClassId, privateClassId):
            self.assertEqual(self.classStore.sharePrivateClassNode(publicClassId, self.user1, self.user2), False)
            self.assertEqual(self.classStore.sharePrivateClassNode(privateClassId, self.user1, self.user2), True)

        nameNode = testCreateNameNode()
    
    def testAddValLink(self):
        pass

if __name__ == "__main__":
    unittest.main()