from gevent.threadpool import ThreadPool
from gevent.pool import Pool
from lxml.html import fromstring
from urlparse import urlsplit, urljoin
import requests
from .utils import timer

def tail(file):
    client.send_status('Spidering {url}...'.format(url=url))
    client.send_result(result)

    html = threadpool.apply(fromstring, [response.text])
    for link in html.cssselect('a'):
        href = link.attrib.get('href').split('#')[0].strip()
        if not href:
            continue
        url = urljoin(response.url, href)
        parts = urlsplit(url)
        if parts.netloc not in domain_whitelist:
            continue
        if url in tested:
            continue
        tested.add(url)
        pool.spawn(spider, client, url, domain_whitelist, pool, threadpool, tested)
    return pool
