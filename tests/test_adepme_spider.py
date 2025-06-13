import os
import pytest
import scrapy
from scrapy.http import HtmlResponse, Request
from deep_research.komkom_scraper.spiders.adepme_spider import AdepmESpider
from deep_research.komkom_scraper.items import OpportunityItem

LIST_PAGE = """
<html>
  <body>
    <section>
      <article>
        <a href="/opportunites/opportunite-1">See more</a>
      </article>
      <article>
        <a href="/opportunites/opportunite-2">See more</a>
      </article>
      <a class="next" href="/opportunites?page=2">Next</a>
    </section>
  </body>
</html>
"""

DETAIL_PAGE = """
<html>
  <head>
    <meta property="article:published_time" content="2023-11-01" />
  </head>
  <body>
    <h1 class="entry-title">Titre de l'Opportunité</h1>
    <article>
      <div class="entry-content">
        <p>Voici la description <b>de l'opportunité</b>.<br>Date limite: 30/11/2023</p>
        <h2>Eligibilité</h2>
        <div>Ouvert aux PME sénégalaises.</div>
      </div>
    </article>
    <strong>Date limite</strong> 30/11/2023
  </body>
</html>
"""

@pytest.fixture
def spider():
    return AdepmESpider.from_crawler(scrapy.crawler.Crawler(scrapy.settings.Settings()))

def test_parse_list_page(spider):
    url = "https://www.adepme.sn/opportunites"
    response = HtmlResponse(url=url, body=LIST_PAGE, encoding='utf-8')
    results = list(spider.parse(response))
    reqs = [r for r in results if isinstance(r, Request)]
    assert len(reqs) == 2  # Two articles
    assert reqs[0].url.endswith('/opportunites/opportunite-1')
    assert reqs[1].url.endswith('/opportunites/opportunite-2')
    # Check pagination
    next_req = [r for r in results if r.url.endswith('?page=2')]
    assert len(next_req) == 1

def test_parse_opportunity(spider):
    url = "https://www.adepme.sn/opportunites/opportunite-1"
    response = HtmlResponse(url=url, body=DETAIL_PAGE, encoding='utf-8')
    items = list(spider.parse_opportunity(response))
    assert len(items) == 1
    item = items[0]
    assert isinstance(item, OpportunityItem)
    assert item['title'] == "Titre de l'Opportunité"
    assert "Voici la description" in item['description']
    assert item['deadline'] == "30/11/2023"
    assert item['publication_date'] == "2023-11-01"
    assert item['opportunity_type'] == "Accompagnement"
    assert "PME sénégalaises" in (item['eligibility'] or "")
    assert item['link'] == url
    assert item['source'] == "ADEPME"