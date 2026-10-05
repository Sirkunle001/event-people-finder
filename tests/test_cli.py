"""Command line interface tests are light; the API client is fixture-tested."""
import os

from event_people_finder.cli import _code_from_target


def test_code_from_target_event_url():
    assert _code_from_target("https://next.brella.io/events/FJ26/home") == "FJ26"
    assert _code_from_target("https://next.brella.io/events/SVNovSummit25") == "SVNovSummit25"


def test_code_from_target_bare_code():
    assert _code_from_target("FJ26") == "FJ26"


def test_code_from_target_arbitrary_url():
    assert _code_from_target("https://lu.ma/someevent") == "someevent"
