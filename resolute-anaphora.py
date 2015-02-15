#!/usr/bin/python2.7
# -!- coding: utf-8 -!-
# usage: resolute-anaphora.py input

import os, sys, codecs
import lemmatizer
import anaphoramllib
import configparser

usage = 'usage: resolute-anaphora.py input'
config_filename = 'config.txt'

def load_pronouns(filename):
    pronouns = []
    inp_file = codecs.open(filename, encoding='utf-8')
    for line in (line_raw.strip('\r\n') for line_raw in inp_file):
        pronouns.extend(line.split('\t')[1:])

    return set(pronouns)

if (__name__ == '__main__'):
    if len(sys.argv) < 2:
        print (usage)
        sys.exit()

    from_stdin = sys.argv[1] == '-'

    text = ''
    words_all = []
    groups_all = []
    resolved = []

    cur_offset = 0

    config = configparser.ConfigParser('config.txt', ['PRONOUNS', 'LANG'])

    lemmatizer = lemmatizer.Lemmatizer('mystem')
    use_conjunctions = config.CONJUNCTIONS if config.HasField('CONJUNCTIONS') else False

    anaph_resolutor = anaphoramllib.AnaphoraDummyResolutor()
    anaph_resolutor.possible_words = load_pronouns(config.PRONOUNS)

    inp_file = codecs.open(sys.argv[1], encoding='utf-8') if not from_stdin else sys.stdin
    for line in inp_file:
        if from_stdin:
            line = line.decode('utf-8')
        line_len = len(line)
        line = line.strip('\r\n')
        text += line

        words = lemmatizer.lemmatize(line.lower())
        groups = lemmatizer.get_groups(words, conjunctions = use_conjunctions)

        for word in words:
            word.offset += cur_offset

        for group in groups:
            group.offset += cur_offset

        cur_offset += line_len

        words_all.extend(words)
        groups_all.extend(groups)

        print line
        for pronoun in (word for word in words if word.lemma in anaph_resolutor.possible_words):
            antecedent = anaph_resolutor.get_antecedent(pronoun, groups_all, lemmatizer)
            resolved.append((pronoun, antecedent if antecedent else type('Word', (object,), {'wordform': '???'})))
            print ' --> '.join(unicode(item.wordform) for item in resolved[-1])

    pass