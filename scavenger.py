#!/usr/bin/python
#encoding:utf8

import urllib2 as url
import string
import urllib
import re
import cookielib
from bs4 import BeautifulSoup
import os

class job_record():
    '''
    this is job class
    from page 1: job_id,Map Total, Map Completed, Reduce Total,Reduce Completed
    from page 2: Submit Host,Submit Host Address, Started at,Running for,runtime
    from page 3: hive.query.string
    '''
    def __init__ (self):
        self.job_id = 0
        self.job_name = 0
        self.map_num = 0
        self.reduce_num = 0
        self.submit_host = ""
        self.submit_address = ""
        self.start_time = ""
        self.runing_time = ""
        self.hive_sql = ""

    def killJob(self):
        '''刽子手'''
        sys_cmd = "hadoop job -kill %s" % self.job_id
        os.system(sys_cmd)

    def mailMan():
        '''张榜公告'''
        print "sent mial"


def get_jobs_html(job_type='job',job_id='all'):
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

def main():
    jobs = {}
    #regex used
    html_result = get_jobs_html()
    running_html = re.findall("<h2.*?id=\"running_jobs\">[\s\S]*?<h2.*?id=\"completed_jobs\">", html_result)
    #print running_html

    #Get-job_id : use bs
    soup = BeautifulSoup(str(running_html))
    for ajob in soup.find_all("a"):
        job_id = ajob.string
        if not jobs.has_key(job_id):
            jobs[job_id] = job_record()
            jobs[job_id].job_id = job_id

    #Get-job map_num & reduce_num 
    mr_details = getList(u"<td id=\"job_.*?<td>NA<\/td><\/tr>", str(running_html).strip() )
    for mr_detail in mr_details:
        #print mr_detail
        job_ids = getList(u".*jobid=([^&]+).*", str(mr_detail).strip() )
        mr_infos = getList(u"<td>(.*?)</td>", str(mr_detail).strip() )
        try :
            job_id = job_ids[0]
            map_num, reduce_num = mr_infos[1], mr_infos[4]
            if not jobs.has_key(job_id):
                print "job %s not in dict" % job_id
            else:
                jobs[job_id].map_num = map_num
                jobs[job_id].reduce_num = reduce_num
        except Exception , e:
            print e
            print "error : %s " % str(mr_detail)

    #enter into page 2
    for job_id in jobs:
        job_detail_html = get_jobs_html('job_detail',job_id)
        #print job_detail_html
        job_detail = getList(u"<\/b>(.*?)<br>", str(job_detail_html).strip() )
        #print  job_detail
        if len(job_detail) == 11:
            user, name, jf, sm_host, sm_address, no_1, no_2, status, start_time, run_time, jb_clean = job_detail 
            jobs[job_id].job_name = name
            jobs[job_id].submit_host = sm_host
            jobs[job_id].submit_address = sm_address
            jobs[job_id].start_time = start_time
            jobs[job_id].running_time = run_time
        elif len(job_detail) == 10:
            user, jf, sm_host, sm_address, no_1, no_2, status, start_time, run_time, jb_clean = job_detail 
            jobs[job_id].job_name = job_id
            jobs[job_id].submit_host = sm_host
            jobs[job_id].submit_address = sm_address
            jobs[job_id].start_time = start_time
            jobs[job_id].running_time = run_time
        else:
            print "len != 11"
            print "error : %s " % str(job_detail)
            continue
    
    #enter into page 3
    for job_id in jobs:
        job_conf_html = get_jobs_html('job_conf',job_id)
        sql_info = getList(u"hive.query.string.*<td.*>([\s\S]+)\s</td>", str(job_conf_html))
        if len(sql_info):
            print job_id
            print sql_info[0].replace('\n','')

if __name__ == '__main__':
    main()

