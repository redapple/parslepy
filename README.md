parslepy
========

Python implementation of the Parsley language for extracting structured data from web pages

Example usage
=============

```
$ python run_parslepy.py --script examples/engadget.let.js --url http://www.engadget.com/
```

References
==========
* https://github.com/fizx/parsley
* https://github.com/fizx/parsley/wiki/JSON-Structure

Dependencies
============
* lxml (http://lxml.de/)

ToDo
====

* support optionality operator ("?")
* support complete arrays with the ! operator (https://github.com/fizx/parsley/wiki/JSON-Structure#requiring-complete-arrays-with-the--operator) 
* support bucketed arrays (https://github.com/fizx/parsley/wiki/JSON-Structure#bucketed-arrays)
