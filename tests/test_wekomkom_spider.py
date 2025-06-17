import pytest
import scrapy
from scrapy.http import HtmlResponse, Request
from komkom_scraper.spiders.wekomkom_spider import WekomkomSpider
from komkom_scraper.items import OpportunityItem

LIST_PAGE = """
<html>
  <body>
    <section>
      <a href="/accompagnement/opp-1">Voir l'offre</a>
      <a href="/accompagnement/opp-2">Voir l'offre</a>
      <a href="/accompagnement/opp-3/info">Voir l'offre</a>
      <a href="/autre-page">Autre</a>
    </section>
  </body>
</html>
"""

DETAIL_PAGE = """
<html>
  <head>
    <meta property="article:published_time" content="2024-05-10" />
    <meta name="date" content="2024-05-10" />
  </head>
  <body>
    <h1>Super Opportunité Wekomkom</h1>
    <article>
      <div>
        <p>Ceci est la <strong>description</strong> principale.</p>
        <p>Vous avez 7 jours pour postuler.</p>
        <p>Bénéficiez d'un financement exceptionnel!</p>
      </div>
    </article>
    <time data-countdown="7 jours pour postuler"></time>
  </body>
</html>
"""

DETAIL_PAGE_FORMATION = """
<html>
  <body>
    <h2>Formation intensive</h2>
    <section>
      <p>Cette offre inclut un coaching sur mesure pour PME.</p>
    </section>
    <meta name="date" content="2024-04-01" />
  </body>
</html>
"""

@pytest.fixture
def spider():
    return WekomkomSpider.from_crawler(scrapy.crawler.Crawler(scrapy.settings.Settings()))

def test_parse_list_page(spider):
    url = "https://wekomkom.com/accompagnement?tag=opportunite"
    response = HtmlResponse(url=url, body=LIST_PAGE, encoding='utf-8')
    results = list(spider.parse(response))
    reqs = [r for r in results if isinstance(r, Request)]
    # There should be 3 valid detail links, not the unrelated one
    assert len(reqs) == 3
    for r in reqs:
        assert "/accompagnement/" in r.url
        assert "autre-page" not in r.url

def test_parse_opportunity(spider):
    url = "https://wekomkom.com/accompagnement/opp-1"
    response = HtmlResponse(url=url, body=DETAIL_PAGE, encoding='utf-8')
    items = list(spider.parse_opportunity(response))
    assert len(items) == 1
    item = items[0]
    assert isinstance(item, OpportunityItem)
    assert item['title'] == "Super Opportunité Wekomkom"
    assert "Ceci est la" in item['description']
    assert item['deadline'] == "7 jours pour postuler"
    assert item['publication_date'] == "2024-05-10"
    assert item['opportunity_type'] == "Financement"
    assert item['eligibility'] is None
    assert item['link'] == url
    assert item['source'] == "WEKOMKOM"

def test_parse_opportunity_formation(spider):
    url = "https://wekomkom.com/accompagnement/opp-formation"
    response = HtmlResponse(url=url, body=DETAIL_PAGE_FORMATION, encoding='utf-8')
    items = list(spider.parse_opportunity(response))
    assert len(items) == 1
    item = items[0]
    assert item['title'] == "Formation intensive"
    assert "coaching" in item['description'].lower()
    assert item['opportunity_type'] == "Formation"
    assert item['publication_date'] == "2024-04-01"