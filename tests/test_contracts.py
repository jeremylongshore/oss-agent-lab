"""Tests for inter-agent contract schemas."""

import pytest
from pydantic import ValidationError

from oss_agent_lab.contracts import (
    Intent,
    Query,
    SessionContext,
    SpecialistRequest,
    SpecialistResponse,
)


class TestQuery:
    def test_minimal(self):
        q = Query(user_input="test query")
        assert q.user_input == "test query"
        assert q.session_id is None
        assert q.context is None

    def test_full(self):
        q = Query(user_input="test", session_id="abc", context={"key": "val"})
        assert q.session_id == "abc"
        assert q.context == {"key": "val"}


class TestIntent:
    def test_create(self):
        i = Intent(action="research", domain="ai", confidence=0.95, parameters={"topic": "llm"})
        assert i.action == "research"
        assert i.confidence == 0.95

    def test_confidence_lower_bound(self):
        i = Intent(action="test", domain="test", confidence=0.0, parameters={})
        assert i.confidence == 0.0

    def test_confidence_upper_bound(self):
        i = Intent(action="test", domain="test", confidence=1.0, parameters={})
        assert i.confidence == 1.0

    def test_confidence_too_high(self):
        with pytest.raises(ValidationError):
            Intent(action="test", domain="test", confidence=1.5, parameters={})

    def test_confidence_negative(self):
        with pytest.raises(ValidationError):
            Intent(action="test", domain="test", confidence=-0.1, parameters={})


class TestSpecialistRequest:
    def test_create(self):
        intent = Intent(action="research", domain="ai", confidence=0.9, parameters={})
        query = Query(user_input="test")
        req = SpecialistRequest(intent=intent, query=query, specialist_name="autoresearch")
        assert req.specialist_name == "autoresearch"
        assert req.tools_requested is None


class TestSpecialistResponse:
    def test_success(self):
        resp = SpecialistResponse(
            specialist_name="autoresearch",
            status="success",
            result={"findings": ["a", "b"]},
        )
        assert resp.status == "success"
        assert resp.metadata is None

    def test_error(self):
        resp = SpecialistResponse(
            specialist_name="autoresearch",
            status="error",
            result=None,
            metadata={"error": "timeout"},
            duration_ms=5000.0,
        )
        assert resp.status == "error"
        assert resp.duration_ms == 5000.0


class TestSessionContext:
    def test_create(self):
        ctx = SessionContext(session_id="s1", history=[{"role": "user", "content": "hi"}])
        assert ctx.session_id == "s1"
        assert len(ctx.history) == 1
        assert ctx.memory is None
