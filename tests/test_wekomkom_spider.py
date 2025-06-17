import pytest
import scrapy
from scrapy.http import HtmlResponse, Request
from komkom_scraper.spiders.adepme_spider import WekomkomSpider
from komkom_scraper.items import OpportunityItem

LIST_PAGE = """
<html>
  <body>
    <div class="cards">
      <a href="/accompagnement/opportunite-1">Voir l'offre</a>
      <a href="/accompagnement/opportunite-2">Voir l'offre</a>
    </div>
  </body>
</html>
"""

DETAIL_PAGE = """
<html>
  <head>
    <meta property="article:published_time" content="2025-04-01" />
  </head>
  <body>
    <h1>Programme YEF 2025</h1>
    <article>
      <div class="description">
        <p>Ceci est une description détaillée.<br>Date limite: 30/06/2025</p>
        <h2>Eligibilité</h2>
        <div>Ouvert aux jeunes africains.</div>
      </div>
    </article>
  </body>
</html>
"""

@pytest.fixture
def spider():
    return WekomkomSpider.from_crawler(scrapy.crawler.Crawler(scrapy.settings.Settings()))

def test_parse_list_page(spider):
    url = "https://wekomkom.com/accompagnement"
    response = HtmlResponse(url=url, body=LIST_PAGE, encoding='utf-8')
    results = list(spider.parse(response))
    reqs = [r for r in results if isinstance(r, Request)]
    assert len(reqs) == 2
    assert reqs[0].url.endswith('/accompagnement/opportunite-1')
    assert reqs[1].url.endswith('/accompagnement/opportunite-2')

def test_parse_opportunity(spider):
    url = "https://wekomkom.com/accompagnement/opportunite-1"
    response = HtmlResponse(url=url, body=DETAIL_PAGE, encoding='utf-8')
    items = list(spider.parse_opportunity(response))
    assert len(items) == 1
    item = items[0]
    assert isinstance(item, OpportunityItem)
    assert item['title'] == "Programme YEF 2025"
    assert "Ceci est une description" in item['description']
    assert item['deadline'] == "30/06/2025"
    assert item['publication_date'] == "2025-04-01"
    assert item['opportunity_type'] == "Accompagnement"
    assert "jeunes africains" in (item['eligibility'] or "").lower()
    assert item['link'] == url
    assert item['source'] == "WEKOMKOM"