# -*- coding: utf-8 -*-

import os
import sys
import re
import time
import inspect
import datetime
import multiprocessing
import getopt
import shutil
import tempfile
import random
import json
import math
import logging
import logging.config
import logging.handlers

logging.basicConfig(
        level = logging.NOTSET , 
        format = "%(asctime)s %(filename)s:%(lineno)d [PID:%(process)d][TID:%(thread)d][Func:%(funcName)s] %(levelname)s: %(message)s" ,
        datefmt = "%a, %Y%m%d %H:%M:%S"
        )
logger = logging.getLogger()

# list转化为string
# @param in_list 待转换list
# @param separator 分隔符
# @return string
def listFormatString(in_list , separator=",") :
    if None==in_list or (not isinstance(in_list , list)) or 0==len(in_list) :
        logger.error("in_list is error.")
        return False
    if not isinstance(separator , str) :
        logger.error("separator is not string.")
        return False
    res = ""
    stan = "{0}" + separator
    for i in range(len(in_list)) :
        res += stan.format(in_list[i])
    return res[:-1]


if __name__ == "__main__" :
    t = ["ab" , 1 , ["c" , 2]]
    print(listFormatString(t))
