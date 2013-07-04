.. parslepy documentation master file, created by
   sphinx-quickstart on Mon Jul  1 15:20:50 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to parslepy's documentation!
====================================

*parslepy* lets you extract content from HTML and XML documents
where **extraction rules are defined using a JSON object**
or equivalent Python :class:`dict`,
where keys are names you want to assign to extracted document elements,
and values are `CSS3 Selectors`_ or `XPath 1.0`_ expressions matching the
document elements.

By default,

* selectors for elements will output their matching element(s)' textual content. (children elements' content is also included)
* Selectors matching element attributes will output the attribute's value.

You can nest objects, generate list of objects, and mix CSS and XPath
-- although not in the same selector.

Parslepy uderstands what `lxml`_ and `cssselect`_ understand,
which is roughly `CSS3 Selectors`_ and `XPath 1.0`_.

Each rule should have the following format::

    output key (mandatory)
        |
      optionality operator (optional)
        |   |
        |   |  scope, always within brackets (optional)
        |   |      |
        v   v      v
    "somekey?(someselector)":   "someCSSSelector"

    or         //           :   "someXPathExpression"

    or         //           :    { ...some other rules... }


And a collection of extraction rules --also called a *parselet*,
or *Parsley script*-- looks like this::

    {
        "somekey": "#someID .someclass",                        # using a CSS selector
        "anotherkey": "//sometag[@someattribute='somevalue']",  # using an XPath expression
        "nestedkey(.somelistclass)": [{                         # CSS selector for multiple elements (scope selector)
            "somenestedkey": "somenestedtag/@someattribute"     # XPath expression for an attribbute
       }]
    }

And the output would be something like::

    {
        "somekey": "some value inside the first element matching the CSS selector",
        "anotherkey": "some value inside the first element matching the XPath expression",
        "nestedkey: [
            {"somenestedkey": "attribute of 1st nested element"},
            {"somenestedkey": "attribute of 2nd nested element"},
            ...
            {"somenestedkey": "attribute of last nested element"}
        ]
    }



*parslepy* is a Python implementation -- using `lxml`_ and `cssselect`_ --
of the Parsley extraction language defined by Kyle Maxwell and Andrew Cantino
(see `parsley`_  and `parsley wiki`_ for details and original C implementation).

.. _CSS3 Selectors: http://www.w3.org/TR/2011/REC-css3-selectors-20110929/
.. _XPath 1.0: http://www.w3.org/TR/xpath/
.. _lxml: http://lxml.de/
.. _cssselect: https://github.com/SimonSapin/cssselect
.. _parsley: https://github.com/fizx/parsley
.. _parsley wiki: https://github.com/fizx/parsley/wiki


Quickstart
----------

    Extract the main heading of the Python.org homepage,
    and the first paragraph below that:

    >>> import parslepy
    >>> rules = {"heading": "#content h1.pageheading", "summary": "#intro > p > strong"}
    >>> parslepy.Parselet(rules).parse("http://www.python.org")
    {'heading': u'Python Programming Language \u2013 Official Website', 'summary': u'Python is a programming language that lets you work more quickly and integrate your systems more effectively. You can learn to use Python and see almost immediate gains in productivity and lower maintenance costs.'}
    >>>

    Extract a page heading and a list of item links from a HTML page as a string:

    >>> import lxml.etree
    >>> import parslepy
    >>> import pprint
    >>> html = """
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
    ... </html>"""
    >>> rules = {
             "heading": "h1#main",
             "news(li.newsitem)": [{
                 "title": ".",
                 "url": "a/@href",
                 "fresh": ".fresh"
             }],
        }
    >>> p = parslepy.Parselet(rules)
    >>> extracted = p.parse_fromstring(html)
    >>> pprint.pprint(extracted)
    {'heading': u'What\u2019s new',
     'news': [{'title': u'This is the first article', 'url': '/article-001.html'},
              {'title': u'A second report on something',
               'url': '/article-002.html'},
              {'fresh': u'New!',
               'title': u'Python is great! New!',
               'url': '/article-003.html'}]}


API
---

:class:`.Parselet` is the main class for extracting content
from documents with *parslepy*.

Instantiate it with a Parsley script, containing
a mapping of name keys, and selectors (CSS or XPath) to apply on documents, or document parts.

Then, run the extraction rules by passing an HTML or XML document to
:meth:`~.Parselet.extract` or :meth:`~.Parselet.parse`

The output will be a :class:`dict` containing the same keys as in your Parsley
script, and, depending on your selectors, values will be:

* text serialization of matching elements
* element attributes
* nested lists of extraction content

.. autoclass:: base.Parselet
    :members: from_jsonfile, from_jsonstring, extract, parse, parse_fromstring

Customizing
-----------

You can use a :class:`.Parselet` directly with it's default configuration,
which should work fine for HTML documents when the content you want to
extract can be accessed by regular CSS3 selectors or XPath 1.0 expressions.

But you can also customize how selectors are interpreted by sub-classing
:class:`.SelectorHandler` and passing an instance of your selector handler
to the Parselet constructor.

.. autoclass:: selectors.Selector

.. autoclass:: selectors.SelectorHandler
    :members:

.. autoclass:: selectors.XPathSelectorHandler

.. autoclass:: selectors.DefaultSelectorHandler

        Example with iTunes RSS feed:

        >>> import lxml.etree
        >>> xml_parser = lxml.etree.XMLParser()
        >>> url = 'http://itunes.apple.com/us/rss/topalbums/limit=10/explicit=true/xml'
        >>> xsh = parslepy.XPathSelectorHandler(
                namespaces={
                    'atom': 'http://www.w3.org/2005/Atom',
                    'im': 'http://itunes.apple.com/rss'
                })
        >>> rules = {
                "entries(//atom:feed/atom:entry)": [
                    {
                        "title": "atom:title",
                        "name": "im:name",
                        "id": "atom:id/@im:id",
                        "artist(im:artist)": {
                            "name": ".",
                            "href": "@href"
                        },
                        "images(im:image)": [{
                            "height": "@height",
                            "url": "."
                        }],
                        "releasedate": "im:releaseDate"
                    }
                ]
            }
        >>> parselet = parslepy.Parselet(rules, selector_handler=xsh)
        >>> parselet.parse(url, parser=xml_parser)
        {'entries': [{'name': u'Born Sinner (Deluxe Version)', ...

Exceptions
----------

.. autoclass:: base.InvalidKeySyntax

.. autoclass:: base.NonMatchingNonOptionalKey


More examples
=============

See https://github.com/redapple/parslepy/wiki#usage

.. include:: ../CHANGELOG
