# -*- coding: utf-8 -*-
import re
import copy

from cssselect import HTMLTranslator
from cssselect.parser import FunctionalPseudoElement
from cssselect.xpath import _unicode_safe_getattr, XPathExpr
import lxml.cssselect
import lxml.etree

import parslepy.funcs


class Selector(object):
    """
    Class of objects returned by :class:`.SelectorHandler` instances'
    (and subclasses) :meth:`~.SelectorHandler.make` method.
    """

    def __init__(self, selector):
        self.selector = selector

    def __repr__(self):
        return "<Selector: inner=%s>" % self.selector


class SelectorHandler(object):
    """
    Called when building abstract Parsley trees
    and when etracting object values during the actual parsing
    of documents

    This should be subclassed to implement the selector processing logic
    you need for your Parsley handling.

    All 3 methods, :meth:`~.SelectorHandler.make`, :meth:`~.SelectorHandler.select`
    and :meth:`~.SelectorHandler.extract` MUST be overridden
    """

    DEBUG = False

    def __init__(self, debug=False):
        if debug:
            self.DEBUG = True

    def make(self, selection_string):
        """
        Interpret a selection_string as a selector
        for elements or element attributes in a (semi-)structured document.
        In case of XPath selectors, this can also be a function call.

        :param selection_string: a string representing a selector
        :rtype: :class:`.Selector`
        """

        raise NotImplementedError

    def select(self, document, selector):
        """
        Apply the selector on the document

        :param document: lxml-parsed document
        :param selector: input :class:`.Selector` to apply on the document
        :rtype: lxml.etree.Element list
        """

        raise NotImplementedError

    def extract(self, document, selector):
        """
        Apply the selector on the document
        and return a value for the matching elements (text content or
        element attributes)

        :param document: lxml-parsed document
        :param selector: input :class:`.Selector`  to apply on the document
        :rtype: depends on the selector (string, boolean value, ...)

        Return value can be single- or multi-valued.
        """

        raise NotImplementedError


class XPathSelectorHandler(SelectorHandler):
    """
    This selector only accepts XPath selectors.

    It understands what lxml.etree.XPath understands, that is XPath 1.0
    expressions
    """

    EXPECTED_NON_ELEMENT_TYPES = [
        bool,
        int,
        float,
        str,
    ]
    try:
        unicode         # Python 2.x
        EXPECTED_NON_ELEMENT_TYPES.append(unicode)
    except NameError:
        pass

    LOCAL_NAMESPACE = 'local-parslepy'
    LOCAL_XPATH_EXTENSIONS = {
        (LOCAL_NAMESPACE, 'text') : parslepy.funcs.xpathtostring,
        (LOCAL_NAMESPACE, 'textnl') : parslepy.funcs.xpathtostringnl,

        # aliases
        (LOCAL_NAMESPACE, 'str') : parslepy.funcs.xpathtostring,
        (LOCAL_NAMESPACE, 'strnl') : parslepy.funcs.xpathtostringnl,
        (LOCAL_NAMESPACE, 'nl') : parslepy.funcs.xpathtostringnl,

        (LOCAL_NAMESPACE, 'html') : parslepy.funcs.xpathtohtml,
        (LOCAL_NAMESPACE, 'xml') : parslepy.funcs.xpathtoxml,
        (LOCAL_NAMESPACE, 'strip') : parslepy.funcs.xpathstrip,

        (LOCAL_NAMESPACE, 'attrname') : parslepy.funcs.xpathattrname,
        (LOCAL_NAMESPACE, 'attrnames') : parslepy.funcs.xpathattrname,   # alias that's probably a better fit
    }
    EXSLT_NAMESPACES={
        'date': 'http://exslt.org/dates-and-times',
        'math': 'http://exslt.org/math',
        're': 'http://exslt.org/regular-expressions',
        'set': 'http://exslt.org/sets',
        'str': 'http://exslt.org/strings',
    }
    _extension_router = {}

    SMART_STRINGS = False
    SMART_STRINGS_FUNCTIONS = [
        (LOCAL_NAMESPACE, 'attrname'),
        (LOCAL_NAMESPACE, 'attrnames'),
    ]

    _selector_cache = {}

    def __init__(self, namespaces=None, extensions=None, context=None, debug=False):
        """
        :param namespaces: namespace mapping as :class:`dict`
        :param extensions: extension :class:`dict`
        :param context: user-context passed to XPath extension functions

        `namespaces` and `extensions` dicts should have the same format
        as for `lxml`_:
        see http://lxml.de/xpathxslt.html#namespaces-and-prefixes
        and `<http://lxml.de/extensions.html#xpath-extension-functions>`_

        Extension functions have a slightly different signature than
        pure-lxml extension functions: they must expect a user-context
        as first argument; all other arguments are the same as for
        `lxml` extensions.

        `context` will be passed as first argument to extension functions
        registered through `extensions`.
        Alternative: user-context can also be passed to :meth:`parslepy.base.Parselet.parse`

        """

        super(XPathSelectorHandler, self).__init__(debug=debug)

        # support EXSLT extensions
        self.namespaces = copy.copy(self.EXSLT_NAMESPACES)

        # add local XPath extension functions
        self._add_parsley_ns(self.namespaces)
        self.extensions = copy.copy(self.LOCAL_XPATH_EXTENSIONS)

        # add user-defined extensions
        self._user_extensions = None
        self.context = context
        if namespaces:
            self.namespaces.update(namespaces)
        if extensions:
            self._user_extensions = extensions
            self._process_extensions(extensions)

        # some functions need smart_strings=True
        self._set_smart_strings_regexps()

    def _test_smart_strings_needed(self, selector):
        return any([r.search(selector)
                    for r in self.smart_strings_regexps])

    def _get_smart_strings_regexps(self, ns, fname):
        # find out what prefixes match the supplied namespace
        prefix_matches = []
        for prefix, namespace in self.namespaces.items():
            if namespace == ns:
                prefix_matches.append(prefix)

        return [re.compile("%s:%s\(" % (p, fname)) for p in prefix_matches]

    def _set_smart_strings_regexps(self):
        self.smart_strings_regexps = []
        # smart_strings for built-in extensions
        for (ns, fname) in self.SMART_STRINGS_FUNCTIONS:
            self.smart_strings_regexps.extend(
                self._get_smart_strings_regexps(ns, fname))

        # smart_strings for user_defined extensions
        if self._user_extensions:
            for (ns, fname) in self._user_extensions:
                self.smart_strings_regexps.extend(
                    self._get_smart_strings_regexps(ns, fname))

    def _make_xpathextension(self, ns, fname):
        def xpath_ext(*args):
            return self._extension_router[(ns, fname)](self.context, *args)

        extension_name = str("xpext_%s_%d" % (fname, hash(ns)))
        xpath_ext.__doc__ = "docstring for %s" % extension_name
        xpath_ext.__name__ = extension_name
        setattr(self, xpath_ext.__name__, xpath_ext)

        return xpath_ext

    def _process_extensions(self, extensions):
        for (ns, fname), func in extensions.items():
            self._extension_router[(ns, fname)] = func
            self.extensions[(ns, fname)] = self._make_xpathextension(ns=ns, fname=fname)

    @classmethod
    def _add_parsley_ns(cls, namespace_dict):
        """
        Extend XPath evaluation with Parsley extensions' namespace
        """

        namespace_dict.update({
            'parslepy' : cls.LOCAL_NAMESPACE,
            'parsley' : cls.LOCAL_NAMESPACE,
        })
        return namespace_dict

    def make(self, selection):
        """
        XPath expression can also use EXSLT functions (as long as they are
        understood by libxslt)
        """

        cached = self._selector_cache.get(selection)
        if cached:
            return cached

        try:
            selector = lxml.etree.XPath(selection,
                namespaces = self.namespaces,
                extensions = self.extensions,
                smart_strings=(self.SMART_STRINGS
                            or self._test_smart_strings_needed(selection)),
                )

        except lxml.etree.XPathSyntaxError as syntax_error:
            syntax_error.msg += ": %s" % selection
            raise syntax_error

        except Exception as e:
            if self.DEBUG:
                print(repr(e), selection)
            raise

        # wrap it/cache it
        self._selector_cache[selection] = Selector(selector)
        return self._selector_cache[selection]

    @classmethod
    def select(cls, document, selector):
        try:
            return selector.selector(document)
        except Exception as e:
            if cls.DEBUG:
                print(str(e))
            return

    def extract(self, document, selector, debug_offset=''):
        """
        Try and convert matching Elements to unicode strings.

        If this fails, the selector evaluation probably already
        returned some string(s) of some sort, or boolean value,
        or int/float, so return that instead.
        """
        selected = self.select(document, selector)
        if selected is not None:

            if isinstance(selected, (list, tuple)):

                # FIXME: return None or return empty list?
                if not len(selected):
                    return

                return [self._extract_single(m) for m in selected]

            else:
                return self._extract_single(selected)

        # selector did not match anything
        else:
            if self.DEBUG:
                print(debug_offset, "selector did not match anything; return None")
            return None

    def _default_element_extract(self, element):
        """
        Overridable method to change how matching Elements
        are represented in output
        """

        return parslepy.funcs.extract_text(element)

    def _extract_single(self, retval):
        # XPath compiled expressions (and CSSSelect translations)
        # can return different types
        # See http://lxml.de/xpathxslt.html#xpath-return-values
        # - True or False, when the XPath expression
        #       has a boolean result
        # - a float, when the XPath expression has a numeric result
        #       (integer or float)
        # - a 'smart' string (as described below),
        #       when the XPath expression has a string result.
        # - a list of items, when the XPath expression has a list as result.
        #       The items may include Elements
        #       (also comments and processing instructions),
        #       strings and tuples.
        #
        #   Note that in the default implementation,
        #   smart strings are disabled
        if type(retval) == lxml.etree._Element:
            return self._default_element_extract(retval)

        elif type(retval) == lxml.etree._Comment:
            return self._default_element_extract(retval)

        elif isinstance(retval, tuple(self.EXPECTED_NON_ELEMENT_TYPES)):
            return retval

        else:
            raise Warning("unusual type %s" % type(retval))
            return retval




class CssTranslator(HTMLTranslator):

    def xpath_pseudo_element(self, xpath, pseudo_element):
        if isinstance(pseudo_element, FunctionalPseudoElement):
            method = 'xpath_%s_functional_pseudo_element' % (
                pseudo_element.name.replace('-', '_'))
            method = _unicode_safe_getattr(self, method, None)
            if not method:
                raise ExpressionError(
                    "The functional pseudo-element ::%s() is unknown"
                % pseudo_element.name)
            xpath = method(xpath, pseudo_element.arguments)
        else:
            method = 'xpath_%s_simple_pseudo_element' % (
                pseudo_element.replace('-', '_'))
            method = _unicode_safe_getattr(self, method, None)
            if not method:
                raise ExpressionError(
                    "The pseudo-element ::%s is unknown"
                    % pseudo_element)
            xpath = method(xpath)
        return xpath

    # functional pseudo-element:
    # element's attribute by name
    def xpath_attr_functional_pseudo_element(self, xpath, arguments):
        attribute_name = arguments[0].value
        other = XPathExpr('@%s' % attribute_name, '', )
        return xpath.join('/', other)

    # pseudo-element:
    # element's text() nodes
    def xpath_text_simple_pseudo_element(self, xpath):
        other = XPathExpr('text()', '', )
        return xpath.join('/', other)

    # pseudo-element:
    # element's comment() nodes
    def xpath_comment_simple_pseudo_element(self, xpath):
        other = XPathExpr('comment()', '', )
        return xpath.join('/', other)


class DefaultSelectorHandler(XPathSelectorHandler):
    """
    Default selector logic, loosely based on the original
    `Parsley` implementation.

    This handler understands what cssselect and lxml.etree.XPath understands,
    that is (roughly) XPath 1.0 and CSS3 for things that dont need browser context
    """

    # newer lxml version (>3) raise SelectorSyntaxError (directly from cssselect)
    # for invalid CSS selectors
    # but older lxml (2.3.8 for example) have cssselect included
    # and for some selectors raise AssertionError and TypeError instead
    CSSSELECT_SYNTAXERROR_EXCEPTIONS = set([
        # we could use lxml.cssselect.SelectorError (parent class for both),
        # but for lxml<3, they're not related
        lxml.cssselect.SelectorSyntaxError,
        # for unsupported pseudo-class or XPath namespaces prefix syntax
        lxml.cssselect.ExpressionError,
    ])
    # this is to add AssertionError and TypeError if lxml < 3.0.0
    for s in ('#a.', '//h1'):
        try:
            lxml.cssselect.CSSSelector(s)
        except Exception as e:
            CSSSELECT_SYNTAXERROR_EXCEPTIONS.add(type(e))
    _css_translator = CssTranslator()

    # example: "a img @src" (fetch the 'src' attribute of an IMG tag)
    # other example: "im|img @im|src" when using namespace prefixes
    REGEX_ENDING_ATTRIBUTE = re.compile(r'^(?P<expr>.+)\s+(?P<attr>@[\:|\w_\d-]+)$')
    def make(self, selection):
        """
        Scopes and selectors are tested in this order:
        * is this a CSS selector with an appended @something attribute?
        * is this a regular CSS selector?
        * is this an XPath expression?

        XPath expression can also use EXSLT functions (as long as they are
        understood by libxslt)
        """
        cached = self._selector_cache.get(selection)
        if cached:
            return cached

        namespaces = self.EXSLT_NAMESPACES
        self._add_parsley_ns(namespaces)
        try:
            # CSS with attribute? (non-standard but convenient)
            # CSS selector cannot select attributes
            # this "<css selector> @<attr>" syntax is a Parsley extension
            # construct CSS selector and append attribute to XPath expression
            m = self.REGEX_ENDING_ATTRIBUTE.match(selection)
            if m:
                # the selector should be a regular CSS selector
                cssxpath = self._css_translator.css_to_xpath(m.group("expr"))

                # if "|" is used for namespace prefix reference,
                #   convert it to XPath prefix syntax
                attribute = m.group("attr").replace('|', ':')

                cssxpath = "%s/%s" % (cssxpath, attribute)
            else:
                cssxpath = self._css_translator.css_to_xpath(selection)

            selector = lxml.etree.XPath(
                cssxpath,
                namespaces = self.namespaces,
                extensions = self.extensions,
                smart_strings=(self.SMART_STRINGS
                            or self._test_smart_strings_needed(selection)),
                )

        except tuple(self.CSSSELECT_SYNTAXERROR_EXCEPTIONS) as syntax_error:
            if self.DEBUG:
                print(repr(syntax_error), selection)
                print("Try interpreting as XPath selector")
            try:
                selector = lxml.etree.XPath(selection,
                    namespaces = self.namespaces,
                    extensions = self.extensions,
                    smart_strings=(self.SMART_STRINGS
                                or self._test_smart_strings_needed(selection)),
                    )

            except lxml.etree.XPathSyntaxError as syntax_error:
                syntax_error.msg += ": %s" % selection
                raise syntax_error

            except Exception as e:
                if self.DEBUG:
                    print(repr(e), selection)
                raise

        # for exception when trying to convert <cssselector> @<attribute> syntax
        except lxml.etree.XPathSyntaxError as syntax_error:
            syntax_error.msg += ": %s" % selection
            raise syntax_error

        except Exception as e:
            if self.DEBUG:
                print(repr(e), selection)
            raise

        # wrap it/cache it
        self._selector_cache[selection] = Selector(selector)
        return self._selector_cache[selection]
