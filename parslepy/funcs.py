# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import re
import lxml.etree
import traceback

# ----------------------------------------------------------------------

try:
    unicode         # Python 2.x
    def lxml_tostring(element, method="text", with_tail=True):
        return lxml.etree.tostring(element, method=method,
                encoding=unicode, with_tail=with_tail)
except NameError:   # Python 3.x
    def lxml_tostring(element, method="text", with_tail=True):
        return lxml.etree.tostring(element, method=method,
                encoding=str, with_tail=with_tail)
except:
    raise

def extract_unicode(element, keep_nl=False, with_tail=True):
    return remove_multiple_whitespaces(
        lxml_tostring(element, method="text", with_tail=with_tail),
        keep_nl=keep_nl).strip()

def extract_html(element, with_tail=False):
    return lxml_tostring(element, method="html", with_tail=with_tail)


REGEX_NEWLINE = re.compile(r'\n')
REGEX_WHITESPACE = re.compile(r'\s+', re.UNICODE)
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
    return tree

NEWLINE_TEXT_TAGS = ['br', 'hr']
NEWLINE_TAIL_TAGS = ['p', 'div',
    'ul', 'li', 'ol',
    'dl', 'dt', 'dd',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
def format_htmltags_to_newline(tree):
    return format_alter_htmltags(tree,
        text_tags=NEWLINE_TEXT_TAGS,
        tail_tags=NEWLINE_TAIL_TAGS,
        replacement="\n")


def tostring(nodes):
    return list(extract_unicode(e) for e in nodes)


def tostringnl(nodes):
    try:
        return list(extract_unicode(format_htmltags_to_newline(e),
                        keep_nl=True)
                    for e in nodes)
    except Exception as e:
        print(traceback.format_exc())
        print(str(e))
        return nodes


def tohtml(nodes):
    return list(extract_html(e) for e in nodes)
