"""Tests for scoring data sources using mocked HTTP responses."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_response(
    *,
    status_code: int = 200,
    json_data: object = None,
    text: str = "",
) -> httpx.Response:
    """Build a fake ``httpx.Response`` without hitting the network."""
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.text = text
    if json_data is not None:
        resp.json.return_value = json_data
    else:
        resp.json.side_effect = ValueError("No JSON")
    resp.raise_for_status = MagicMock()
    return resp


def _mock_client(response: httpx.Response) -> AsyncMock:
    """Return an ``AsyncMock`` that behaves like ``httpx.AsyncClient``."""
    client = AsyncMock()
    client.get = AsyncMock(return_value=response)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    return client


# ---------------------------------------------------------------------------
# DevHunt
# ---------------------------------------------------------------------------


class TestDevhunt:
    @pytest.mark.asyncio
    async def test_happy_path(self) -> None:
        from scoring.sources.devhunt import fetch_signals

        resp = _mock_response(json_data={"tools": [{"upvotes": 50}]})
        client = _mock_client(resp)
        with patch("scoring.sources.devhunt.httpx.AsyncClient", return_value=client):
            result = await fetch_signals("owner/repo")
        assert "upvotes" in result
        assert isinstance(result["upvotes"], float)

    @pytest.mark.asyncio
    async def test_network_error(self) -> None:
        from scoring.sources.devhunt import fetch_signals

        client = AsyncMock()
        client.get = AsyncMock(side_effect=httpx.ConnectError("offline"))
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)
        with patch("scoring.sources.devhunt.httpx.AsyncClient", return_value=client):
            result = await fetch_signals("owner/repo")
        assert result == {"upvotes": 0.0}

    @pytest.mark.asyncio
    async def test_malformed_json(self) -> None:
        from scoring.sources.devhunt import fetch_signals

        resp = _mock_response(json_data="not a dict or list")
        client = _mock_client(resp)
        with patch("scoring.sources.devhunt.httpx.AsyncClient", return_value=client):
            result = await fetch_signals("owner/repo")
        assert "upvotes" in result


# ---------------------------------------------------------------------------
# TheRundown
# ---------------------------------------------------------------------------


class TestTheRundown:
    @pytest.mark.asyncio
    async def test_mention_found(self) -> None:
        from scoring.sources.therundown import fetch_signals

        html = "<html><body>Check out owner/repo today</body></html>"
        resp = _mock_response(text=html)
        client = _mock_client(resp)
        with patch("scoring.sources.therundown.httpx.AsyncClient", return_value=client):
            result = await fetch_signals("owner/repo")
        assert result["mention"] == 1.0

    @pytest.mark.asyncio
    async def test_mention_not_found(self) -> None:
        from scoring.sources.therundown import fetch_signals

        resp = _mock_response(text="<html><body>Nothing relevant</body></html>")
        client = _mock_client(resp)
        with patch("scoring.sources.therundown.httpx.AsyncClient", return_value=client):
            result = await fetch_signals("owner/repo")
        assert result["mention"] == 0.0

    @pytest.mark.asyncio
    async def test_network_error(self) -> None:
        from scoring.sources.therundown import fetch_signals

        client = AsyncMock()
        client.get = AsyncMock(side_effect=httpx.ConnectError("offline"))
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)
        with patch("scoring.sources.therundown.httpx.AsyncClient", return_value=client):
            result = await fetch_signals("owner/repo")
        assert result == {"mention": 0.0}


# ---------------------------------------------------------------------------
# HackerNews
# ---------------------------------------------------------------------------


class TestHackerNews:
    @pytest.mark.asyncio
    async def test_happy_path(self) -> None:
        from scoring.sources.hackernews import fetch_signals

        resp = _mock_response(
            json_data={
                "hits": [
                    {"objectID": "1", "points": 200, "num_comments": 50},
                    {"objectID": "2", "points": 100, "num_comments": 30},
                ]
            }
        )
        client = _mock_client(resp)
        with patch("scoring.sources.hackernews.httpx.AsyncClient", return_value=client):
            result = await fetch_signals("owner/repo")
        assert "frontpage_score" in result
        assert "community_depth" in result
        assert result["frontpage_score"] > 0

    @pytest.mark.asyncio
    async def test_no_hits(self) -> None:
        from scoring.sources.hackernews import fetch_signals

        resp = _mock_response(json_data={"hits": []})
        client = _mock_client(resp)
        with patch("scoring.sources.hackernews.httpx.AsyncClient", return_value=client):
            result = await fetch_signals("owner/repo")
        assert result["frontpage_score"] == 0.0
        assert result["community_depth"] == 0.0

    @pytest.mark.asyncio
    async def test_network_error(self) -> None:
        from scoring.sources.hackernews import fetch_signals

        client = AsyncMock()
        client.get = AsyncMock(side_effect=httpx.ConnectError("offline"))
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)
        with patch("scoring.sources.hackernews.httpx.AsyncClient", return_value=client):
            result = await fetch_signals("owner/repo")
        assert result == {"frontpage_score": 0.0, "community_depth": 0.0}


# ---------------------------------------------------------------------------
# OSSInsight
# ---------------------------------------------------------------------------


class TestOSSInsight:
    @pytest.mark.asyncio
    async def test_happy_path(self) -> None:
        from scoring.sources.ossinsight import fetch_signals

        resp = _mock_response(json_data={"data": {"stars": 5000, "contributors": 15}})
        client = _mock_client(resp)
        with patch("scoring.sources.ossinsight.httpx.AsyncClient", return_value=client):
            result = await fetch_signals("owner/repo")
        assert "growth_curve" in result
        assert "contributor_diversity" in result

    @pytest.mark.asyncio
    async def test_invalid_repo_format(self) -> None:
        from scoring.sources.ossinsight import fetch_signals

        result = await fetch_signals("no-slash-here")
        assert result == {"growth_curve": 0.0, "contributor_diversity": 0.0}

    @pytest.mark.asyncio
    async def test_network_error(self) -> None:
        from scoring.sources.ossinsight import fetch_signals

        client = AsyncMock()
        client.get = AsyncMock(side_effect=httpx.ConnectError("offline"))
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)
        with patch("scoring.sources.ossinsight.httpx.AsyncClient", return_value=client):
            result = await fetch_signals("owner/repo")
        assert result == {"growth_curve": 0.0, "contributor_diversity": 0.0}


# ---------------------------------------------------------------------------
# Reddit
# ---------------------------------------------------------------------------


class TestReddit:
    @pytest.mark.asyncio
    async def test_happy_path(self) -> None:
        from scoring.sources.reddit import fetch_signals

        resp = _mock_response(
            json_data={
                "data": {
                    "children": [
                        {"data": {"score": 100}},
                        {"data": {"score": 200}},
                    ]
                }
            }
        )
        client = _mock_client(resp)
        with patch("scoring.sources.reddit.httpx.AsyncClient", return_value=client):
            result = await fetch_signals("owner/repo")
        assert "community_depth" in result
        assert result["community_depth"] > 0

    @pytest.mark.asyncio
    async def test_no_posts(self) -> None:
        from scoring.sources.reddit import fetch_signals

        resp = _mock_response(json_data={"data": {"children": []}})
        client = _mock_client(resp)
        with patch("scoring.sources.reddit.httpx.AsyncClient", return_value=client):
            result = await fetch_signals("owner/repo")
        assert result["community_depth"] == 0.0

    @pytest.mark.asyncio
    async def test_network_error(self) -> None:
        from scoring.sources.reddit import fetch_signals

        client = AsyncMock()
        client.get = AsyncMock(side_effect=httpx.ConnectError("offline"))
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)
        with patch("scoring.sources.reddit.httpx.AsyncClient", return_value=client):
            result = await fetch_signals("owner/repo")
        assert result == {"community_depth": 0.0}


# ---------------------------------------------------------------------------
# GitHub Trending
# ---------------------------------------------------------------------------


class TestGitHubTrending:
    @pytest.mark.asyncio
    async def test_fetch_trending_happy_path(self) -> None:
        from scoring.sources.github_trending import fetch_trending

        html = """
        <article class="Box-row">
          <h2><a href="/owner/repo">owner / repo</a></h2>
          <p>A cool repo</p>
          <span class="d-inline-block float-sm-right">100 stars today</span>
        </article>
        """
        resp = _mock_response(text=html)
        client = _mock_client(resp)
        with patch("scoring.sources.github_trending.httpx.AsyncClient", return_value=client):
            result = await fetch_trending()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_signals_not_trending(self) -> None:
        from scoring.sources.github_trending import get_signals

        resp = _mock_response(text="<html><body>No repos</body></html>")
        client = _mock_client(resp)
        with patch("scoring.sources.github_trending.httpx.AsyncClient", return_value=client):
            result = await get_signals("owner/repo")
        assert result == {"star_velocity": 0.0, "trending_position": 0.0}

    @pytest.mark.asyncio
    async def test_network_error(self) -> None:
        from scoring.sources.github_trending import fetch_trending

        client = AsyncMock()
        client.get = AsyncMock(side_effect=httpx.ConnectError("offline"))
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)
        with patch("scoring.sources.github_trending.httpx.AsyncClient", return_value=client):
            result = await fetch_trending()
        assert result == []


# ---------------------------------------------------------------------------
# TrendShift
# ---------------------------------------------------------------------------


class TestTrendShift:
    @pytest.mark.asyncio
    async def test_happy_path(self) -> None:
        from scoring.sources.trendshift import fetch_signals

        resp = _mock_response(json_data=[{"full_name": "owner/repo", "momentum_score": 0.75}])
        client = _mock_client(resp)
        with patch("scoring.sources.trendshift.httpx.AsyncClient", return_value=client):
            result = await fetch_signals("owner/repo")
        assert "momentum_score" in result
        assert result["momentum_score"] > 0

    @pytest.mark.asyncio
    async def test_repo_not_found(self) -> None:
        from scoring.sources.trendshift import fetch_signals

        resp = _mock_response(json_data=[])
        client = _mock_client(resp)
        with patch("scoring.sources.trendshift.httpx.AsyncClient", return_value=client):
            result = await fetch_signals("owner/repo")
        assert result == {"momentum_score": 0.0}

    @pytest.mark.asyncio
    async def test_network_error(self) -> None:
        from scoring.sources.trendshift import fetch_signals

        client = AsyncMock()
        client.get = AsyncMock(side_effect=httpx.ConnectError("offline"))
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)
        with patch("scoring.sources.trendshift.httpx.AsyncClient", return_value=client):
            result = await fetch_signals("owner/repo")
        assert result == {"momentum_score": 0.0}
