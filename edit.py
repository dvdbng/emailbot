from pyshutils import *
import sys

cmd = sys.argv[1]
conf = sys.argv[2]

noise_mails = load("/usr/lib/emailrobot/noise-" + conf,set([]))
if cmd == "list":
    print "\n".join(noise_mails)
elif cmd == "rm":
    noise_mails.remove(sys.argv[2])
    save("/usr/lib/emailrobot/noise-" + conf,noise_mails)
