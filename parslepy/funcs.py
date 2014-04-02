# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import re
import lxml.etree
#import traceback

# ----------------------------------------------------------------------

try:
    unicode         # Python 2.x
    def lxml_element2string(element, method="text", with_tail=False):
        return lxml.etree.tostring(element, method=method,
                encoding=unicode, with_tail=with_tail)
except NameError:   # Python 3.x
    def lxml_element2string(element, method="text", with_tail=False):
        return lxml.etree.tostring(element, method=method,
                encoding=str, with_tail=with_tail)
except:
    raise

def extract_text(element, keep_nl=False, with_tail=False):
    return remove_multiple_whitespaces(
        lxml_element2string(element, method="text", with_tail=with_tail),
        keep_nl=keep_nl).strip()

def extract_html(element, with_tail=False):
    return lxml_element2string(element, method="html", with_tail=with_tail)

def extract_xml(element, with_tail=False):
    return lxml_element2string(element, method="xml", with_tail=with_tail)

REGEX_NEWLINE = re.compile(r'\n')
REGEX_WHITESPACE = re.compile(r'\s+', re.UNICODE)
def remove_multiple_whitespaces(input_string, keep_nl=False):

    if keep_nl:
        lines = REGEX_NEWLINE.split(input_string)
        return "\n".join([remove_multiple_whitespaces(l) for l in lines])
    else:
        return REGEX_WHITESPACE.sub(" ", input_string).strip()


def format_alter_htmltags(tree, tags=[], replacement=" "):
    regex_repl_start = re.compile(r'^\s*%s' % replacement, re.UNICODE)
    context = lxml.etree.iterwalk(tree, events=("end", ))
    tag_set = set(tags)
    for action, elem in context:
        if elem.tag not in tag_set:
            continue
        if elem.tail is None:
            elem.tail = replacement
        elif not regex_repl_start.search(elem.tail):
            elem.tail = "%s%s" % (replacement, elem.tail)
    return tree


HTML_BLOCK_ELEMENTS = [
    'address',
    'article',
    'aside',
    'audio',
    'blockquote',
    'br',
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
def format_htmlblock_tags(tree, replacement="\n"):
    return format_alter_htmltags(tree,
        tags=HTML_BLOCK_ELEMENTS,
        replacement=replacement)


def elements2text(nodes, with_tail=True):
    return [extract_text(e, with_tail=with_tail) for e in nodes]


def elements2textnl(nodes, with_tail=True, replacement="\n"):
    return [extract_text(
                format_htmlblock_tags(e, replacement=replacement),
                with_tail=with_tail,
                keep_nl=True)
            for e in nodes]

def elements2html(nodes):
    return [extract_html(e) for e in nodes]

def elements2xml(nodes):
    return [extract_xml(e) for e in nodes]

# ----------------------------------------------------------------------

def test_listitems_type(itemlist, checktype):
    return all([isinstance(i, checktype) for i in itemlist])

def check_listitems_types(itemlist):
    return list(set([type(i) for i in itemlist]))

def apply2elements(elements, element_func, notelement_func=None):
    ltype = check_listitems_types(elements)
    if ltype == [lxml.etree._Element]:
        return element_func(elements)
    elif notelement_func:
        return notelement_func(elements)
    else:
        return elements

#def apply2element(element, element_func, notelement_func=None):
    #if type(element) == lxml.etree._Element:
        #return element_func(element)
    #elif notelement_func:
        #return notelement_func(element)
    #else:
        #return element

try:
    unicode         # Python 2.x
    def xpathtostring(context, nodes, with_tail=True, *args):
        return apply2elements(
            nodes,
            element_func=lambda nodes: elements2text(
                nodes, with_tail=with_tail),
            notelement_func=lambda nodes: [
                remove_multiple_whitespaces(unicode(s))
                    for s in nodes],
        )

except NameError:   # Python 3.x
    def xpathtostring(context, nodes, with_tail=True, *args):
        return apply2elements(
            nodes,
            element_func=lambda nodes: elements2text(
                nodes, with_tail=with_tail),
            notelement_func=lambda nodes: [
                remove_multiple_whitespaces(str(s))
                    for s in nodes],
        )

def xpathtostringnl(context, nodes, with_tail=True, replacement="\n", *args):
    return apply2elements(nodes,
        element_func=lambda nodes: elements2textnl(
            nodes, with_tail=with_tail, replacement=replacement))

def xpathtohtml(context, nodes):
    return apply2elements(nodes,
        element_func=lambda nodes: elements2html(nodes))

def xpathtoxml(context, nodes):
    return apply2elements(nodes,
        element_func=lambda nodes: elements2xml(nodes))

try:
    unicode         # Python 2.x
    def xpathstrip(context, nodes, stripchars=None, with_tail=True, *args):
        if test_listitems_type(nodes, lxml.etree._Element):
            return [s.strip(stripchars)
                    for s in elements2text(
                        nodes, with_tail=with_tail)]
        else:
            return [unicode(s).strip(stripchars) for s in nodes]

except NameError:   # Python 3.x
    def xpathstrip(context, nodes, stripchars=None, with_tail=True, *args):
        if test_listitems_type(nodes, lxml.etree._Element):
            return [s.strip(stripchars)
                    for s in elements2text(
                        nodes, with_tail=with_tail)]
        else:
            return [str(s).strip(stripchars) for s in nodes]


def xpathattrname(context, attributes, *args):
    return [a.attrname for a in attributes]
