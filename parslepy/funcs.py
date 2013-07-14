# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import re
import lxml.etree
#import traceback

# ----------------------------------------------------------------------

try:
    unicode         # Python 2.x
    def lxml_element2string(element, method="text", with_tail=True):
        return lxml.etree.tostring(element, method=method,
                encoding=unicode, with_tail=with_tail)
except NameError:   # Python 3.x
    def lxml_element2string(element, method="text", with_tail=True):
        return lxml.etree.tostring(element, method=method,
                encoding=str, with_tail=with_tail)
except:
    raise

def extract_text(element, keep_nl=False, with_tail=True):
    return remove_multiple_whitespaces(
        lxml_element2string(element, method="text", with_tail=with_tail),
        keep_nl=keep_nl).strip()

def extract_html(element, with_tail=False):
    return lxml_element2string(element, method="html", with_tail=with_tail)

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
    tag_set = set(text_tags + tail_tags)
    for action, elem in context:
        if elem.tag not in tag_set:
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

HTML_BLOCK_ELEMENTS = [
    'address',
    'article',
    'aside',
    'audio',
    'blockquote',
    'canvas',
    'div',
    'dl', 'dd', 'dt',
    'fieldset',
    'figcaption',
    'figure',
    'footer',
    'form',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'header',
    'hgroup',
    'hr',
    'noscript',
    'li', 'ol', 'ul',
    'output',
    'p',
    'pre',
    'section',
    'table',
    'tfoot',
    'video',
]
NEWLINE_TEXT_TAGS = ['br', 'hr']
def format_htmltags_to_newline(tree):
    return format_alter_htmltags(tree,
        text_tags=NEWLINE_TEXT_TAGS,
        tail_tags=HTML_BLOCK_ELEMENTS,
        replacement="\n")


def tostring(nodes, with_tail=True):
    return [extract_text(e, with_tail=with_tail) for e in nodes]


def tostringnl(nodes, with_tail=True):
    try:
        return [extract_text(format_htmltags_to_newline(e),
                        with_tail=with_tail, keep_nl=True)
                    for e in nodes]
    except Exception as e:
        #print(traceback.format_exc())
        #print(str(e))
        return nodes


def tohtml(nodes):
    return [extract_html(e) for e in nodes]
