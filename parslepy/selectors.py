# -*- coding: utf-8 -*-

import lxml.cssselect
import lxml.etree
import parslepy.funcs
import re

def test_listitems_type(itemlist, checktype):
    return all([isinstance(i, checktype) for i in itemlist])

def check_listitems_types(itemlist):
    return list(set([type(i) for i in itemlist]))

try:
    unicode         # Python 2.x
    def xpathtostring(context, nodes, with_tail=True, *args):
        ltype = check_listitems_types(nodes)
        if ltype == [lxml.etree._Element]:
            return parslepy.funcs.tostring(nodes, with_tail=with_tail)
        #elif ltype == [lxml.etree._ElementUnicodeResult]:
        else:
            try:
                return [parslepy.funcs.remove_multiple_whitespaces(unicode(s))
                        for s in nodes]
            except Exception as e:
                print(e)
except NameError:   # Python 3.x
    def xpathtostring(context, nodes, with_tail=True, *args):
        ltype = check_listitems_types(nodes)
        if ltype == [lxml.etree._Element]:
            return parslepy.funcs.tostring(nodes, with_tail=with_tail)

        #elif ltype == [lxml.etree._ElementUnicodeResult]:
        else:
            try:
                return [parslepy.funcs.remove_multiple_whitespaces(str(s))
                        for s in nodes]
            except Exception as e:
                print(e)

def xpathtostringnl(context, nodes, with_tail=True, *args):
    return parslepy.funcs.tostringnl(nodes, with_tail=with_tail)

def xpathtohtml(context, nodes):
    return parslepy.funcs.tohtml(nodes)

def xpathstrip(context, nodes, stripchars, with_tail=True, *args):
    if test_listitems_type(nodes, lxml.etree._Element):
        return map(
            lambda s: s.strip(stripchars),
            parslepy.funcs.tostring(nodes, with_tail=with_tail))
    else:
        return map(lambda s: unicode(s).strip(stripchars), nodes)

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
    PARSLEY_NAMESPACE = 'local-parsley'
    PARSLEY_XPATH_EXTENSIONS = {
        (PARSLEY_NAMESPACE, 'str') : xpathtostring,
        (PARSLEY_NAMESPACE, 'strnl') : xpathtostringnl,
        (PARSLEY_NAMESPACE, 'nl') : xpathtostringnl,
        (PARSLEY_NAMESPACE, 'html') : xpathtohtml,
        (PARSLEY_NAMESPACE, 'strip') : xpathstrip,
    }
    EXSLT_NAMESPACES={
        'date': 'http://exslt.org/dates-and-times',
        'math': 'http://exslt.org/math',
        're': 'http://exslt.org/regular-expressions',
        'set': 'http://exslt.org/sets',
        'str': 'http://exslt.org/strings',
    }
    _extension_router = {}

    _selector_cache = {}

    def __init__(self, namespaces=None, extensions=None, context=None, debug=False):
        """
        :param namespaces: namespace mapping as :class:`dict`
        :param extensions: extension :class:`dict`

        See `<http://lxml.de/extensions.html#xpath-extension-functions>`_
        """

        super(XPathSelectorHandler, self).__init__(debug=debug)

        # support EXSLT extensions
        self.namespaces = self.EXSLT_NAMESPACES
        self._add_parsley_ns(self.namespaces)
        self.extensions = self.PARSLEY_XPATH_EXTENSIONS
        self.context = context

        # add user-defined extensions
        if namespaces:
            self.namespaces.update(namespaces)
        if extensions:
            self._process_extensions(extensions)

    def _make_xpathextension(self, fname):
        def xpath_ext(*args):
            return self._extension_router[fname](self.context, *args)
        xpath_ext.__doc__ = "docstring for xpext_%s" % fname
        xpath_ext.__name__ = "xpext_%s" % fname
        setattr(self, xpath_ext.__name__, xpath_ext)
        return xpath_ext

    def _process_extensions(self, extensions):
        for (ns, fname), func in extensions.iteritems():
            self._extension_router[fname] = func
            self.extensions[(ns, fname)] = self._make_xpathextension(fname=fname)

    @classmethod
    def _add_parsley_ns(cls, namespace_dict):
        """
        Extend XPath evaluation with Parsley extensions' namespace
        """

        namespace_dict.update({
            'parsley' : cls.PARSLEY_NAMESPACE,
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
                extensions = self.extensions)

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
        returned some string(s) of some sort, so return that instead.
        """
        selected = self.select(document, selector)
        if selected:
            if self.DEBUG:
                print(debug_offset, selected)

            if isinstance(selected, (list, tuple)):

                # try decoding to a string if no text() or prsl:str() has been used
                try:
                    retval = parslepy.funcs.tostring(selected)
                    if self.DEBUG:
                        print(debug_offset, "return", retval)
                    return retval

                # assume the selection is already a string (or string list)
                except Exception as e:
                    if self.DEBUG:
                        print(debug_offset, "tostring failed:", str(e))
                        print(debug_offset, "return", selected)
                    return selected
            else:
                if self.DEBUG:
                    print(debug_offset, "selected is not a list; return", selected)
                return selected

        # selector did not match anything
        else:
            if self.DEBUG:
                print(debug_offset, "selector did not match anything; return None")
            return None


class DefaultSelectorHandler(XPathSelectorHandler):
    """
    Default selector logic, loosely based on the original
    implementation.

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
                # so should be converted directly using cssselect
                cssselector = m.group("expr")
                cssxpath = lxml.cssselect.CSSSelector(cssselector,
                    namespaces = self.namespaces).path

                # if "|" is used for namespace prefix reference,
                #   convert it to XPath prefix syntax
                attribute = m.group("attr").replace('|', ':')

                selector = lxml.etree.XPath(
                    "%s/%s" % (cssxpath, attribute),
                    namespaces = self.namespaces,
                    extensions = self.extensions)
            else:
                selector = lxml.cssselect.CSSSelector(selection,
                    namespaces = self.namespaces)

        except tuple(self.CSSSELECT_SYNTAXERROR_EXCEPTIONS) as syntax_error:
            if self.DEBUG:
                print(repr(syntax_error), selection)
                print("Try interpreting as XPath selector")
            try:
                selector = lxml.etree.XPath(selection,
                    namespaces = self.namespaces,
                    extensions = self.extensions)

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
