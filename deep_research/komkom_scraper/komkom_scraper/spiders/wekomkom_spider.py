import scrapy
import re
from komkom_scraper.items import OpportunityItem

class WekomkomSpider(scrapy.Spider):
    name = 'wekomkom_spider'
    allowed_domains = ['wekomkom.com']
    start_urls = ['https://wekomkom.com/accompagnement?tag=opportunite']

    def parse(self, response):
        # Find all anchors with text "Voir l'offre" or href matching /accompagnement/.+
        detail_links = set()

        # Anchors with text "Voir l'offre"
        links_text = response.xpath("//a[contains(normalize-space(text()), \"Voir l'offre\")]/@href").getall()
        detail_links.update(links_text)

        # Anchors with href matching /accompagnement/.+
        links_href = response.xpath("//a[re:match(@href, '^/accompagnement/.+')]/@href", namespaces={"re": "http://exslt.org/regular-expressions"}).getall()
        detail_links.update(links_href)

        for href in detail_links:
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_opportunity)

        # TODO: Handle infinite scroll / load more (API or dynamic content)

    def parse_opportunity(self, response):
        def get_text(query):
            # Try CSS selector first, then XPath if not found
            res = response.css(query).get()
            if res:
                return res.strip()
            res = response.xpath(query).get()
            return res.strip() if res else ''

        def get_html(query):
            htmls = response.css(query).getall()
            if htmls:
                return ''.join(htmls).strip()
            htmls = response.xpath(query).getall()
            return ''.join(htmls).strip() if htmls else None

        # Title: first h1 or h2 text
        title = get_text('h1::text') or get_text('h2::text')

        # Description: main article/section outerHTML, fallback to body
        description = (
            get_html('article')
            or get_html('section')
            or response.xpath('//body').get()
        )

        # Deadline: pattern "XX jours pour postuler" or time[data-countdown]
        deadline = None
        m = re.search(r"(\d+\s+jours\s+pour\s+postuler)", response.text, re.IGNORECASE)
        if m:
            deadline = m.group(1)
        else:
            countdown = response.xpath("//time[@data-countdown]/@data-countdown").get()
            if countdown:
                deadline = countdown

        # Publication date: meta tags
        publication_date = (
            response.css('meta[property="article:published_time"]::attr(content)').get()
            or response.css('meta[name="date"]::attr(content)').get()
            or response.css('meta[name="pubdate"]::attr(content)').get()
        )

        opportunity_type = 'Accompagnement'
        desc_text = description.lower() if description else ""
        if any(kw in desc_text for kw in ['financement', 'subvention', 'prêt']):
            opportunity_type = 'Financement'
        elif any(kw in desc_text for kw in ['formation', 'coaching']):
            opportunity_type = 'Formation'

        eligibility = None  # Not clearly separated

        yield OpportunityItem(
            title=title,
            description=description,
            deadline=deadline,
            publication_date=publication_date,
            opportunity_type=opportunity_type,
            eligibility=eligibility,
            link=response.url,
            source='WEKOMKOM',
        )