'''
Created on Aug 6, 2014

@author: sushant pradhan
'''
from pymongo.mongo_client import MongoClient
from src.store.StoreFactory import StoreFactory
from src.store.dbConnection import DBConnection
import unittest
from src.store.constants import ID_KEY, DOMAIN_KEY, FORM_KEY, NAME_NODE_ID_KEY
from src.store.userStore import UserStore

class VerbStoreTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.client = MongoClient('localhost', 27017)
        self.client.drop_database('test')
        dbConn = DBConnection('test')
        self.formNodes = self.client.test.formNodes
        self.verbNodes = self.client.test.verbNodes
        self.classNodes = self.client.test.classNodes
        self.nameNodes = self.client.test.nameNodes
        self.stringNodes = self.client.test.stringNodes

        self.storeFactory = StoreFactory(dbConn, '/TalenticaWorkspace/TLabs/graphite-python/RNA/src/store/users')
        self.publicFormStore = self.storeFactory.publicFormStore
        self.publicVerbStore = self.storeFactory.publicVerbStore
        self.publicClassStore = self.storeFactory.publicClassStore
        
        self.userStore = UserStore(dbConn)
        self.user1 = self.userStore.createUserNode("prasu05", "p$5%t")
        self.user2 = self.userStore.createUserNode("prasu06", "^%sf$")
        self.userVerbStore = self.storeFactory.getPrivateVerbStore(self.user1)

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

    def testCreateVerbNode(self):
        verbNode = self.publicVerbStore.createVerbNode("email", self.classNode)
        self.assertNotEqual(self.publicVerbStore.getVerbNode(verbNode[ID_KEY]), None)
    
    def testAddDomain(self):
        verbNode = self.publicVerbStore.createVerbNode("email", self.classNode)
        classNode = self.publicClassStore.createClassNode("Article")
        self.assertEqual(1, len(verbNode[DOMAIN_KEY]))
        self.assertEqual(self.publicVerbStore.addDomain(verbNode, classNode), True)
        self.assertEqual(2, len(self.publicVerbStore.getVerbNode(verbNode[ID_KEY])[DOMAIN_KEY]))

    def testAddForm(self):
        formNode = self.publicFormStore.createFormNode("https://pypi.python.org/pypi/YURL/0.12")
        verbNode = self.publicVerbStore.createVerbNode("email", self.classNode)
        self.assertEqual(False, verbNode.has_key(FORM_KEY))
        self.assertEqual(self.publicVerbStore.addForm(verbNode, formNode), True)
        self.assertEqual(True, self.publicVerbStore.getVerbNode(verbNode[ID_KEY]).has_key(FORM_KEY))

    def testCreatePrivateVerbNode(self):
        privateVerb = self.userVerbStore.createPrivateVerbNode("email")
        self.assertNotEqual(self.userVerbStore.getPrivateVerbNode(privateVerb[NAME_NODE_ID_KEY], privateVerb[ID_KEY]), None)

    def testAddPrivateDomain(self):
        privateVerb = self.userVerbStore.createPrivateVerbNode("email")
        classNode = self.publicClassStore.createClassNode("Article")
        self.assertEqual(self.userVerbStore.addPrivateDomain(privateVerb, classNode), True)
        self.assertNotEqual(self.userVerbStore.getPrivateVerbNode(privateVerb[NAME_NODE_ID_KEY], privateVerb[ID_KEY]), None)

    def testAddPrivateForm(self):
        privateVerb = self.userVerbStore.createPrivateVerbNode("email")
        formNode = self.publicFormStore.createFormNode("https://pypi.python.org/pypi/YURL/0.12")
        self.assertEqual(self.userVerbStore.addPrivateForm(privateVerb, formNode), True)
        self.assertNotEqual(self.userVerbStore.getPrivateVerbNode(privateVerb[NAME_NODE_ID_KEY], privateVerb[ID_KEY]), None)
    
    def testSharePrivateVerbNode(self):
        privateVerb = self.userVerbStore.createPrivateVerbNode("email")
        classNode = self.publicClassStore.createClassNode("Article")
        formNode = self.publicFormStore.createFormNode("https://pypi.python.org/pypi/YURL/0.12")
        self.assertEqual(self.userVerbStore.addPrivateDomain(privateVerb, classNode), True)
        self.assertEqual(self.userVerbStore.addPrivateForm(privateVerb, formNode), True)
        self.assertEqual(self.userVerbStore.sharePrivateVerbNode(privateVerb, self.user2), True)
        user2VerbStore = self.storeFactory.getPrivateVerbStore(self.user2)
        print user2VerbStore.getPrivateVerbNode(privateVerb[NAME_NODE_ID_KEY], privateVerb[ID_KEY])

    def __clean__(self):
        self.client.test.formNodes.remove()
        self.client.test.verbNodes.remove()
        self.client.test.classNodes.remove()
        self.client.test.nameNodes.remove()
        self.client.test.stringNodes.remove()

if __name__ == "__main__":
    unittest.main()
