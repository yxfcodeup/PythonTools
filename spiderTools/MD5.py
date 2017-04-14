# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime
import multiprocessing
import re
import getopt
import urllib
import json
import logging
import logging.config
import logging.handlers
import hashlib

logging.basicConfig(
        level = logging.NOTSET , 
        format = "%(asctime)s %(filename)s:%(lineno)d [PID:%(process)d][TID:%(thread)d][Func:%(funcName)s] %(levelname)s: %(message)s" ,
        datefmt = "%a, %Y%m%d %H:%M:%S"
        )
logger = logging.getLogger()

def getmd5(in_str) :
    res = ""
    md = hashlib.md5()
    md.update(in_str.encode("utf-8"))
    res = md.hexdigest()
    return res

def getsha(in_str , tag=1) :
    if 1 == tag :
        return hashlib.sha1().update(in_str.encode("utf-8")).hexdigest()
    elif 224 == tag :
        return hashlib.sha224().update(in_str.encode("utf-8")).hexdigest()
    elif 256 == tag :
        return hashlib.sha256().update(in_str.encode("utf-8")).hexdigest()
    elif 384 == tag :
        return hashlib.sha384().update(in_str.encode("utf-8")).hexdigest()
    elif 512 == tag :
        return hashlib.sha512().update(in_str.encode("utf-8")).hexdigest()
    else :
        logger.error("support list: 1, 224, 256, 384, 512")
        return False


if __name__ == "__main__" :
    a = "https://seleniumhq.github.io/selenium/docs/api/py/selenium/selenium.selenium.html#module-selenium.selenium"
    b = getmd5(a)
    print(b)
