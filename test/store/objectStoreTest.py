'''
Created on Aug 6, 2014

@author: sushant pradhan
'''
from pymongo.mongo_client import MongoClient
from src.store.StoreFactory import StoreFactory
from src.store.dbConnection import DBConnection
import unittest
from src.store.constants import ID_KEY, NAME_NODE_ID_KEY
from src.store.userStore import UserStore

class ObjectStoreTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.client = MongoClient('localhost', 27017)
        self.client.drop_database('test')
        dbConn = DBConnection('test')
        self.objNodes = self.client.test.objNodes
        self.classNodes = self.client.test.classNodes
        self.propNodes = self.client.test.propNodes
        self.nameNodes = self.client.test.nameNodes

        self.storeFactory = StoreFactory(dbConn, '/TalenticaWorkspace/TLabs/graphite-python/RNA/src/store/users')
        self.publicObjectStore = self.storeFactory.publicObjectStore
        self.publicClassStore = self.storeFactory.publicClassStore
        self.publicPropertyStore = self.storeFactory.publicPropertyStore

        self.userStore = UserStore(dbConn)
        self.user1 = self.userStore.createUserNode("prasu05", "p$5%t")
        self.user2 = self.userStore.createUserNode("prasu06", "^%sf$")
        self.user1ObjStore = self.storeFactory.getPrivateObjectStore(self.user1)
        self.user2ObjStore = self.storeFactory.getPrivateObjectStore(self.user2)

    def setUp(self):
        self.__clean__()
        self.classNode = self.publicClassStore.createClassNode("User")

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.__clean__()

    @classmethod
    def tearDownClass(self):
        self.client = MongoClient('localhost', 27017)
        self.client.drop_database('test')

    def testCreateObjectNode(self):
        objNode = self.publicObjectStore.createObjectNode("sushant pradhan", self.classNode)
        self.assertNotEqual(self.publicObjectStore.getObjectNode(objNode[ID_KEY]), None)

    def testCreatePrivateObjectNode(self):
        objNode = self.user1ObjStore.createPrivateObjectNode("sushant pradhan", self.classNode)
        self.assertEqual(self.publicObjectStore.getObjectNode(objNode[ID_KEY]), None)
        self.assertNotEqual(self.user1ObjStore.getPrivateObjectNode(objNode[NAME_NODE_ID_KEY],
                                                                   objNode[ID_KEY]), None)

    def testSharePrivateObjectNode(self):
        objNode = self.user1ObjStore.createPrivateObjectNode("sushant pradhan", self.classNode)
        self.assertEqual(self.user2ObjStore.getPrivateObjectNode(objNode[NAME_NODE_ID_KEY],
                                                                   objNode[ID_KEY]), None)
        self.assertEqual(self.user1ObjStore.sharePrivateObjectNode(objNode, self.user2), True)
        self.assertNotEqual(self.user2ObjStore.getPrivateObjectNode(objNode[NAME_NODE_ID_KEY],
                                                                   objNode[ID_KEY]), None)
        self.assertEqual(self.publicObjectStore.getObjectNode(objNode[ID_KEY]), None)
        self.assertNotEqual(self.user1ObjStore.getPrivateObjectNode(objNode[NAME_NODE_ID_KEY],
                                                                   objNode[ID_KEY]), None)

    def testAddPublicProperty(self):
        class1 = self.publicClassStore.createClassNode("testClass1")
        class2 = self.publicClassStore.createClassNode("testClass2")
        prop1 = self.publicPropertyStore.createPropertyNode("testProp", class1, class2)
        prop2 = self.publicPropertyStore.createPropertyNode("testProp1", class1)
        testObjNode = self.publicObjectStore.createObjectNode("testObject", class1)
        valNode = self.nameNodes.find_one()
        self.assertEqual(self.publicObjectStore.addPublicProperty(testObjNode, prop2, valNode), True)
        valNode2 = self.publicObjectStore.createObjectNode("testObject", class2)
        self.assertEqual(self.publicObjectStore.addPublicProperty(testObjNode, prop1, valNode2), True)
        print valNode

    def __clean__(self):
        self.client.test.objNodes.remove()
        self.client.test.classNodes.remove()
        self.client.test.propNodes.remove()
        self.client.test.nameNodes.remove()
        self.client.test.stringNodes.remove()

if __name__ == "__main__":
    unittest.main()
