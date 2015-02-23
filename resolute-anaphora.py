#!/usr/bin/python2.7
# -!- coding: utf-8 -!-
# usage: resolute-anaphora.py input

from __future__ import unicode_literals

import os, sys, codecs
import lemmatizer
import anaphoramllib
import argparse
import configparser

usage = 'usage: resolute-anaphora.py input'
config_filename = 'config.txt'

def output_plain(resolved, filename):
    result = []
    for pair in resolved:
        result.append(' --> '.join(unicode(item.wordform) for item in pair))

    return '\n'.join(result)

def output_xml(resolved, filename):
    result = []
    result.append('<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n<documents>')
    result.append('<document file="{}">'.format(filename))
    xml_tmpl = '  <chain>\n' \
               '    <item sh="{ant_offset}" ln="{ant_len}" type="anaph">\n' \
               '      <cont><![CDATA[{ant_wordform}]]></cont>\n' \
               '    </item>\n' \
               '    <item sh="{ana_offset}" ln="{ana_len}" type="anaph">\n' \
               '      <cont><![CDATA[{ana_wordform}]]></cont>\n' \
               '    </item>\n' \
               '  </chain>\n'
    for pair in resolved:
        result.append(xml_tmpl.format(ant_offset=pair[1].offset,
                                      ant_len=pair[1].length,
                                      ant_wordform=pair[1].wordform,
                                      ana_offset=pair[0].offset,
                                      ana_len=pair[0].length,
                                      ana_wordform=pair[0].wordform))

    result.append(u'</document>\n</documents>')
    return '\n'.join(result)

def output_brat(resolved, filename):
    pass

output_functions = {'plain': output_plain, 'xml': output_xml, 'brat': output_brat}

def load_pronouns(filename):
    pronouns = []
    inp_file = codecs.open(filename, encoding='utf-8')
    for line in (line_raw.strip('\r\n') for line_raw in inp_file):
        pronouns.extend(line.split('\t')[1:])

    return set(pronouns)

if (__name__ == '__main__'):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("input", help="input filename or '-' to read from STDIN")
    arg_parser.add_argument("-f", "--format", help="output format", choices=output_functions.keys(), default="plain")
    arg_parser.add_argument("-c", "--config", help="path to config file (default: ./config.txt)", default="config.txt")
    args = arg_parser.parse_args()

    from_stdin = args.input == '-'

    text = ''
    words_all = []
    groups_all = []
    resolved = []

    cur_offset = 0

    if not os.path.exists(args.config):
        sys.stderr.write('No config file was found in the specified path: {}\n'.format(args.config))
        sys.exit(1)

    config = configparser.ConfigParser(args.config, ['PRONOUNS', 'LANG'])

    lemmatizer = lemmatizer.Lemmatizer('mystem')
    use_conjunctions = config.CONJUNCTIONS if config.HasField('CONJUNCTIONS') else False

    anaph_resolutor = anaphoramllib.AnaphoraAgrResolutor(lemmatizer)
    anaph_resolutor.possible_words = load_pronouns(config.PRONOUNS)

    inp_file = codecs.open(args.input, encoding='utf-8') if not from_stdin else sys.stdin
    for line in inp_file:
        line_len = len(line)
        line = line.strip('\r\n')
        text += line

        words = lemmatizer.lemmatize(line.lower())
        groups = lemmatizer.get_groups(words, conjunctions = use_conjunctions)

        # something is wrong here
        #for word in words:
        #    word.offset += cur_offset

        for group in groups:
            group.offset += cur_offset

        cur_offset += line_len# - (words[-1].offset + words[-1].length)

        words_all.extend(words)
        groups_all.extend(groups)

        for pronoun in (word for word in groups if word.lemma in anaph_resolutor.possible_words and word.tag['pos'].endswith('PRO')):
            antecedent = anaph_resolutor.get_antecedent(pronoun, groups_all)
            resolved.append((pronoun, antecedent if antecedent else type(b'Word', (object,), {'wordform': '???', 'offset': 0, 'length': 0})))
    print output_functions[args.format](resolved, args.input).encode('utf-8')