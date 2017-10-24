.. parslepy documentation master file, created by
   sphinx-quickstart on Mon Jul  1 15:20:50 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

parslepy -- Documentation
=========================

Introduction
------------

*parslepy* lets you extract content from HTML and XML documents
**using rules defined in a JSON object** (or a Python :class:`dict`).
The object keys mean the names you want to assign for the data in each
document section and the values are CSS selectors or XPath expressions
that will match the document parts (elements or attributes).

Here is an example for extracting questions in StackOverflow first page::

    {
        "first_page_questions(//div[contains(@class,'question-summary')])": [{
            "title": ".//h3/a",
            "tags": "div.tags",
            "votes": "div.votes div.mini-counts",
            "views": "div.views div.mini-counts",
            "answers": "div.status div.mini-counts"
        }]
    }

Some details
^^^^^^^^^^^^

*parslepy* is a Python implementation (built on top of `lxml`_ and `cssselect`_)
of the `Parsley DSL`_ for extraction content from structured documents,
defined by Kyle Maxwell and Andrew Cantino
(see the `parsley wiki`_ for more details and original C implementation).

The default behavior for the selectors is:

* selectors for elements will output their matching textual content (children elements' content is also included)
* selectors matching element attributes will output the attribute's value

So, if you use ``//h1/a`` in a selector, *parslepy* will extract the text inside of the ``a`` element
and its children, and if you use ``//h1/a/@href`` it will extract the value for ``href``, i.e.,
the address the link is pointing to.


You can also nest objects, generate lists of objects, and mix CSS and XPath
-- although not in the same selector.

*parslepy* understands what `lxml`_ and `cssselect`_ understand,
which is roughly `CSS3 Selectors`_ and `XPath 1.0`_.


.. _CSS3 Selectors: http://www.w3.org/TR/2011/REC-css3-selectors-20110929/
.. _XPath 1.0: http://www.w3.org/TR/xpath/
.. _lxml: http://lxml.de/
.. _cssselect: https://github.com/SimonSapin/cssselect
.. _Parsley DSL: https://github.com/fizx/parsley
.. _parsley wiki: https://github.com/fizx/parsley/wiki


Syntax summary
^^^^^^^^^^^^^^

Here is a quick description of the rules format::

    output key (mandatory)
        |
        |  optionality operator (optional)
        |   |
        |   |   scope, always within brackets (optional)
        |   |      |
        v   v      v
    "somekey?(someselector)":   "someCSSSelector"

    or         //           :   "someXPathExpression"

    or         //           :   ["someXPathOrCSSExpression"]

    or         //           :    { ...some other rules... }

    or         //           :    [{ ...some other rules... }]


A collection of extraction rules (also called a *parselet*,
or *Parsley script*) looks like this in JSON format::

    {
        "somekey": "#someID .someclass",                        # using a CSS selector
        "anotherkey": "//sometag[@someattribute='somevalue']",  # using an XPath expression
        "nestedkey(.somelistclass)": [{                         # CSS selector for multiple elements (scope selector)
            "somenestedkey": "somenestedtag/@someattribute"     # XPath expression for an attribbute
       }]
    }

... or like this in YAML format:

    ---
    somekey: "#someID .someclass"                        # using a CSS selector
    anotherkey: "//sometag[@someattribute='somevalue']"  # using an XPath expression
    nestedkey(.somelistclass):                           # CSS selector for multiple elements (scope selector)
    - somenestedkey: somenestedtag/@someattribute        # XPath expression for an attribbute

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



Quickstart
----------

Install
^^^^^^^

From PyPI
#########

You can install *parslepy* from `PyPI <https://pypi.python.org/pypi/parslepy>`_:

.. code-block:: bash

    sudo pip install parslepy


From latest source
##################

You can also install from source code (make sure you have the
``lxml`` and ``cssselect`` libraries already installed):

.. code-block:: bash

    git clone https://github.com/redapple/parslepy.git
    sudo python setup.py install

You probably want also to make sure the tests passes:

.. code-block:: bash

    sudo pip install nosetests # only needed if you don't have nosetests installed
    nosetests -v tests

Usage
^^^^^

Here are some examples on how to use parslepy.
You can also check out the examples and tutorials at `parsley's wiki at GitHub <https://github.com/redapple/parslepy/wiki#usage>`_.

Extract the questions from StackOverflow first page:

    >>> import parslepy, urllib2
    >>> rules = {"questions(//div[contains(@class,'question-summary')])": [{"title": ".//h3/a", "votes": "div.votes div.mini-counts"}]}
    >>> parslepy.Parselet(rules).parse(urllib2.urlopen('http://stackoverflow.com'))
    {'questions': [{'title': u'node.js RSS memory grows over time despite fairly consistent heap sizes',
        'votes': u'0'},
        {'title': u'SQL query for count of predicate applied on rows of subquery',
        'votes': u'3'},
        ...
    }

Extract a page heading and a list of item links from a string containing HTML:

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
    >>>


Extract using the rules in a JSON file (from *parslepy*'s ``examples/`` directory):

.. code-block:: bash

    # Parselet file containing CSS selectors
    $ cat examples/engadget_css.let.json
    {
        "sections(nav#nav-main > ul li)": [{
            "title": ".",
            "url": "a.item @href",
        }]
    }
    $ python run_parslepy.py --script examples/engadget_css.let.json --url http://www.engadget.com
    {u'sections': [{u'title': u'News', u'url': '/'},
                {u'title': u'Reviews', u'url': '/reviews/'},
                {u'title': u'Features', u'url': '/features/'},
                {u'title': u'Galleries', u'url': '/galleries/'},
                {u'title': u'Videos', u'url': '/videos/'},
                {u'title': u'Events', u'url': '/events/'},
                {u'title': u'Podcasts',
                    u'url': '/podcasts/the-engadget-podcast/'},
                {u'title': u'Engadget Show', u'url': '/videos/show/'},
                {u'title': u'Topics', u'url': '#nav-topics'}]}


You may want to check out the other examples given in the ``examples/`` directory.
You can run them using the ``run_parslepy.py`` script like shown above.


Selector syntax
^^^^^^^^^^^^^^^

*parslepy* understands `CSS3 Selectors`_ and `XPath 1.0`_ expressions.

Select elements attributes by name
##################################

It also accepts `Parsley DSL`_'s ``@attributename`` at the end of CSS
selectors, to get the attribute(s) of the preceding selected element(s).
*parslepy* supports `Scrapy`_'s ``::attr(attributename)`` functional pseudo
element extension to CCS3, which gets attributes by ``attributename``.

See the two syntax variants in use:

.. code-block:: bash

    >>> import parslepy
    >>> import pprint
    >>>
    >>> html = """
    ... <!DOCTYPE html>
    ... <html>
    ... <head>
    ...     <title>Sample document to test parslepy</title>
    ...     <meta http-equiv="content-type" content="text/html;charset=utf-8" />
    ... </head>
    ... <body>
    ... <div>
    ... <a class="first" href="http://www.example.com/first">First link</a>
    ... <a class="second" href="http://www.example.com/second">Second link</a>
    ... </div>
    ... </body>
    ... </html>"""
    >>> rules = {
    ...      "links": {
    ...         "first_class": ["a.first::attr(href)"],
    ...         "second_class": ["a.second @href"],
    ...     }
    ... }
    >>> p = parslepy.Parselet(rules)
    >>> extracted = p.parse_fromstring(html)
    >>> pprint.pprint(extracted)
    {'links': {'first_class': ['http://www.example.com/first'],
               'second_class': ['http://www.example.com/second']}}
    >>>


Select text and comments nodes
##############################

Borrowing from `Scrapy`_'s extension to CCS3 selectors,
*parslepy* supports ``::text`` and ``::comment`` pseudo
elements (resp. get text nodes of an element, and extract
comments in XML/HTML elements)

.. code-block:: bash

    >>> import parslepy
    >>> import pprint
    >>>
    >>> html = """
    ... <!DOCTYPE html>
    ... <html>
    ... <head>
    ...     <title>Sample document to test parslepy</title>
    ...     <meta http-equiv="content-type" content="text/html;charset=utf-8" />
    ... </head>
    ... <body>
    ... <h1 id="main">News</h1>
    ... <!-- this is a comment -->
    ... <div>
    ... <p>Something to say</p>
    ... <!-- this is another comment -->
    ... </div>
    ... </body>
    ... </html>"""
    >>> rules = {
    ...      "comments": {
    ...         "all": ["::comment"],
    ...         "inside_div": "div::comment"
    ...     }
    ... }
    >>> p = parslepy.Parselet(rules)
    >>> extracted = p.parse_fromstring(html)
    >>> pprint.pprint(extracted)
    {'comments': {'all': [u'this is a comment', u'this is another comment'],
                  'inside_div': u'this is another comment'}}
    >>>


.. _CSS3 Selectors: http://www.w3.org/TR/2011/REC-css3-selectors-20110929/
.. _XPath 1.0: http://www.w3.org/TR/xpath/
.. _Parsley DSL: https://github.com/fizx/parsley
.. _Scrapy: http://scrapy.org/


Dependencies
------------

The current dependencies of the master branch are:

* lxml>=2.3 (http://lxml.de/, https://pypi.python.org/pypi/lxml)
* cssselect (https://github.com/SimonSapin/cssselect/, https://pypi.python.org/pypi/cssselect) (for lxml>=3)


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
    :members: parse, from_jsonfile, from_jsonstring, from_yamlfile, from_yamlstring, extract, parse_fromstring, keys

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
        >>>
        >>> # register Atom and iTunes namespaces with prefixes "atom" and "im"
        ... # with a custom SelectorHandler
        ... xsh = parslepy.XPathSelectorHandler(
        ...     namespaces={
        ...         'atom': 'http://www.w3.org/2005/Atom',
        ...         'im': 'http://itunes.apple.com/rss'
        ...     })
        >>>
        >>> # use prefixes to target elements in the XML document
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
    The optional boolean second parameter indicates whether *tail* content
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

*parslepy* also lets you define your own XPath extensions, just like
`lxml`_ does, except the function you register must accept a user-supplied
context object passed as first argument, subsequent arguments to your extension
function will be the same as for `lxml`_ extensions, i.e. an XPath context,
followed by matching elements and whatever additional parameters your XPath
call passes.

The user-supplied context should be passed to :meth:`parslepy.base.Parselet.parse`,
or globally to a XPathSelectorHandler subclass instance passed to instantiate a Parselet.

Let's illustrate this with a custom extension to make `<img>` @src
attributes "absolute".

Suppose we already have an extraction rule that outputs the `@src` attributes
from `<img>` tags on the Python.org homepage:

    >>> import parslepy
    >>> import pprint
    >>> parselet = parslepy.Parselet({"img_abslinks": ["//img/@src"]})
    >>> pprint.pprint(parselet.parse('http://www.python.org'))
    {'img_abslinks': ['/images/python-logo.gif',
                      '/images/trans.gif',
                      '/images/trans.gif',
                      '/images/donate.png',
                      '/images/worldmap.jpg',
                      '/images/success/afnic.fr.png']}

We now want to generate full URLs for these images, not relative to
http://www.python.org.

**First we need to define our extension function as a Python function**:

*parslepy*'s extension functions must accept a user-context as first argument,
then should expect an XPath context, followed by elements or strings
matching the XPath expression,
and finally whatever other parameters are passed to the function call
in extraction rules.

In our example, we expect `@src` attribute values as input from XPath,
and combine them with a base URL (via `urlparse.urljoin()`),
the URL from which the HTML document was fetched.
The base URL will be passed as user-context, and we will receive it as
first argument.
So the Python extension function may look like this:

    >>> import urlparse
    >>> def absurl(ctx, xpctx, attributes, *args):
    ...         # user-context "ctx" will be the URL of the page
    ...         return [urlparse.urljoin(ctx, u) for u in attributes]
    ...

**Then, we need to register this function with parslepy** through
a custom selector handler, with a custom namespace and its prefix:

    >>> # choose a prefix and namespace, e.g. "myext" and "local-extensions"
    ... mynamespaces = {
    ...         "myext": "local-extensions"
    ...     }
    >>> myextensions = {
    ...         ("local-extensions", "absurl"): absurl,
    ...     }
    >>>
    >>> import parslepy
    >>> sh = parslepy.DefaultSelectorHandler(
    ...         namespaces=mynamespaces,
    ...         extensions=myextensions)
    >>>


Now we can use this **absurl()** XPath extension within *parslepy* rules,
with the "myext" prefix
(**do not forget to pass your selector handler** to your Parselet instance):

    >>> rules = {"img_abslinks": ["myext:absurl(//img/@src)"]}
    >>> parselet = parslepy.Parselet(rules, selector_handler=sh)

And finally, run the extraction rules on Python.org's homepage again,
with a context argument set to the URL

    >>> import pprint
    >>> pprint.pprint(parselet.parse('http://www.python.org',
    ...         context='http://www.python.org'))
    {'img_abslinks': ['http://www.python.org/images/python-logo.gif',
                      'http://www.python.org/images/trans.gif',
                      'http://www.python.org/images/trans.gif',
                      'http://www.python.org/images/donate.png',
                      'http://www.python.org/images/worldmap.jpg',
                      'http://www.python.org/images/success/afnic.fr.png']}
    >>>

In this case, it may feel odd to have to pass the URL *twice*,
but parse(*URL*) does not store the URL anywhere, it processes only
the HTML stream from the page.

More examples
=============

Check out more examples and tutorials at `parsley's wiki at GitHub <https://github.com/redapple/parslepy/wiki#usage>`_.

.. include:: ../CHANGELOG
