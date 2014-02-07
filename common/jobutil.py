import ConfigParser
import os

def get_job_conf(section, option):
    config_path = os.path.join(os.environ["TANK_HOME"], "config/job.conf")
    cf = ConfigParser.ConfigParser()
    cf.read(config_path)
    opt = cf.get(section, option)
    if opt:
        return int(opt)
    else:
        return 0

def get_max_running_time():
    default_max_running_time = 3600
    max_running_time = get_job_conf('job', 'max_running_time') 
    if max_running_time == 0:
        return default_max_running_time
    else:
        return max_running_time

def get_max_map_num():
    default_max_map_num = 10000
    max_map_num = get_job_conf('job', 'max_map_num')
    if max_map_num == 0:
        return default_max_map_num
    else:
        return max_map_num

