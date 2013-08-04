.. parslepy documentation master file, created by
   sphinx-quickstart on Mon Jul  1 15:20:50 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to parslepy's documentation!
====================================

*parslepy* lets you extract content from HTML and XML documents
where **extraction rules are defined using a JSON object**
or equivalent Python :class:`dict`,
where keys are names you want to assign to target document sections,
elements or attributes,
and values are `CSS3 Selectors`_ or `XPath 1.0`_ expressions matching
these document parts.

By default,

* selectors for elements will output their matching element(s)' textual content.
  (children elements' content is also included)
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

Install
^^^^^^^

* using PyPi (https://pypi.python.org/pypi/parslepy)

.. code-block:: bash

    $ [sudo] pip install parslepy

* using source code

.. code-block:: bash

    $ git clone https://github.com/redapple/parslepy.git
    $ [sudo] python setup.py install

Usage
^^^^^

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
    ...      "heading": "h1#main",
    ...      "news(li.newsitem)": [{
    ...          "title": ".",
    ...          "url": "a/@href",
    ...          "fresh": ".fresh"
    ...      }],
    ... }
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

.. autoclass:: parslepy.base.Parselet
    :members: parse, from_jsonfile, from_jsonstring, extract, parse_fromstring

Customizing
-----------

You can use a :class:`.Parselet` directly with it's default configuration,
which should work fine for HTML documents when the content you want to
extract can be accessed by regular CSS3 selectors or XPath 1.0 expressions.

But you can also customize how selectors are interpreted by sub-classing
:class:`.SelectorHandler` and passing an instance of your selector handler
to the Parselet constructor.

.. autoclass:: parslepy.selectors.Selector

.. autoclass:: parslepy.selectors.SelectorHandler
    :members:

.. autoclass:: parslepy.selectors.XPathSelectorHandler

.. autoclass:: parslepy.selectors.DefaultSelectorHandler

        Example with iTunes RSS feed:

        >>> import lxml.etree
        >>> xml_parser = lxml.etree.XMLParser()
        >>> url = 'http://itunes.apple.com/us/rss/topalbums/limit=10/explicit=true/xml'
        >>> xsh = parslepy.XPathSelectorHandler(
        ...     namespaces={
        ...         'atom': 'http://www.w3.org/2005/Atom',
        ...         'im': 'http://itunes.apple.com/rss'
        ...     })
        >>> rules = {
        ...     "entries(//atom:feed/atom:entry)": [
        ...         {
        ...             "title": "atom:title",
        ...             "name": "im:name",
        ...             "id": "atom:id/@im:id",
        ...             "artist(im:artist)": {
        ...                 "name": ".",
        ...                 "href": "@href"
        ...             },
        ...             "images(im:image)": [{
        ...                 "height": "@height",
        ...                 "url": "."
        ...             }],
        ...             "releasedate": "im:releaseDate"
        ...         }
        ...     ]
        ... }
        >>> parselet = parslepy.Parselet(rules, selector_handler=xsh)
        >>> parselet.parse(url, parser=xml_parser)
        {'entries': [{'name': u'Born Sinner (Deluxe Version)', ...

Exceptions
----------

.. autoexception:: parslepy.base.InvalidKeySyntax

.. autoexception:: parslepy.base.NonMatchingNonOptionalKey


Extension functions
-------------------

*parslepy* extends XPath 1.0 functions through `lxml`_'s XPath extensions.
See http://lxml.de/extensions.html for details.

Built-in extensions
^^^^^^^^^^^^^^^^^^^

*parslepy* comes with a few XPath extension functions. These functions
are available by default when you use :class:`.XPathSelectorHandler`
or :class:`.DefaultSelectorHandler`.

*   ``parslepy:text(xpath_expression[, false()])``:
    returns the text content for elements matching *xpath_expression*.
    The optional boolean second parameter indicate wheter *tail* content
    should be included or not.
    (Internally, this calls `lxml.etree.tostring(..., method="text", encoding=unicode)`.)
    Use *true()* and *false()* XPath functions, not only *true* or *false*,
    (or 1 or 0). Defaults to *true()*.

    >>> import parslepy
    >>> doc = """<!DOCTYPE html>
    ... <html>
    ... <head>
    ...     <title>Some page title</title>
    ... </head>
    ...
    ... <body>
    ...     <h1>Some heading</h1>
    ...
    ...     Some text
    ...
    ...     <p>
    ...     Some paragraph
    ...     </p>
    ... </body>
    ...
    ... </html>"""
    >>> rules = {"heading": "h1"}
    >>>
    >>> # default text extraction includes tail text
    ... parslepy.Parselet(rules).parse_fromstring(doc)
    {'heading': u'Some heading Some text'}
    >>>
    >>> # 2nd argument to false means without tail text
    ... rules = {"heading": "parslepy:text(//h1, false())"}
    >>> parslepy.Parselet(rules).parse_fromstring(doc)
    {'heading': 'Some heading'}
    >>>
    >>> # 2nd argument to true is equivalent to default text extraction
    >>> rules = {"heading": "parslepy:text(//h1, true())"}
    >>> parslepy.Parselet(rules).parse_fromstring(doc)
    {'heading': 'Some heading Some text'}
    >>>

    See http://lxml.de/tutorial.html#elements-contain-text for details
    on how `lxml`_ handles text and tail element properties

*   ``parslepy:textnl(xpath_expression)``:
    similar to ``parslepy:text()`` but appends `\\n` characters to HTML
    block elements such as `<br>`, `<hr>`, `<div>`

    >>> import parslepy
    >>> doc = """<!DOCTYPE html>
    ... <html>
    ... <head>
    ...     <title>Some page title</title>
    ... </head>
    ... <body>
    ... <h1>Some heading</h1><p>Some paragraph<div>with some span inside</div>ending now.</p>
    ... </body>
    ... </html>
    ... """
    >>> parslepy.Parselet({"heading": "parslepy:text(//body)"}).parse_fromstring(doc)
    {'heading': 'Some headingSome paragraphwith some span insideending now.'}
    >>>
    >>> parslepy.Parselet({"heading": "parslepy:textnl(//body)"}).parse_fromstring(doc)
    {'heading': 'Some heading\nSome paragraph\nwith some span inside\nending now.'}
    >>>


*   ``parslepy:html(xpath_expression)``
    returns the HTML content for elements matching *xpath_expression*.
    Internally, this calls `lxml.html.tostring(element)`.

    >>> import parslepy
    >>> doc = """<!DOCTYPE html>
    ... <html>
    ... <head>
    ...     <title>Some page title</title>
    ... </head>
    ... <body>
    ... <h1>(Some heading)</h1>
    ... <h2>[some sub-heading]</h2>
    ... </body>
    ... </html>
    ... """
    >>> parslepy.Parselet({"heading": "parslepy:html(//h1)"}).parse_fromstring(doc)
    {'heading': '<h1>(Some heading)</h1>'}
    >>> parslepy.Parselet({"heading": "parslepy:html(//body)"}).parse_fromstring(doc)
    {'heading': '<body>\n<h1>(Some heading)</h1>\n<h2>[some sub-heading]</h2>\n</body>'}
    >>>


*   ``parslepy:xml(xpath_expression)``
    returns the XML content for elements matching *xpath_expression*.
    Internally, this calls `lxml.etree.tostring(element)`.

*   ``parslepy:strip(xpath_expression[, chars])``
    behaves like Python's `strip()` method for strings but for the text
    content of elements matching *xpath_expression*.
    See http://docs.python.org/2/library/string.html#string.strip

    >>> import parslepy
    >>> doc = """<!DOCTYPE html>
    ... <html>
    ... <head>
    ...     <title>Some page title</title>
    ... </head>
    ... <body>
    ... <h1>(Some heading)</h1>
    ... <h2>[some sub-heading]</h2>
    ... </body>
    ... </html>
    ... """
    >>> parslepy.Parselet({"heading": "parslepy:strip(//h2, '[')"}).parse_fromstring(doc)
    {'heading': 'some sub-heading]'}
    >>> parslepy.Parselet({"heading": "parslepy:strip(//h2, ']')"}).parse_fromstring(doc)
    {'heading': '[some sub-heading'}
    >>> parslepy.Parselet({"heading": "parslepy:strip(//h2, '[]')"}).parse_fromstring(doc)
    {'heading': 'some sub-heading'}
    >>> parslepy.Parselet({"heading": "parslepy:strip(//h1, '()')"}).parse_fromstring(doc)
    {'heading': 'Some heading'}
    >>>

*   ``parslepy:attrname(xpath_expression_matching_attribute)``
    returns name of an attribute. This works with the catch-all-attributes
    `@*` expression or a specific attribute expression like `@class`.
    It may sound like a useless extension but it can be useful
    when combined with the simple `@*` selector like in the example below:

    >>> img_attributes = {
    ...     "images(img)": [{
    ...         "attr_names": ["parslepy:attrname(@*)"],
    ...         "attr_vals": ["@*"],
    ...     }]
    ... }
    >>> extracted = parslepy.Parselet(img_attributes).parse('http://www.python.org')
    >>> for r in extracted["images"]:
    ...:     print dict(zip(r.get("attr_names"), r.get("attr_vals")))
    ...:
    {'src': '/images/python-logo.gif', 'alt': 'homepage', 'border': '0', 'id': 'logo'}
    {'src': '/images/trans.gif', 'alt': 'skip to navigation', 'border': '0', 'id': 'skiptonav'}
    {'src': '/images/trans.gif', 'alt': 'skip to content', 'border': '0', 'id': 'skiptocontent'}
    {'width': '116', 'alt': '', 'src': '/images/donate.png', 'title': '', 'height': '42'}
    {'width': '94', 'style': 'align:center', 'src': '/images/worldmap.jpg', 'alt': '[Python resources in languages other than English]', 'height': '46'}
    {'src': '/images/success/Carmanah.png', 'alt': 'success story photo', 'class': 'success'}


User-defined extensions
^^^^^^^^^^^^^^^^^^^^^^^
*parslepy* also lets you define your own XPath extension, just like
`lxml`_ does, except the function you register must accept a user-supplied
context object passed as first argument, subsequent arguments to your extension
function will the same as for `lxml`_ extensions, i.e. an XPath context,
followed by matching elements and whatever additional parameters your XPath
call passes.

The user-supplied context should be passed to :meth:`parslepy.base.Parselet.parse`.

More examples
=============

See https://github.com/redapple/parslepy/wiki#usage

.. include:: ../CHANGELOG
