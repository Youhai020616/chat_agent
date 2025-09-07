# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Repository overview
- This repository currently contains a project concept/design document: pre.md, which outlines a LangGraph-based multi-agent system for SEO and GEO optimization.
- There are no build, lint, or test configurations present yet (no package.json, pyproject.toml, Makefile, Dockerfile, CI configs, or test frameworks are detected).

Commands
- Build: Not defined. No build tooling or configuration found in the repository.
- Lint/Format: Not defined. No linter/formatter configuration files found.
- Tests: Not defined. No test framework or configuration files found.
- Single test execution: Not applicable until a test framework is added.

Action for future updates: Once implementation and tooling are added (e.g., package.json or pyproject.toml, Makefile, CI), update this section with concrete commands for installing dependencies, running the app, linting, and executing tests (including single-test invocations).

High-level architecture and intent (from pre.md)
- Goal: Build an SEO and GEO optimization tool using LangGraph where multiple specialized AI agents collaborate to produce a comprehensive optimization plan for a website.
- Core agents and responsibilities:
  - 关键词分析Agent (Keyword Analysis): keyword research, competition analysis, search volume/difficulty assessment, long-tail discovery.
  - 内容优化Agent (Content Optimization): on-page SEO analysis, title/description suggestions, content structure improvements.
  - 技术SEO Agent (Technical SEO): site technical checks, page speed optimization suggestions, mobile-friendliness checks.
  - 地理定位优化Agent (GEO/Local): local search optimization, Google My Business improvements, geo-keyword strategy.
  - 链接建设Agent (Link Building): external link opportunities, internal link structure improvements, link quality evaluation.
- Orchestration flow (as envisioned):
  1) Analyze target site to establish an initial analysis context
  2) Run agents in parallel on the shared analysis context (keyword/content/technical/geo)
  3) Integrate results and prioritize into an actionable optimization plan
- LangGraph is intended for state management and flow control to coordinate agent collaboration and information sharing.

Illustrative workflow (from pre.md)
- The design document includes a function stub seo_optimization_workflow() showing the intended sequence: initial analyze_website() → parallel agent analyses → integrate_results([...]) to produce the final optimization_plan.

What to expect once implementation begins
- Orchestrator: Entry point that constructs LangGraph nodes/edges, manages the shared state, and coordinates agent execution and result integration.
- Agents: Individually testable components encapsulating domain-specific analysis. Each should accept the shared site analysis context and return structured results suitable for integration.
- Integrator/Prioritizer: Merges agent outputs and orders recommendations by impact/effort.

Key document
- pre.md — the source of truth for the system’s intended capabilities, agents, and workflow. Keep WARP.md aligned with updates to this document.

