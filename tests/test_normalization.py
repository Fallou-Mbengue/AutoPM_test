import pytest
from deep_research.komkom_scraper.pipelines import NormalizationPipeline

def test_clean_text_html():
    html = "<p>Hello <b>World</b>!</p>"
    cleaned = NormalizationPipeline.clean_text(html)
    assert cleaned == "Hello World!"

def test_clean_text_whitespace():
    text = "  This   is  a   test.\nNew line. "
    cleaned = NormalizationPipeline.clean_text(text)
    assert cleaned == "This is a test. New line."

@pytest.mark.parametrize("date_str,expected", [
    ("2023-12-31", "2023-12-31"),
    ("31-12-2023", "2023-12-31"),
    ("31/12/2023", "2023-12-31"),
    ("December 31, 2023", "2023-12-31"),
    ("31 December 2023", "2023-12-31"),
])
def test_parse_date_formats(date_str, expected):
    result = NormalizationPipeline.parse_date(date_str)
    assert result.isoformat() == expected

def test_parse_date_invalid():
    assert NormalizationPipeline.parse_date("not a date") is None

def test_fingerprint_item_consistency():
    item = {'title': 'Grant', 'deadline': '2023-12-31', 'link': 'https://a.com'}
    fp1 = NormalizationPipeline.fingerprint_item(item)
    fp2 = NormalizationPipeline.fingerprint_item(item)
    assert fp1 == fp2
    item2 = {'title': 'Grant', 'deadline': '2023-12-31', 'link': 'https://b.com'}
    assert fp1 != NormalizationPipeline.fingerprint_item(item2)