import imaplib2, re, datetime
import config
from threading import Event
from pyshutils import *

noise_mails = load("noise",set([]))

M = imaplib2.IMAP4_SSL(config.HOST,config.PORT)
M.login(config.USER,config.PASS)
M.select("INBOX")
idle_event = Event()


def callback(*args,**kwargs):
    idle_event.set()

def remove_re(subject):
    m = re.search("\s*(Re:(\s*))*",subject) # Note that this will allways match
    return subject[m.end():]

def get_subjet(headers):
    subject = None
    subject_header = "Subject: "
    for header in headers.split("\r\n"):
        if header.startswith(subject_header):
            subject = remove_re(header[len(subject_header):])
    assert subject is not None
    return subject


def msg_iterator(M,query):
    status,res = M.search(None, query)
    assert status == "OK"
    assert len(res)>0
    for i in res[0].split():
        status,headers = M.fetch(i,"(BODY.PEEK[HEADER])")
        assert status == "OK"
        if len(headers)>0 and headers[0] is not None:
            yield (i,get_subjet(headers[0][1]))
        else:
            print "Mensaje sin cabeceras", headers

# Buscar nuevos mensajes marcados como "Ruido"
def find_noise(M):
    changed = False
    M.select("AddRuido")

    for i,subject in msg_iterator(M,"ALL"):
        noise_mails.add(subject)
        changed = True
        print "Nueva conversacion ruidosa", subject
        M.copy(i,"Ruido")
        M.store(i,"+FLAGS","\\Deleted")
    M.expunge()

    M.select("INBOX")
    date = (datetime.date.today() - datetime.timedelta(5)).strftime("%d-%b-%Y")
    for i,subject in msg_iterator(M,"(SENTSINCE "+date+")"):
        if subject in noise_mails:
            print "Filtered by noise-filter:", subject
            M.copy(i,"Ruido")
            M.store(i,"+FLAGS","\\Deleted")
    M.expunge()

    if changed:
        print "saving..."
        save("noise",noise_mails)

while True:
    find_noise(M)
    print "idling..."
    M.idle(callback=callback)
    idle_event.wait()
    idle_event.clear()

