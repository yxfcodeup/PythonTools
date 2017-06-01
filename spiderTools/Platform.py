import os
import sys
import re
import time
import math
import datetime
import platform
import logging
import logging.config
import logging.handlers
from multiprocessing import cpu_count

logging.basicConfig(
        level = logging.NOTSET , 
        format = "%(asctime)s %(filename)s:%(lineno)d [PID:%(process)d][TID:%(thread)d][Func:%(funcName)s] %(levelname)s: %(message)s" ,
        datefmt = "%a, %Y%m%d %H:%M:%S"
        )
logger = logging.getLogger()

def getPlatform() :
    pf = (platform.system()).lower()
    if "linux" in pf :
        return 1
    elif "windows" in pf :
        return 2
    else :
        return 0

def cpuCount() :
    return cpu_count()


if __name__ == "__main__" :
    print(cpuCount())
