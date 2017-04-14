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

logging.basicConfig(
        level = logging.NOTSET , 
        format = "%(asctime)s %(filename)s:%(lineno)d [PID:%(process)d][TID:%(thread)d][Func:%(funcName)s] %(levelname)s: %(message)s" ,
        datefmt = "%a, %Y%m%d %H:%M:%S"
        )
logger = logging.getLogger()

# 快速生成同一个函数多进程处理dict或者list数据
# @param func 所要使用的函数名
# @param args_tuple 常规参数
# @param sep_data 需要在多进程中处理的dict或者list参数
def multiProcessGo(func=None , args_tuple=() , sep_data=None , pn_start=0 , pn_end=1) :
    #func: function name
    #args_tuple: args tuple --> (a , b , c)
    #pn_start,pn_end: unsigned int
    if None == func :
        logger.error("param func is None!")
        return False
    if (not isinstance(pn_start , int)) or pn_start < 0 :
        logger.error("pn_start is error!")
        return False
    if (not isinstance(pn_end , int)) or pn_end <= 0 :
        logger.error("pn_end is error!")
        return False
    process_dict = {}
    process_info_dict = {}
    if None == sep_data :
        for pn in range(pn_start , pn_end) :
            process_dict[pn] = multiprocessing.Process(target=func , args=args_tuple+(pn,))
            process_info_dict[pn] = {
                "function_name":func.__name__ , 
                "function_args":args_tuple+(pn , ) ,
                }
            logger.info("Start process[" + str(pn) + "]: " + str(func.__name__) + str(args_tuple+(pn,)))
        for pn,p in process_dict.items() :
            p.daemon = True
            p.start()
        for pn,p in process_dict.items() :
            p.join()
    elif (not isinstance(sep_data , list)) or len(sep_data) < (pn_end - pn_start) :
        logger.error("sep_data is error!sep_data must be a list and the length must be equal to (pn_end-pn_start)!")
        return False
    else :
        i = 0
        for pn in range(pn_start , pn_end) :
            process_dict[pn] = multiprocessing.Process(target=func , args=args_tuple + (sep_data[i] , pn))
            process_info_dict[pn] = {
                "function_name":func.__name__ , 
                "function_args":args_tuple+(sep_data[i] , pn) ,
                }
            logger.info("Start process[" + str(pn) + "]: " + str(func.__name__) + str(args_tuple+("sep_data" , pn)))
            i += 1
        for pn,p in process_dict.items() :
            p.daemon = True
            p.start()
        for pn,p in process_dict.items() :
            p.join()

# 快速生成同一个函数多进程处理dict或者list数据
# @param func 所要使用的函数名
# @param args_tuple 常规参数
# @param sep_data 已分隔好的，需要在多进程中处理的dict或者list。eg:[[...] , [...] , ...]
def multiProcessGo(func=None , args_tuple=() , sep_data=None , pn_start=0 , pn_end=1 , process_num=None) :
    if None == func :
        logger.error("param func is None!")
        return False
    process_dict = {}
    process_info_dict = {}
    if None == sep_data :
        pass
    else :
        if (not isinstance(sep_data , list)) or (not isinstance(sep_data , dict)) :
            logger.error("sep_data is error!sep_data must be a list or dict!")
            return False

def splitList(data_list , cpy_num=1) :
    sep_list = []
    step = int(len(data_list)/cpy_num + 1)
    start = 0
    end = step
    for i in range(cpy_num) :
        if i != cpy_num-1 :
            sep_list.append(data_list[start:end])
            start += step
            end += step
        else :
            sep_list.append(data_list[start:])
    return sep_list


def splitDict(data_dict , cpy_num) :
    sep_list = []
    data = {}
    i = 0
    wlen = len(data_dict)
    iend = int(wlen/cpy_num + 1)
    tag = 0
    for k,v in data_dict.items() :
        data[k] = v
        i += 1
        tag += 1
        if i >= iend :
            sep_list.append(data)
            data = {}
            i = 0
        if tag >= wlen :
            sep_list.append(data)
    return sep_list

if __name__ == "__main__" :
    a = []
    for i in range(1000) :
        a.append(i)
    b = splitList(a , 3)
    print(b[0])
    print(b[1])
    print(b[2])
