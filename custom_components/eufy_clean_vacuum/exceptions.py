"""Exceptions for Eufy Clean integration."""

class EufyCleanError(Exception):
    """Base exception for Eufy Clean."""

class InvalidAuth(EufyCleanError):
    """Error to indicate invalid authentication."""

class CannotConnect(EufyCleanError):
    """Error to indicate we cannot connect."""

ERROR_MESSAGES = {
    5002: "Invalid email or password",
    5004: "Account has been frozen",
    5005: "Account not found",
    5006: "Account has been deleted",
    5008: "Account format error",
    # Add more error codes as we discover them
}
