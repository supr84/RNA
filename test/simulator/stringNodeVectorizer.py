'''
Created on Aug 5, 2014

@author: sushant pradhan
'''
from src.store.stringStore import StringStore
from src.store.dbConnection import DBConnection
from bson.objectid import ObjectId
import os
DIR = '/TalenticaWorkspace/TLabs/graphite-python/RNA/test/simulator/data/englishwords'

class StringNodeVectorizer(object):
    '''
    classdocs
    '''
    def __init__(self, dbConn):
        '''
        Constructor
        '''
        self.dbConn = dbConn
        self.stringStore = StringStore(dbConn)

    def vectorizeString(self, stringNode):
        vector = ()
        if None != stringNode and stringNode.has_key('name'):
            name = stringNode['name'].lower()
            vector += (len(name),)
            for i in range(0,len(name)):
                vector += (ord(name[i]),)
            vector += (str(stringNode['_id']),)
            return vector
        else:
            return None

if __name__ == '__main__':

    fileList = os.listdir(DIR)
    dbConn = DBConnection(None)
    snv = StringNodeVectorizer(dbConn)
    outputFile = open('vectors','w')
    for file in fileList:
        filePath = "%s/%s" %(DIR, file)
        with open(filePath) as fp:
            for line in fp:
                name = line.replace('\n','')
                nameNode = {'name':name, '_id':name}
                outputFile.write('%s\n' % str(snv.vectorizeString(nameNode)) )
    outputFile.close()
