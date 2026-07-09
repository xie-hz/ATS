"""Service layer: business logic, state machines, and data-scope filtering.

Data scope is injected here (not in routes) so every list/get is automatically
restricted by the caller's role, avoiding per-route permission conditions.
"""
