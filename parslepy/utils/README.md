### Tools for Scrapy framework ###

* `parslepy.utils.scrapytools.ParsleyItemClassLoader`
* `parslepy.utils.scrapytools.ParsleyItemLoaderConfig`
* `parslepy.utils.scrapytools.ParsleyImplicitItemClassLoader`: EXPERIMENTAL, TO BE DOCUMENTED

Provide your Parsley script at the command line:

```
$ scrapy crawl MySpider -a parseletfile=myparselet.let.json
```

with a Scrapy spider similar to this:
```python
from mycrawler.items import MyItem
import parslepy

from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst
from parslepy.utils.scrapytools import ParsleyItemClassLoader, ParsleyItemLoaderConfig

class MyItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class MySpider(BaseSpider):
    name = "MySpider"
    allowed_domains = ["example.com"]
    start_urls = ["http://www.example.com/index.html"]

    def __init__(self, parseletfile=None):

        if parseletfile:
            with open(parseletfile) as jsonfp:
                self.parselet = parslepy.Parselet.from_jsonfile(jsonfp)

    def parse(self, response):

        loader = ParsleyItemClassLoader(
                        parselet=self.parselet,
                        configs=[
                            ParsleyItemLoaderConfig(
                                MyItem,
                                MyItemLoader)
                        ],
                        response=response)
        for i in loader.iter_items(response):
            yield i
```
