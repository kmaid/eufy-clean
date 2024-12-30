"""Exceptions for Eufy Clean."""

class EufyCleanError(Exception):
    """Base exception for Eufy Clean."""


class CannotConnect(EufyCleanError):
    """Error to indicate we cannot connect."""


class InvalidAuth(EufyCleanError):
    """Error to indicate there is invalid auth."""
