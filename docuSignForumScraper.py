import os
import re
import urllib2
import datetime
import numpy

alllinks = []
timelist = []
for filename in os.listdir(os.getcwd()):
    if filename.endswith(".rss"):
        f=open(filename, 'r')
        linktext = ''
        linkurl = ''
        for line in f:
            linktext = re.search('(<guid>)(.+?)(<\/guid>)', line)    
            
            if linktext:
                linkurl= linktext.group(2)
                alllinks.append(linkurl)
        f.close()

mainmessage = ''
reply = ''
maindateobj = datetime.datetime.today()
replydateobj = datetime.datetime.today()
for item in alllinks:
    print "==="
    print "working on thread\n" + item
    response = urllib2.urlopen(item)
    html = response.read()    
    tuples = re.findall('lia-message-posted-on\">\s+<span class=\"local-date\">\\xe2\\x80\\x8e(.*?)<\/span>\s+<span class=\"local-time\">([\w:\sAM|PM]+)<\/span>', html)	
    mainmessage = tuples[0]
    if len(tuples) > 1:
        reply = tuples[1]
    if mainmessage:
        print "main: "
        #print mainmessage
        maindateasstr = mainmessage[0] + " " + mainmessage[1]
        print maindateasstr
        maindateobj = datetime.datetime.strptime(maindateasstr, '%m-%d-%Y %I:%M %p')
    if reply:
        print "reply: "
        #print reply
        replydateasstr = reply[0] + " " + reply[1]
        print replydateasstr
        replydateobj = datetime.datetime.strptime(replydateasstr, '%m-%d-%Y %I:%M %p')

        # only calculate difference if there was a reply 
        difference = replydateobj - maindateobj
        totalseconds = difference.total_seconds()
        timeinhours =  (difference.days*86400+difference.seconds)/3600
        # this is a hack to take care of negative times
        # I should probably handle this with timezones but alas
        if timeinhours > 1:
            print timeinhours
            timelist.append(timeinhours)
            
print "when all is said and done, in hours:"
print numpy.mean(timelist)
print numpy.std(timelist)
print numpy.median(timelist)
