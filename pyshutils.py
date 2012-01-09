#!/bin/env python

# Python bash-style scripting helpers

from os import chdir as cd
import os, pickle

def load(filename,default):
    try:
        return pickle.load(open(filename,"r"))
    except IOError,e:
        return default

def save(filename,obj):
    pickle.dump(obj,open(filename,"w"))




