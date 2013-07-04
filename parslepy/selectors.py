# -*- coding: utf-8 -*-

import lxml.cssselect
import lxml.etree
import parslepy.funcs
import re

def xpathtostring(context, nodes):
    return parslepy.funcs.tostring(nodes)

def xpathtostringnl(context, nodes):
    return parslepy.funcs.tostringnl(nodes)

def xpathtohtml(context, nodes):
    return parslepy.funcs.tohtml(nodes)


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
    }
    EXSLT_NAMESPACES={
        'math': 'http://exslt.org/math',
        're': 'http://exslt.org/regular-expressions',
        'str': 'http://exslt.org/strings',
    }
    _selector_cache = {}

    def __init__(self, namespaces=None, extensions=None, debug=False):
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

        # add user-defined extensions
        if namespaces:
            self.namespaces.update(namespaces)
        if extensions:
            self.extensions.update(extensions)

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
            if self.DEBUG:
                print(repr(syntax_error), selection)
            raise

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

    # example: "a img @src" (fetch the 'src' attribute of an IMG tag)
    REGEX_ENDING_ATTRIBUTE = re.compile(r'^(?P<expr>.+)\s+(?P<attr>@[\w_\d-]+)$')
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
            # construct CSS selector and append attribute to XPath expression
            m = self.REGEX_ENDING_ATTRIBUTE.match(selection)
            if m:
                cssselector = m.group("expr")
                attribute = m.group("attr")
                cssxpath = lxml.cssselect.CSSSelector(cssselector).path
                selector = lxml.etree.XPath("%s/%s" % (cssxpath, attribute))
            else:
                selector = lxml.cssselect.CSSSelector(selection)

        except (
                lxml.cssselect.SelectorSyntaxError,
                AssertionError,
                TypeError) as syntax_error:
            if self.DEBUG:
                print(repr(syntax_error), selection)
                print("Try interpreting as XPath selector")
            try:
                selector = lxml.etree.XPath(selection,
                    namespaces = self.namespaces,
                    extensions = self.extensions)

            except lxml.etree.XPathSyntaxError as syntax_error:
                if self.DEBUG:
                    print(repr(syntax_error), selection)
                raise

            except Exception as e:
                if self.DEBUG:
                    print(repr(e), selection)
                raise

        except Exception as e:
            if self.DEBUG:
                print(repr(e), selection)
            raise

        # wrap it/cache it
        self._selector_cache[selection] = Selector(selector)
        return self._selector_cache[selection]
