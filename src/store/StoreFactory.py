'''
Created on Aug 8, 2014

@author: sushant pradhan
'''
from src.store.classStore import ClassStore
from src.store.constants import USER_NAME_KEY, USER_SECRET_KEY, CLASS_STORE_TYPE, \
    PROP_STORE_TYPE, PUBLIC_PROP_STORE, PUBLIC_CLASS_STORE, PRIVATE_PROP_STORE, \
    PRIVATE_CLASS_STORE, PUBLIC_FORM_STORE, VERB_STORE_TYPE, FORM_STORE_TYPE,\
    PRIVATE_FORM_STORE, OBJECT_STORE_TYPE
from src.store.propertyStore import PropertyStore
import imp
from src.store.formStore import FormStore
from src.store.verbStore import VerbStore
from src.store.objectStore import ObjectStore

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
        pvs = self.__loadStore__(userNode, VERB_STORE_TYPE)
        pfs = self.__loadStore__(userNode, FORM_STORE_TYPE)
        pos = self.__loadStore__(userNode, OBJECT_STORE_TYPE)

        pcs.__setattr__(PRIVATE_PROP_STORE, pps)
        pos.__setattr__(PRIVATE_PROP_STORE, pps)
        pps.__setattr__(PRIVATE_CLASS_STORE, pcs)
        pvs.__setattr__(PRIVATE_CLASS_STORE, pcs)
        pos.__setattr__(PRIVATE_CLASS_STORE, pcs)
        pvs.__setattr__(PRIVATE_FORM_STORE, pfs)
#        
        self.userClassStores[userNode[USER_NAME_KEY]] = pcs
        self.userPropStores[userNode[USER_NAME_KEY]] = pps
        self.userVerbStores[userNode[USER_NAME_KEY]] = pvs
        self.userFormStores[userNode[USER_NAME_KEY]] = pfs
        self.userObjStores[userNode[USER_NAME_KEY]] = pos

    def __init__(self, dbConn, sourcePath):
        '''
        Constructor
        '''
        self.dbConn = dbConn
        self.publicVerbStore = VerbStore(dbConn)
        self.publicFormStore = FormStore(dbConn)
        self.publicClassStore = ClassStore(dbConn)
        self.publicPropertyStore = PropertyStore(dbConn)
        self.publicObjectStore = ObjectStore(dbConn)

        self.publicClassStore.__setattr__(PUBLIC_PROP_STORE, self.publicPropertyStore)
        self.publicObjectStore.__setattr__(PUBLIC_PROP_STORE, self.publicPropertyStore)
        self.publicPropertyStore.__setattr__(PUBLIC_CLASS_STORE, self.publicClassStore)
        self.publicVerbStore.__setattr__(PUBLIC_CLASS_STORE, self.publicClassStore)
        self.publicObjectStore.__setattr__(PUBLIC_CLASS_STORE, self.publicClassStore)
        self.publicVerbStore.__setattr__(PUBLIC_FORM_STORE, self.publicFormStore)

        self.privateStoreSourcePath = sourcePath
        self.userClassStores = {}
        self.userPropStores = {}
        self.userObjStores = {}
        self.userVerbStores = {}
        self.userFormStores = {}

    def getPrivateClassStore(self, userNode):
        if not self.userClassStores.has_key(userNode[USER_NAME_KEY]):
            self.__loadPrivateStore__(userNode)
        return self.userClassStores.get(userNode[USER_NAME_KEY])

    def getPrivatePropertyStore(self, userNode):
        if not self.userPropStores.has_key(userNode[USER_NAME_KEY]):
            self.__loadPrivateStore__(userNode)
        return self.userPropStores.get(userNode[USER_NAME_KEY])

    def getPrivateVerbStore(self, userNode):
        if not self.userVerbStores.has_key(userNode[USER_NAME_KEY]):
            self.__loadPrivateStore__(userNode)
        return self.userVerbStores.get(userNode[USER_NAME_KEY])

    def getPrivateFormStore(self, userNode):
        if not self.userFormStores.has_key(userNode[USER_NAME_KEY]):
            self.__loadPrivateStore__(userNode)
        return self.userFormStores.get(userNode[USER_NAME_KEY])

    def getPrivateObjectStore(self, userNode):
        if not self.userObjStores.has_key(userNode[USER_NAME_KEY]):
            self.__loadPrivateStore__(userNode)
        return self.userObjStores.get(userNode[USER_NAME_KEY])
