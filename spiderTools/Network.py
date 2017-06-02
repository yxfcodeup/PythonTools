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
import socket
import optparse
import logging
import logging.config
import logging.handlers

logging.basicConfig(
        level = logging.NOTSET , 
        format = "%(asctime)s %(filename)s:%(lineno)d [PID:%(process)d][TID:%(thread)d][Func:%(funcName)s] %(levelname)s: %(message)s" ,
        datefmt = "%a, %Y%m%d %H:%M:%S"
        )
logger = logging.getLogger()

def ping(url , times=10) :
    def isnumber(nstr) :
        if type(nstr) != type(str()) :
            logger.info(str(nstr) + " is not string!Cannot judge it!")
            return False
        num_str = ""
        num_dot = 0
        for i in range(len(nstr)) :
            ns = nstr[i]
            if 0==i and ("0"==ns or "."==ns) :
                return False
            if "0"!=ns and "1"!=ns and "2"!=ns and "3"!=ns and "4"!=ns and "5"!=ns\
                    and "6"!=ns and "7"!=ns and "8"!=ns and "9"!=ns and "."!=ns :
                return False
            if "." == ns :
                num_dot += 1
        if num_dot > 1 :
            return False
        return True

    #ping.sh
    #> PING=`ping -c $1 $2`
    #> echo $PING
    shell_path = "./sh"
    ping_shell = "./sh/ping.sh"
    if not os.path.exists(shell_path) :
        logger.warning("./sh do not exists!")
        os.mkdir(shell_path)
    if not os.path.exists(ping_shell) :
        logger.warning("./sh/ping.sh do not exists!")
        os.system("echo '#/bin/bash' >> ./sh/ping.sh")
        os.system("echo 'PING=`ping -c $1 $2`' >> ./sh/ping.sh")
        os.system("echo 'echo $PING' >> ./sh/ping.sh")
        os.system("chmod 755 ./sh/ping.sh")
    logger.info(ping_shell + " " + str(times) + " " + str(url))
    res = os.popen(ping_shell + " " + str(times) + " " + str(url)).read()
    min_avg_max_mdev_rex = "min/avg/max/mdev = ([\d\.]{1,10}/[\d\.]{1,10}/[\d\.]{1,10}/[\d\.]{1,10}) ms"
    pac_loss_rex = "([\d\.]{1,5})% packet loss"
    min_avg_max_mdev_mh = re.findall(re.compile(min_avg_max_mdev_rex) , str(res))
    pac_loss_mh = re.findall(re.compile(pac_loss_rex) , str(res))
    if 1 != len(min_avg_max_mdev_mh) :
        logger.error(str(res))
        return False
    if 1 != len(pac_loss_mh) :
        logger.error(str(res))
        return False
    min_avg_max_mdev = str(min_avg_max_mdev_mh[0]).split("/")
    avg_time = min_avg_max_mdev[1]
    pac_loss = pac_loss_mh[0]
    if isnumber(str(avg_time)) :
        avg_time = float(avg_time)
    if isnumber(str(pac_loss)) :
        pac_loss = float(pac_loss)
    return [avg_time , pac_loss]


def wget(wget_command) :
    #wget.sh
    #WGET=`$1`
    shell_path = "./sh"
    wget_shell = "./sh/wget.sh"
    if not os.path.exists(shell_path) :
        logger.warning("./sh do not exists!")
        os.mkdir(shell_path)
    if not os.path.exists(wget_shell) :
        logger.warning("./sh/wget.sh not exists!")
        os.system("echo '#/bin/bash' >> ./sh/wget.sh")
        os.system("echo 'WGET=`$1`' >> ./sh/wget.sh")
    logger.info(wget_command)
    os.system(wget_command)
    return True


def getParsedArgs() :
    usage = "Usage: %prog host[options]"
    # Create the parser
    parser = optparse.OptionParser(
            description = "ping hosts using tcp syn packets" ,
            usage=usage , 
        )
    parser.add_option("-t" , action="store_false" , default=False , 
            help="ping host until stopped with 'control-c'")
    parser.add_option("-n" , dest="count" , default=4 , type=int , 
            help="number of requests to send (default: %default)")
    parser.add_option("-p" , dest="port" , default=80 , type=int , 
            help="port number to use (default: %default)")
    parser.add_option("-w" , dest="timeout" , default=3 , type=int , 
            help="timeout in seconds to wait for reply (default: %default)")

    # Print help if no argument is given
    if 1 == len(sys.argv) :
        parser.print_help()
        sys.exit(1)

    # Parser the args
    (options , args) = parser.parse_args()
    
    # Some args validation
    if 0 == len(args) :
        parser.error("host not informed")
    if len(args) > 1 :
        parser.error("incorrect number of arguments")
    if options.port <= 0 or options.port > 65535 :
        parser.error("port must be a number between 1 and 65535")
    if options.timeout < 1 :
        parser.error("timeout must be a positive number")
    if options.count <= 0 :
        parser.error("count must be a positive number")
    return (options , args)

# 获取域名对应的ip地址
# @param host 域名
# @return remote_ip || False
def get_ip(host) :
    try :
        remote_ip = socket.gethostbyname(host)
    except Exception as e :
        if "Errno" in str(e) or "-2" in str(e) or "not know" in str(e) :
            logger.error("unknown host!")
        else :
            logger.error(str(e))
        #sys.exit(1)
        return False
    return remote_ip

# ping域名
def ping(host , port , timeout) :
    try :
        s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    except socket.error as e :
        logger.error("Failed. (socket error: " + str(e) + ")")
        sys.exit(1)
    s.settimeout(timeout)
    t0 = time.time()
    s.connect((host , port))
    #s.shutdown(socket.SHUT_DOWN)
    s.close()
    t1 = time.time()
    dt = t1 - t0
    return dt

# ping客户端
# @param host 域名或者IP地址
# @param port 端口号
# @param timeout
# @param is_ctrl_c 通过control-c中断ping，反之则在ping指定次数后自动中断
# @param count 指定ping的次数
# @return 丢包比例(0~1.0)，最小延迟，最大延迟，平均延迟
#NOTE:
#参考1：https://github.com/pdrb/synping.git
#参考2：https://github.com/emamirazavi/python3-ping.git
def pingCli(host , port=80 , timeout=3 , is_ctrl_c=False , count=4) :
    if (not isinstance(port , int)) or port <= 0 or port > 65535 :
        logger.error("port must be a number between 1 and 65535")
        return False
    if (not isinstance(timeout , int)) or timeout < 1 :
        logger.error("timeout must be a positive number")
        return False
    if not isinstance(is_ctrl_c , bool) :
        logger.error("ping host until stopped with 'control-c'")
        return False
    if (not isinstance(count , int)) or count <= 0 :
        logger.error("count must be a positive number")
        return False

    # Needed variables
    times = []
    sent = 0
    rcvd = 0
    total = 0

    # Get the host IP
    remote_ip = get_ip(host)
    # Print the appropriate beginning message
    if False == remote_ip :
        logger.error("Can not get the ip of host[" + str(host) + "]")
        sys.exit(1)

    # Begin the pinging
    try :
        while True :
            # Timer needed for refused connections
            tr0 = time.time()
            try :
                dt = ping(remote_ip , port , timeout)
                times.append(dt)
                sent += 1
                rcvd += 1
                logger.info("Reply from %s:%d time=%.2f ms" % (remote_ip , port , dt*1000))
            except Exception as e :
                logger.error(str(e))
                tr1 = time.time()
                # If the host respond with a refused message it means it is alive, 111 and 10061 are Errno codes for linux and windows
                if "111" in str(e) or "10061" in str(e) or "refused" in str(e) :
                    ttr = tr1 - tr0
                    times.append(ttr)
                    sent += 1
                    rcvd += 1
                    logger.info("Reply from %s:%d time=%.2f ms" % (remote_ip , port , ttr*1000))
                elif "timed out" in str(e) :
                    sent += 1
                    logger.info("Timed out after " + str(timeout) + " seconds")
                elif "22" in str(e) or "argument" in str(e) :
                    logger.error("invalid host")
                    sys.exit(1)
                else :
                    sent += 1
                    logger.error(str(e))
            # End the loop if needed
            if not is_ctrl_c :
                if sent == count :
                    break
            # Sleep between the requests
            time.sleep(1)
    # Catch the kyeboard interrupt to end the loop
    except KeyboardInterrupt :
        logger.warning("Aborted.")

    # Early exit without sending packets
    if 0 == sent :
        sys.exit(1)

    # If no packets received print appropriate message and end the program
    if 0 == rcvd :
        logger.warning("Didn\'t receive any packets...")
        logger.warning("Host is probably DOWN or firewalled.")
        sys.exit(1)

    # Calculate the arverage time
    for t in times :
        total += t
    average = total / rcvd

    # print the summary
    logger.info("Statistics:")
    logger.info("-" * 50)
    logger.info("Host: %s" % host)
    logger.info("Sent: %d packets\tReceived: %d packets\tLost: %d packets (%.2f%%)" % (sent , rcvd , sent - rcvd , float(sent - rcvd) / sent * 100))
    logger.info("Min time: %.2f ms\tMax time: %.2fms\tAverage time: %.2f ms" % (min(times) * 1000 , max(times) * 1000 , average * 1000))
    
    return [float(sent - rcvd) / sent , min(times) * 1000 , max(times) * 1000 , average * 1000]



if __name__ == "__main__" :
    url = "www.baidu.com"
    print(get_ip(url))
    pingCli(url)
    #wget_command = "wget -r -P ./a http://diameizi.diandian.com 2>|./b/log.txt"
    #wget(wget_command)
