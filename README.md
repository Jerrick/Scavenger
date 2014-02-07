#Scavenger
使用背景:
    Hadoop 集群中会运行很多个Job, Job可能来源于MR脚本、Hive SQL 、Pig 脚本等, 最初公司的集群没有管理Job, 有些mapper数过大的Job会抢占所有的资源，造成其他Job进程的阻塞。而最初都是看JobTracker(50030)时发现再人工kill, 非常不够智能。所以就有了本项目的设想，监控JobTracker上的job，发现超过设定好的最大Mapper数或最长时间则kill 掉，然后邮件报告出来。

其他：
1. 很早的一个项目设想，虽然通过Hadoop的调度器可以规避本项目处理的问题，但是还是想自己写一下玩玩。
2. 代码写的很烂，但是我会一点点完善，欢迎各路大神留言指教 :)
3. 项目目前私有，初版完成后会公开
4. GitHub有同一项目，更新慢于git@osc
5. 部分代码仅适合笔者公司环境，使用时请修改，如kill job部分
6. 例行执行参考，crontab方案：*/2 * * * * cd ~/git-osc/Scavenger/; . env.sh; python scavenger.py >> /tmp/sca.log 2>&1 & 

