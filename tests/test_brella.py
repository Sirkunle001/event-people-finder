import json

from event_people_finder.brella import _bio_text
from event_people_finder.export import dedupe, write_speakers

BODY = json.dumps({
    "data": [
        {"attributes": {"first-name": "Adi", "last-name": "Levanon",
                        "job-title": "Founder & Managing Partner",
                        "company-name": "Selah Ventures", "photo-url": None,
                        "bio": {"blocks": [{"key": "6j376", "text": "Bio line one."},
                                           {"key": "7k485", "text": "Bio line two."}]}}},
        {"attributes": {"first-name": "Adam", "last-name": "Zerda",
                        "job-title": "Founder & CEO", "company-name": "Visby Medical"}},
        {"attributes": {"first-name": "Adi", "last-name": "Levanon",
                        "job-title": "Founder & Managing Partner",
                        "company-name": "Selah Ventures"}},  # dupe
    ],
    "links": {"next": None},
})


def test_bio_text_joins_draftjs_blocks():
    bio = {"blocks": [{"key": "a", "text": "One."}, {"key": "b", "text": "Two."}]}
    assert _bio_text(bio) == "One.\nTwo."


def test_bio_text_plain_string():
    assert _bio_text("plain bio") == "plain bio"
    assert _bio_text(None) == ""


def test_dedupe_by_name_company():
    rows = [{"name": "Adi Levanon", "company": "Selah Ventures", "x": 1},
            {"name": "Adi Levanon", "company": "Selah Ventures", "x": 2},
            {"name": "Adam Zerda", "company": "Visby Medical", "x": 3}]
    out, dropped = dedupe(rows, ("name", "company"))
    assert len(out) == 2 and dropped == 1


def test_write_speakers(tmp_path):
    rows = [{"name": "Adi Levanon", "first": "Adi", "last": "Levanon",
             "title": "Founder & Managing Partner", "company": "Selah Ventures",
             "bio": "Bio.", "photo": ""}]
    p = tmp_path / "speakers.csv"
    n = write_speakers(rows, str(p), "FJ26")
    assert n == 1
    text = p.read_text(encoding="utf-8-sig")
    assert "Selah Ventures" in text and "FJ26" in text
