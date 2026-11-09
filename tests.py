"""Offline tests for advanced_research.main. The Swarms API and Exa are
replaced with fakes, so no keys or network are needed."""

import json

import httpx
import pytest

import advanced_research.main as m
from advanced_research.main import (
    AdvancedResearch,
    AdvancedResearchAdditionalConfig,
    ResearchAPIError,
    SourceRegistry,
    _parse_json,
    _split_report,
    build_references,
    create_json_file,
    execute_worker_search_agents,
    generate_id,
    run_agent,
)


def make_result(url, title="Title", text="Page text"):
    return {
        "url": url,
        "title": title,
        "published_date": "2026-01-02",
        "text": text,
        "highlights": [text[:20]],
    }


@pytest.fixture(autouse=True)
def keys(monkeypatch):
    monkeypatch.setenv("SWARMS_API_KEY", "sk-test")
    monkeypatch.setenv("EXA_API_KEY", "exa-test")


def test_generate_id_is_unique_and_timestamped():
    first, second = generate_id(), generate_id()
    assert first != second
    assert first.startswith("AdvancedResearch-")
    assert len(first.split("-time-")[1]) == 14


def test_each_instance_gets_its_own_id():
    assert AdvancedResearch().id != AdvancedResearch().id


def test_verbose_prints_agent_outputs(monkeypatch, capsys):
    fake_pipeline(monkeypatch, ["Report [1]"])
    AdvancedResearch(max_loops=1, verbose=True).run("query")
    out = capsys.readouterr().out
    assert "[Director-Agent (plan)]" in out
    assert "[Worker-Search-Agent-1 (search round 1)]" in out
    assert "[Director-Agent (report)]" in out
    assert "[Director-Agent (citations)]" in out
    assert "[Citation-Agent (final report)]" in out


def test_verbose_off_is_silent(monkeypatch, capsys):
    fake_pipeline(monkeypatch, ["Report [1]"])
    AdvancedResearch(max_loops=1, verbose=False).run("query")
    assert "[Director-Agent" not in capsys.readouterr().out


def test_create_json_file_merges_into_existing_object(tmp_path):
    path = tmp_path / "out.json"
    create_json_file({"a": 1}, str(path))
    create_json_file({"b": 2}, str(path))
    assert json.loads(path.read_text()) == {"a": 1, "b": 2}


def test_parse_json_reads_fenced_and_bare_objects():
    assert _parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert _parse_json('Here it is: {"b": [1, 2]} done') == {
        "b": [1, 2]
    }
    assert _parse_json("no json here") is None


def test_split_report_reads_the_trailing_decision():
    text = 'Report [1]\n\n```json\n{"needs_more_research": true, "gaps": ["g1"]}\n```'
    assert _split_report(text) == ("Report [1]", True, ["g1"])
    assert _split_report("Report only") == ("Report only", False, [])


def test_source_registry_numbers_each_url_once():
    registry = SourceRegistry()
    assert registry.add(make_result("https://a")) == 1
    assert registry.add(make_result("https://b")) == 2
    assert registry.add(make_result("https://a")) == 1
    assert "[2] Title (2026-01-02)" in registry.format([2])


def test_references_list_only_known_cited_sources():
    registry = SourceRegistry()
    registry.add(make_result("https://a", "A"))
    registry.add(make_result("https://b", "B"))
    references = build_references("x [2] y [9] z [2]", registry)
    assert references == "[2] B, 2026-01-02. https://b"


def test_swarms_agent_sends_the_agent_config_and_reads_its_reply(
    monkeypatch,
):
    sent = {}

    def fake_post(url, headers, json, timeout):
        sent.update(url=url, headers=headers, body=json)
        return httpx.Response(
            200,
            json={
                "outputs": [
                    {"role": "user", "content": "task"},
                    {"role": "Planner", "content": [{"tool": 1}]},
                    {"role": "Planner", "content": "the answer"},
                ],
                "usage": {"total_cost": 0.01},
            },
        )

    monkeypatch.setattr(m.httpx, "post", fake_post)
    text, cost = m.swarms_agent(
        "Planner", "sys", "task", model_name="gpt-5.5", max_tokens=50
    )
    assert (text, cost) == ("the answer", 0.01)
    assert sent["url"].endswith("/v1/agent/completions")
    assert sent["headers"]["x-api-key"] == "sk-test"
    assert sent["body"]["agent_config"]["model_name"] == "gpt-5.5"
    assert sent["body"]["agent_config"]["max_tokens"] == 50


def test_missing_key_is_a_clear_error(monkeypatch):
    monkeypatch.delenv("SWARMS_API_KEY")
    with pytest.raises(ResearchAPIError, match="SWARMS_API_KEY"):
        m.swarms_agent("A", "sys", "task")


def test_gateway_timeout_is_not_retried(monkeypatch):
    calls = []
    clock = iter([0.0, 30.0])
    monkeypatch.setattr(m.time, "monotonic", lambda: next(clock))
    monkeypatch.setattr(
        m.httpx,
        "post",
        lambda *a, **k: calls.append(1) or httpx.Response(503),
    )
    with pytest.raises(ResearchAPIError, match="30-second"):
        m.swarms_agent("A", "sys", "task")
    assert len(calls) == 1


def test_rate_limit_is_retried(monkeypatch):
    responses = iter(
        [
            httpx.Response(429),
            httpx.Response(
                200,
                json={
                    "outputs": [{"role": "A", "content": "ok"}],
                    "usage": {"total_cost": 0},
                },
            ),
        ]
    )
    monkeypatch.setattr(m.time, "sleep", lambda s: None)
    monkeypatch.setattr(
        m.httpx, "post", lambda *a, **k: next(responses)
    )
    assert m.swarms_agent("A", "sys", "task")[0] == "ok"


def test_exa_search_requests_text_and_parses_results(monkeypatch):
    sent = {}

    def fake_post(url, headers, json, timeout):
        sent.update(url=url, headers=headers, body=json)
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "url": "https://a",
                        "title": "A",
                        "publishedDate": "2026-03-04T00:00:00Z",
                        "text": "body",
                        "highlights": ["h"],
                    },
                    {"title": "no url"},
                ]
            },
        )

    monkeypatch.setattr(m.httpx, "post", fake_post)
    results = m.exa_search("query", num_results=3, max_characters=200)
    assert sent["url"].endswith("/search")
    assert sent["headers"]["x-api-key"] == "exa-test"
    assert sent["body"]["numResults"] == 3
    assert sent["body"]["contents"]["text"]["maxCharacters"] == 200
    assert results == [
        {
            "url": "https://a",
            "title": "A",
            "published_date": "2026-03-04",
            "text": "body",
            "highlights": ["h"],
        }
    ]


def test_subagent_runs_follow_up_searches_then_stops(monkeypatch):
    searches, prompts = [], []
    monkeypatch.setattr(
        m,
        "exa_search",
        lambda q, n, c: searches.append(q)
        or [make_result(f"https://{len(searches)}")],
    )
    replies = iter(
        [
            '{"findings": "partial [1]", "follow_up_queries": ["narrow"], "coverage_assessment": "partial"}',
            '{"findings": "full [1][2]", "key_facts": ["f [2]"], "follow_up_queries": ["more"], "coverage_assessment": "comprehensive"}',
        ]
    )
    monkeypatch.setattr(
        m,
        "swarms_agent",
        lambda **k: prompts.append(k["task"]) or (next(replies), 0.5),
    )
    config = AdvancedResearchAdditionalConfig(worker_search_rounds=3)
    result = run_agent(
        1,
        {"objective": "obj", "search_queries": ["broad"]},
        SourceRegistry(),
        config,
    )
    assert searches == ["broad", "narrow"]
    assert result["findings"] == "full [1][2]"
    assert result["source_numbers"] == [1, 2]
    assert result["cost"] == 1.0
    assert "Search round 2 of 3" in prompts[1]


def test_execute_worker_search_agents_returns_text(monkeypatch):
    monkeypatch.setattr(
        m,
        "run_agent",
        lambda i, q, registry, config, verbose=False: {
            "objective": q,
            "findings": f"found {i}",
        },
    )
    assert (
        execute_worker_search_agents(["q1", "q2"])
        == "q1\nfound 1\n\nq2\nfound 2"
    )


def fake_pipeline(monkeypatch, synthesis_replies):
    """Fake Exa and every Swarms API agent for a full run."""
    monkeypatch.setattr(
        m,
        "exa_search",
        lambda q, n, c: [make_result(f"https://{q}")],
    )
    calls = []
    synthesis = iter(synthesis_replies)

    def fake_agent(agent_name, system_prompt, task, **kwargs):
        calls.append(agent_name)
        if "Lead Researcher in a multi-agent" in system_prompt:
            return (
                '{"complexity": "comparison", "subtasks": ['
                '{"objective": "o1", "search_queries": ["s1"]},'
                '{"objective": "o2", "search_queries": ["s2"]}]}',
                0.1,
            )
        if "Research Subagent" in system_prompt:
            return (
                '{"findings": "fact [1]", "coverage_assessment": "comprehensive"}',
                0.1,
            )
        if "final research report" in system_prompt:
            return next(synthesis), 0.1
        return "Cited report [2] and [1] and [7]", 0.1

    monkeypatch.setattr(m, "swarms_agent", fake_agent)
    return calls


def test_run_returns_a_cited_report_with_references(monkeypatch):
    fake_pipeline(monkeypatch, ["Report [1]"])
    research = AdvancedResearch(max_loops=1)
    report = research.run("query")
    assert report.startswith("Cited report [2] and [1] and [7]")
    references = report.split("## References")[1]
    # Source numbers depend on which parallel worker finishes first.
    assert "https://s1" in references
    assert "https://s2" in references
    assert "[1]" in references and "[2]" in references
    assert "[7]" not in references
    assert research.total_cost == pytest.approx(0.5)


def test_run_stops_when_the_lead_finds_no_gaps(monkeypatch):
    calls = fake_pipeline(
        monkeypatch,
        [
            'R1\n```json\n{"needs_more_research": false, "gaps": []}\n```',
            "unused",
        ],
    )
    AdvancedResearch(max_loops=3).run("query")
    assert calls.count("Director-Agent") == 3


def test_run_researches_gaps_in_another_loop(monkeypatch):
    calls = fake_pipeline(
        monkeypatch,
        [
            'R1\n```json\n{"needs_more_research": true, "gaps": ["g"]}\n```',
            'R2\n```json\n{"needs_more_research": true, "gaps": ["h"]}\n```',
        ],
    )
    AdvancedResearch(max_loops=2).run("query")
    assert calls.count("Director-Agent") == 5


def test_output_types(monkeypatch):
    fake_pipeline(monkeypatch, ["Report [1]", "Report [1]"])
    history = AdvancedResearch(output_type="list").run("query")
    assert [message["role"] for message in history] == [
        "human",
        "Director-Agent",
        "Worker-Search-Agent-1",
        "Worker-Search-Agent-2",
        "Citation-Agent",
    ]
    assert isinstance(
        AdvancedResearch(output_type="json").run("query"), str
    )
    with pytest.raises(ValueError):
        AdvancedResearch(output_type="yaml")


def test_run_requires_a_task():
    with pytest.raises(ValueError):
        AdvancedResearch().run()
