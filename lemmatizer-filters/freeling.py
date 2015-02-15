#!/usr/bin/python2.7
# -!- coding: utf-8 -!-
# usage: freeling.py

import os, subprocess
import sys
if os.path.exists('libfreeling.py'):
    import libfreeling

usage = 'usage: freeling.py'

"""
This is the recommended way to check against part of speech. Add a lambda-function for the desired POS
and use it in your code in the following way: pos_filters['desired_pos'](word), where word is a list
"""
pos_filters = {
    'noun': lambda x: x.tag.startswith('N') or x.tag.startswith('PP'),
    'adj': lambda x: x.tag.startswith('A'),# or x.tag.startswith('R'),
    'properNoun': lambda x: x.tag.startswith('NP'),
    'pronoun': lambda x: x.tag.startswith('E'),
    'comma': lambda x: x.tag == 'Fc',
    'prep': lambda x: x.tag == 'B0',
    'insideQuote': lambda x: x.tag == 'Fra' or x.tag.startswith('QuO'),
    'closeQuote': lambda x: x.tag == 'Frc',
    'firstName': lambda x: x.tag.startswith('N') and x.tag[6] == 'N',
    'secondName': lambda x: (x.tag.startswith('N') and x.tag[6] in ['F', 'S']) or (
        x.tag.startswith('A') and x.tag[5] in ['F', 'S']),  # 'conj': lambda x: x.tag == 'C0' or x.tag == 'Fc'
    'conj': lambda x: x.tag == 'C0',
    'quant': lambda x: x.tag.startswith('Z')
}

"""
This is the list of groups which we are trying to extract. To disable any of the groups, just comment it
"""
agreement_filters = {
    'adjNoun': lambda adj, noun: 'NN' + noun.tag[2:] if (
        pos_filters['adj'](adj) and pos_filters['noun'](noun) and adj.tag[2] == noun.tag[3]) else None,
    #'prepNP': lambda prep, noun: 'PP00000000' if (pos_filters['prep'](prep) and pos_filters['noun'](noun)) else None,
    # 'insideQuote': lambda quote, word: 'QuO' if pos_filters['insideQuote'](quote) else None,
    #'closeQuote': lambda quote, closeQuote: 'QuC' if pos_filters['insideQuote'](quote) and pos_filters['closeQuote'](closeQuote) else None,
    #'name': lambda name, famName: 'NN' + name.tag[2:] if pos_filters['firstName'](name) and pos_filters['secondName'](
    #    famName) else None,[]p
    'quantNoun': lambda quant, noun: 'NN%sP0%s' % (noun.tag[2] if quant.tag[1] != 'N' else 'N', noun.tag[5:]) if (
        pos_filters['quant'](quant) and pos_filters['noun'](noun) and (
            quant.tag[1] == noun.tag[2] or (quant.tag[1] == 'N' and noun.tag[2] == 'G'))) else None
}

np_conjunction = lambda word1, conj, word2: 'NN' if (
    pos_filters['noun'](word1) and pos_filters['noun'](word2) and pos_filters['conj'](conj)) else None


def test_daemon_connection():
    result = tag_text_daemon(u'мама мыла раму')
    return result != None

def tag_text_daemon(text):
    """
    Method for text tagging using Freeling analyzer daemon
    """
    freeling = subprocess.Popen([u'analyzer_client', u'50005'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    tagged = freeling.communicate(text.encode('utf-8'))[0].decode('utf-8').strip().split('\n')

    if len(tagged) == 1 and tagged[0] == u'':
        raise EnvironmentError(61, 'Connection refused by Freeling daemon')
        #return None

    return [type('Word', (object,),
                 dict(zip(['wordform', 'lemma', 'tag', 'prob', 'type'], word.split(' ') + ['word'])))
            for word in tagged
            if ' ' in word]


def load_freeling(freelingdir, lang):
    """
    Method for loading Freeling module
    """
    freelingdata_lang = os.path.join(freelingdir, lang)
    libfreeling.util_init_locale('default')
    maco_options = libfreeling.maco_options('ru')
    maco_options.set_active_modules(0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0)
    maco_options.set_data_files('',
                                freelingdata_lang + "locucions.dat",
                                freelingdir + "common/quantities_default.dat",
                                freelingdata_lang + "afixos.dat",
                                freelingdata_lang + "probabilitats.dat",
                                freelingdata_lang + "dicc.src",
                                '',
                                freelingdir + "common/punct.dat")
    tokenizer = libfreeling.tokenizer(freelingdata_lang + 'tokenizer.dat')
    maco = libfreeling.maco(maco_options)
    splitter = libfreeling.splitter(freelingdata_lang + 'splitter.dat')
    tagger = libfreeling.hmm_tagger(freelingdata_lang + 'tagger.dat', 1, 2)

    sys.stderr.write('tagger loaded\n')

    return lambda line: tagger.analyze(maco.analyze(splitter.split(tokenizer.tokenize(line), 0)))


def tag_text_module(text, freeling_process):
    """
    Method for text tagging using Freeling Python API
    """
    ret = []
    for item in freeling_process(text):
        words = item.get_words()
        for word in words:
            new_word = type('Word', (object,),
                            {'wordform': word.get_form(),
                             'lemma': word.get_analysis()[0].get_lemma(),
                             'tag': word.get_analysis()[0].get_tag() ,#+ ('0' * 8 if word.get_analysis()[0].get_tag() == 'NP' else ''),
                             'prob': word.get_analysis()[0].get_prob(),
                             'type': 'word'})
            ret.append(new_word)

    return ret

def tag_text(text, freeling_process=None):
    return tag_text_module(text, freeling_process) if freeling_process else tag_text_daemon(text)