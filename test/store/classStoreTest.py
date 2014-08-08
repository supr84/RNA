'''
Created on Aug 6, 2014

@author: sushant pradhan
'''
from pymongo.mongo_client import MongoClient
from src.store.StoreFactory import StoreFactory
from src.store.constants import ID_KEY, NAME_NODE_ID_KEY
from src.store.dbConnection import DBConnection
from src.store.userStore import USerStore
import unittest


class CLassStoreTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.client = MongoClient('localhost', 27017)
        self.client.drop_database('test')
        dbConn = DBConnection('test')
        self.storeFactory = StoreFactory(dbConn, '/TalenticaWorkspace/TLabs/graphite-python/RNA/src/store/users')
        self.publicClassStore = self.storeFactory.publicClassStore
        self.publicPropStore = self.storeFactory.publicPropertyStore
        self.userStore = USerStore(dbConn)
        self.user1 = self.userStore.createUserNode("prasu05", "p$5%t")
        self.user2 = self.userStore.createUserNode("prasu06", "^%sf$")
        userClassStore = self.storeFactory.getPrivateClassStore(self.user1)
        self.privateDomainClass = userClassStore.createPrivateClassNode('privateDomainClass')
        self.publicDomainClass = self.publicClassStore.createClassNode("publicDomainClass")
        self.privateRangeClass = userClassStore.createPrivateClassNode('privateRangeClass')
        self.publicRangeClass = self.publicClassStore.createClassNode("publicRangeClass")

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.client.test.propNodes.remove()
        self.client.test.classNodes.remove()

    @classmethod
    def tearDownClass(self):
        self.client = MongoClient('localhost', 27017)
        self.client.drop_database('test')

    def testCreatePublicAndGetPublicNode(self):
        publicClass = self.publicClassStore.createClassNode("publicClass")
        self.assertEqual(publicClass, self.publicClassStore.getClassNode(publicClass[ID_KEY]))

    def testCreatePublicAndGetPrivateNode(self):
        publicClass = self.publicClassStore.createClassNode("publicClass")
        userClassStore = self.storeFactory.getPrivateClassStore(self.user1)
        publicClassviaPrivateStore = userClassStore.getPrivateClassNode(publicClass[NAME_NODE_ID_KEY], publicClass[ID_KEY])
        self.assertEqual(publicClass, publicClassviaPrivateStore)

    def testCreatePrivateAndGetPublicNode(self):
        userClassStore = self.storeFactory.getPrivateClassStore(self.user1)
        privateClass = userClassStore.createPrivateClassNode('privateClass')
        privateClzViaPublicStore = self.publicClassStore.getClassNode(privateClass[ID_KEY])
        self.assertEqual(privateClzViaPublicStore, None)

    def testCreatePrivateAndGetPrivateNode(self):
        userClassStore = self.storeFactory.getPrivateClassStore(self.user1)
        privateClass = userClassStore.createPrivateClassNode('privateClass')
        privateClzViaPrivateStore = userClassStore.getPrivateClassNode(privateClass[NAME_NODE_ID_KEY], privateClass[ID_KEY])
        self.assertEqual(privateClass, privateClzViaPrivateStore)

    def testSharePublicClassNode(self):
        user1ClassStore = self.storeFactory.getPrivateClassStore(self.user1)
        publicClass = self.publicClassStore.createClassNode("publicClass")
        self.assertEqual(user1ClassStore.sharePrivateClassNode(publicClass, None), False)

    def testSharePrivateClassNodeByOwnerWithNoProperty(self):
        user1ClassStore = self.storeFactory.getPrivateClassStore(self.user1)
        user2ClassStore = self.storeFactory.getPrivateClassStore(self.user2)
        privateClass = user1ClassStore.createPrivateClassNode('privateClass')
        self.assertEqual(user2ClassStore.getPrivateClassNode(privateClass[NAME_NODE_ID_KEY], privateClass[ID_KEY]), None)
        self.assertEqual(user1ClassStore.sharePrivateClassNode(privateClass, self.user2), True)
        self.assertNotEqual(user2ClassStore.getPrivateClassNode(privateClass[NAME_NODE_ID_KEY], privateClass[ID_KEY]), None)

    def testSharePrivateClassNodeByOwnerWithProperties(self):
        user1ClassStore = self.storeFactory.getPrivateClassStore(self.user1)
        user1PropStore = self.storeFactory.getPrivatePropertyStore(self.user1)
        user2ClassStore = self.storeFactory.getPrivateClassStore(self.user2)
        privateDomain = user1ClassStore.createPrivateClassNode('privateDomainClass')
        privateRange = user1ClassStore.createPrivateClassNode('privateRangeClass')
        user1PropStore.createPrivatePropertyNode('privateProp3', privateDomain, privateRange)
        self.assertEqual(user2ClassStore.getPrivateClassNode(privateDomain[NAME_NODE_ID_KEY], privateDomain[ID_KEY]), None)
        self.assertEqual(user1ClassStore.sharePrivateClassNode(privateDomain, self.user2), True)
        self.assertNotEqual(user2ClassStore.getPrivateClassNode(privateDomain[NAME_NODE_ID_KEY], privateDomain[ID_KEY]), None)

    def testSharePrivateClassNodeByNonOwner(self):
        user1ClassStore = self.storeFactory.getPrivateClassStore(self.user1)
        user2ClassStore = self.storeFactory.getPrivateClassStore(self.user2)
        privateClass = user1ClassStore.createPrivateClassNode('privateClass')
        self.assertEqual(user2ClassStore.sharePrivateClassNode(privateClass, None), False)

    def testAdd_PrivateDomain_PrivateClass(self):
        user1ClassStore = self.storeFactory.getPrivateClassStore(self.user1)
        user1PropStore = self.storeFactory.getPrivatePropertyStore(self.user1)
        user = user1ClassStore.createPrivateClassNode('user')
        place = user1ClassStore.createPrivateClassNode('place')
        institution = user1ClassStore.createPrivateClassNode('institution')

        location = user1PropStore.createPrivatePropertyNode('location', user, place)
        beforeAdding = user1ClassStore.getPrivateClassNode(institution[NAME_NODE_ID_KEY], institution[ID_KEY])
        self.assertEqual(beforeAdding.has_key('p$5%tdomain'), False)
        self.assertEqual(user1ClassStore.addPrivateDomain(institution, location),True)
        afterAdding = user1ClassStore.getPrivateClassNode(institution[NAME_NODE_ID_KEY], institution[ID_KEY])
        self.assertEqual(afterAdding.has_key('p$5%tdomain'), True)

    def testAdd_PrivateDomain_PublicClass(self):
        user1ClassStore = self.storeFactory.getPrivateClassStore(self.user1)
        user1PropStore = self.storeFactory.getPrivatePropertyStore(self.user1)
        user = user1ClassStore.createPrivateClassNode('user')
        place = user1ClassStore.createPrivateClassNode('place')
        institution = self.publicClassStore.createClassNode('institution')

        location = user1PropStore.createPrivatePropertyNode('location', user, place)
        beforeAdding = user1ClassStore.getPrivateClassNode(institution[NAME_NODE_ID_KEY], institution[ID_KEY])
        self.assertEqual(beforeAdding.has_key('p$5%tdomain'), False)
        self.assertEqual(user1ClassStore.addPrivateDomain(institution, location),True)
        afterAdding = user1ClassStore.getPrivateClassNode(institution[NAME_NODE_ID_KEY], institution[ID_KEY])
        self.assertEqual(afterAdding.has_key('p$5%tdomain'), True)

    def testAdd_PublicDomain_PrivateClass(self):
        user1ClassStore = self.storeFactory.getPrivateClassStore(self.user1)
        user = self.publicClassStore.createClassNode('user')
        place = self.publicClassStore.createClassNode('place')
        institution = user1ClassStore.createPrivateClassNode('institution')
        
        location = self.publicPropStore.createPropertyNode('location', user, place)
        beforeAdding = user1ClassStore.getPrivateClassNode(institution[NAME_NODE_ID_KEY], institution[ID_KEY])
        self.assertEqual(beforeAdding.has_key('p$5%tdomain'), False)
        self.assertEqual(user1ClassStore.addPrivateDomain(institution, location),True)
        afterAdding = user1ClassStore.getPrivateClassNode(institution[NAME_NODE_ID_KEY], institution[ID_KEY])
        self.assertEqual(afterAdding.has_key('p$5%tdomain'), True)

    def testAdd_PublicDomain_PublicClass(self):
        user1ClassStore = self.storeFactory.getPrivateClassStore(self.user1)
        user = self.publicClassStore.createClassNode('user')
        place = self.publicClassStore.createClassNode('place')
        institution = self.publicClassStore.createClassNode('institution')
        
        location = self.publicPropStore.createPropertyNode('location', user, place)
        beforeAdding = user1ClassStore.getPrivateClassNode(institution[NAME_NODE_ID_KEY], institution[ID_KEY])
        self.assertEqual(beforeAdding.has_key('p$5%tdomain'), False)
        self.assertEqual(user1ClassStore.addPrivateDomain(institution, location),True)
        afterAdding = user1ClassStore.getPrivateClassNode(institution[NAME_NODE_ID_KEY], institution[ID_KEY])
        self.assertEqual(afterAdding.has_key('p$5%tdomain'), True)

    def testAddValLink(self):
        pass

if __name__ == "__main__":
    unittest.main()