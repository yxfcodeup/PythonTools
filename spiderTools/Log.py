# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime
import multiprocessing
import configparser
import re
import getopt
import urllib
import random
import json
import pickle
import logging
import logging.config
import logging.handlers
import hashlib
from operator import add , itemgetter


class Log() :
    # 日志类初始化
    # @param log_dir 日志文件路径
    # @param log_file 日志文件名
    # @param basic_way 是否使用基本日志
    # @param log_level 日志等级
    def __init__(self , log_dir=None , log_file=None , basic_way=True , log_level="NOTSET") :
        self.log_dir = None
        self.log_file = None
        self.logger = None
        if None == log_file :
            logging.basicConfig(
                level = logging.NOTSET , format = "%(asctime)s %(filename)s:%(lineno)d [PID:%(process)d][TID:%(thread)d][Func:%(funcName)s] %(levelname)s: %(message)s" ,
                datefmt = "%a, %Y%m%d %H:%M:%S"
                )
        else :
            try :
                if False == os.path.exists(log_dir) :
                    os.mkdir(log_dir)
                if False == os.path.exists(log_file) :
                    with open(log_file , "w") as f :
                        f.write("")
            except Exception as e :
                print("Log __init__ ERROR: " + str(e))
                print("Exit...")
                exit(1)
            self.log_dir = log_dir
            self.log_file = log_file
            if basic_way :
                logging.basicConfig(
                    level=logging.NOTSET ,
                    format = "%(asctime)s %(filename)s:%(lineno)d [PID:%(process)d][TID:%(thread)d][Func:%(funcName)s] %(levelname)s: %(message)s" ,
                    datefmt = "%a, %Y%m%d %H:%M:%S" ,
                    filename = self.log_file ,
                    filemode = "a")
                self.logger = logging.getLogger()
            else :
                logging_config_dict = {
                    "version":1 , 
                    "disable_existing_loggers":False , 
                    "formatters":{
                        "standard":{
                            "format":"%(asctime)s %(filename)s:%(lineno)d [PID:%(process)d][TID:%(thread)d][Func:%(funcName)s] %(levelname)s: %(message)s" 
                            } , 
                        } , 
                    "handlers":{
                        "handler_root":{
                            "level":"NOTSET" , 
                            "formatter":"standard" , 
                            "class":"logging.handlers.RotatingFileHandler" , 
                            "filename":self.log_file , 
                            "maxBytes":1024*1024 , 
                            "backupCount":0 , 
                            } , 
                        "handler_stderr":{
                            "level":"INFO" , 
                            "formatter":"standard" , 
                            "class":"logging.StreamHandler" , 
                            "stream":"ext://sys.stderr"
                            } , 
                        } , 
                    "root":{
                        "handlers":["handler_root" , "handler_stderr"] ,  
                        "level":log_level
                        } , 
                    }
                logging.config.dictConfig(logging_config_dict)
            self.logger = logging.getLogger()
    
    def info(self , info_str) :
        self.logger.info(str(info_str))

    def error(self , err_str) :
        self.logger.error(str(err_str))

    def warning(self , war_str) :
        self.logger.warning(str(war_str))
