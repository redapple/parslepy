# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from parslepy.selectors import DefaultSelectorHandler, SelectorHandler, Selector
import lxml.etree
import lxml.html
import re
import json


# http://stackoverflow.com/questions/11301138/how-to-check-if-variable-is-string-with-python-2-and-3-compatibility
try:
    isinstance("", basestring)
    def isstr(s):
        return isinstance(s, basestring)
except NameError:
    def isstr(s):
        return isinstance(s, str)

# ----------------------------------------------------------------------

# compiled Parsley scripts look like this
# ParsleyNode(
#       ParsleyContext(key, options[, Selector]): ParsleyNode(...),
#           ...or
#       ParsleyContext(key, options[, Selector]): Selector,
#       ...)
# --> a tree of ParsleyNode instances,
#     with terminal leaves of type Selector,
#     a parent ParsleyNode having 1 or more ParsleyNode children
#     references through ParsleyContext keys
#
class ParsleyNode(dict):
    pass


class ParsleyContext(object):
    """
    Stores parameters associated with extraction keys in `ParsleyNode` trees.
    Used as keys in `ParsleyNode` objects
    """

    def __init__(self, key, operator=None, required=True, scope=None, iterate=False):
        """
        Only `key` is required

        Arguments:
        operator (str)     -- "?" optional,  "!" for complete arrays; defaults to None (i.e. required)
        required (boolean) -- whether the key is required in the output (defaults to True)
        scope (`Selector`) -- restrict extraction to elements matching this selector
        iterate (boolean)  -- whether multiple objects will be extracted (defaults to False)
        """

        self.key = key
        self.operator = operator
        self.required = required
        self.scope = scope
        self.iterate = iterate

    def __repr__(self):
        return "<ParsleyContext: k=%s; op=%s; required=%s; scope=%s; iter=%s>" % (
            self.key, self.operator, self.required, self.scope, self.iterate)


class NonMatchingNonOptionalKey(RuntimeError):
    pass


class InvalidKeySyntax(SyntaxError):
    pass


class Parselet(object):
    """
    Abstract representation of a Parsley script.

    Instances should be initialized with a dict representing
    key-to-objects mapping/structure to extract

    Two helper methods instantiate the Parselet
    from JSON Parsley scripts, either as files or strings
    """
    DEBUG = False
    SPECIAL_LEVEL_KEY = "--"
    KEEP_ONLY_FIRST_ELEMENT_IF_LIST = True
    STRICT_MODE = False

    def __init__(self, parselet, selector_handler=None, strict=False, debug=False):
        """
        Take a parselet (dict) and optional selector_handler
        (SelectorHandler subclass instance)
        and build an abstract representation of the Parsley extraction
        logic.
        Set the strict (boolean) parameter to True is you want to
        enforce that missing required keys raise an Exception
        (defaults to lenient/non-strict mode)

        The internal abstract Parsley tree is a dict/tree of ParsleyNode
        objects, with leaves being of type Selector (terminal elements).

        Parent and child ParsleyNode instances are linked through
        ParsleyContext keys.
        """
        if debug:
            self.DEBUG = True
        if strict:
            self.STRICT_MODE = True

        self.parselet =  parselet

        if not selector_handler:
            self.selector_handler = DefaultSelectorHandler(debug=self.DEBUG)

        elif not(isinstance(selector_handler, SelectorHandler)):
            raise ValueError("You must provide a SelectorHandler instance")

        else:
            self.selector_handler = selector_handler

        self.compile()

    # accept comments in parselets
    REGEX_COMMENT_LINE = re.compile(r'^\s*#')
    @classmethod
    def from_jsonfile(cls, fp, debug=False):
        """
        Create a Parselet instance from fp (an open file pointer) containing
        the Parsley script as JSON

        >>> import parslepy
        >>> with open('parselet.js') as fp:
        ...     parslepy.Parselet.from_jsonfile(fp)
        ...
        <parslepy.base.Parselet object at 0x2014e50>
        >>>
        """

        return cls._from_jsonlines(fp, debug=debug)

    @classmethod
    def from_jsonstring(cls, s, debug=False):
        """
        Create a Parselet instance from s (str) containing
        the Parsley script as JSON

        >>> import parslepy
        >>> parsley_string = '{ "title": "h1", "link": "a @href"}'
        >>> parslepy.Parselet.from_jsonstring(parsley_string)
        <parslepy.base.Parselet object at 0x183a050>
        >>>
        """

        return cls._from_jsonlines(s.split("\n"), debug=debug)

    @classmethod
    def _from_jsonlines(cls, lines, debug=False):
        """
        Interpret input lines as a JSON Parsley script.
        Python-style comment lines are skipped.
        """

        return cls(json.loads(
                "\n".join([l for l in lines if not cls.REGEX_COMMENT_LINE.match(l)])
            ), debug=debug)

    def parse(self, f, parser=None):
        """
        Parse an HTML document f (a file-like object) and
        return the extacted object following the Parsley script structure.

        Arguments:
        f       -- file-like objects containing an HTML or XML document
        parser  -- (optional) lxml parser instance; defaults to lxml.etree.HTMLParser()
        """
        if parser is None:
            parser = lxml.etree.HTMLParser()
        doc = lxml.html.parse(f, parser=parser).getroot()
        return self.extract(doc)

    def compile(self):
        """
        Build the abstract Parsley tree starting from the root node
        (recursive)
        """
        if not isinstance(self.parselet, dict):
            raise ValueError(
                "Parselet must be a dict of some sort. Or use .from_jsonstring() or .from_jsonfile()")
        self.parselet_tree = self._compile(self.parselet)

    VALID_KEY_CHARS = "\w-"
    SUPPORTED_OPERATORS = "?"   # "!" not supported for now
    REGEX_PARSELET_KEY = re.compile(
        "^(?P<key>[%(validkeychars)s]+)(?P<operator>[%(suppop)s])?(\((?P<scope>.+)\))?$" % {
            'validkeychars': VALID_KEY_CHARS,
            'suppop': SUPPORTED_OPERATORS}
        )
    def _compile(self, parselet_node, level=0):
        """
        Build part of the abstract Parsley extraction tree

        Arguments:
        parselet_node (dict) -- part of the Parsley tree to compile
                                (can be the root dict/node)
        level (int)          -- current recursion depth (used for debug)
        """

        if self.DEBUG:
            debug_offset = "".join(["    " for x in range(level)])

        if self.DEBUG:
            print(debug_offset, "%s::compile(%s)" % (
                self.__class__.__name__, parselet_node))

        if isinstance(parselet_node, dict):
            parselet_tree = ParsleyNode()
            for k, v in list(parselet_node.items()):

                # we parse the key raw elements but without much
                # interpretation (which is done by the SelectorHandler)
                try:
                    m = self.REGEX_PARSELET_KEY.match(k)
                    if not m:
                        if self.DEBUG:
                            print(debug_offset, "could not parse key", k)
                        raise InvalidKeySyntax(k)
                except:
                    raise InvalidKeySyntax("Key %s is not valid" % k)

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
                # FIXME: should we support multiple selectors in list?
                #        e.g. { "titles": ["h1", "h2", "h3", "h4"] }
                if isinstance(v, (list, tuple)):
                    v = v[0]
                    iterate = True
                else:
                    iterate = False

                # keys in the abstract Parsley trees are of type `ParsleyContext`
                try:
                    parsley_context = ParsleyContext(
                        key,
                        operator=operator,
                        required=key_required,
                        scope=self.selector_handler.make(scope) if scope else None,
                        iterate=iterate)
                except SyntaxError:
                    if self.DEBUG:
                        print("Invalid scope:", k, scope)
                    raise

                if self.DEBUG:
                    print(debug_offset, "current context:", parsley_context)

                # go deeper in the Parsley tree...
                try:
                    child_tree = self._compile(v, level=level+1)
                except SyntaxError:
                    if self.DEBUG:
                        print("Invalid value: ", v)
                    raise
                except:
                    raise

                if self.DEBUG:
                    print(debug_offset, "child tree:", child_tree)

                parselet_tree[parsley_context] = child_tree

            return parselet_tree

        # a string leaf should match some kind of selector,
        # let the selector handler deal with it
        elif isstr(parselet_node):
            return self.selector_handler.make(parselet_node)
        else:
            raise ValueError(
                    "Unsupported type(%s) for Parselet node <%s>" % (
                        type(parselet_node), parselet_node))

    def extract(self, document):
        """
        Extract values as a dict object following the structure
        of the Parsley script (recursive)
        """

        return self._extract(self.parselet_tree, document)

    def _extract(self, parselet_node, document, level=0):
        """
        Extract values at this document node level
        using the parselet_node instructions:
        - go deeper in tree
        - or call selector handler in case of a terminal selector leaf
        """

        if self.DEBUG:
            debug_offset = "".join(["    " for x in range(level)])

        # we must go deeper in the Parsley tree
        if isinstance(parselet_node, ParsleyNode):

            output = {}

            # process all children
            for ctx, v in list(parselet_node.items()):
                if self.DEBUG:
                    print(debug_offset, "context:", ctx, v)
                extracted=None
                try:
                    # scoped-extraction:
                    # extraction should be done deeper in the document tree
                    if ctx.scope:
                        extracted = []
                        selected = self.selector_handler.select(document, ctx.scope)
                        if selected:
                            for i, elem in enumerate(selected, start=1):
                                parse_result = self._extract(v, elem, level=level+1)

                                if isinstance(parse_result, (dict, str)):
                                    extracted.append(parse_result)

                                elif isinstance(parse_result, list):
                                    extracted.extend(parse_result)

                            if self.DEBUG:
                                print(debug_offset,
                                    "parsed %d elements in scope (%s)" % (i, ctx.scope))

                    # local extraction
                    else:
                        extracted = self._extract(v, document, level=level+1)
                except NonMatchingNonOptionalKey as e:
                    if self.DEBUG:
                        print(debug_offset, str(e))
                    if not ctx.required or not self.STRICT_MODE:
                        output[ctx.key] = {}
                    else:
                        raise
                except Exception as e:
                    if self.DEBUG:
                        print(str(e))
                    raise

                # keep only the first element if we're not in an array
                if self.KEEP_ONLY_FIRST_ELEMENT_IF_LIST:
                    try:
                        if (    isinstance(extracted, list)
                            and extracted
                            and not ctx.iterate):

                            if self.DEBUG:
                                print(debug_offset, "keep only 1st element")
                            extracted =  extracted[0]

                    except Exception as e:
                        if self.DEBUG:
                            print(str(e))
                            print(debug_offset, "error getting first element")

                # extraction for a required key gave nothing
                if (    self.STRICT_MODE
                    and ctx.required
                    and extracted is None):
                    raise NonMatchingNonOptionalKey(
                        'key "%s" is required but yield nothing\nCurrent path: %s/(%s)\n' % (
                            ctx.key,
                            document.getroottree().getpath(document),v
                            )
                        )

                # special key to extract a selector-defined level deeper
                # but still output at same level
                # this can be useful for breaking up long selectors
                # or when you need to mix XPath and CSS selectors
                # e.g.
                # {
                #   "something(#content div.main)": {
                #       "--(.//div[re:test(@class, 'style\d{3,6}')])": {
                #           "title": "h1",
                #           "subtitle": "h2"
                #       }
                #   }
                # }
                #
                if ctx.key == self.SPECIAL_LEVEL_KEY:
                    if isinstance(extracted, dict):
                        output.update(extracted)
                    elif isinstance(extracted, list):
                        if extracted:
                            raise RuntimeError(
                                "could not merge non-empty list at higher level")
                        else:
                            #empty list, dont bother?
                            pass
                else:
                    if extracted is not None:
                        output[ctx.key] = extracted
                    else:
                        # do not add this optional key/value pair in the output
                        pass
            return output

        elif isinstance(parselet_node, Selector):
            return self.selector_handler.extract(document, parselet_node)

        else:
            # FIXME: can this happen?
            #        if selector handler returned None at compile time,
            #        probably yes
            pass
