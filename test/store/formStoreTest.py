'''
Created on Aug 6, 2014

@author: sushant pradhan
'''
from pymongo.mongo_client import MongoClient
from src.store.StoreFactory import StoreFactory
from src.store.dbConnection import DBConnection
import unittest
from src.store.constants import ID_KEY
from src.store.userStore import UserStore

class FormStoreTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.client = MongoClient('localhost', 27017)
        self.client.drop_database('test')
        dbConn = DBConnection('test')
        self.formNodes = self.client.test.formNodes
        self.storeFactory = StoreFactory(dbConn, '/TalenticaWorkspace/TLabs/graphite-python/RNA/src/store/users')
        self.publicFormStore = self.storeFactory.publicFormStore

        self.userStore = UserStore(dbConn)
        self.user1 = self.userStore.createUserNode("prasu05", "p$5%t")
        self.user2 = self.userStore.createUserNode("prasu06", "^%sf$")
        self.userFormStore = self.storeFactory.getPrivateFormStore(self.user1)

    def setUp(self):
        self.__clean__()

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.__clean__()

    @classmethod
    def tearDownClass(self):
        self.client = MongoClient('localhost', 27017)
        self.client.drop_database('test')


    def testCreatePublicFormNode(self):
        formNode = self.publicFormStore.createFormNode("https://pypi.python.org/pypi/YURL/0.12")
        self.assertNotEqual(None, self.publicFormStore.getFormNode(formNode[ID_KEY]))

    def testCreatePrivateFormNode(self):
        formNode = self.userFormStore.createPrivateFormNode("https://pypi.python.org/pypi/YURsL/0.123")
        self.assertEqual(None, self.publicFormStore.getFormNode(formNode[ID_KEY]))
        self.assertNotEqual(None, self.userFormStore.getPrivateFormNode(formNode[ID_KEY]))

    def __clean__(self):
        self.client.test.fromNodes.remove()
        
if __name__ == "__main__":
    unittest.main()
