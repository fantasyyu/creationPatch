#!/usr/bin/env python

import smtplib
import email
from email.parser import Parser
from email.mime.text import MIMEText
from email.header import decode_header
from email.utils import parseaddr

import datetime

#server = smtplib.SMTP(smtp_server, 25)
#server.set_debuglevel(1)
#server.login(from_addr,password)
#server.sendmail(from_addr,[to_addrs],msg.as_string())
#server.quit()

import logging

def send_mail(content):
    sender='jian.yu@autodesk.com'
    mailto_list=['jian.yu@autodesk.com']
    msg = MIMEText("Please get your patch from "+content,_subtype='plain')
    subject = "Your Patch is ready"
    try:
        msg['From'] = sender
        msg['To'] = ','.join(mailto_list)
        msg['Subject'] = subject
        text = msg.as_string()
        s = smtplib.SMTP('connect.autodesk.com')
        s.sendmail(sender, mailto_list, text)
        s.quit()
        return True
    except Exception as e:
        print (str(e))
        return False

#send_mail("\\\\10.148.172.132\\shared\\patch\\"+ProductAliasName+"_patch.msp")
now = datetime.datetime.now()

print ("Current date and time using instance attributes:")
print ("Current year: %d" % now.year)
print ("Current month: %d" % now.month)
print ("Current day: %d" % now.day)
print ("Current hour: %d" % now.hour)
print ("Current minute: %d" % now.minute)
print ("Current second: %d" % now.second)
print ("Current microsecond: %d" % now.microsecond)
