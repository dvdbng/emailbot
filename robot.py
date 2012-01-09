import imaplib2, re, datetime
from email.parser import Parser
from email.header import decode_header
import config
from threading import Event
from pyshutils import *

noise_mails = load("noise",set([]))

M = imaplib2.IMAP4_SSL(config.HOST,config.PORT)
M.login(config.USER,config.PASS)
M.select("INBOX")
parser = Parser()
idle_event = Event()


def callback(*args,**kwargs):
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
    print "finding noise..."
    find_noise(M)
    print "idling..."
    M.idle(callback=callback)
    idle_event.wait()
    idle_event.clear()
