# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from parslepy.selectors import DefaultSelectorHandler, SelectorHandler, Selector
import lxml.etree
import lxml.html
import re
import json
import yaml

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
    """
    Raised by a :class:`.Parselet` instance while extracting content in strict mode,
    when a required key does not yield any content.

    >>> import parslepy
    >>> html = '''
    ... <!DOCTYPE html>
    ... <html>
    ... <head>
    ...     <title>Sample document to test parslepy</title>
    ...     <meta http-equiv="content-type" content="text/html;charset=utf-8" />
    ... </head>
    ... <body>
    ... <h1 id="main">What&rsquo;s new</h1>
    ... <ul>
    ...     <li class="newsitem"><a href="/article-001.html">This is the first article</a></li>
    ...     <li class="newsitem"><a href="/article-002.html">A second report on something</a></li>
    ...     <li class="newsitem"><a href="/article-003.html">Python is great!</a> <span class="fresh">New!</span></li>
    ... </ul>
    ... </body>
    ... </html>
    ... '''
    >>> rules = {
    ...     "heading1": "h1#main",
    ...     "heading2": "h2#main",
    ... }
    >>> p = parslepy.Parselet(rules, strict=True)
    >>> try:
    ...     p.parse_fromstring(html)
    ... except parslepy.base.NonMatchingNonOptionalKey as e:
    ...     print "Missing mandatory key"
    Missing mandatory key
    """

    pass


class InvalidKeySyntax(SyntaxError):
    """
    Raised when the input Parsley script's syntax is invalid

    >>> import parslepy
    >>> try:
    ...     p = parslepy.Parselet({"heading@": "#main"})
    ... except parslepy.base.InvalidKeySyntax as e:
    ...     print e
    Key heading@ is not valid
    """

    pass


class Parselet(object):

    DEBUG = False
    SPECIAL_LEVEL_KEY = "--"
    KEEP_ONLY_FIRST_ELEMENT_IF_LIST = True
    STRICT_MODE = False

    def __init__(self, parselet, selector_handler=None, strict=False, debug=False):
        """
        Take a parselet and optional selector_handler
        and build an abstract representation of the Parsley extraction
        logic.

        Four helper class methods can be used to instantiate a Parselet
        from JSON/YAML rules: :meth:`.from_jsonstring`, :meth:`.from_jsonfile`,
        :meth:`.from_yamlstring`, :meth:`.from_yamlfile`.

        :param dict parselet: Parsley script as a Python dict object
        :param boolean strict: Set to *True* is you want to
            enforce that missing required keys raise an Exception; default is False
            (i.e. lenient/non-strict mode)
        :param selector_handler: an instance of :class:`selectors.SelectorHandler`
            optional selector handler instance;
            defaults to an instance of :class:`selectors.DefaultSelectorHandler`
        :raises: :class:`.InvalidKeySyntax`

        Example:

        >>> import parslepy
        >>> rules = {
        ...     "heading": "h1#main",
        ...     "news(li.newsitem)": [{
        ...         "title": ".",
        ...         "url": "a/@href"
        ...     }],
        ... }
        >>> p = parslepy.Parselet(rules)
        >>> type(p)
        <class 'parslepy.base.Parselet'>

        Use :meth:`~base.Parselet.extract` or :meth:`~base.Parselet.parse`
        to get extracted content from documents.
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
    def from_jsonfile(cls, fp, selector_handler=None, strict=False, debug=False):
        """
        Create a Parselet instance from a file containing
        the Parsley script as a JSON object

        >>> import parslepy
        >>> with open('parselet.json') as fp:
        ...     parslepy.Parselet.from_jsonfile(fp)
        ...
        <parslepy.base.Parselet object at 0x2014e50>

        :param file fp: an open file-like pointer containing the Parsley script
        :rtype: :class:`.Parselet`

        Other arguments: same as for :class:`.Parselet` contructor
        """

        return cls._from_jsonlines(fp,
            selector_handler=selector_handler, strict=strict, debug=debug)

    @classmethod
    def from_yamlfile(cls, fp, selector_handler=None, strict=False, debug=False):
        """
        Create a Parselet instance from a file containing
        the Parsley script as a YAML object

        >>> import parslepy
        >>> with open('parselet.yml') as fp:
        ...     parslepy.Parselet.from_yamlfile(fp)
        ...
        <parslepy.base.Parselet object at 0x2014e50>

        :param file fp: an open file-like pointer containing the Parsley script
        :rtype: :class:`.Parselet`

        Other arguments: same as for :class:`.Parselet` contructor
        """

        return cls.from_yamlstring(fp.read(), selector_handler=selector_handler, strict=strict, debug=debug)

    @classmethod
    def from_yamlstring(cls, s, selector_handler=None, strict=False, debug=False):
        """
        Create a Parselet instance from s (str) containing
        the Parsley script as YAML

        >>> import parslepy
        >>> parsley_string = '---\ntitle: h1\nlink: a @href'
        >>> p = parslepy.Parselet.from_yamlstring(parsley_string)
        >>> type(p)
        <class 'parslepy.base.Parselet'>
        >>>

        :param string s: a Parsley script as a YAML string
        :rtype: :class:`.Parselet`

        Other arguments: same as for :class:`.Parselet` contructor
        """

        return cls(yaml.load(s), selector_handler=selector_handler, strict=strict, debug=debug)

    @classmethod
    def from_jsonstring(cls, s, selector_handler=None, strict=False, debug=False):
        """
        Create a Parselet instance from s (str) containing
        the Parsley script as JSON

        >>> import parslepy
        >>> parsley_string = '{ "title": "h1", "link": "a @href"}'
        >>> p = parslepy.Parselet.from_jsonstring(parsley_string)
        >>> type(p)
        <class 'parslepy.base.Parselet'>
        >>>

        :param string s: a Parsley script as a JSON string
        :rtype: :class:`.Parselet`

        Other arguments: same as for :class:`.Parselet` contructor
        """

        return cls._from_jsonlines(s.split("\n"),
            selector_handler=selector_handler, strict=strict, debug=debug)

    @classmethod
    def _from_jsonlines(cls, lines, selector_handler=None, strict=False, debug=False):
        """
        Interpret input lines as a JSON Parsley script.
        Python-style comment lines are skipped.
        """

        return cls(json.loads(
                "\n".join([l for l in lines if not cls.REGEX_COMMENT_LINE.match(l)])
            ), selector_handler=selector_handler, strict=strict, debug=debug)

    def parse(self, fp, parser=None, context=None):
        """
        Parse an HTML or XML document and
        return the extacted object following the Parsley rules give at instantiation.

        :param fp: file-like object containing an HTML or XML document, or URL or filename
        :param parser: *lxml.etree._FeedParser* instance (optional); defaults to lxml.etree.HTMLParser()
        :param context: user-supplied context that will be passed to custom XPath extensions (as first argument)
        :rtype: Python :class:`dict` object with mapped extracted content
        :raises: :class:`.NonMatchingNonOptionalKey`

        To parse from a string, use the :meth:`~base.Parselet.parse_fromstring` method instead.

        Note that the fp paramater is passed directly
        to `lxml.etree.parse <http://lxml.de/api/lxml.etree-module.html#parse>`_,
        so you can also give it an URL, and lxml will download it for you.
        (Also see `<http://lxml.de/tutorial.html#the-parse-function>`_.)
        """

        if parser is None:
            parser = lxml.etree.HTMLParser()
        doc = lxml.etree.parse(fp, parser=parser).getroot()
        return self.extract(doc, context=context)

    def parse_fromstring(self, s, parser=None, context=None):
        """
        Parse an HTML or XML document and
        return the extacted object following the Parsley rules give at instantiation.

        :param string s: an HTML or XML document as a string
        :param parser: *lxml.etree._FeedParser* instance (optional); defaults to lxml.etree.HTMLParser()
        :param context: user-supplied context that will be passed to custom XPath extensions (as first argument)
        :rtype: Python :class:`dict` object with mapped extracted content
        :raises: :class:`.NonMatchingNonOptionalKey`

        """
        if parser is None:
            parser = lxml.etree.HTMLParser()
        doc = lxml.etree.fromstring(s, parser=parser)
        return self.extract(doc, context=context)

    def compile(self):
        """
        Build the abstract Parsley tree starting from the root node
        (recursive)
        """
        if not isinstance(self.parselet, dict):
            raise ValueError("Parselet must be a dict of some sort. Or use .from_jsonstring(), " \
                ".from_jsonfile(), .from_yamlstring(), or .from_yamlfile()")
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

    def extract(self, document, context=None):
        """
        Extract values as a dict object following the structure
        of the Parsley script (recursive)

        :param document: lxml-parsed document
        :param context: user-supplied context that will be passed to custom XPath extensions (as first argument)
        :rtype: Python *dict* object with mapped extracted content
        :raises: :class:`.NonMatchingNonOptionalKey`

        >>> import lxml.etree
        >>> import parslepy
        >>> html = '''
        ... <!DOCTYPE html>
        ... <html>
        ... <head>
        ...     <title>Sample document to test parslepy</title>
        ...     <meta http-equiv="content-type" content="text/html;charset=utf-8" />
        ... </head>
        ... <body>
        ... <h1 id="main">What&rsquo;s new</h1>
        ... <ul>
        ...     <li class="newsitem"><a href="/article-001.html">This is the first article</a></li>
        ...     <li class="newsitem"><a href="/article-002.html">A second report on something</a></li>
        ...     <li class="newsitem"><a href="/article-003.html">Python is great!</a> <span class="fresh">New!</span></li>
        ... </ul>
        ... </body>
        ... </html>
        ... '''
        >>> html_parser = lxml.etree.HTMLParser()
        >>> doc = lxml.etree.fromstring(html, parser=html_parser)
        >>> doc
        <Element html at 0x7f5fb1fce9b0>
        >>> rules = {
        ...     "headingcss": "#main",
        ...     "headingxpath": "//h1[@id='main']"
        ... }
        >>> p = parslepy.Parselet(rules)
        >>> p.extract(doc)
        {'headingcss': u'What\u2019s new', 'headingxpath': u'What\u2019s new'}

        """
        if context:
            self.selector_handler.context = context
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

            # default output
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

                                if isinstance(parse_result, (list, tuple)):
                                    extracted.extend(parse_result)
                                else:
                                    extracted.append(parse_result)

                                # if we're not in an array,
                                # we only care about the first iteration
                                if not ctx.iterate:
                                    break

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

                # replace empty-list result when not looping by empty dict
                if (    isinstance(extracted, list)
                    and not extracted
                    and not ctx.iterate):
                        extracted = {}

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
                    # required keys are handled above
                    if extracted is not None:
                        output[ctx.key] = extracted
                    else:
                        # do not add this optional key/value pair in the output
                        pass

            return output

        # a leaf/Selector node
        elif isinstance(parselet_node, Selector):
            return self.selector_handler.extract(document, parselet_node)

        else:
            # FIXME: can this happen?
            #        if selector handler returned None at compile time,
            #        probably yes
            pass

    def keys(self):
        """
        Return a list of 1st level keys of the output data model

        >>> import parslepy
        >>> rules = {
        ...     "headingcss": "#main",
        ...     "headingxpath": "//h1[@id='main']"
        ... }
        >>> p = parslepy.Parselet(rules)
        >>> sorted(p.keys())
        ['headingcss', 'headingxpath']

        """
        return self._keys(self.parselet_tree)

    def _keys(self, parselet_node):
        keys = []
        if isinstance(parselet_node, ParsleyNode):
            for ctx, v in list(parselet_node.items()):
                if ctx.key == self.SPECIAL_LEVEL_KEY:
                    keys.extend(self._keys(v))
                else:
                    keys.append(ctx.key)
        return keys

# alias
Parslet = Parselet


if __name__ == "__main__":
    import doctest
    doctest.testmod()
