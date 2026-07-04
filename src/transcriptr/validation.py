from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ValidationResult:
    """Class to collect errors and warnings during validation."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0


class InputValidator:
    """Validate input files"""


# @classmethod
def validate(cls, config: Path) -> ValidationResult:
    result = ValidationResult()
    cls._validate_fastqs(config, result)
    cls._validate_fastq_format(config, result)
    cls._validate_paired_reads(config, result)
    cls._validate_hisat2_index(config, result)
    cls._validate_gtf(config, result)
    cls._validate_sample_name(config, result)
    cls._validate_tools(config, result)

    return result
