parslepy
========

(partial) Python/Lxml implementation of the Parsley language for extracting structured data from web pages.

**This *Parsley* has nothing to do with https://pypi.python.org/pypi/Parsley**

### Install ###

```bash
$ python setup.py install
...or
$ sudo python setup.py install
```

### Example usage from the command line ###

```python
>>> import parslepy
>>> import urllib
>>> import pprint
>>> parselet = parslepy.Parselet({"titles": ["h1,h2,h3,h4,h5,h6"], "links": ["a @href"]})
>>> pprint.pprint(parselet.parse(urllib.urlopen('http://www.facebook.com')))
{'links': ['/',
           'http://www.facebook.com/recover/initiate',
           '#',
           '/legal/terms',
           '/about/privacy',
           '/help/cookies',
           '/pages/create/',
           'https://www.facebook.com/',
...
           'http://www.facebook.com/policies/?ref=pf',
           'http://www.facebook.com/help/?ref=pf',
           '/ajax/intl/language_dialog.php?uri=https%3A%2F%2Fwww.facebook.com%2F'],
 'titles': [u'Inscription',
            u'C\u2019est gratuit (et \xe7a le restera toujours).',
            u'JavaScript est d\xe9sactiv\xe9 dans votre navigateur.',
            u'Test de s\xe9curit\xe9']}
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

### References ###

* https://github.com/fizx/parsley
* https://github.com/fizx/parsley/wiki/JSON-Structure
* http://snipplr.com/view/67016/parsley-spider/
* https://news.ycombinator.com/item?id=1585301

### Dependencies ###

* lxml (http://lxml.de/)

### Run tests using `nose` ###

```bash
$ nosetests -v tests
```


### ToDo ###

* add more tests
* support XPath functions with CSS selectors
* <del>support optionality operator ("?")</del>
* support complete arrays with the "!" operator (https://github.com/fizx/parsley/wiki/JSON-Structure#requiring-complete-arrays-with-the--operator)
* support bucketed arrays (https://github.com/fizx/parsley/wiki/JSON-Structure#bucketed-arrays)
* investigate PyParsley API
