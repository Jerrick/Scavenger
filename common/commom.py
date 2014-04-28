import ConfigParser
import os

def get_common_conf(section, option):
    config_path = os.path.join(os.environ["TANK_HOME"], "config/commom.conf")
    cf = ConfigParser.ConfigParser()
    cf.read(config_path)
    opt = cf.get(section, option)
    if opt:
        return opt
    else:
        return 0

def get_master_ip():
    default_master_ip = "172.0.0.1"
    master_ip = get_common_conf('scavenger', 'master_ip') 
    if master_ip == 0:
        return default_master_ip
    else:
        return master_ip

def get_jump_to_kill_job():
    default_jump_to_kill_job = 10000
    jump_to_kill_job = get_common_conf('scavenger', 'jump_to_kill_job')
    if jump_to_kill_job == 0:
        return default_jump_to_kill_job
    else:
        return jump_to_kill_job

