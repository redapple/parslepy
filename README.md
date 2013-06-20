parslepy
========

(partial) Python/Lxml implementation of the Parsley language for extracting structured data from web pages.

**This *Parsley* has nothing to do with the parsing library https://pypi.python.org/pypi/Parsley**

Kudos go to Kyle Maxwell (@fizx) for coming up with this smart and easy syntax to define extracting rules.

### References ###

* https://github.com/fizx/parsley
* https://github.com/fizx/parsley/wiki/JSON-Structure
* http://snipplr.com/view/67016/parsley-spider/
* https://news.ycombinator.com/item?id=1585301

### Dependencies ###

* lxml (http://lxml.de/)

### Install ###

```bash
$ python setup.py install
...or
$ sudo python setup.py install
```

### Example usage from Python shell ###

```python
>>> import parslepy
>>> import urllib2
>>> import pprint
>>> rules = {"titles": ["h1,h2"], "links((//a[re:test(@href, '^http://')])[position()<=10])": [{"name":".","url": "@href"}]}
>>> pprint.pprint(rules)
{"links((//a[re:test(@href, '^http://')])[position()<=10])": [{'name': '.',
                                                               'url': '@href'}],
 'titles': ['h1,h2']}
>>> parselet = parslepy.Parselet(rules)
>>> url = 'http://en.wikipedia.org/wiki/Python_(programming_language)'
>>> req = urllib2.Request(url)
>>> ua = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36'
>>> req.add_header('User-Agent', ua)
>>> extracted = parselet.parse(urllib2.urlopen(req))
>>> pprint.pprint(extracted)
{'links': [{'name': u'Official website', 'url': 'http://www.python.org/'},
           {'name': u'"Why was Python created in the first place?".',
            'url': 'http://docs.python.org/faq/general.html#why-was-python-created-in-the-first-place'},
           {'name': u'"Interview with Guido van Rossum (July 1998)".',
            'url': 'http://www.amk.ca/python/writing/gvr-interview'},
           {'name': u'"An Introduction to Python for UNIX/C Programmers".',
            'url': 'http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.38.2023'},
           {'name': u'"Classes".',
            'url': 'http://docs.python.org/tutorial/classes.html'},
           {'name': u'"The Python 2.3 Method Resolution Order". Python Software Foundation. "The C3 method itself has nothing to do with Python, since it was invented by people working on Dylan and it is described in a paper intended for lispers"',
            'url': 'http://www.python.org/download/releases/2.3/mro/'},
           {'name': u'"Functional Programming HOWTO".',
            'url': 'http://docs.python.org/howto/functional.html'},
           {'name': u'"PEP 255 \u2013 Simple Generators".',
            'url': 'http://www.python.org/dev/peps/pep-0255/'},
           {'name': u'"PEP 318 \u2013 Decorators for Functions and Methods".',
            'url': 'http://www.python.org/dev/peps/pep-0318/'},
           {'name': u'"More Control Flow Tools".',
            'url': 'http://docs.python.org/py3k/tutorial/controlflow.html'}],
 'titles': [u'Python (programming language)',
            u'Contents',
            u'History[edit]',
            u'Features and philosophy[edit]',
            u'Syntax and semantics[edit]',
            u'Libraries[edit]',
            u'Development environments[edit]',
            u'Implementations[edit]',
            u'Development[edit]',
            u'Naming[edit]',
            u'Use[edit]',
            u'Impact[edit]',
            u'See also[edit]',
            u'References[edit]',
            u'Further reading[edit]',
            u'External links[edit]',
            u'Navigation menu']}
>>>
```

### Example usage with parselet file ###


```bash
$ cat examples/engadget.let.js
{
    "sections(nav#nav-main > ul li)": [{
        "title": ".",
        "url_css": "a.item @href",
        "url_xpath": "a[re:test(@class, 'item')]/@href"
    }]
}
$ python run_parslepy.py --script examples/engadget.let.js --url http://www.engadget.com/
{u'sections': [{u'title': u'News', u'url_css': '/', u'url_xpath': '/'},
               {u'title': u'Reviews',
                u'url_css': '/reviews/',
                u'url_xpath': '/reviews/'},
               {u'title': u'Features',
                u'url_css': '/features/',
                u'url_xpath': '/features/'},
               {u'title': u'Galleries',
                u'url_css': '/galleries/',
                u'url_xpath': '/galleries/'},
               {u'title': u'Videos',
                u'url_css': '/videos/',
                u'url_xpath': '/videos/'},
               {u'title': u'Events',
                u'url_css': '/events/',
                u'url_xpath': '/events/'},
               {u'title': u'Podcasts',
                u'url_css': '/podcasts/the-engadget-podcast/',
                u'url_xpath': '/podcasts/the-engadget-podcast/'},
               {u'title': u'Engadget Show',
                u'url_css': '/videos/show/',
                u'url_xpath': '/videos/show/'},
               {u'title': u'Topics',
                u'url_css': '#nav-topics',
                u'url_xpath': '#nav-topics'}]}

```



### Run tests using `nose` ###

```bash
$ nosetests -v tests
```


### ToDo ###

* add more tests
* support XPath functions with CSS selectors
* ~~support optionality operator ("?")~~
* support complete arrays with the "!" operator (https://github.com/fizx/parsley/wiki/JSON-Structure#requiring-complete-arrays-with-the--operator)
* support bucketed arrays (https://github.com/fizx/parsley/wiki/JSON-Structure#bucketed-arrays);
see https://github.com/redapple/parslepy/wiki/Implementing-bucketed-arrays-(work-in-progess)
* investigate PyParsley API
