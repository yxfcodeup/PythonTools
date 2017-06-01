# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime
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
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import *
from selenium.webdriver.common.proxy import *
from selenium.webdriver.support.wait import *

logging.basicConfig(
        level = logging.NOTSET , 
        format = "%(asctime)s %(filename)s:%(lineno)d [PID:%(process)d][TID:%(thread)d][Func:%(funcName)s] %(levelname)s: %(message)s" ,
        datefmt = "%a, %Y%m%d %H:%M:%S"
        )
logger = logging.getLogger()

# selenium爬虫类
class SeleniumSpider() :
    # @param proxy_dict 代理，eg:{"nettype":"http" , "ip":"211.100.29.195" , "port":"82"}
    # @param is_browser_profile 是否使用自定义配置
    def __init__(self , proxy_dict=None , is_browser_profile=False) :
        self.display = None
        self.browser = None
        self.is_browser_profile = False
        self.proxy_type = 2
        self.proxy_dict = None
        if is_browser_profile :
            self.is_browser_profile = is_browser_profile
            if (not isinstance(proxy_dict , dict)) or 3 != len(proxy_dict) :
                logger.error("proxy_dict error,please check it(" + str(proxy_dict) + ")!")
                logger.error("proxy_dict example:{\"nettype\":\"http\" , \"ip\":\"211.100.29.195\" , \"port\":\"82\"")
                sys.exit(1)
            else :
                if "http"!=proxy_dict["nettype"] and "https"!=proxy_dict["nettype"] :
                    logger.error("nettype must be \"http\" or \"https\".")
                    logger.error(str(proxy_dict))
                    sys.exit(1)
                ip_rex = "([\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3})"
                ip_mh = re.findall(re.compile(ip_rex) , proxy_dict["ip"])
                if 1 != len(ip_mh) :
                    logger.error("ip is error!")
                    logger.error(str(proxy_dict))
                    sys.exit(1)
                if not proxy_dict["port"].isdigit() :
                    logger.error("port is error!")
                    logger.error(str(proxy_dict))
                    sys.exit(1)
                self.proxy_dict = proxy_dict
        else :
            self.is_browser_profile = False

    # 开始运行
    def startSelenium(self) :
        try :
            #self.display = Display(visible=0 , size=(1024,768))
            self.display = Display(visible=0 , size=(1366,768))
            #self.display = Display(visible=0 , size=(1920,1080))
            self.display.start()
        except Exception as e :
            logger.error("Start display failed!" + str(e))
            return False
        if self.is_browser_profile :
            try :
                #Plan A:
                browser_profile = webdriver.FirefoxProfile()
                browser_profile.set_preference("network.proxy.type" , self.proxy_type)
                #{"nettype":"http" , "ip":"211.100.29.195" , "port":"82"}
                proxy_url = str(self.proxy_dict["nettype"]) + "://" + str(self.proxy_dict["ip"]) + ":" + str(self.proxy_dict["port"])
                browser_profile.set_preference("network.proxy.autoconfig_url" , proxy_url)
                browser_profile.update_preferences()
                """
                #Plan B:
                proxy_url = str(self.proxy_dict["nettype"]) + "://" + str(self.proxy_dict["ip"]) + ":" + str(self.proxy_dict["port"])
                browser_profile = Proxy({
                        "proxyType":ProxyType.MANUAL , 
                        "httpProxy":proxy_url , 
                        "ftpProxy":proxy_url , 
                        "sslProxy":proxy_url , 
                        "noProxy":"" , 
                    })
                """
            except Exception as e :
                logger.error("FirefoxProfile error!")
                logger.error(str(e))
                return False

            try :
                self.browser = webdriver.Firefox(firefox_profile=browser_profile)
            except Exception as e :
                logger.error("Create webdriver.Firefox error: " + str(e))
                return False
        else :
            try :
                self.browser = webdriver.Firefox()
            except Exception as e :
                logger.error("Create webdriver.Firefox error: " + str(e))
                return False

    def stopSelenium(self) :
        self.browser.quit()
        self.display.stop()

    def restartSelenium(self , proxy_dict=None , is_browser_profile=False) :
        self.stopSelenium()
        self.browser = None
        self.__init__(proxy_dict , is_browser_profile)
        self.startSelenium()

    def refresh(self) :
        self.browser.refresh()

    def getWebsite(self , url , stop_try=5) :
        browser_get = True
        try_again = True
        try_times = 0
        if (not isinstance(stop_try , int)) and stop_try <= 0 :
            stop_try = 1
        while try_again :
            try :
                self.browser.get(url)
                self.browser.implicitly_wait(30)
                #self.browser.set_page_load_timeout(30)
                #self.browser.set_script_timeout(30)
            except Exception as e :
                logger.error(str(url))
                logger.error(str(e))
                time.sleep(2)
                try_times += 1
                if try_times <= stop_try :
                    continue
                else :
                    logger.error("try more than " + str(stop_try) + " times: " + str(url))
                    browser_get = False
            try_again = False
        if browser_get :
            return True
        else :
            return False
    
    # 精确定位一个元素位置
    def getElementByXpath(self , xpath) :
        try :
            #elements_wait = WebDriverWait(self.browser , 30)
            #elements = elements_wait.until(lambda driver:driver.find_elements_by_xpath(xpath))
            elements = self.browser.find_elements_by_xpath(xpath)
        except Exception as e :
            logger.error(str(e))
            return False
        if 0 == len(elements) : 
            logger.error("Zero element found,please check the xpath(" + str(xpath) + ")!")
            return False
        elif len(elements) > 1 :
            logger.error("More than one element,please check the xpath(" + str(xpath) + ")!")
            return False
        return elements[0]

    # 同时定位多个类似的元素位置
    def getElementsByXpath(self , xpath , number_of_elements=None) :
        try :
            #elements_wait = WebDriverWait(self.browser , 30)
            #elements = elements_wait.until(lambda driver:driver.find_elements_by_xpath(xpath))
            elements = self.browser.find_elements_by_xpath(xpath)
        except Exception as e :
            logger.error(str(e))
            return False
        if 0 == len(elements) :
            logger.error("Zero element found,please chech the xpath(" + str(xpath) + ")!")
            return False
        elif None != number_of_elements and number_of_elements != len(elements) :
            logger.error("Not the number of elements(" + str(number_of_elements) +") input,please check the xpath(" + str(xpath) + ")!")
            return False
        return elements

    # 获取元素位置
    # @param tag 标签名
    # @param ele 元素名
    # @param xpath xpath
    def getElements(self , tag="" , ele="" , xpath=None) :
        if None == xpath :
            xpath = ""
            if ""==tag and ""==ele :
                xpath = "//*"
            elif ""!=tag and ""==ele :
                xpath = "//" + tag + "[@*]"
            elif ""==tag and ""!=ele :
                xpath = "//*[@" + ele + "]"
            elif ""!=tag and ""!=ele :
                xpath = "//" + tag + "[@" + ele + "]"
            else :
                logger.error("tag(" + str(tag) + ") and ele(" + str(ele) + ") is error!")
                return False
        try :
            elements = self.browser.find_elements_by_xpath(xpath)
        except Exception as e :
            logger.error(str(e))
            return False
        return elements

    # 获取元素的属性
    def getAttributesOfElements(self , att=None , tag="" , ele="" , xpath=None) :
        if None == att :
            logger.error("att(" + str(att) + ") is error!")
            return False
        if None == xpath :
            xpath = ""
            if ""==tag and ""==ele :
                xpath = "//*"
            elif ""!=tag and ""==ele :
                xpath = "//" + tag + "[@*]"
            elif ""==tag and ""!=ele :
                xpath = "//*[@" + ele + "]"
            elif ""!=tag and ""!=ele :
                xpath = "//" + tag + "[@" + ele + "]"
            else :
                logger.error("tag(" + str(tag) + ") and ele(" + str(ele) + ") is error!")
                return False
        results = []
        elems = self.browser.find_elements_by_xpath(xpath)
        for elem in elems :
            try :
                att_res = elem.get_attribute(att)
                results.append(att_res)
            except Exception as e :
                logger.error(str(e))
                continue
        return results

    # 获取网页源码
    # @param browser_or_element 指定获取某元素或者整个网页
    def getPageSource(self , browser_or_element , element=None) :
        page_html = ""
        if 1 == browser_or_element :
            # 获取整个网页源码
            try :
                page_html = self.browser.page_source
            except Exception as e :
                logger.error(str(e))
                return False
        elif 2 == browser_or_element :
            # 获取指定元素源码
            if None == element :
                logger.error("element is None.")
                return False
            try :
                page_html = element.get_attribute("innerHTML")
            except Exception as e :
                logger.error(str(e))
                return False
        return page_html
    
if __name__ == "__main__" :
    url = "http://www.autohome.com.cn/use/"
    #http;111.13.136.46;80
    proxy_dict = {"nettype":"http" , "ip":"117.90.0.229" , "port":"9000"}
    sesp = SeleniumSpider(proxy_dict , is_browser_profile=True)
    sesp.startSelenium()
    sesp.getWebsite(url)
    html = sesp.getPageSource(1)
    print(len(html))
    sesp.stopSelenium()
