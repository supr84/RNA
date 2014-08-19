'''
Created on Aug 6, 2014

@author: sushant pradhan
'''
from pymongo.mongo_client import MongoClient
from src.store.StoreFactory import StoreFactory
from src.store.constants import ID_KEY, NAME_NODE_ID_KEY
from src.store.dbConnection import DBConnection
from src.store.userStore import UserStore
import unittest

class PropStoreTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.client = MongoClient('localhost', 27017)
        self.client.drop_database('test')
        dbConn = DBConnection('test')
        self.classNodes = self.client.test.classNodes
        self.propNodes = self.client.test.propNodes
        self.storeFactory = StoreFactory(dbConn, '/TalenticaWorkspace/TLabs/graphite-python/RNA/src/store/users')
        self.publicClassStore = self.storeFactory.publicClassStore
        self.publicPropStore = self.storeFactory.publicPropertyStore
        self.userStore = UserStore(dbConn)
        self.user1 = self.userStore.createUserNode("prasu05", "p$5%t")
        self.user2 = self.userStore.createUserNode("prasu06", "^%sf$")

    def setUp(self):
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

    def __classFactory__(self, privateDomain=False, privateRange=False):
        domainClass = None
        rangeClass = None
        if privateDomain:
            domainClass = self.privateDomainClass
        else:
            domainClass = self.publicDomainClass
        if privateRange:
            rangeClass = self.privateRangeClass
        else:
            rangeClass = self.publicRangeClass
        return (domainClass, rangeClass)

    def testCreatePublicAndGetPublicNode(self):

        def testCreate_PublicDomain_PublicProperty_PublicRange():
            (publicDomain, publicRange) = self.__classFactory__(False, False)
            publicProp = self.publicPropStore.createPropertyNode('publilcProp1', publicDomain, publicRange)
            print publicProp
            self.assertEqual(publicProp, self.publicPropStore.getPropertyNode(publicProp[ID_KEY]))

        def testCreate_PublicDomain_PublicProperty_PrivateRange():
            (publicDomain, privateRange) = self.__classFactory__(False, True)
            publicProp = self.publicPropStore.createPropertyNode('publilcProp2', publicDomain, privateRange)
            self.assertEqual(publicProp, None)

        def testCreate_PrivateDomain_PublicProperty_PublicRange():
            (privateDomain, publicRange) = self.__classFactory__(True, False)
            publicProp = self.publicPropStore.createPropertyNode('publilcProp3', privateDomain, publicRange)
            self.assertEqual(publicProp, None)

        def testCreate_PrivateDomain_PublicProperty_PrivateRange():
            (privateDomain, privateRange) = self.__classFactory__(True, True)
            publicProp = self.publicPropStore.createPropertyNode('publilcProp4', privateDomain, privateRange)
            self.assertEqual(publicProp, None)

        testCreate_PublicDomain_PublicProperty_PublicRange()
        testCreate_PublicDomain_PublicProperty_PrivateRange()
        testCreate_PrivateDomain_PublicProperty_PublicRange()
        testCreate_PrivateDomain_PublicProperty_PrivateRange()
#
    def testCreatePublicAndGetPrivateNode(self):
        def testCreate_PublicDomain_PublicProperty_PublicRange():
            userPropStore = self.storeFactory.getPrivatePropertyStore(self.user1)
            (publicDomain, publicRange) = self.__classFactory__(False, False)
            publicProp = self.publicPropStore.createPropertyNode('publilcProp', publicDomain, publicRange)
            self.assertEqual(publicProp, userPropStore.getPrivatePropertyNode(publicProp[ID_KEY]))

        testCreate_PublicDomain_PublicProperty_PublicRange()

    def testCreatePrivateAndGetPublicNode(self):
        userPropStore = self.storeFactory.getPrivatePropertyStore(self.user1)
        userClassStore = self.storeFactory.getPrivateClassStore(self.user1)
        def testCreate_PublicDomain_PrivateProperty_PublicRange():
            (publicDomain, publicRange) = self.__classFactory__(False, False)
            privateProp = userPropStore.createPrivatePropertyNode('privateProp', publicDomain, publicRange)
            self.assertEqual(self.publicPropStore.getPropertyNode(privateProp.get(ID_KEY)), None)
            pcn = userClassStore.getPrivateClassNode(publicDomain[ID_KEY])
            self.assertEqual(pcn.has_key('p$5%tdomain'), True)
            pub = self.publicClassStore.getClassNode(publicDomain[ID_KEY])
            self.assertEqual(pub.has_key('p$5%tdomain'), False)
            self.assertEqual(pub.has_key('domain'), False)

        def testCreate_PublicDomain_PrivateProperty_PrivateRange():
            (publicDomain, privateRange) = self.__classFactory__(False, True)
            privateProp = userPropStore.createPrivatePropertyNode('privateProp2', publicDomain, privateRange)
            self.assertEqual(self.publicPropStore.getPropertyNode(privateProp.get(ID_KEY)), None)

            pr = userClassStore.getPrivateClassNode(privateRange[ID_KEY])
            self.assertEqual(pr.has_key('p$5%trange'), True)
            self.assertEqual(privateProp[ID_KEY] in pr.get('p$5%trange'), True)
            self.assertEqual(pr.has_key('range'), False)

            pd = userClassStore.getPrivateClassNode(publicDomain[ID_KEY])
            self.assertEqual(pd.has_key('p$5%tdomain'), True)
            self.assertEqual(privateProp[ID_KEY] in pd.get('p$5%tdomain'), True)
            self.assertEqual(pd.has_key('domain'), False)

        def testCreate_PrivateDomain_PrivateProperty_PublicRange():
            (privateDomain, publicRange) = self.__classFactory__(True, False)
            privateProp = userPropStore.createPrivatePropertyNode('privateProp3', privateDomain, publicRange)
            self.assertEqual(self.publicPropStore.getPropertyNode(privateProp.get(ID_KEY)), None)

            pr = userClassStore.getPrivateClassNode(publicRange[ID_KEY])
            self.assertEqual(pr.has_key('p$5%trange'), True)
            self.assertEqual(privateProp[ID_KEY] in pr.get('p$5%trange'), True)
            self.assertEqual(pr.has_key('range'), False)

            pd = userClassStore.getPrivateClassNode(privateDomain[ID_KEY])
            self.assertEqual(pd.has_key('p$5%tdomain'), True)
            self.assertEqual(privateProp[ID_KEY] in pd.get('p$5%tdomain'), True)
            self.assertEqual(pd.has_key('domain'), False)

        def testCreate_PrivateDomain_PrivateProperty_PrivateRange():
            (privateDomain, privateRange) = self.__classFactory__(True, True)
            privateProp = userPropStore.createPrivatePropertyNode('privateProp4', privateDomain, privateRange)
            self.assertEqual(self.publicPropStore.getPropertyNode(privateProp.get(ID_KEY)), None)

            pr = userClassStore.getPrivateClassNode(privateRange[ID_KEY])
            self.assertEqual(pr.has_key('p$5%trange'), True)
            self.assertEqual(privateProp[ID_KEY] in pr.get('p$5%trange'), True)
            self.assertEqual(pr.has_key('range'), False)

            pd = userClassStore.getPrivateClassNode(privateDomain[ID_KEY])
            self.assertEqual(pd.has_key('p$5%tdomain'), True)
            self.assertEqual(privateProp[ID_KEY] in pd.get('p$5%tdomain'), True)
            self.assertEqual(pd.has_key('domain'), False)

        testCreate_PublicDomain_PrivateProperty_PublicRange()
        testCreate_PublicDomain_PrivateProperty_PrivateRange()
        testCreate_PrivateDomain_PrivateProperty_PublicRange()
        testCreate_PrivateDomain_PrivateProperty_PrivateRange()

    def testCreatePrivateAndGetPrivateNode(self):
        userPropStore = self.storeFactory.getPrivatePropertyStore(self.user1)
        def testCreate_PublicDomain_PrivateProperty_PublicRange():
            (publicDomain, publicRange) = self.__classFactory__(False, False)
            privateProp = userPropStore.createPrivatePropertyNode('privateProp', publicDomain, publicRange)
            get =  userPropStore.getPrivatePropertyNode(privateProp[ID_KEY])
            self.assertEqual(get, privateProp)

        def testCreate_PublicDomain_PrivateProperty_PrivateRange():
            (publicDomain, privateRange) = self.__classFactory__(False, True)
            privateProp = userPropStore.createPrivatePropertyNode('privateProp2', publicDomain, privateRange)
            get =  userPropStore.getPrivatePropertyNode(privateProp[ID_KEY])
            self.assertEqual(get, privateProp)

        def testCreate_PrivateDomain_PrivateProperty_PublicRange():
            (privateDomain, publicRange) = self.__classFactory__(True, False)
            privateProp = userPropStore.createPrivatePropertyNode('privateProp3', privateDomain, publicRange)
            get =  userPropStore.getPrivatePropertyNode(privateProp[ID_KEY])
            self.assertEqual(get, privateProp)

        def testCreate_PrivateDomain_PrivateProperty_PrivateRange():
            (privateDomain, privateRange) = self.__classFactory__(True, True)
            privateProp = userPropStore.createPrivatePropertyNode('privateProp4', privateDomain, privateRange)
            get =  userPropStore.getPrivatePropertyNode(privateProp[ID_KEY])
            self.assertEqual(get, privateProp)

        testCreate_PublicDomain_PrivateProperty_PublicRange()
        testCreate_PublicDomain_PrivateProperty_PrivateRange()
        testCreate_PrivateDomain_PrivateProperty_PublicRange()
        testCreate_PrivateDomain_PrivateProperty_PrivateRange()

    def testSharePrivatePropertyNodeByOwner(self):
        user1PropStore = self.storeFactory.getPrivatePropertyStore(self.user1)
        user2PropStore = self.storeFactory.getPrivatePropertyStore(self.user2)
        (publicDomain, privateRange) = self.__classFactory__(False, True)
        privateProp = user1PropStore.createPrivatePropertyNode('privateProp2', publicDomain, privateRange)
        self.assertEqual(user2PropStore.getPrivatePropertyNode(privateProp[ID_KEY]), None)
        self.assertEqual(user1PropStore.sharePrivatePropertyNode(privateProp, self.user2), True)
        self.assertNotEqual(user2PropStore.getPrivatePropertyNode(privateProp[ID_KEY]), None)

    def testSharePrivatePropertyNodeByNonOwner(self):
        user1PropStore = self.storeFactory.getPrivatePropertyStore(self.user1)
        user2PropStore = self.storeFactory.getPrivatePropertyStore(self.user2)
        (publicDomain, privateRange) = self.__classFactory__(False, True)
        privateProp = user1PropStore.createPrivatePropertyNode('privateProp2', publicDomain, privateRange)
        self.assertEqual(user2PropStore.sharePrivatePropertyNode(privateProp, None), False)

    def testSharePublicPropertyNode(self):
        userPropStore = self.storeFactory.getPrivatePropertyStore(self.user1)
        (publicDomain, publicRange) = self.__classFactory__(False, False)
        publicProp = self.publicPropStore.createPropertyNode('publilcProp1', publicDomain, publicRange)
        self.assertEqual(userPropStore.sharePrivatePropertyNode(publicProp, self.user2), False)

    def testAdd_PublicDomain_PublicProperty(self):
        userPropStore = self.storeFactory.getPrivatePropertyStore(self.user1)
        user = self.publicClassStore.createClassNode('user')
        place = self.publicClassStore.createClassNode('place')
        institution = self.publicClassStore.createClassNode('institution')

        location = self.publicPropStore.createPropertyNode('location', user, place)
        beforeAdding = userPropStore.getPrivatePropertyNode(location[ID_KEY])
        self.assertEqual(beforeAdding.has_key('p$5%tdomain'), False)
        self.assertEqual(userPropStore.addPrivateDomain(location, institution), True)
        afterAdding = userPropStore.getPrivatePropertyNode(location[ID_KEY])
        self.assertEqual(afterAdding.has_key('p$5%tdomain'), True)

    def testAdd_PublicDomain_PrivateProperty(self):
        user1ClassStore = self.storeFactory.getPrivateClassStore(self.user1)
        user1PropStore = self.storeFactory.getPrivatePropertyStore(self.user1)
        user = user1ClassStore.createPrivateClassNode('user')
        place = user1ClassStore.createPrivateClassNode('place')
        institution = self.publicClassStore.createClassNode('institution')

        location = user1PropStore.createPrivatePropertyNode('location', user, place)

        beforeAdding = user1PropStore.getPrivatePropertyNode(location[ID_KEY])
        self.assertEqual(institution[ID_KEY] in beforeAdding.get('p$5%tdomain'), False)
        self.assertEqual(user1PropStore.addPrivateDomain(location, institution), True)
        afterAdding = user1PropStore.getPrivatePropertyNode(location[ID_KEY])
        self.assertEqual(institution[ID_KEY] in afterAdding.get('p$5%tdomain'), True)

    def testAdd_PrivateDomain_PublicProperty(self):
        user1ClassStore = self.storeFactory.getPrivateClassStore(self.user1)
        user1PropStore = self.storeFactory.getPrivatePropertyStore(self.user1)
        user = self.publicClassStore.createClassNode('user')
        place = self.publicClassStore.createClassNode('place')
        institution = user1ClassStore.createPrivateClassNode('institution')

        location = self.publicPropStore.createPropertyNode('location', user, place)
        beforeAdding = user1PropStore.getPrivatePropertyNode(location[ID_KEY])
        self.assertEqual(beforeAdding.has_key('p$5%tdomain'), False)
        self.assertEqual(user1PropStore.addPrivateDomain(location, institution), True)
        afterAdding = user1PropStore.getPrivatePropertyNode(location[ID_KEY])
        self.assertEqual(afterAdding.has_key('p$5%tdomain'), True)

    def testAdd_PrivateDomain_PrivateProperty(self):
        user1ClassStore = self.storeFactory.getPrivateClassStore(self.user1)
        user1PropStore = self.storeFactory.getPrivatePropertyStore(self.user1)
        user = user1ClassStore.createPrivateClassNode('user')
        place = user1ClassStore.createPrivateClassNode('place')
        institution = user1ClassStore.createPrivateClassNode('institution')

        location = user1PropStore.createPrivatePropertyNode('location', user, place)
        beforeAdding = user1PropStore.getPrivatePropertyNode(location[ID_KEY])
        self.assertEqual(institution[ID_KEY] in beforeAdding.get('p$5%tdomain'), False)
        self.assertEqual(user1PropStore.addPrivateDomain(location, institution), True)
        afterAdding = user1PropStore.getPrivatePropertyNode(location[ID_KEY])
        self.assertEqual(institution[ID_KEY] in afterAdding.get('p$5%tdomain'), True)

if __name__ == "__main__":
    unittest.main()
