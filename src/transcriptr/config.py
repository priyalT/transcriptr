from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel


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
