#!/bin/bash

#source ~/.bashrc
#source /etc/profile
function getCurrentPath() 
{
    local _tmp_=`echo $0|grep "^/"`
    if test "${_tmp_}"
    then
        dirname $0
    else 
        dirname `pwd`/$0
    fi
}
workdir=$(getCurrentPath)
ttg="/."
ta=${workdir:${#workdir}-2:${#workdir}}
if [ "$ttg" = "$ta" ] 
then
    workdir=${workdir:0:-2}
fi

:<<!
logfile="${workdir}/logs/run.log"
function log()
{
    echo `date '+%Y-%m-%d %H:%M:%S'` $*
    echo `date '+%Y-%m-%d %H:%M:%S'` $* >> ${logfile}
}
!
function log()
{
    echo `date '+%Y-%m-%d %H:%M:%S'` $* 
}

pre_time=`date +%Y%m%d%H -d '-4 hours'`
test_time=`date +%Y%m%d%H%M%S`

#-------------------------------------Customize----------------------------------+
#
#--------------------------------------------------------------------------------+

echo $workdir
log "-----------------------------------------------------------------------------"
log "start"
python3 ${workdir}/__easy_setup__.py -p "${workdir}"
log "end"
log "-----------------------------------------------------------------------------"
