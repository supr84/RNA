'''
Created on Aug 8, 2014

@author: sushant pradhan
'''
from src.store.classStore import ClassStore
from src.store.constants import USER_NAME_KEY, USER_SECRET_KEY, CLASS_STORE_TYPE, \
    PROP_STORE_TYPE
from src.store.propertyStore import PropertyStore
import imp

class StoreFactory(object):
    '''
    classdocs
    '''
    def __loadStore__(self, userNode, storeType):
            privateClassStoreSource = "%s/private%s.py" % (self.privateStoreSourcePath, storeType)
            file = open(privateClassStoreSource)
            contents = file.read()
            userStoreSource = contents.replace('__FACTORY__USER__NAME__PLACE__HOLDER__', userNode[USER_NAME_KEY])
            userStoreSource = userStoreSource.replace('__FACTORY__USER__SECRET__PLACE__HOLDER__', userNode[USER_SECRET_KEY])
            userClassStoreSource = "%s/%s%s.py" %  (self.privateStoreSourcePath,userNode[USER_NAME_KEY], storeType)
            userClassStoreSourceFile = open(userClassStoreSource,'w')
            userClassStoreSourceFile.write(userStoreSource)
            userClassStoreSourceFile.close()
            imp.load_source('uprvtclz', userClassStoreSource)
            className = '%s%s' % (userNode[USER_NAME_KEY], storeType)
            from uprvtclz import *
            ps = locals()[className](self.dbConn, userNode[USER_NAME_KEY])
            return ps

    def __loadPrivateStore__(self, userNode):
        
        
        pcs = self.__loadStore__(userNode, CLASS_STORE_TYPE)
        pps = self.__loadStore__(userNode, PROP_STORE_TYPE)
        pcs.__setattr__('privatePropStore', pps)
        pps.__setattr__('privateClassStore', pcs)
#        
        self.userClassStores[userNode[USER_NAME_KEY]] = pcs
        self.userPropStores[userNode[USER_NAME_KEY]] = pps

    def __init__(self, dbConn, sourcePath):
        '''
        Constructor
        '''
        self.dbConn = dbConn
        self.publicClassStore = ClassStore(dbConn)
        self.publicPropertyStore = PropertyStore(dbConn)
        self.publicClassStore.setPropStore(self.publicPropertyStore)
        self.publicPropertyStore.setClassStore(self.publicClassStore)
        self.privateStoreSourcePath = sourcePath
        self.userClassStores = {}
        self.userPropStores = {}
        self.userObjStores = {}
        
    def getPublicObjectStore(self):
        pass
    
    def getPrivateClassStore(self, userNode):
        if not self.userClassStores.has_key(userNode[USER_NAME_KEY]):
            self.__loadPrivateStore__(userNode)
        return self.userClassStores.get(userNode[USER_NAME_KEY])

    def getPrivatePropertyStore(self, userNode):
        if not self.userPropStores.has_key(userNode[USER_NAME_KEY]):
            self.__loadPrivateStore__(userNode)
        return self.userPropStores.get(userNode[USER_NAME_KEY])

    def getPrivateObjectStore(self, userNode):
        return self.userObjStores.get(userNode[USER_NAME_KEY])
