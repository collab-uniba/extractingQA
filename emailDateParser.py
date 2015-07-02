import os
import re
import email.utils
import time
import datetime
import numpy

originals = {}
replies = {}
timelist = []
        
for filename in os.listdir(os.getcwd()):
    if filename.endswith(".txt"):
        f=open(filename, 'r')
        i=''
        m=''
        d=''
        for line in f:
            irt = re.search('(In\-Reply\-To: <)(.+?)@', line)    
            mid = re.search('(Message\-ID: <)(.+?)@', line)
            dt = re.search('(Date: )(.+?)\r', line)
            if irt: 
                i= irt.group(2) 
            if mid:
                m= mid.group(2)
            if dt:
                d= dt.group(2)
        f.close()
        if i and d:
            replies[i] = d
        if m and d:
            originals[m] = d
               
for (messageid, origdate) in originals.items():
    try:
        if replies[messageid]:
            replydate = replies[messageid]                
            try:
                parseddate = email.utils.parsedate(origdate)
                parsedreply = email.utils.parsedate(replydate)
            except:
                pass
            try:
                # this still creates some malformed (error) times
                timeddate = time.mktime(parseddate)
                timedreply = time.mktime(parsedreply)
            except:
                pass
            try:
                dtdate = datetime.datetime.fromtimestamp(timeddate)
                dtreply = datetime.datetime.fromtimestamp(timedreply)
            except:
                pass
            try:
                difference = dtreply - dtdate
                totalseconds = difference.total_seconds()
                timeinhours =  (difference.days*86400+difference.seconds)/3600
                # this is a hack to take care of negative times
                # I should probably handle this with timezones but alas
                if timeinhours > 1:
                    #print timeinhours
                    timelist.append(timeinhours)
            except:
                pass
    except:
        pass
        
print numpy.mean(timelist)
print numpy.std(timelist)
print numpy.median(timelist)
