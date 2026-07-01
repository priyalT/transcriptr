
from typing import Optional, Dict, Any

class TranscriptrError(Exception):
    """
    Base exception for all application errors
    """
    default_message = "Transcriptr failed."
    def __init__(self, 
                 message: str | None = None,
                 context: Optional[Dict[str, Any]] = None,
                 ):
        if message is None:
            message = self.default_message
        super().__init__(message)
        self.message = message
        self.context = context or {}
        

class ConfigValidationError(TranscriptrError):
    """
    Raised when config validation fails
    """
    default_message = "Config validation failed."

class InputValidationError(TranscriptrError):
    """
    Raised when input validation fails
    """
    default_message = "Input validation failed."

class TranscriptrIOError(TranscriptrError):
    """
    Raised when file I/O for Transcriptr fails
    """
    default_message = "File I/O failed."

class FASTQParseError(TranscriptrIOError):
    """
    Raised when FASTQ parsing fails
    """
    default_message = "FASTQ parsing failed."

class ReportWriteError(TranscriptrIOError):
    """
    Raised when report writing fails
    """
    default_message = "Report writing failed."

class MetricParseError(TranscriptrError):
    """
    Raised when metric parsing fails
    """
    default_message = "Metric parsing failed."

class NextflowError(TranscriptrError):
    """
    Raised when Nextflow fails
    """
    default_message = "Nextflow failed."

class PlottingError(TranscriptrError):
    """
    Raised when plotting fails
    """
    default_message = "Plotting failed."