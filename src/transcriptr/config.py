from enum import StrEnum
from pathlib import Path
from transcriptr.exceptions import (
    ConfigValidationError,
    TranscriptrIOError,
)
import yaml
from pydantic import BaseModel, ValidationError


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Aligner(StrEnum):
    STARSOLO = "starsolo"
    ALEVIN = "alevin"
    KALLISTO = "kallisto"


class SampleConfig(BaseModel):
    name: str
    reads: list[Path]
    chemistry: str = "auto"


class GenomeConfig(BaseModel):
    species: str
    reference: Path
    annotation: Path


class QCConfig(BaseModel):
    run_fastqc: bool
    min_genes: int
    min_cells: int
    max_mt: float


class AlignmentConfig(BaseModel):
    tool: Aligner
    threads: int
    extra_args: list[str]


class ScanpyConfig(BaseModel):
    normalize: bool
    log1p: bool
    n_top_genes: int
    n_neighbors: int
    n_pcs: int
    resolution: float


class ReportConfig(BaseModel):
    html: bool
    plots: bool
    pdf: bool


class ResourceConfig(BaseModel):
    cpus: int
    memory: str


class LogConfig(BaseModel):
    level: LogLevel
    save_command: bool
    verbose: bool


class OutputConfig(BaseModel):
    directory: Path
    overwrite: bool
    compress: bool


class TranscriptrConfig(BaseModel):
    samples: list[SampleConfig]
    genome: GenomeConfig
    qc: QCConfig
    alignment: AlignmentConfig
    scanpy: ScanpyConfig
    report: ReportConfig
    resources: ResourceConfig
    logging: LogConfig
    output: OutputConfig


class ConfigManager:
    """Utility class for creating, validating and converting configuration files."""

    @staticmethod
    def init(path: Path) -> None:
        """Create a template configuration file."""
        if path.exists():
            raise FileExistsError(
                f"{path} already exists. Use another filename or remove it first."
                )
        else:
            template = {
                "samples": [
                    {
                        "name": "sample1",
                        "reads": [
                            "reads/sample_R1.fastq.gz",
                            "reads/sample_R2.fastq.gz",
                        ],
                        "chemistry": "auto",
                    }
                ],
                "genome": {
                    "species": "human",
                    "reference": "reference/genome.fa",
                    "annotation": "reference/genes.gtf",
                },
                "qc": {
                    "run_fastqc": True,
                    "min_genes": 200,
                    "min_cells": 3,
                    "max_mt": 5.0,
                },
                "alignment": {
                    "tool": "starsolo",
                    "threads": 8,
                    "extra_args": [],
                },
                "scanpy": {
                    "normalize": True,
                    "log1p": True,
                    "n_top_genes": 2000,
                    "n_neighbors": 15,
                    "n_pcs": 50,
                    "resolution": 1.0,
                },
                "report": {
                    "html": True,
                    "plots": True,
                    "pdf": False,
                },
                "resources": {
                    "cpus": 8,
                    "memory": "32 GB",
                },
                "logging": {
                    "level": "INFO",
                    "save_command": True,
                    "verbose": False,
                },
                "output": {
                    "directory": "results",
                    "overwrite": False,
                    "compress": False,
                },
            }

            with path.open("w", encoding="utf-8") as file:
                yaml.safe_dump(template, file, sort_keys=False)

    @staticmethod
    def check(path: Path) -> TranscriptrConfig:
        """Validate a configuration file."""

        return ConfigManager.load(path)

    @staticmethod
    def _resolve(path: Path, config_dir: Path) -> Path:
        """Resolve relative paths against the configuration directory."""

        if path.is_absolute():
            return path

        return (config_dir / path).resolve()

    @staticmethod
    def load(path: Path) -> TranscriptrConfig:
        """Load and validate a configuration file."""

        try:
            with path.open("r", encoding="utf-8") as file:
                data = yaml.safe_load(file)

            config = TranscriptrConfig.model_validate(data)

            config_dir = path.parent

            config.genome.reference = ConfigManager._resolve(
                config.genome.reference,
                config_dir,
            )

            config.genome.annotation = ConfigManager._resolve(
                config.genome.annotation,
                config_dir,
            )

            config.output.directory = ConfigManager._resolve(
                config.output.directory,
                config_dir,
            )

            for sample in config.samples:
                sample.reads = [
                    ConfigManager._resolve(read, config_dir) for read in sample.reads
                ]

            return config

        except FileNotFoundError as e:
            raise TranscriptrIOError(f"Configuration file not found: {path}") from e

        except yaml.YAMLError as e:
            raise ConfigValidationError(f"Invalid YAML syntax in '{path}': {e}") from e

        except ValidationError as e:
            raise ConfigValidationError(f"Configuration validation failed:\n{e}") from e

    @staticmethod
    def to_nextflow_params(config: TranscriptrConfig) -> dict:
        """Convert a validated configuration into Nextflow parameters."""

        return {
            "samples": [
                {
                    "name": sample.name,
                    "reads": [str(read) for read in sample.reads],
                    "chemistry": sample.chemistry,
                }
                for sample in config.samples
            ],
            "species": config.genome.species,
            "reference": str(config.genome.reference),
            "annotation": str(config.genome.annotation),
            "aligner": config.alignment.tool.value,
            "threads": config.alignment.threads,
            "extra_args": config.alignment.extra_args,
            "run_fastqc": config.qc.run_fastqc,
            "min_genes": config.qc.min_genes,
            "min_cells": config.qc.min_cells,
            "max_mt": config.qc.max_mt,
            "normalize": config.scanpy.normalize,
            "log1p": config.scanpy.log1p,
            "n_top_genes": config.scanpy.n_top_genes,
            "n_neighbors": config.scanpy.n_neighbors,
            "n_pcs": config.scanpy.n_pcs,
            "resolution": config.scanpy.resolution,
            "html_report": config.report.html,
            "plots": config.report.plots,
            "pdf_report": config.report.pdf,
            "cpus": config.resources.cpus,
            "memory": config.resources.memory,
            "log_level": config.logging.level.value,
            "save_command": config.logging.save_command,
            "verbose": config.logging.verbose,
            "output_dir": str(config.output.directory),
            "overwrite": config.output.overwrite,
            "compress": config.output.compress,
        }
