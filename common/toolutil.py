#!/usr/bin/python
#encoding:utf8
import re
import urllib2 as url
import string
import urllib
import cookielib

def getList(regex,text):
    '''
    输入：正则表达式，文本
    输出：匹配到的数组(默认使用findall匹配)
    '''
    arr = []
    res = re.findall(regex, text)
    if res:
        for r in res:
            arr.append(r)
    return arr

def strToArray(line):
    arr = []
    for value in line.split(','):
        arr.append(value)
    return arr

def getJobsHtml(job_type='job',job_id='all'):
    '''获取页面html'''
    if job_type == 'job':
        query = "http://hd00:50030/jobtracker.jsp" #hd00的写法不可依赖
    elif job_type == 'job_detail':
        query = "http://hd00:50030/jobdetails.jsp?jobid=" + job_id
    elif job_type == 'job_conf':
        query = "http://hd00:50030/jobconf.jsp?jobid=" + job_id
    else:
        print "do'not support. use <job> or <jobdetail> "
    cj = cookielib.CookieJar()
    opener=url.build_opener(url.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent', 'Opera/9.23')]
    url.install_opener(opener)
    req=url.Request(query)
    response =url.urlopen(req)
    html = response.read().decode('utf-8')
    return html

def parseRunningTime(running_time):
    '''将执行时间转成s'''
    running_time_int = 0
    try:
        if len(running_time.split(',')) == 2:
            times = getList(u"([\d]+)mins[\D]+([\d]+)sec", str(running_time).strip() )
            running_time_int =  int( times[0][0] ) * 60 + int(times[0][1])
        elif len(running_time.split(',')) == 1:
            times = getList(u"([\d]+)sec", str(running_time).strip() )
            running_time =  int( times[0][0] )
    except Exception,e :
        print e
    return running_time_int
