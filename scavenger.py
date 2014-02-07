#!/usr/bin/python
#encoding:utf8

import urllib2 as url
import string
import urllib
import re
import time
import cookielib
from bs4 import BeautifulSoup
import os
from common.toolutil import getList, getJobsHtml, parseRunningTime
from common.jobutil import get_max_running_time, get_max_map_num
from common.mailman import sendEmailByDefault
import pdb

class Job():
    '''Job类'''

    def __init__ (self):
        '''Job初始化'''
        self.job_id = 0
        self.job_name = 0
        self.map_num = 0
        self.reduce_num = 0
        self.submit_host = ""
        self.submit_address = ""
        self.start_time = ""
        self.running_time = ""
        self.hive_sql = ""

    def who_am_i(self):
        '''打印Job信息'''
        htmlText = "<br><b>++++++++++++ begin ++++++++++++++<b><br>"
        htmlText += "job_id=%s <br>" % self.job_id
        htmlText += "map_num=%d <br>" % self.map_num
        htmlText += "reduce_num=%d <br>" % self.reduce_num
        htmlText += "running_time=%s <br>" % self.running_time
        htmlText += "job_name=%s <br>" % self.job_name
        htmlText += "job_sql=%s <br>" % self.hive_sql
        htmlText += "<b>++++++++++++ end ++++++++++++++<b><br>"
        return htmlText
    
    def self_check(self, max_map_num, max_time_num):
        '''自杀函数'''
        if self.map_num >= max_map_num or parseRunningTime(self.running_time) > max_time_num :
            return True, self.who_am_i()
        else:
            return False, False

class Scavenger():

    def __init__(self):
        '''清道夫born'''
        self.job_list = {}
        self.job_query = "http://hd00:50030/jobtracker.jsp"
        self.job_detail_query = "http://hd00:50030/jobdetails.jsp?jobid="
        self.job_conf_query = "http://hd00:50030/jobconf.jsp?jobid="
        self.max_map_num = get_max_map_num()
        self.max_running_time = get_max_running_time()
        self.kill_list = set()
        self.mail_title = "scavenger邮件报告"
        self.mail_text = "被杀掉的Job&其信息"
        self.mail_html = "被杀掉的Job&其信息"
    
    def get_jobs(self):
        '''初始化jobs字典'''
        html_result = getJobsHtml()
        running_html = re.findall("<h2.*?id=\"running_jobs\">[\s\S]*?<h2.*?id=\"completed_jobs\">", html_result)

        #Get-job_id : use bs
        soup = BeautifulSoup(str(running_html))
        for ajob in soup.find_all("a"):
            job_id = ajob.string
            if not self.job_list.has_key(job_id):
                self.job_list[job_id] = Job()
                self.job_list[job_id].job_id = job_id

        #Get-job map_num & reduce_num 
        mr_details = getList(u"<td id=\"job_.*?<td>NA<\/td><\/tr>", str(running_html).strip() )
        for mr_detail in mr_details:
            #print mr_detail
            job_ids = getList(u".*jobid=([^&]+).*", str(mr_detail).strip() )
            mr_infos = getList(u"<td>(.*?)</td>", str(mr_detail).strip() )
            try :
                job_id = job_ids[0]
                map_num, reduce_num = mr_infos[1], mr_infos[4]
                if not self.job_list.has_key(job_id):
                    print "job %s not in dict" % job_id
                else:
                    self.job_list[job_id].map_num = int(map_num)
                    self.job_list[job_id].reduce_num = int(reduce_num)
            except Exception , e:
                print e
                print "error : %s " % str(mr_detail)


    def get_jobs_detail(self):
        '''获取job的详细配置'''
        for job_id in self.job_list:
            job_detail_html = getJobsHtml('job_detail',job_id)
            job_detail = getList(u"<\/b>(.*?)<br>", str(job_detail_html).strip() )
            if len(job_detail) == 11:
                user, name, jf, sm_host, sm_address, no_1, no_2, status, start_time, run_time, jb_clean = job_detail 
                self.job_list[job_id].job_name = name
                self.job_list[job_id].submit_host = sm_host
                self.job_list[job_id].submit_address = sm_address
                self.job_list[job_id].start_time = start_time
                self.job_list[job_id].running_time = run_time
            elif len(job_detail) == 10:
                user, jf, sm_host, sm_address, no_1, no_2, status, start_time, run_time, jb_clean = job_detail 
                self.job_list[job_id].job_name = job_id
                self.job_list[job_id].submit_host = sm_host
                self.job_list[job_id].submit_address = sm_address
                self.job_list[job_id].start_time = start_time
                self.job_list[job_id].running_time = run_time
            else:
                print "len != 11"
                print "error : %s " % str(job_detail)


    def get_jobs_conf(self):
        '''获取Job的hive.sql'''
        for job_id in self.job_list:
            job_conf_html = getJobsHtml('job_conf',job_id)
            sql_info = getList(u"hive.query.string.*<td.*>([\s\S]+)\s</td>", str(job_conf_html))
            if len(sql_info):
                self.job_list[job_id].hive_sql = sql_info[0].replace('\n','')
            else:
                sql_info = getList(u"hive.query.string.*<td.*>([\s\S]+)</td>[\s\S]+<td width=\"35%\"><b>mapred.working.dir", str(job_conf_html))
                if len(sql_info):
                    self.job_list[job_id].hive_sql = sql_info[0].replace('\n','')
                else:
                    self.job_list[job_id].hive_sql = "no hive sql"

    def check_jobs(self):
        '''检查job,需要杀掉的添加到列表,并拿到Job信息'''
        for job_id in self.job_list:
            to_kill, to_kill_job_info = self.job_list[job_id].self_check(self.max_map_num, self.max_running_time)
            if to_kill:
                self.kill_list.add(job_id)
                self.mail_html += to_kill_job_info.encode('utf8')

    def kill_jobs(self):
        '''杀掉Jobs'''
        if len(self.kill_list) > 0:
            #sys_cmd = "hadoop job -kill %s" % " ".join(self.kill_list)
            sys_cmd = "ssh jiankuiwang@sys11  ssh work@dm02 hadoop job -kill %s" % " ".join(self.kill_list)
            print sys_cmd
            os.system(sys_cmd)
        else:
            pass

    def kill_report(self):
        '''邮件报告'''
        if len(self.kill_list) > 0:
            sendEmailByDefault(self.mail_title, self.mail_text, self.mail_html)
        else:
            pass

def main():
    print "++++++++++++++++++++++++ life begin ++++++++++++++++++++++++++++++++"
    scavenger = Scavenger()
    scavenger.get_jobs()
    scavenger.get_jobs_detail()
    scavenger.get_jobs_conf()
    print "to check jobs"
    scavenger.check_jobs()
    print "to kill jobs"
    scavenger.kill_jobs()
    print "to mail report"
    scavenger.kill_report()
    print "done %s " % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    print "++++++++++++++++++++++++ end the life ++++++++++++++++++++++++++++++++"
        
if __name__ == '__main__':
    main()

