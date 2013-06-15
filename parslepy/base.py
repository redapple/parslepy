#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml
import lxml.etree
import lxml.cssselect
import re
from .funcs import *
import json

def xpathtostring(context, nodes):
    return tostring(nodes)

def xpathtostringnl(context, nodes):
    return tostringnl(nodes)

# ----------------------------------------------------------------------

# compiled Parsley scripts look like this
# ParsleyNode(
#       ParsleyContext(key, options[, Selector]): ParsleyNode(...),
#           ...or
#       ParsleyContext(key, options[, Selector]): Selector,
#       ...)

class ParsleyNode(dict):
    pass


class ParsleyContext(object):
    def __init__(self, key, operator=None, required=None, scope=None, iterate=False):
        self.key = key
        self.operator = operator
        self.required = required
        self.scope = scope
        self.iterate = iterate

    def __repr__(self):
        return u"<ParsleyContext: k=%s; op=%s; required=%s; scope=%s; iter=%s>" % (
            self.key, self.operator, self.required, self.scope, self.iterate)


class Selector(object):
    def __init__(self, selector):
        self.selector = selector


class SelectorHandler(object):
    DEBUG = False

    def make(self):
        raise NotImplemented

    def select(self, document):
        raise NotImplemented

    def extract(self):
        raise NotImplemented


class DefaultSelectorHandler(SelectorHandler):

    XPATH_EXTENSIONS = {
        ('parsley', 'str') : xpathtostring,
        ('parsley', 'strnl') : xpathtostringnl,
        ('parsley', 'nl') : xpathtostringnl,
    }
    EXSLT_NAMESPACES={
        'math': 'http://exslt.org/math',
        're': 'http://exslt.org/regular-expressions',
        'str': 'http://exslt.org/strings',
    }


    @classmethod
    def _add_parsley_extension_functions(cls, namespace_dict):
        namespace_dict.update({
            'prsl' : 'parsley',
            'parsley' : 'parsley'
        })
        return namespace_dict

    REGEX_ENDING_ATTRIBUTE = re.compile(r'^(?P<expr>.+)\s+(?P<attr>@[\w_\d]+)$')
    @classmethod
    def make(cls, selection):

        namespaces = cls.EXSLT_NAMESPACES
        cls._add_parsley_extension_functions(namespaces)
        try:
            # CSS with attribute? (non-standard but convenient)
            # construct CSS selector and append attribute to XPath expression
            m = cls.REGEX_ENDING_ATTRIBUTE.match(selection)
            if m:
                cssselector = m.group("expr")
                attribute = m.group("attr")
                cssxpath = lxml.cssselect.CSSSelector(cssselector).path
                selector = lxml.etree.XPath("%s/%s" % (cssxpath, attribute))
            else:
                selector = lxml.cssselect.CSSSelector(selection)

        except Exception as e:
            if cls.DEBUG:
                print selection, "is not a CSS selector"
                print str(e)
            try:
                selector = lxml.etree.XPath(selection,
                    namespaces = namespaces,
                    extensions = cls.XPATH_EXTENSIONS)
            except Exception as e:
                if cls.DEBUG:
                    print selection, "is not a XPath selector"
                    print str(e)
                return None
        # wrap it
        return Selector(selector)

    @classmethod
    def select(cls, document, selector):
        try:
            return selector.selector(document)
        except Exception, e:
            print str(e)
            return

    def extract(self, document, parselet_node, debug_offset=''):
        selected = self.select(document, parselet_node)
        if selected:
            if self.DEBUG:
                print debug_offset, selected
            if isinstance(selected, (list, tuple)):

                # try decoding to a string if no text() or prsl:str() has been used
                try:
                    retval = tostring(selected)
                    if self.DEBUG:
                        print debug_offset, "return", retval
                    return retval

                # assume the selection is already a string(-list)
                except Exception as e:
                    if self.DEBUG:
                        print debug_offset, "tostring failed:", str(e)
                        print debug_offset, "return", selected
                    return selected
            else:
                if self.DEBUG:
                    print debug_offset, "selected is not a list; return", selected
                return selected

        # selector did not match anything
        else:
            if self.DEBUG:
                print debug_offset, "selector did not match anything; return", {}
            return None


class Parselet(object):

    DEBUG = False
    SPECIAL_LEVEL_KEY = "--"

    def __init__(self, parselet, selector_handler=None, debug=False):
        if debug:
            self.DEBUG = True
        self.parselet =  parselet

        if not selector_handler:
            self.selector_handler = DefaultSelectorHandler()

        elif not(isinstance(SelectorHandler)):
            raise ValueError("You must provide a SelectorHandler instance")

        else:
            self.selector_handler = selector_handler

        self.compile()

    # accept comments in parselets
    REGEX_COMMENT_LINE = re.compile(r'^\s*#')
    @classmethod
    def from_jsonfile(cls, fp, debug=False):
        return cls._from_jsonlines(fp, debug=debug)

    @classmethod
    def from_jsonstring(cls, s, debug=False):
        return cls._from_jsonlines(s.split("\n"), debug=debug)

    @classmethod
    def _from_jsonlines(cls, lines, debug=False):
        return cls(json.loads(
                u"\n".join([l for l in lines if not cls.REGEX_COMMENT_LINE.match(l)])
            ), debug=debug)

    def parse(self, f):
        doc = lxml.html.parse(f).getroot()
        return self.extract(doc)

    def compile(self):
        self.parselet_tree = self._compile(self.parselet)

    REGEX_PARSELET_KEY = re.compile("(?P<key>[^()!+?]+)(?P<operator>[+!?])?(\((?P<scope>.+)\))?")
    def _compile(self, parselet_node, level=0):

        if self.DEBUG:
            debug_offset = "".join(["    " for x in range(level)])

        if self.DEBUG:
            print debug_offset, "%s::compile(%s)" % (
                self.__class__.__name__, parselet_node)

        if isinstance(parselet_node, dict):
            parselet_tree = ParsleyNode()
            for k, v in parselet_node.iteritems():

                m = self.REGEX_PARSELET_KEY.match(k)
                if not m:
                    if self.DEBUG:
                        print debug_offset, "could not parse key", k
                    continue

                key = m.group('key')
                # by default, fields are required
                key_required = True
                operator = m.group('operator')
                if operator == '?':
                    key_required = False
                # FIXME: "!" operator not supported (complete array)
                scope = m.group('scope')

                # example: get list of H3 tags
                # { "titles": ["h3"] }
                if isinstance(v, (list, tuple)):
                    v = v[0]
                    iterate = True
                else:
                    iterate = False

                parsley_context = ParsleyContext(
                    key,
                    operator=operator,
                    required=key_required,
                    scope=self.selector_handler.make(scope) if scope else None,
                    iterate=iterate)

                if self.DEBUG:
                    print debug_offset, "current context:", parsley_context

                child_tree = self._compile(v, level=level+1)
                if self.DEBUG:
                    print debug_offset, "child tree:", child_tree

                parselet_tree[parsley_context] = child_tree

            return parselet_tree

        # a string leaf should match some kind of selector
        elif isinstance(parselet_node, basestring):
            return self.selector_handler.make(parselet_node)

    def extract(self, document):
        return self._extract(self.parselet_tree, document)

    def _extract(self, parselet_node, document, level=0):

        if self.DEBUG:
            debug_offset = "".join(["    " for x in range(level)])

        if isinstance(parselet_node, ParsleyNode):

            output = {}

            for ctx, v in parselet_node.iteritems():
                if self.DEBUG:
                    print debug_offset, "context:", ctx, v

                if ctx.scope:
                    extracted = []
                    selected = self.selector_handler.select(document, ctx.scope)
                    if selected:
                        for i, elem in enumerate(selected, start=1):
                            parse_result = self._extract(v, elem, level=level+1)

                            if isinstance(parse_result, (dict, basestring)):
                                extracted.append(parse_result)

                            elif isinstance(parse_result, list):
                                extracted.extend(parse_result)

                        if self.DEBUG:
                            print debug_offset, "parsed %d elements in scope (%s)" % (i, ctx.scope)

                else:
                    extracted = self._extract(v, document, level=level+1)

                # keep only the first element if we're not in an array
                try:
                    if (    isinstance(extracted, list)
                        and extracted
                        and not ctx.iterate):

                        if self.DEBUG:
                            print debug_offset, "keep only 1st element"
                        extracted =  extracted[0]

                except Exception as e:
                    if self.DEBUG:
                        print str(e)
                        print debug_offset, "error getting first element"

                # special key to extract hierarchically
                # but still output at same level
                if (    ctx.key == self.SPECIAL_LEVEL_KEY
                    and isinstance(extracted, dict)):
                    output.update(extracted)
                else:
                    output[ctx.key] = extracted
            return output

        elif isinstance(parselet_node, Selector):
            return self.selector_handler.extract(document, parselet_node)
