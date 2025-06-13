import scrapy
from deep_research.komkom_scraper.items import OpportunityItem

class AdepmESpider(scrapy.Spider):
    name = 'adepme_opportunity'
    allowed_domains = ['adepme.sn']
    start_urls = ['https://www.adepme.sn/opportunites']

    def parse(self, response):
        # For each listing article, follow link to detail page
        for article in response.css('article'):
            link = article.css('a::attr(href)').get()
            if link:
                yield response.follow(link, callback=self.parse_opportunity)
        # Pagination: follow 'a.next' link if exists
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_opportunity(self, response):
        def get_text(css_sel):
            return response.css(css_sel).get(default='').strip()

        def get_html(css_sel):
            htmls = response.css(css_sel).getall()
            return ''.join(htmls).strip() if htmls else None

        title = get_text('h1.entry-title::text')
        description = get_html('article .entry-content')
        # Deadline: look for Date limite
        deadline = response.xpath(
            "//strong[contains(translate(text(),'DATE LIMITE', 'date limite'), 'date limite')]/following-sibling::text()"
        ).get()
        if not deadline:
            # try regex
            import re
            m = re.search(r"Date limite[^\d]*(\d{2}[/-]\d{2}[/-]\d{4})", response.text, re.IGNORECASE)
            deadline = m.group(1) if m else None

        # publication_date: meta or visible date
        publication_date = response.css('meta[property="article:published_time"]::attr(content)').get()
        if not publication_date:
            # try to find date in visible parts
            pub_date_text = response.css('span.published::text, time.published::attr(datetime)').get()
            publication_date = pub_date_text.strip() if pub_date_text else None

        opportunity_type = 'Accompagnement'
        desc_text = description.lower() if description else ""
        if any(kw in desc_text for kw in ['financement', 'subvention', 'prêt']):
            opportunity_type = 'Financement'
        elif any(kw in desc_text for kw in ['formation', 'coaching']):
            opportunity_type = 'Formation'

        eligibility = None
        # Try to find eligibility section
        eligibility_header = response.xpath(
            "//h2[contains(translate(text(),'ELIGIBILITÉ', 'eligibilité'), 'eligibilité') or contains(translate(text(),'CONDITIONS', 'conditions'), 'conditions')]"
        )
        if eligibility_header:
            node = eligibility_header[0]
            sibling = node.xpath('following-sibling::*[1]')
            eligibility = sibling.get() if sibling else None

        yield OpportunityItem(
            title=title,
            description=description,
            deadline=deadline,
            publication_date=publication_date,
            opportunity_type=opportunity_type,
            eligibility=eligibility,
            link=response.url,
            source='ADEPME',
        )