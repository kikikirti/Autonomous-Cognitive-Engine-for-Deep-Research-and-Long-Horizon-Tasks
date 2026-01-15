# ADR-0001: Initial Architecture

## Context
We need a modular, testable agent system for long-horizon tasks.

## Decision
Use an orchestrator `Agent` that composes Memory, Planner, Queue, Reasoner, ToolExecutor, Reflector.

## Consequences
- Each component can be unit-tested independently.
- Future changes (e.g., swap RAG backend) won't break the whole system.