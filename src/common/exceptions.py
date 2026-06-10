"""Custom pipeline exceptions."""


class PipelineError(Exception):
    """Base exception for pipeline errors."""


class ValidationError(PipelineError):
    """Raised when data validation fails."""


class LoadError(PipelineError):
    """Raised when warehouse load fails."""
