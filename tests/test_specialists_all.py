"""Comprehensive integration tests for all 9 specialists."""

from __future__ import annotations

from typing import ClassVar

import pytest

from oss_agent_lab.contracts import Intent, Query, SpecialistRequest, SpecialistResponse


def _make_request(
    specialist_name: str,
    user_input: str,
    action: str = "research",
    domain: str = "ai",
    **params: object,
) -> SpecialistRequest:
    return SpecialistRequest(
        intent=Intent(
            action=action,
            domain=domain,
            confidence=0.9,
            parameters=dict(params),
        ),
        query=Query(user_input=user_input),
        specialist_name=specialist_name,
    )


# ---------------------------------------------------------------------------
# Browser AI
# ---------------------------------------------------------------------------


class TestBrowserAi:
    @pytest.mark.asyncio
    async def test_execute(self) -> None:
        from agents.specialists.browser_ai.agent import BrowserAiSpecialist

        s = BrowserAiSpecialist()
        req = _make_request(
            "browser_ai", "Scrape example.com",
            action="browse", domain="web", url="https://example.com",
        )
        resp = await s.execute(req)
        assert resp.status == "success"
        assert resp.specialist_name == "browser_ai"

    def test_attributes(self) -> None:
        from agents.specialists.browser_ai.agent import BrowserAiSpecialist

        s = BrowserAiSpecialist()
        assert s.name == "browser_ai"
        assert s.source_repo == "lightpanda-io/browser"
        assert len(s.tools) >= 3

    def test_tools(self) -> None:
        from agents.specialists.browser_ai.tools import (
            extract_content,
            navigate,
            take_screenshot,
        )

        assert isinstance(navigate("https://example.com"), dict)
        assert isinstance(extract_content("https://example.com"), dict)
        assert isinstance(take_screenshot("https://example.com"), dict)


# ---------------------------------------------------------------------------
# Knowledge Graph
# ---------------------------------------------------------------------------


class TestKnowledgeGraph:
    @pytest.mark.asyncio
    async def test_execute(self) -> None:
        from agents.specialists.knowledge_graph.agent import KnowledgeGraphSpecialist

        s = KnowledgeGraphSpecialist()
        req = _make_request(
            "knowledge_graph", "Build graph of repo dependencies",
            action="knowledge_graph", domain="code",
        )
        resp = await s.execute(req)
        assert resp.status == "success"
        assert resp.specialist_name == "knowledge_graph"

    def test_attributes(self) -> None:
        from agents.specialists.knowledge_graph.agent import KnowledgeGraphSpecialist

        s = KnowledgeGraphSpecialist()
        assert s.name == "knowledge_graph"
        assert len(s.tools) >= 3

    def test_tools(self) -> None:
        from agents.specialists.knowledge_graph.tools import (
            build_graph,
            find_relationships,
            query_graph,
        )

        graph = build_graph("test_source")
        assert isinstance(graph, dict)
        assert isinstance(query_graph("test query"), dict)
        assert isinstance(find_relationships("entity_a", "entity_b"), dict)


# ---------------------------------------------------------------------------
# Stock Analyst
# ---------------------------------------------------------------------------


class TestStockAnalyst:
    @pytest.mark.asyncio
    async def test_execute(self) -> None:
        from agents.specialists.stock_analyst.agent import StockAnalystSpecialist

        s = StockAnalystSpecialist()
        req = _make_request(
            "stock_analyst", "Analyze AAPL",
            action="analyze", domain="finance", ticker="AAPL",
        )
        resp = await s.execute(req)
        assert resp.status == "success"
        assert resp.specialist_name == "stock_analyst"

    def test_attributes(self) -> None:
        from agents.specialists.stock_analyst.agent import StockAnalystSpecialist

        s = StockAnalystSpecialist()
        assert s.name == "stock_analyst"
        assert "finance" in s.capabilities or "analyze" in s.capabilities
        assert len(s.tools) >= 3

    def test_tools(self) -> None:
        from agents.specialists.stock_analyst.tools import (
            analyze_ticker,
            news_sentiment,
            technical_indicators,
        )

        assert isinstance(analyze_ticker("AAPL"), dict)
        assert isinstance(technical_indicators("AAPL"), dict)
        assert isinstance(news_sentiment("AAPL"), dict)


# ---------------------------------------------------------------------------
# Opinion Analyst
# ---------------------------------------------------------------------------


class TestOpinionAnalyst:
    @pytest.mark.asyncio
    async def test_execute(self) -> None:
        from agents.specialists.opinion_analyst.agent import OpinionAnalystSpecialist

        s = OpinionAnalystSpecialist()
        req = _make_request(
            "opinion_analyst", "Analyze sentiment of this review",
            action="sentiment", domain="general",
        )
        resp = await s.execute(req)
        assert resp.status == "success"
        assert resp.specialist_name == "opinion_analyst"

    def test_attributes(self) -> None:
        from agents.specialists.opinion_analyst.agent import OpinionAnalystSpecialist

        s = OpinionAnalystSpecialist()
        assert s.name == "opinion_analyst"
        assert "sentiment" in s.capabilities
        assert len(s.tools) >= 3

    def test_tools(self) -> None:
        from agents.specialists.opinion_analyst.tools import (
            analyze_sentiment,
            detect_stance,
            measure_bias,
        )

        sent = analyze_sentiment("This product is great!")
        assert isinstance(sent, dict)
        assert "sentiment" in sent

        stance = detect_stance("I support this policy", "policy")
        assert isinstance(stance, dict)

        bias = measure_bias("This is clearly the best option ever!!!")
        assert isinstance(bias, dict)


# ---------------------------------------------------------------------------
# GUI Agent
# ---------------------------------------------------------------------------


class TestGuiAgent:
    @pytest.mark.asyncio
    async def test_execute(self) -> None:
        from agents.specialists.gui_agent.agent import GuiAgentSpecialist

        s = GuiAgentSpecialist()
        req = _make_request(
            "gui_agent", "Click the login button",
            action="gui_automation", domain="web",
        )
        resp = await s.execute(req)
        assert resp.status == "success"
        assert resp.specialist_name == "gui_agent"

    def test_attributes(self) -> None:
        from agents.specialists.gui_agent.agent import GuiAgentSpecialist

        s = GuiAgentSpecialist()
        assert s.name == "gui_agent"
        assert len(s.tools) >= 3

    def test_tools(self) -> None:
        from agents.specialists.gui_agent.tools import (
            detect_elements,
            fill_form,
            interact_element,
        )

        elements = detect_elements("https://example.com")
        assert isinstance(elements, dict)

        interaction = interact_element("elem_1")
        assert isinstance(interaction, dict)

        form = fill_form("https://example.com", {"username": "test"})
        assert isinstance(form, dict)


# ---------------------------------------------------------------------------
# Sandbox
# ---------------------------------------------------------------------------


class TestSandbox:
    @pytest.mark.asyncio
    async def test_execute(self) -> None:
        from agents.specialists.sandbox.agent import SandboxSpecialist

        s = SandboxSpecialist()
        req = _make_request(
            "sandbox", "Run print('hello')",
            action="execute", domain="code",
        )
        resp = await s.execute(req)
        assert resp.status == "success"
        assert resp.specialist_name == "sandbox"

    def test_attributes(self) -> None:
        from agents.specialists.sandbox.agent import SandboxSpecialist

        s = SandboxSpecialist()
        assert s.name == "sandbox"
        assert "execute" in s.capabilities or "code_execution" in s.capabilities
        assert len(s.tools) >= 3

    def test_tools(self) -> None:
        from agents.specialists.sandbox.tools import (
            execute_code,
            list_runtimes,
            validate_code,
        )

        result = execute_code("print('hello')")
        assert isinstance(result, dict)

        validation = validate_code("print('hello')")
        assert isinstance(validation, dict)

        runtimes = list_runtimes()
        assert isinstance(runtimes, dict)


# ---------------------------------------------------------------------------
# All-specialist consistency checks
# ---------------------------------------------------------------------------


class TestAllSpecialistConsistency:
    """Verify all 10 specialists follow the same contract."""

    SPECIALIST_CLASSES: ClassVar[list[tuple[str, str]]] = [
        ("agents.specialists.autoresearch.agent", "AutoresearchSpecialist"),
        ("agents.specialists.swarm_predict.agent", "SwarmPredictSpecialist"),
        ("agents.specialists.deer_flow.agent", "DeerFlowSpecialist"),
        ("agents.specialists.browser_ai.agent", "BrowserAiSpecialist"),
        ("agents.specialists.knowledge_graph.agent", "KnowledgeGraphSpecialist"),
        ("agents.specialists.stock_analyst.agent", "StockAnalystSpecialist"),
        ("agents.specialists.opinion_analyst.agent", "OpinionAnalystSpecialist"),
        ("agents.specialists.gui_agent.agent", "GuiAgentSpecialist"),
        ("agents.specialists.sandbox.agent", "SandboxSpecialist"),
        ("agents.specialists.repo_scanner.agent", "RepoScannerSpecialist"),
    ]

    def _import_specialist(self, module_path: str, class_name: str) -> object:
        import importlib
        mod = importlib.import_module(module_path)
        return getattr(mod, class_name)()

    def test_all_have_required_attributes(self) -> None:
        for mod_path, cls_name in self.SPECIALIST_CLASSES:
            s = self._import_specialist(mod_path, cls_name)
            assert hasattr(s, "name"), f"{cls_name} missing name"
            assert hasattr(s, "description"), f"{cls_name} missing description"
            assert hasattr(s, "source_repo"), f"{cls_name} missing source_repo"
            assert hasattr(s, "capabilities"), f"{cls_name} missing capabilities"
            assert hasattr(s, "output_formats"), f"{cls_name} missing output_formats"
            assert hasattr(s, "tools"), f"{cls_name} missing tools"
            assert len(s.name) > 0, f"{cls_name} has empty name"
            assert len(s.capabilities) >= 1, f"{cls_name} has no capabilities"
            assert len(s.tools) >= 1, f"{cls_name} has no tools"

    def test_all_have_skill_metadata(self) -> None:
        for mod_path, cls_name in self.SPECIALIST_CLASSES:
            s = self._import_specialist(mod_path, cls_name)
            meta = s.get_skill_metadata()
            assert "name" in meta, f"{cls_name} metadata missing name"
            assert "source_repo" in meta, f"{cls_name} metadata missing source_repo"
            assert "capabilities" in meta, f"{cls_name} metadata missing capabilities"
            assert "tools" in meta, f"{cls_name} metadata missing tools"

    @pytest.mark.asyncio
    async def test_all_execute_successfully(self) -> None:
        test_cases = [
            ("autoresearch", "Research AI safety"),
            ("swarm_predict", "Predict market trends"),
            ("deer_flow", "Generate a report"),
            ("browser_ai", "https://example.com"),
            ("knowledge_graph", "Build a code graph"),
            ("stock_analyst", "Analyze TSLA"),
            ("opinion_analyst", "Check sentiment"),
            ("gui_agent", "Click login button"),
            ("sandbox", "Run hello world"),
            ("repo_scanner", "test/trending-repo"),
        ]
        for (mod_path, cls_name), (name, query) in zip(
            self.SPECIALIST_CLASSES, test_cases, strict=True,
        ):
            s = self._import_specialist(mod_path, cls_name)
            req = _make_request(name, query)
            resp = await s.execute(req)
            assert isinstance(resp, SpecialistResponse), (
                f"{cls_name} didn't return SpecialistResponse"
            )
            assert resp.status == "success", f"{cls_name} status={resp.status}"
            assert resp.specialist_name == name, (
                f"{cls_name} wrong specialist_name: {resp.specialist_name}"
            )
