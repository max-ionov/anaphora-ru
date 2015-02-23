#!/usr/bin/python2.7
# -!- coding: utf-8 -!-
# usage: anaphoramllib.py

from __future__ import unicode_literals

import os, sys, codecs, re
import cPickle
import lemmatizer

from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn import tree, svm
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline

class AnaphoraResolutor:
    def __init__(self, lemmatizer):
        self.lemmatizer = lemmatizer

    def get_antecedent(self, group, groups):
        return None

    #def resolute_anaphora(self, groups):
    #    return []

class AnaphoraMLResolutor(AnaphoraResolutor):
    def load_model(self):
        pass

class AnaphoraDummyResolutor(AnaphoraResolutor):
    def group_fits(self, potential_antecedent, anaphor):
        return True

    def get_antecedent(self, target_group, groups):
        antecedents = sorted([group for group in groups
                              if group.offset < target_group.offset and self.lemmatizer.module.pos_filters['noun'](group)
                             and self.group_fits(group, target_group)],
                             key=lambda x: x.offset, reverse=True)
        return antecedents[0] if len(antecedents) > 0 else None

class AnaphoraAgrResolutor(AnaphoraDummyResolutor):
    def group_fits(self, potential_antecedent, anaphor):
        return self.lemmatizer.module.same_grammemmes('gender', (potential_antecedent, anaphor)) and \
                self.lemmatizer.module.same_grammemmes('number', (potential_antecedent, anaphor))
        #return 'ед' in potential_antecedent.tag['gr'] and 'ед' in anaphor.tag['gr']