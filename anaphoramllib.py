#!/usr/bin/python2.7
# -!- coding: utf-8 -!-
# usage: anaphoramllib.py

import os, sys, codecs, re
import cPickle
import lemmatizer

from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn import tree, svm
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline

class AnaphoraResolutor:
    def __init__(self):
        pass

    def get_antecedent(self, group, groups, lemmatizer):
        return None

    #def resolute_anaphora(self, groups):
    #    return []

class AnaphoraMLResolutor(AnaphoraResolutor):
    def load_model(self):
        pass

class AnaphoraDummyResolutor(AnaphoraResolutor):
    def get_antecedent(self, target_group, groups, lemmatizer):
        antecedents = sorted([group for group in groups
                              if group.offset < target_group.offset and lemmatizer.module.pos_filters['noun'](group)],
                             key=lambda x: x.offset, reverse=True)
        return antecedents[0] if len(antecedents) > 0 else None