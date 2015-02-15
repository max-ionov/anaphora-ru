#!/usr/bin/python2.7
# usage: train-anaphora.py corpus-path model-name

import os, sys, codecs
import cPickle as pckl
from lxml import etree

import anaphoramllib

usage = "train-anaphora.py corpus-path model-name"

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print (usage)
        sys.exit()

    anaphora_resolutor = anaphoramllib.AnaphoraMLResolutor()