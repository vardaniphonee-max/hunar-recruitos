import asyncio

from app.providers.demo import DemoPeopleSearchProvider, DemoVoiceProvider
from app.schemas import SearchCriteria


def test_demo_people_search_is_explicitly_labelled():
    provider = DemoPeopleSearchProvider()
    results, raw = asyncio.run(provider.search(SearchCriteria(
        role_id=1, titles=["Customer Success Manager"], locations=["Bengaluru"]
    )))
    assert results
    assert all(result.is_demo for result in results)
    assert all(result.source.startswith("demo") for result in results)
    assert raw["demo"] is True


def test_demo_voice_never_returns_live_claim():
    provider = DemoVoiceProvider()
    result = asyncio.run(provider.create_call(
        agent_id="demo", callee_name="Test Candidate", mobile_number="+910000000000",
        custom_data={}, request_id="demo-request", callback_config=None,
    ))
    assert result["is_demo"] is True
    assert result["id"].startswith("demo-call-")
