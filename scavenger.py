#!/usr/bin/python
#encoding:utf8

import urllib2 as url
import string
import urllib
import re
import cookielib

def get_jobs_html(type,job_id):
    if type == 'job':
        query = "http://hd00:50030/jobtracker.jsp" #hd00的写法不可依赖
    elif type == 'jobdetail':
        query = "http://hd00:50030/jobconf.jsp?jobid=" + job_id
    else:
        print "do'not support. user <job> or <jobdetail> "
    cj = cookielib.CookieJar()
    opener=url.build_opener(url.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent', 'Opera/9.23')]
    url.install_opener(opener)
    req=url.Request(query)
    response =url.urlopen(req)
    html = response.read().decode('utf-8')
    return html

def getList(regex,text):
    arr = []
    res = re.findall(regex, text)
    if res:
        for r in res:
            arr.append(r)
    return arr

def main():
    jobs = []
    html_result = get_jobs_html("job","all")
    running_html = re.findall("<h2.*?id=\"running_jobs\">[\s\S]*?<h2.*?id=\"completed_jobs\">", html_result)
    #print running_html
    attrList = getList(u"<a.*?href=\"(.*?)\".*?>(.*?)</a>", str(running_html))
    for item in attrList:
        jobs.append(item[1])
    
    print jobs
    
    for job_id in jobs:
        job_detail_html = get_jobs_html('jobdetail',job_id)
        #print job_detail_html
        detail_html = re.findall("<b>mapred.*?map.*?tasks<\/b>.*?<td width=\"65%\">([\s\S]*?)<\/td>[\s\S]*?mapred.*?local.*?dir.*?minspacekill[\s\S]*?<b>hive.*?query.*?string<\/b>.*?<td width=\"65%\">([\s\S]*?)<\/td>[\s\S]*?mapred.*?working.*?dir", job_detail_html)
        print detail_html
        #job_info = getList(u"<a.*?href=\"jobconf.*?jsp.*?jobid=(.*?)\">(.*?)<\/a>.*?Started.*?<\/b>(.*?)<br>.*?Running.*?<\/b>(.*?)<br>.*?", str(detail_html))
        #print job_info
        #for item in job_info:
        #    print item

if __name__ == '__main__':
    main()

