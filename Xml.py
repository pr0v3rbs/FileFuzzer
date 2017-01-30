from xml.etree.ElementTree import *
from random import *
import ast

class Xml():
    def __init__(self):
        self.mutationList = []
        self.targetFile = ''
        self.data = ''
        self.mData = ''
        self.minimizeIdx = 0
        self.minimizeInfo = []
        self.mutationNumber = ['0', '0.0', '-1', '-1.0', '1', '1.0', '100', '100.0', '1000', '1000.0', '1023', '1023.0', '1024', '1024.0', '1025', '1025.0', '4294967296', '4294967296.0', '4294967295', '4294967295.0', '4294967297', '4294967297.0', '2147483648', '2147483648.0', '2147483647', '2147483647.0', '2147483649', '2147483649.0']

    def getTagName_(self, idx):
        tag_name = ''
        while self.data[idx] not in [' ', '>', '/']:
            tag_name += self.data[idx]
            idx += 1
        return tag_name, self.data.find('>', idx)

    def getTagType_(self, sIdx, eIdx):
        curIdx = sIdx
        tagTypes = []
        while curIdx < eIdx - 2:
            curIdx = self.data.find(" ", curIdx)
            typeName = self.data[curIdx + 1:self.data.find("=", curIdx + 2)]
            curIdx = self.data.find('"', curIdx + len(typeName))
            typeValue = self.data[curIdx + 1:self.data.find('"', curIdx + 1)]
            #if ord(typeValue[0]) >= 128:
            #    typeValue = typeValue.decode('utf-8')
            curIdx = self.data.find('"', curIdx + 1 + len(typeValue)) + 1
            tagTypes.append([typeName, typeValue])
        return tagTypes

    def makeTagList_(self):
        idx = 0
        beginIdx = 0
        tag_list = []

        idx = self.data.find("<HWPML")
        while idx != -1:
            if self.data[idx + 1] != '/': # tag start
                tag_list.append({"sIdx":idx})
                tag_name, beginIdx = self.getTagName_(idx + 1)
                tag_list[-1]["name"] = tag_name
                if self.data[beginIdx - 1] == '/': # single tag
                    tag_list[-1]["eIdx"] = beginIdx + 1
                if self.data[beginIdx - 1] == '"' or self.data[beginIdx - 2] == '"':
                    tag_list[-1]["tagsIdx"] = tag_list[-1]["sIdx"] + len(tag_list[-1]["name"]) + 2
                    tag_list[-1]["tageIdx"] = beginIdx if self.data[beginIdx - 1] == '"' else beginIdx - 1
                    tag_list[-1]["tagTypes"] = self.getTagType_(tag_list[-1]["sIdx"], beginIdx)
            else:   # tag end
                tag_name, beginIdx = self.getTagName_(idx + 2)
                for tagIdx in range(len(tag_list))[::-1]:
                    if "eIdx" not in tag_list[tagIdx] and tag_list[tagIdx]["name"] == tag_name:
                        tag_list[tagIdx]["eIdx"] = beginIdx + 1
                        break
            idx = self.data.find('<', beginIdx)

        return tag_list

    def makeMutationList_(self):
        mutation_idx_list = []
        tagList = self.makeTagList_()
        tagTypeCount = 0
        tagTypesMap = {}
        for tagInfo in tagList:
            if tagInfo.has_key("tagTypes"):
                tagTypesMap[tagInfo["tagsIdx"]] = tagInfo

        for idx in sorted(sample(tagTypesMap, randrange(1, 100)))[::-1]: # descending order
            mutationTag = tagTypesMap[idx]
            for j, tagType in enumerate(mutationTag["tagTypes"]):
                if randrange(3) != '0': continue # not mutate all of types(33% mutate rate)
                checkString = tagType[1]
                unit = ''
                if checkString.endswith("mm") or checkString.endswith("cm"):
                    checkString = checkString[:-2]
                    unit = checkString[-2:]
                try:
                    float(checkString)
                except:
                    continue
                mutationTag["tagTypes"][j] = [tagType[0], choice(self.mutationNumber) + unit]
            self.mutationList.append(mutationTag)

    def mutate_(self):
        self.mData = bytearray(self.data)
        for mutation in self.mutationList: # descending order
            typeString = str(mutation["tagTypes"])
            typeString = typeString[3:].replace("', '", "='").replace("'], ['", "' ")[:-2]
            self.mData = self.mData[:mutation["tagsIdx"]] + typeString + self.mData[mutation["tageIdx"]:]

    def runMutation(self, targetFile):
        self.targetFile = targetFile
        self.data = open(self.targetFile, 'rb').read()
        self.mutationList = []
        self.minimizeIdx = 0
        self.minimizeInfo = []
        self.makeMutationList_()
        self.mutate_()
        open(self.targetFile, 'wb').write(self.mData)

    def isMinimizeFinished(self):
        if self.minimizeIdx == len(self.mutationList):
            return True
        return False

    def runMinimize(self):
        self.minimizeInfo = self.mutationList[self.minimizeIdx]
        del self.mutationList[self.minimizeIdx]
        self.mutate_()
        open(self.targetFile, 'wb').write(self.mData)

    def updateMinimizeCrash(self, result):
        if result == False:
            self.mutationList.insert(self.minimizeIdx, self.minimizeInfo)
            self.minimizeIdx += 1
