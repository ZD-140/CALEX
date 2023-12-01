import Leveltools
from Leveltools import DatePoint, DateRange
from Leveltools import *
import pandas as pd
# import spacy
import nltk
import sys
import re


my_datefinder = Leveltools.my_datefinder()
my_parser = Leveltools.my_parser()

# DCT = DatePoint(year="2022")
# nlp = spacy.load("en_core_web_sm")

class Level0():
    def __init__(self, inputString, output_token=None, input_tmp=None):
        self.inputString = inputString
        self.output_token = []
        self.input_tmp = inputString
        self.indicate_numlst = []

    def token(self):
        punctuation = ',.\'\";'
        # self.output_token = re.split(r'[;,.\s]\s*',self.inputString)
        self.output_token = re.split(r' ', self.input_tmp)
        tmp = self.output_token
        for i in range(len(tmp)):
            for j in range(len(tmp[i])):
                if tmp[i][j] in punctuation:
                    tmp_lst = list(tmp[i])
                    tmp_lst.insert(j+1, " ")
                    tmp_lst.insert(j, " ")
                    tmp_string = ''.join(tmp_lst)
                    tmp[i] = tmp_string
                    break
        tmp = " ".join(tmp)
        self.output_token = re.split(r' ', tmp)
        return

    def translate(self):
        matches = my_datefinder.my_find_date(text=self.input_tmp)
        # indicate_numlst = []
        for indicate, date_string in matches:
            self.indicate_numlst.append(indicate[0])
            # print(date_string)
            date_dict = my_parser.my_parse(date_string[0])
            # print(date_dict)
            if "year" not in date_dict.keys():
                date_dict["year"] = "NULL"
            if "month" not in date_dict.keys():
                date_dict["month"] = "NULL"
            if "day" not in date_dict.keys():
                date_dict["day"] = "NULL"

            # sys.exit()

            res_translate = str(str(date_dict["year"])+"/"+str(date_dict["month"])+"/"+str(date_dict["day"]))
            self.input_tmp = self.input_tmp.replace(date_string[0],res_translate)
        # print(self.inputString)
        # self.inputString = [self.inputString]
        self.token()


        """
        indicate_pos = []
        for i in indicate_numlst:
            num = 0
            for j in range(len(self.inputString)):
                if self.inputString[j] == " ":
                    num += 1
                if j > i[0] and j < i[1]:
                    indicate_pos.append(num)
                    break

        print(indicate_pos)
        """

        return

class Level1():
    def __init__(self, inputStrLst, indicate_numlst, ruleFile=r"./rules/level1Rule.csv"):
        self.ruleDataFrame = Leveltools.read_csv(ruleFile)
        self.indicate_numlst = indicate_numlst
        self.inputStrLst = inputStrLst
        self.outputStrDP = []
        self.tagDP_lst=[]

    def run(self):
        # self.inputStrLst = self.tagged()

        for i, token in enumerate(self.inputStrLst):
            for j, row in self.ruleDataFrame.iterrows():
                # print(row)
                match = re.compile(row["input"])
                search_obj = match.search(token)
                if search_obj != None:
                    DP_tmp = eval(row["output"])
                    self.tagDP_lst.append((i,DP_tmp))
        tmp = self.inputStrLst
        for i in self.tagDP_lst:
            tmp[i[0]] = i[1]
        self.outputStrDP = tmp

        pos = 0
        for i in self.outputStrDP:
            if isinstance(i, DatePoint):
                i.pos = tuple(self.indicate_numlst[pos])
                # print(i)
                pos += 1

class Level2():
    def __init__(self, inputList,ruleFile=r"./rules/level2Rule.csv"):
        self.ruleDataFrame = Leveltools.read_csv(ruleFile)
        self.inputList = inputList
        self.outputList = []

    def run(self):
        inputLst = []

        for j, row in self.ruleDataFrame.iterrows():
            for current_pos, current in enumerate(self.inputList):
                inputLst = self.inputList
                if isinstance(current, DatePoint):
                    continue
                match = eval(row["input"])
                if type(match) == type(None):
                    continue
                if type(match) != bool:
                    res = eval(row["output"])
                    self.inputList[current_pos] = res
                else:
                    if match:
                        eval(row["output"])
        self.outputList = inputLst

class Level3():
    def __init__(self, inputList, ruleFile=r"./rules/level3Rule.csv"):
        self.ruleDataFrame = Leveltools.read_csv(ruleFile)
        self.inputList = inputList
        self.outputList = []

    def run(self):
        inputLst = []
        for j, row in self.ruleDataFrame.iterrows():
            for current_pos, current in enumerate(self.inputList):
                inputLst = self.inputList
                try:
                    match = eval(row["input"])
                except TypeError:
                    continue
                if type(match) == type(None):
                    continue
                if type(match) != bool:
                    res = eval(row["output"])
                    self.inputList[current_pos] = res
                else:
                    if match:
                        res = eval(row["output"])
                        self.inputList[current_pos] = res
        self.outputList = inputLst

class Level4():
    def __init__(self, inputList):
        self.inputList = inputList
        self.outputList = []

    def run(self):
        tmp_lst = []
        for i in self.inputList:
            if isinstance(i, DatePoint):
                if i.weight >=0 and i.in_DateRange == False:
                    tmp_lst.append(i.__str__())
            if isinstance(i, DateRange):
                if i.combined == False:
                    tmp_lst.append(i.__str__())
        for i in tmp_lst:
            self.outputList.append(i)

def run(string, DCT_):
    global DCT
    DCT = DCT_
    in_level0 = Level0(string)
    in_level0.translate()
    tmp = in_level0.output_token
    indicate_numlst = in_level0.indicate_numlst

    in_level1 = Level1(tmp, indicate_numlst)
    in_level1.run()
    tmp = in_level1.outputStrDP
    # print("level1: ",tmp)

    in_level2 = Level2(in_level1.outputStrDP)
    in_level2.run()
    tmp = in_level2.outputList
    # print("level2: ", tmp)

    in_level3 = Level3(in_level2.outputList)
    in_level3.run()
    tmp = in_level3.outputList
    # print("level3: ", tmp)

    in_level4 = Level4(tmp)
    in_level4.run()
    tmp = in_level4.outputList
    return tmp

# token_string = ["I", "have", "been", "Kiledelphia", ""]

if __name__ == "__main__":
    # string = "I came in Killadelphia in 2021 May 21st, and my son came in Dec.."
    # string="I came in Killadelphia in May 21st, and my son came in next decades."

    # string = "I have to rote 2001 pages from last 3 years."
    # string = "I have to rote 2020 pages last 3 years since 2015."

    # string = "I have wrote 2019 pages in 2020. And I have rote the book from May 2018"
    in_level0 = Level0(string)
    in_level0.translate()
    tmp = in_level0.output_token
    indicate_numlst = in_level0.indicate_numlst
    print("Level0 Output: ",tmp)
    print("--------------------------------------------")
    in_level1 = Level1(tmp, indicate_numlst)
    in_level1.run()
    tmp = in_level1.outputStrDP
    print("Level1 Output: ", tmp)
    print("--------------------------------------------")
    in_level2 = Level2(in_level1.outputStrDP)
    in_level2.run()
    tmp = in_level2.outputList
    print("Level2 Output: ", tmp)
    print("--------------------------------------------")
    in_level3 = Level3(in_level2.outputList)
    in_level3.run()
    tmp = in_level3.outputList
    print("Level3 Output: ", tmp)
    print("--------------------------------------------")
    in_level4 = Level4(tmp)
    in_level4.run()
    tmp = in_level4.outputList
    print(tmp)

    """
    string = "I came in Killadelphia in 2021 May 21st, and my son came in 2022."

    matches = my_datefinder.my_find_date(text=string)
    for indicate, date_string in matches:
        print(indicate, date_string)
        date_dict = my_parser.my_parse(date_string[0])
        print(date_dict)
    # date_dict = my_parser.my_parse(date_string)
    # print(date_dict)
    """