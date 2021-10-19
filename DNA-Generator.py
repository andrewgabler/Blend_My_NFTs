import bpy
import os
import sys

dir = os.path.dirname(bpy.data.filepath)
sys.path.append(dir)

import itertools
import time
import copy
import re
import json
import conFig
import importlib
importlib.reload(conFig)
from conFig import *

time_start = time.time()

def returnData():
   '''
   Generates important variables, dictionaries, and lists needed to be stored to catalog the NFTs.
   :return: listAllCollections, attributeCollections, attributeCollections1, hierarchy, variantMetaData, possibleCombinations
   '''
   listAllCollections = []

   for i in bpy.data.collections:
      listAllCollections.append(i.name)

   listAllCollections.remove("Script_Ignore")

   exclude = ["_","1","2","3","4","5","6","7","8","9","0"]
   attributeCollections = copy.deepcopy(listAllCollections)

   def filter_num():
      """This function removes items from 'attributeCollections' if they include values from the 'exclude' variable.
      It removes child collections from the parent collections in from the "listAllCollections" list.
      """
      for x in attributeCollections:
         if any(a in x for a in exclude):
            attributeCollections.remove(x)

   for i in range(len(listAllCollections)):
       filter_num()

   attributeVariants = [x for x in listAllCollections if x not in attributeCollections]
   attributeCollections1 = copy.deepcopy(attributeCollections)

   def getChildren():
      parentDictionary = {}
      for i in attributeCollections1:
         colParLong = list(bpy.data.collections[str(i)].children)
         colParShort =[]
         for x in colParLong:
            colParShort.append(x.name)
         parentDictionary[i] = colParShort
      return parentDictionary

   hierarchy = getChildren()

   def numOfCombinations(hierarchy):
      hierarchyByNum = []
      for i in hierarchy:
         hierarchyByNum.append(len(hierarchy[i]))
      combinations = 1
      for i in hierarchyByNum:
         combinations = combinations*i
      return combinations

   possibleCombinations = numOfCombinations(hierarchy)

   def attributeData(attributeVariants):
      allAttDataList = {}
      for i in attributeVariants:

         def getParent(i):
            parent = ""
            for w in hierarchy:
               listChild = hierarchy[w]
               if i in listChild:
                  parent = w

            return parent

         def getStr(i):
            name_1 = re.sub(r'[^a-zA-Z]', "", i)
            return name_1

         def getOrder_rarity(i):
            x = re.sub(r'[a-zA-Z]', "", i)
            a = x.split("_")
            del a[0]
            return list(a)

         fullName = i
         name = getStr(i)
         orderRarity = getOrder_rarity(i)
         number = orderRarity[0]
         rarity = orderRarity[1]
         parentCollection = getParent(i)

         eachObject = {"fullName": fullName, "name": name, "number": number, "rarity": rarity, "parentCollection": parentCollection}

         allAttDataList[fullName] = eachObject
      return allAttDataList

   variantMetaData = attributeData(attributeVariants)

   for i in variantMetaData:
      def cameraToggle(i,toggle = True):
         bpy.data.collections[i].hide_render = toggle
         bpy.data.collections[i].hide_viewport = toggle
      cameraToggle(i)
   return listAllCollections, attributeCollections, attributeCollections1, hierarchy, variantMetaData, possibleCombinations

listAllCollections, attributeCollections, attributeCollections1, hierarchy, variantMetaData, possibleCombinations = returnData()

def generateNFT_DNA(variantMetaData, possibleCombinations):
   '''
   :param variantMetaData: The variantMetaData
   :return: the batch dictionary of the NFT's being created, there dna, and attributes
   '''
   batchDataDictionary = {}

   print("-----------------------------------------------------------------------------")
   print("Generating " + str(possibleCombinations) + " combinations of DNA...")
   print("")

   listOptionVari = []

   for i in hierarchy:
      numChild = len(hierarchy[i])
      possibleNums = list(range(1, numChild + 1))
      listOptionVari.append(possibleNums)

   allDNAList = list(itertools.product(*listOptionVari))
   allDNAstr = []

   for i in allDNAList:
      dnaStr = ""
      for j in i:
         num = "-" + str(j)
         dnaStr += num

      dna = ''.join(dnaStr.split('-', 1))
      allDNAstr.append(dna)

   #Data stored in batchDataDictionary:
   batchDataDictionary["numNFTsGenerated"] = possibleCombinations
   batchDataDictionary["variantMetaData"] = variantMetaData
   batchDataDictionary["DNAList"] = allDNAstr
   return batchDataDictionary

DataDictionary = generateNFT_DNA(variantMetaData, possibleCombinations)

def sendToJSON():
   '''
   Sends 'batchDataDictionary' dictionary to the NFTRecord.json file.
   '''
   file_name = os.path.join(save_path, "NFTRecord.json")
   ledger = json.load(open(file_name))

   num = 1
   for i in ledger:
      num += 1
   ledger[num] = DataDictionary

   ledger = json.dumps(ledger, indent=1, ensure_ascii=True)

   with open(file_name, 'w') as outfile:
      outfile.write(ledger + '\n')
   print("")
   print("All possible combinations of DNA sent to NFTRecord.json with " + str(possibleCombinations) + "\nNFT DNA sequences generated in %.4f seconds" % (time.time() - time_start))
   print("")
   print("If you want the number of NFT DNA sequences to be higher, please add more variants or attributes to your .blend file")
   print("")
   print("༼ ºل͟º ༼ ºل͟º ༼ ºل͟º ༽ ºل͟º ༽ ºل͟º ༽")
   print("")

sendToJSON()

'''Utility functions:'''

def turnAll(toggle):
   '''
   Turns all renender and viewport cameras off or on for all collections in the scene.
   :param toggle: False = turn all cameras on
                  True = turn all cameras off
   '''
   for i in listAllCollections:
      bpy.data.collections[i].hide_render = toggle
      bpy.data.collections[i].hide_viewport = toggle

#turnAll(False)

# ONLY FOR TESTING, DO NOT EVER USE IF RECORD IS FULL OF REAL DATA
# THIS WILL DELETE THE RECORD:
# Also don't forget to add an empty list when its done to NFTRecord or else this file can't run properly.
def clearNFTRecord(AREYOUSURE):
   if AREYOUSURE == True:
      file_name = os.path.join(save_path, "NFTRecord.json")
      print("Wiping NFTRecord.json of all data...")

      ledger = json.load(open(file_name))

      with open(file_name, 'w') as outfile:
         ledger.clear()
         outfile.close()

#clearNFTRecord()