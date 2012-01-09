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
    print args, kwargs
    idle_event.set()

def extract_id(header):
    m = re.search("<([^>]+)>",header)
    assert m is not None
    return m.groups(1)

def parse_headers(headers):
    id=None
    reply=None
    for header in headers.split("\r\n"):
        if header.startswith("In-Reply-To: "):
            reply = extract_id(header)
        elif header.startswith("Message-ID: "):
            id = extract_id(header)
    return id,reply


# Buscar nuevos mensajes marcados como "Ruido"
def find_noise(M):
    changed = False
    M.select("AddRuido")
    status,res = M.search(None, "ALL")
    assert status == "OK"
    assert len(res)>0
    for i in res[0].split():
        status,headers = M.fetch(i,"(BODY.PEEK[HEADER])")
        assert status == "OK"
        if len(headers)>0 and headers[0] is not None:
            id,reply = parse_headers(headers[0][1])
            if id is not None:
                noise_mails.add(id)
                noise_mails.add(reply)
                print "Nueva conversacion ruidosa", id
                changed = True
                M.copy(i,"Ruido")
                M.store(i,"+FLAGS","\\Deleted")
        else:
            print "Mensaje sin cabeceras WTF."
    M.expunge()

    M.select("INBOX")
    date = (datetime.date.today() - datetime.timedelta(5)).strftime("%d-%b-%Y")
    status,res = M.search(None, "(SENTSINCE "+date+")")
    assert status == "OK"
    assert len(res)>0
    for i in res[0].split():
        status,headers = M.fetch(i,"(BODY.PEEK[HEADER])")
        assert status == "OK"
        if len(headers)>0 and headers[0] is not None:
            id,reply = parse_headers(headers[0][1])
            if reply is not None and reply in noise_mails:
                print "Filtered by noise-filter:", id
                noise_mails.add(id)
                changed = True
                M.copy(i,"Ruido")
                M.store(i,"+FLAGS","\\Deleted")
        else:
            print "Mensaje sin cabeceras WTF."
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

