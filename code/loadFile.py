import pandas as pd
import spacy
import numerizer
import json
import Levels
import Leveltools

nlp = spacy.load("en_core_web_sm")

class CLAEXText:
    def __init__(self, sent=None, DCT="NULL",tok=None, calex=None):
        self.sent = sent
        self.DCT = DCT
        self.tok = tok
        self.calex = calex

    def __str__(self):
        return ("DCT: {DCT_}, \nsent: {sent_}, \ntok: {tok_}, \ncalex: {calex_}".format(DCT_=self.DCT,sent_=self.sent,tok_ = self.tok,calex_=self.calex))

    def token(self):
        tokenize = []
        sent_tmp = self.sent
        for i in sent_tmp.split():
            document = nlp(i)
            all_tags = {w: w.pos_ for w in document}
            tokenize.append(all_tags)
        self.tok = tokenize
        return

    def load(self,inputstring=None,fileName=None):
        DCT_ = input("Please input DCT (YYYY-MM-DD) or NULL: \n")
        if DCT_ == "NULL":
            DCT_ = ["NULL", "NULL", "NULL"]
        else:
            DCT_ = DCT_.split("-")
        if fileName != None:
            output = []
            with open(fileName, "r") as file:
                data = file.readlines()
            for i in data:
                removed = i.strip().lower()
                if removed != "":
                    output.append(removed)
        else:
            if inputstring == None:
                output_string = input("Please input the string: \n")
            # output = [output_string.lower()]
            else:
                output_string = inputstring
            output = [output_string.lower()]
        string_lst_number = []
        for i in output:
            string = nlp(i)
            tmp_number = string._.numerize()
            for j in list(tmp_number.keys()):
                i = i.replace(str(j), tmp_number[j])
            string_lst_number.append(i)

        self.sent = "".join(string_lst_number)
        self.DCT = Leveltools.DatePoint(year=DCT_[0], month=DCT_[1], day=DCT_[2])
        return

    def calexfunc(self):
        self.calex =  Levels.run(self.sent, self.DCT)

    def save(self, savefile="CALEX.json"):
        output_dict = {"DCT":self.DCT.__str__(),"text":self.sent, "tokens":str(self.tok),"calex":self.calex}
        with open(savefile, "w") as file:
            json.dump(output_dict,file,indent=2)
        # print("finish saving")



if __name__ == "__main__":
    """
    output = inputFile(fileName)
    # output = inputText()
    output.token()
    print(output)
    """


    # fileName = None
    output = CLAEXText()
    output.load()
    output.token()
    output.calexfunc()
    print(output)

    output.save()
