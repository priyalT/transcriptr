from enum import StrEnum
from pathlib import Path
import yaml
from pydantic import BaseModel, ValidationError
import rich_click as click


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
    @staticmethod
    def load(path: Path) -> TranscriptrConfig:
        try:
            with path.open("r") as file:
                data = yaml.safe_load(file)
            
            config = TranscriptrConfig.model_validate(data)
            config_dir = path.parent

            if not config.genome.reference.is_absolute():
                config.genome.reference = (
                    config_dir / config.genome.reference
                ).resolve()
            
            for sample in config.samples:
                sample.reads = [
                    (config_dir / read).resolve()
                    if not read.is_absolute()
                    else read
                    for read in sample.reads
                ]

            if not config.output.directory.is_absolute():
                config.output.directory = (
                    config_dir / config.output.directory
                ).resolve()

            return config

        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Configuration file not found: {path}"
            ) from e

        except yaml.YAMLError as e:
            raise ValueError(
                f"Invalid YAML syntax in '{path}': {e}"
            ) from e

        except ValidationError as e:
            raise ValueError(
                f"Configuration validation failed:\n{e}"
            ) from e
    
    @staticmethod
    def to_nextflow_params(config: TranscriptrConfig) -> dict:
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
