import datefinder
import datetime
import six
from dateutil.parser import parser
from dateutil.parser import parse
import types
from dateutil.parser import ParserError
from calendar import monthrange
from dateutil import relativedelta
import pandas as pd
import nltk
import re
import json



class DatePoint():
    def __init__(self, year="NULL", month="NULL", day="NULL", pos=None, bufferYear=None, NULL=False):
        self.year = year
        self.month = month
        self.day = day
        self.pos = pos
        self.bufferYear = bufferYear
        self.weight = 0
        self.in_DateRange = False
        self.NULL = NULL

    def __str__(self):
        # return "DatePoint: {year_}-{month_}-{day_}, weight: {weight_}".format(year_=self.year,month_=self.month,day_=self.day, weight_=self.weight)
        # return "DatePoint: {year_}-{month_}-{day_}  Position: {pos_}".format(year_=self.year, month_=self.month,day_=self.day, pos_=self.pos)
        output_dict = {"Year":self.year, "Month":self.month, "Day":self.day, "Position":self.pos}
        # return json.dumps(output_dict, indent=2, separators=(',', ':'))
        return str(output_dict)


class DateRange():
    def __init__(self, from_DP=None, to_DP=None):



        if from_DP == None:
            self.from_DP = DatePoint(NULL=True)
        else:
            self.from_DP = from_DP
        if to_DP == None:
            self.to_DP = DatePoint(NULL=True)
        else:
            self.to_DP = to_DP

        self.combined = False

    def __str__(self):
        return "DateRange: from {from_DP_} to {to_DP_}".format(from_DP_=self.from_DP, to_DP_=self.to_DP)



def read_csv(fileName):
    df = pd.read_csv(fileName)
    return df


# xxxxxxxxxxxxxxxxx
def my_find_date(self, text, source=False, index=False, strict=False):
    tmp_lst = []
    indices_iter, date_string_iter = None, None
    for date_string, indices, captures in self.extract_date_strings(
            text, strict=strict
    ):

        try:
            as_dt = parse(date_string)
        except (ValueError, OverflowError):
            continue
        if date_string not in tmp_lst:
            tmp_lst.append(date_string)
            indices_iter = (indices, )
            date_string_iter = (date_string,)
            yield indices_iter, date_string_iter

    """
    if len(indices_iter) == 1:
        indices_iter = indices_iter[0]
    if len(date_string_iter) == 1:
        date_string_iter = date_string_iter[0]
    """
    return

# xxxxxxxxxxxxxxxxx
def my_parse(self, timestr, default=None,
              ignoretz=False, tzinfos=None, **kwargs):
    if default is None:
        default = datetime.datetime.now().replace(hour=0, minute=0,
                                                  second=0, microsecond=0)

    res, skipped_tokens = self._parse(timestr, **kwargs)

    if res is None:
        raise ParserError("Unknown string format: %s", timestr)

    if len(res) == 0:
        raise ParserError("String does not contain a date: %s", timestr)

    try:
        ret = self.my_build_naive(res, default)
    except ValueError as e:
        six.raise_from(ParserError(e.args[0] + ": %s", timestr), e)

    if not ignoretz:
        ret = self._build_tzaware(ret, res, tzinfos)

    if kwargs.get('fuzzy_with_tokens', False):
        return ret, skipped_tokens
    else:
        return ret

# xxxxxxxxxxxxxxxxx
def my_build_naive(self, res, default):
    repl = {}
    for attr in ("year", "month", "day", "hour",
                 "minute", "second", "microsecond"):
        value = getattr(res, attr)
        if value is not None:
            repl[attr] = value

    if 'day' not in repl:
        cyear = default.year if res.year is None else res.year
        cmonth = default.month if res.month is None else res.month
        cday = default.day if res.day is None else res.day

        if cday > monthrange(cyear, cmonth)[1]:
            repl['day'] = monthrange(cyear, cmonth)[1]

    return repl

# xxxxxxxxxxxxxxxxx
def my_datefinder():
    init_datefinder = datefinder.DateFinder()
    init_datefinder.my_find_date = types.MethodType(my_find_date, init_datefinder)
    # init_datefinder.find_date = types.MethodType(my_find_date, init_datefinder)
    return init_datefinder

# xxxxxxxxxxxxxxxxx
def my_parser():
    init_parser = parser()
    init_parser.my_build_naive = types.MethodType(my_build_naive, init_parser)
    init_parser.my_parse = types.MethodType(my_parse,init_parser)
    return init_parser


def is_preposition(current):
    if isinstance(current, DatePoint):
        return False

    if nltk.pos_tag([current])[0][1] == "IN":
        return True
    else:
        return False

def is_noun(current):
    if isinstance(current, DatePoint):
        return False
    if re.match(r"<(.*?)>", current):
        return False
    if current == "":
        return False
    if nltk.pos_tag([current])[0][1][:2] == "NN" or nltk.pos_tag([current])[0][1] == "PRP":
        return True
    else:
        return False


def postDP_weight(inputLst, current_pos, value):
    for i in range(current_pos,len(inputLst)):
        if isinstance(inputLst[i],DatePoint):
            inputLst[i].weight += value
            return
        if inputLst[i] == "":
            return
        if is_noun(inputLst[i]):
            return

def preDP_weight(inputLst, current_pos, value):
    for i in range(current_pos-1, -1, -1):
        if isinstance(inputLst[i], DatePoint):
            inputLst[i].weight += value
            return
        if inputLst[i] == "":
            return

def postDP(inputList, current_pos):
    if isinstance(inputList[current_pos+1], DatePoint):
        if inputList[current_pos+1].weight >= 0:
            inputList[current_pos+1].in_DateRange = True
            return inputList[current_pos+1]
    return False

def is_formerDR(current):
    if isinstance(current, DateRange):
        if not current.from_DP.NULL and current.to_DP.NULL:
            return True
    return False

def is_latterDR(current):
    if isinstance(current, DateRange):
        if current.from_DP.NULL and not current.to_DP.NULL:
            return True
    return False

def postpDR(inputLst, current_pos):
    for i in range(current_pos,len(inputLst)):
        if is_latterDR(inputLst[i]) and inputLst[i].combined == False:
            inputLst[i].combine = True
            return inputLst[i]
    return False

def prepDR(inputLst, current_pos):
    for i in range(current_pos-1, -1, -1):
        if is_formerDR(inputLst[i]):
            return inputLst[i]
    return False

def is_day(current):
    if isinstance(current, DatePoint):
        if current.year == "NULL" and current.month == "NULL" and current.day != "NULL":
            return True
    return False

def find_last(inputLst, current_pos):
    if inputLst[current_pos-1] == "<last>":
        return True
    return False

def find_next(inputLst, current_pos):
    if inputLst[current_pos-1] == "<next>":
        return True
    return False

def multi(current, value):
    current.day = str(value * int(current.day))
    return current

def day2year(current):
    # print(current)
    current.year = current.day
    current.day = "NULL"
    return current

def add(DP1, DP2):
    if DP1.year != "NULL" and DP2 != "NULL":
        year = str(int(DP1.year) + int(DP2.year))
    elif DP1.year != "NULL" and DP2 == "NULL":
        year = DP1.year
    elif DP1.year == "NULL" and DP2 != "NULL":
        year = DP2.year
    else:
        year = "NULL"
    newDP = DatePoint(year=year)
    return newDP

def find_year(inputLst, current_pos):
    if inputLst[current_pos+1] == ("years" or "year"):
        return True
    return False

def find_decade(inputLst, current_pos):
    if inputLst[current_pos] == "<decade>":
        return True
    return False

def find_centry(inputLst, current_pos):
    if inputLst[current_pos] == "<centry>":
        return True
    return False



if __name__ == "__main__":
    my_datefinder = my_datefinder()
    my_parser = my_parser()

    string = "I came in Kiledelphia in 2021 May 21st, and my son came in 2022."
    matches = my_datefinder.my_find_date(text=string)
    for i,j in matches:
        print(i)
        print(j)


# string = "in 2021 May 21st"

# indices, date_string = init_datefinder.my_find_date(text=string)
# print(date_string)
# date_dict = init_parser.my_parse(date_string)
# print(date_dict)
