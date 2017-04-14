# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime
import random
import multiprocessing
import re
import getopt
import urllib
import requests
import json
import logging
import logging.config
import logging.handlers
from bs4 import BeautifulSoup

logging.basicConfig(
        level = logging.NOTSET , 
        format = "%(asctime)s %(filename)s:%(lineno)d [PID:%(process)d][TID:%(thread)d][Func:%(funcName)s] %(levelname)s: %(message)s" ,
        datefmt = "%a, %Y%m%d %H:%M:%S"
        )
logger = logging.getLogger()

class BS4Spider() :
    def __init__(self) :
        self.soup = None

    # @param html string,html text
    # @return bool
    def createSoup(self , html) :
        try :
            self.soup = BeautifulSoup(str(html) , "lxml")
        except Exception as e :
            logger.error(str(e))
            return False
        return True

    # 唯一匹配
    # @param fname HTML标签名
    # @param fattrs 属性索引集，默认使用。eg:{"class":"sister"}
    # @param frecursive 是否搜索当前标签所有子孙节点
    # @return soup_match 被匹配结果
    def matchOne(self , fname , fattrs=None , frecursive=True) :
        soup_match = None
        if None == fattrs :
            try :
                soup_match = self.soup.find_all(name=fname , recursive=frecursive)
            except Exception as e :
                logger.error(str(e))
                return False
        else :
            if isinstance(fattrs , dict) and len(fattrs) > 0 :
                soup_match = self.soup.find_all(name=fname , attrs=fattrs , recursive=frecursive)
            else :
                logger.error("The fattrs is not dict or lenght is 0.")
                return False
        if 1 == len(soup_match) :
            try :
                soup_match = soup_match[0]
            except Exception as e :
                logger.error(str(e))
                return False
            return soup_match
        elif 0 == len(soup_match) :
            logger.error("There is zero result matched,please check the fname(" + str(name) + ") and the fattrs(" + str(fattrs) + ") and the frecursive(" + str(frecursive) + ")!")
            return False
        else :
            logger.error("More than one result matched,please check the fname(" + str(fname) + ") and the fattrs(" + str(fattrs) + ") and the frecursive(" + str(frecursive) + ")!")
            #return False
            return soup_match[0]

    # 匹配所有结果
    # @param fattrs 属性索引集，默认使用。eg:{"class":"sister"}
    # @param frecursive 是否搜索当前标签所有子孙节点
    # @return soup_match 被匹配结果
    def matchAll(self , fname , fattrs=None , frecursive=True) :
        soup_match = None
        if None == fattrs :
            try :
                soup_match = self.soup.find_all(name=fname , recursive=frecursive)
            except Exception as e :
                logger.error(str(e))
                return False
        else :
            if isinstance(fattrs , dict) and len(fattrs) > 0 :
                soup_match = self.soup.find_all(name=fname , attrs=fattrs , recursive=frecursive)
            else :
                logger.error("The fattrs is not dict or lenght is 0.")
                return False
        return soup_match
