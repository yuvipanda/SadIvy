#!/usr/bin/env python
import gammu
import sys
import codecs

sm = gammu.StateMachine()
sm.ReadConfig()
sm.Init()

status = sm.GetSMSStatus()

remain = status['SIMUsed'] + status['PhoneUsed'] + status['TemplatesUsed']

start = True
folder = int(sys.argv[1])
f = codecs.open(sys.argv[2], 'w', 'utf-8')

while remain > 0:
    if start:
        sms = sm.GetNextSMS(Start = True, Folder = 0)
        start = False
    else:
        sms = sm.GetNextSMS(Location = sms[0]['Location'], Folder = 0)
    remain = remain - len(sms)

    for m in sms:
        if folder == m['Folder']:
            f.write('%-15s: %s' % ('Number', m['Number']) + "\n")
            f.write('%-15s: %s' % ('Date', str(m['DateTime'])) + "\n")        
            f.write(m['Text'] + "\n")
            f.write("--------------\n")

f.close()
