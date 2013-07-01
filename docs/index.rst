.. parslepy documentation master file, created by
   sphinx-quickstart on Mon Jul  1 15:20:50 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to parslepy's documentation!
====================================

Parslepy lets you extract content from HTML and XML documents
where extraction rules are defined using a JSON object
or equivalent Python dict,
where keys are names you want to assign to extracted content,
and values are CSS selectors or XPath expressions.

Parslepy is a Python implementation -- using lxml and cssselect --
of the Parsley extraction language defined by Kyle Maxwell and Andrew Cantino
(see `<https://github.com/fizx/parsley>`_ for details and original C implementation).

You can nest objects, generate list of objects, and (to
a certain extent) mix CSS and XPath.

Parslepy uderstands what lxml and cssselect understand,
which is roughly CSS3 and XPath 1.0.

Quickstart
----------

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

:class:`base.Parselet` is the basis class for extracting content
from document.

Instantiate it with a Parsley script, containing
a mapping of name keys (for your extracted content elements),
and selectors (CSS or XPath) to apply on documents, or document parts.

Then, run the extraction rules by passing an HTML or XML document to
:meth:`~base.Parselet.extract` or :meth:`~base.Parselet.parse`

The output will be a dict containing the same keys as in your Parsley
script, and, depending on your selectors, values will be:
* text serialization of matching elements
* element attributes
* nested lists of extraction content

.. autoclass:: base.Parselet
    :members: from_jsonfile, from_jsonstring, extract, parse

Customizing
-----------

You can customize how selectors are interpreted by sub-classing
:class:`.SelectorHandler`

.. autoclass:: selectors.Selector
.. autoclass:: selectors.SelectorHandler
    :members:
.. autoclass:: selectors.DefaultSelectorHandler
.. autoclass:: selectors.XPathSelectorHandler

        Example with iTunes RSS feed parsing:

        >>> import lxml.etree
        >>> xml_parser = lxml.etree.XMLParser()
        >>> import urllib2
        >>> url = 'https://itunes.apple.com/us/rss/topalbums/limit=10/explicit=true/xml'
        >>> req = urllib2.Request(url)
        >>> root = lxml.etree.parse(urllib2.urlopen(req), parser=xml_parser).getroot()
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

Exceptions
----------

.. autoclass:: base.NonMatchingNonOptionalKey
.. autoclass:: base.InvalidKeySyntax

More examples
=============

See https://github.com/redapple/parslepy/wiki#usage

.. include:: ../CHANGELOG
