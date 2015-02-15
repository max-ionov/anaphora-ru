#!/usr/bin/python2.7
# -!- coding: utf-8 -!-
# author: Max Ionov, max.ionov@gmail.com

import os, sys, codecs

FILTERS_PATH = 'lemmatizer-filters/'

class Lemmatizer:
    """
    This is the class for tagging and parsing text.
    It is library-independent in such way: for the desired library there should be python module
    in the folder FILTERS_PATH with the following elements implemented:
     # tag_text -- method that takes text as input and returns list of tagged items, objects with three fields: wordform, lemma, tag
     # pos_filters -- dictionary of lambda expressions like 'noun', 'adj' that Lemmatizer class can operate with
     # agreement_filters -- dictionary of lambda expressions used for chunk parsing
     # np_conjunction -- lambda expression used for conjunction parsing
    """

    def __init__(self, lemmatizer_filter):
        if not os.path.isfile(FILTERS_PATH + lemmatizer_filter + '.py'):
            raise AttributeError('No lemmatizer filters named %s' % lemmatizer_filter)
        sys.path.append(FILTERS_PATH)
        self.module = __import__(lemmatizer_filter)
        self.tagger = self.module.load()

    def _new_word(self, class_name, attr_dict):
        return type(class_name, (object,), attr_dict)

    def _normalize_groups(self, groups):
        for group in groups:
            group.wordform = group.wordform.replace(u'« ', u'«').replace(u' »', u'»').replace(u' , ', u', ')
            group.lemma = group.lemma.replace(u'« ', u'«').replace(u' »', u'»').replace(u' , ', u', ')

        return groups

    def _is_group(self, word1, word2):
        group = None
        for agr in self.module.agreement_filters:
            res = self.module.agreement_filters[agr](word1, word2)
            if res:
                group = res
                break

        return self._new_word('Group',
                              {'wordform': word1.wordform + ' ' + word2.wordform,
                               'lemma': word1.lemma + ' ' + word2.lemma,
                               'tag': group,
                               'prob': str(float(word1.prob) * float(word2.prob)),
                               'offset': word1.offset,
                               'length': (word2.offset + word2.length) - word1.offset,
                               'type': 'agr'})\
            if group else None

    def set_tagger(self, tagger):
        self.tagger = tagger

    def is_saved(self, filename):
        return os.path.isfile(filename + '.words')

    def is_saved_groups(self, filename):
        return os.path.isfile(filename + '.groups')

    def save(self, filename):
        pass


    def load(self, filename):
        pass

    def get_conjunctions(self, items):
        groups = items[:]
        was_merge = True

        while was_merge:
            was_merge = False
            for i in range(2, len(groups)):
                if i >= len(groups):
                    continue
                res = self.module.np_conjunction(groups[i - 2], groups[i - 1], groups[i])
                if res:
                    main_word_tag = groups[i - 2].tag
                    conj_group = self._new_word('Group',
                                          {'wordform': ' '.join(item.wordform for item in groups[i-2:i+1]),
                                           'lemma': ' '.join(item.lemma for item in groups[i-2:i+1]),
                                           'tag': res,
                                           'prob': 1.0,
                                           'offset': groups[i-2].offset,
                                           'length': (groups[i].offset + groups[i].length) - groups[i-2].offset,
                                           'type': 'conj'})
                    was_merge = True
                    groups.pop(i-2)
                    groups.pop(i-2)
                    groups.pop(i-2)
                    groups.insert(i-2, conj_group)

        return self._normalize_groups(groups)

    def get_groups(self, items, conjunctions = False):
        groups = items[:]
        was_merge = True

        while was_merge:
            was_merge = False
            for i in range(1, len(groups)):
                group = self._is_group(groups[i - 1], groups[i])
                if group:
                    was_merge = True
                    groups.pop(i - 1)
                    groups.pop(i - 1)
                    groups.insert(i - 1, group)

                    break

        return self.get_conjunctions(self._normalize_groups(groups)) if conjunctions else self._normalize_groups(groups)

    def lemmatize(self, text, start_offset = 0, load_from = None):
        return self.module.tag_text(text, self.tagger if self.tagger else None)