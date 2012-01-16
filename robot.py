#!/usr/bin/env python

import imaplib2, re, datetime
from email.parser import Parser
from email.header import decode_header
import config
from threading import Event
from daemon import Daemon
from pyshutils import *

noise_mails = load("/usr/lib/emailrobot/noise",set([]))
last_connect = None

parser = Parser()
idle_event = Event()

def connect():
    global last_connect
    # Don't connect twice in 5 minutes, since the server probably overloaded
    assert last_connect is None or (datetime.datetime.now() - datetime.timedelta(0, 60*5)) > last_connect
    last_connect = datetime.datetime.now()
    M = imaplib2.IMAP4_SSL(config.HOST, config.PORT)
    M.login(config.USER, config.PASS)
    M.select("INBOX")
    return M

def callback(arg):
    global aborted
    res,arg,abr = arg
    if abr is not None:
        print "aborted", abr
        aborted = True

    idle_event.set()

def remove_re(subject):
    m = re.search("\s*(Re:(\s*))*",subject) # Note that this will allways match
    return re.sub("\s+"," ",subject[m.end():])

def get_subjet(headers):
    dh = decode_header(parser.parsestr(headers,headersonly=True)["Subject"])
    return remove_re(''.join([ unicode(t[0], t[1] or "ASCII") for t in dh ]))

def msg_iterator(M,query):
    status,res = M.search(None, query)
    assert status == "OK"
    assert len(res)>0
    ids = res[0].split()
    if len(ids)>0:
        status,headers = M.fetch(",".join(ids),"(BODY.PEEK[HEADER.FIELDS (subject)])")
        assert status == "OK"
        for i in range(len(ids)):
            yield (ids[i],get_subjet(headers[i*2][1]))

def delete_messages(msglist,M):
    if len(msglist) > 0:
        msgs = ",".join(msglist)
        assert M.copy(msgs,"Ruido")[0] == "OK"
        assert M.store(msgs,"+FLAGS","\\Deleted")[0] == "OK"
        assert M.expunge()[0] == "OK"

# Buscar nuevos mensajes marcados como "Ruido"
def find_noise(M):
    changed = False
    M.select("AddRuido")
    msgs = []

    for i,subject in msg_iterator(M,"ALL"):
        noise_mails.add(subject)
        msgs.append(i)
        changed = True
        print "Nueva conversacion ruidosa", subject

    delete_messages(msgs,M)
    msgs = []

    M.select("INBOX")
    date = (datetime.date.today() - datetime.timedelta(5)).strftime("%d-%b-%Y")
    for i,subject in msg_iterator(M,"(SENTSINCE "+date+")"):
        if subject in noise_mails:
            print "Filtered by noise-filter:", subject
            msgs.append(i)

    delete_messages(msgs,M)

    if changed:
        print "saving..."
        save("/usr/lib/emailrobot/noise",noise_mails)

class MailRobot(Daemon):
    def run(self):
        global M,aborted
        M = connect()
        while True:
            print "finding noise..."
            find_noise(M)
            print "idling..."
            M.idle(callback=callback)
            idle_event.wait()
            idle_event.clear()
            if aborted: # Connection reset
                aborted = False
                M = connect()

MailRobot("/var/run/emailrobot.pid",stdout="/var/log/emailrobot.log",stderr=None).start()

