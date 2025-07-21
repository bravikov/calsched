"""
calsched package

This package provides a scheduler for recurring events. Users can create and cancel events
that execute a specified function at regular intervals. Each event triggers a function
with positional (args) and keyword (kwargs) arguments at the defined interval.
Designed for integration into larger applications requiring basic recurring event management.
"""

from .core import CalendarScheduler
