from pyshutils import *
import sys

cmd = sys.argv[1]

noise_mails = load("/usr/lib/emailrobot/noise",set([]))
if cmd == "list":
    print "\n".join(noise_mails)
elif cmd == "rm":
    noise_mails.remove(sys.argv[2])
    save("/usr/lib/emailrobot/noise",noise_mails)
