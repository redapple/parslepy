#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import lxml.etree

# ----------------------------------------------------------------------

def extract_unicode(element, keep_nl=False, with_tail=True):
    try:
        return remove_multiple_whitespaces(
            lxml.etree.tostring(element, method="text", with_tail=with_tail,
                encoding=str),
            keep_nl=keep_nl).strip()
    except TypeError:
        return remove_multiple_whitespaces(
            lxml.etree.tostring(element, method="text", with_tail=with_tail,
                encoding=unicode),
            keep_nl=keep_nl).strip()
    except:
        raise


REGEX_NEWLINE = re.compile(r'\n')
REGEX_WHITESPACE = re.compile(r'\s{1,}', re.UNICODE)
def remove_multiple_whitespaces(input_string, keep_nl = False):

    if keep_nl:
        lines = REGEX_NEWLINE.split(input_string)
        return "\n".join([remove_multiple_whitespaces(l) for l in lines])
    else:
        return REGEX_WHITESPACE.sub(" ", input_string).strip()


def format_alter_htmltags(tree, text_tags=[], tail_tags=[], replacement=" "):
    context = lxml.etree.iterwalk(tree, events=("end", ))
    for action, elem in context:
        if elem.tag not in set(text_tags + tail_tags):
            continue
        if elem.tag in text_tags:
            if elem.text is None:
                elem.text = replacement
            else:
                elem.text += replacement
        elif elem.tag in tail_tags:
            if elem.tail is None:
                elem.tail = replacement
            else:
                elem.tail += replacement

def format_htmltags_to_newline(tree):
    format_alter_htmltags(tree,
        text_tags=['br', 'hr'],
        tail_tags=['p', 'div', 'ul', 'li', 'ol', 'dl', 'dt', 'dd', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
        replacement="\n")


def tostring(nodes):
    return list(extract_unicode(e) for e in nodes)


def tostringnl(nodes):
    try:
        o = []
        for e in nodes:
            format_htmltags_to_newline(e)
            o.append(extract_unicode(e, keep_nl=True))
        return o
    except Exception as e:
        print((str(e)))
        return nodes
