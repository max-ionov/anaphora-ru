#!/usr/bin/python2.7
# -!- coding: utf-8 -!-
# usage: freeling.py

from __future__ import unicode_literals

import os, sys
import re
import pymystem3

"""
This is the recommended way to check against part of speech. Add a lambda-function for the desired POS
and use it in your code in the following way: pos_filters['desired_pos'](word), where word is a list
"""
pos_filters = {
    'noun': lambda x: x.tag['pos'] in ['S', 'NP', 'PP'],
    'adj': lambda x: x.tag['pos'] in ['A', 'ANUM'],
    'properNoun': lambda x: len(x.tag['gr'] & frozenset([u'имя', u'фам'])) > 0,
    'pronoun': lambda x: x.tag['pos'] == ['SPRO'],
    'comma': lambda x: x.wordform == u',',
    'prep': lambda x: x.tag['pos'] == 'PR',
    'firstName': lambda x: x.tag['pos'] == 'S' and u'имя' in x.tag['gr'],
    'secondName': lambda x: x.tag['pos'] in ['A', 'S'] and u'фам' in x.tag['gr'],
    'middleName': lambda x: x.tag['pos'] == 'S' and u'отч' in x.tag['gr'],
    'conj': lambda x: x.tag['pos'] == 'CONJ' and x.wordform in [u'и', u'а', u'но'],
    'quant': lambda x: x.tag['pos'] == 'NUM',
}

gram_values = {
    'number': frozenset(['ед', 'мн']),
    'gender': frozenset(['муж', 'сред', 'жен']),
    'case': frozenset(['им', 'род', 'дат', 'вин', 'твор', 'пр', 'парт', 'местн', 'зват'])
}

def same_grammemmes(name, words):
    if name not in gram_values:
        return True

    for feature in gram_values[name]:
        if all(feature in item.tag['gr'] for item in words):
            return True
    return False


"""
This is the list of groups which we are trying to extract. To disable any of the groups, just comment it
"""
agreement_filters = {
    'adjNoun': lambda adj, noun: {'pos': 'NP', 'gr': noun.tag['gr']} if (
        pos_filters['adj'](adj) and pos_filters['noun'](noun) and
        same_grammemmes('number', (adj, noun)))
    else None,

    'quantNoun': lambda quant, noun: {'pos': 'NP', 'gr': noun.tag['gr']} if (
        pos_filters['quant'](quant) and pos_filters['noun'](noun) and
        same_grammemmes('number', (quant, noun)))
    else None,

    'name': lambda name, surname: {'pos': 'NP', 'gr': name.tag['gr']} if (
        pos_filters['firstName'](name) and (pos_filters['secondName'](surname) or pos_filters['middleName'](surname)) and
        same_grammemmes('number', (name, surname)) and same_grammemmes('case', (name, surname)))
    else None
}

np_conjunction = lambda word1, conj, word2: {'pos': 'NP', 'gr': [u'мн']} if (
    pos_filters['noun'](word1) and pos_filters['noun'](word2) and pos_filters['conj'](conj)) else None


def load():
    parser = pymystem3.Mystem()
    return lambda text: parser.analyze(text)

tokens_to_skip = ['', ' ', '\n', '\r', '\t', '«', '»', '"']
rx_grammemmes_splitter = re.compile('[^А-ЯЁа-яёA-Za-z]', re.UNICODE)

def tag_text(text, analyzer):
    ret = []
    text_part = text[:]
    prev_offset = 0

    for word in analyzer(text):
        if word['text'].strip(' ') in tokens_to_skip:
            continue
        word_info = word['analysis'][0] if 'analysis' in word and len(word['analysis']) > 0 else None
        new_word = type(b'Word', (object,),
                        {'wordform': word['text'],
                         'lemma': word_info['lex'] if word_info else word['text'],
                         'tag': word_info['gr'] if word_info else 'PUNCT',
                         'prob': 1.0,
                         'offset': prev_offset + text_part.find(word['text']),
                         'length': len(word['text']),
                         'type': 'word'})


        grammemmes = rx_grammemmes_splitter.split(new_word.tag)
        new_word.tag = {'pos': grammemmes[0], 'gr': frozenset(grammemmes[1:])}
        ret.append(new_word)

        text_part = text[new_word.offset + new_word.length:]
        prev_offset = new_word.offset + new_word.length

    return ret