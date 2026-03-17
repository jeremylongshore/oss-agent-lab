"""Tests for SessionMemory — in-memory + file persistence."""

from __future__ import annotations

from pathlib import Path

import pytest

from agents.memory.session import SessionMemory
from oss_agent_lab.contracts import SessionContext


class TestSessionMemory:
    def test_init_generates_session_id(self) -> None:
        mem = SessionMemory()
        assert mem.session_id is not None
        assert len(mem.session_id) > 0

    def test_init_custom_session_id(self) -> None:
        mem = SessionMemory(session_id="my-session")
        assert mem.session_id == "my-session"

    @pytest.mark.asyncio
    async def test_store_and_recall(self) -> None:
        mem = SessionMemory()
        await mem.store({"role": "user", "content": "Research transformers"})
        await mem.store({"role": "assistant", "content": "Found 5 papers on transformers"})

        results = await mem.recall("transformers")
        assert len(results) >= 1
        # Both entries mention transformers
        assert any("transformers" in str(r).lower() for r in results)

    @pytest.mark.asyncio
    async def test_recall_empty_query(self) -> None:
        mem = SessionMemory()
        await mem.store({"content": "test"})
        results = await mem.recall("")
        assert results == []

    @pytest.mark.asyncio
    async def test_recall_no_matches(self) -> None:
        mem = SessionMemory()
        await mem.store({"content": "about cats and dogs"})
        results = await mem.recall("quantum physics")
        assert results == []

    @pytest.mark.asyncio
    async def test_recall_top_k(self) -> None:
        mem = SessionMemory()
        for i in range(10):
            await mem.store({"content": f"entry {i} about AI"})

        results = await mem.recall("AI", top_k=3)
        assert len(results) == 3

    def test_get_context(self) -> None:
        mem = SessionMemory(session_id="ctx-test")
        ctx = mem.get_context()
        assert isinstance(ctx, SessionContext)
        assert ctx.session_id == "ctx-test"
        assert ctx.history == []

    @pytest.mark.asyncio
    async def test_get_context_with_history(self) -> None:
        mem = SessionMemory(session_id="ctx-test-2")
        await mem.store({"role": "user", "content": "hello"})
        ctx = mem.get_context()
        assert len(ctx.history) == 1
        assert ctx.history[0]["role"] == "user"

    @pytest.mark.asyncio
    async def test_persist_and_load(self, tmp_path: Path) -> None:
        # Store and persist
        mem1 = SessionMemory(session_id="persist-test", persist_dir=str(tmp_path))
        await mem1.store({"role": "user", "content": "remember this"})
        await mem1.persist()

        # Verify file was written
        session_file = tmp_path / "persist-test.json"
        assert session_file.exists()

        # Load in a new instance
        mem2 = SessionMemory(session_id="persist-test", persist_dir=str(tmp_path))
        ctx = mem2.get_context()
        assert len(ctx.history) == 1
        assert ctx.history[0]["content"] == "remember this"

    @pytest.mark.asyncio
    async def test_auto_persist_on_store(self, tmp_path: Path) -> None:
        mem = SessionMemory(session_id="auto-persist", persist_dir=str(tmp_path))
        await mem.store({"content": "auto saved"})
        # Should have auto-persisted
        session_file = tmp_path / "auto-persist.json"
        assert session_file.exists()

    @pytest.mark.asyncio
    async def test_load_corrupted_file(self, tmp_path: Path) -> None:
        # Write corrupted JSON
        session_file = tmp_path / "corrupt.json"
        session_file.write_text("not json {{{")

        mem = SessionMemory(session_id="corrupt", persist_dir=str(tmp_path))
        ctx = mem.get_context()
        assert ctx.history == []

    @pytest.mark.asyncio
    async def test_load_nonexistent_session(self, tmp_path: Path) -> None:
        mem = SessionMemory(session_id="nonexistent", persist_dir=str(tmp_path))
        ctx = mem.get_context()
        assert ctx.history == []

    @pytest.mark.asyncio
    async def test_recall_relevance_ordering(self) -> None:
        mem = SessionMemory()
        await mem.store({"content": "cats and dogs"})
        await mem.store({"content": "AI research on transformers"})
        await mem.store({"content": "AI models and AI safety in AI research"})

        results = await mem.recall("AI models safety")
        assert len(results) >= 2
        # "AI models and AI safety in AI research" matches 3 terms; "AI research on
        # transformers" matches only 1 ("ai").  Higher match count ranks first.
        assert "models" in str(results[0]).lower()
        assert "safety" in str(results[0]).lower()
