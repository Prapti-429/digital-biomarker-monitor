"""Application service package.

Service modules are intentionally not imported here. Importing concrete
services from package initialization creates import-time side effects and can
introduce circular imports between FastAPI dependencies and authentication.
Import the required service directly from its module instead.
"""

__all__: list[str] = []
