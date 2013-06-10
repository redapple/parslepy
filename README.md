parslepy
========

Python/Lxml implementation of the Parsley language for extracting structured data from web pages.

Example usage
=============

```
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

References
==========
* https://github.com/fizx/parsley
* https://github.com/fizx/parsley/wiki/JSON-Structure
* http://snipplr.com/view/67016/parsley-spider/

Dependencies
============
* lxml (http://lxml.de/)

ToDo
====

* add tests
* support XPath functions with CSS selectors
* support optionality operator ("?")
* support complete arrays with the ! operator (https://github.com/fizx/parsley/wiki/JSON-Structure#requiring-complete-arrays-with-the--operator) 
* support bucketed arrays (https://github.com/fizx/parsley/wiki/JSON-Structure#bucketed-arrays)
* investigate PyParsley API
