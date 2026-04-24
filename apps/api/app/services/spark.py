from dataclasses import dataclass
from shutil import which

from app.core.config import settings

try:
    from delta import configure_spark_with_delta_pip
    from pyspark.sql import SparkSession
except ImportError:  # pragma: no cover
    SparkSession = None
    configure_spark_with_delta_pip = None


@dataclass
class SparkRuntimeStatus:
    available: bool
    app_name: str
    master: str
    warehouse_dir: str
    detail: str


def spark_runtime_status() -> SparkRuntimeStatus:
    java_available = which("java") is not None
    available = (
        SparkSession is not None
        and configure_spark_with_delta_pip is not None
        and java_available
    )
    if SparkSession is None or configure_spark_with_delta_pip is None:
        detail = "pyspark/delta-spark dependencies are not installed"
    elif not java_available:
        detail = "java runtime is not available on PATH"
    else:
        detail = "ready"
    return SparkRuntimeStatus(
        available=available,
        app_name=settings.spark_app_name,
        master=settings.spark_master_url,
        warehouse_dir=settings.spark_warehouse_dir,
        detail=detail,
    )


def build_spark_session():
    if SparkSession is None or configure_spark_with_delta_pip is None:
        raise RuntimeError("Spark runtime dependencies are not installed")
    if which("java") is None:
        raise RuntimeError("Java runtime is not available on PATH")

    builder = (
        SparkSession.builder.appName(settings.spark_app_name)
        .master(settings.spark_master_url)
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.sql.warehouse.dir", settings.spark_warehouse_dir)
        .config("spark.hadoop.fs.s3a.endpoint", settings.s3_endpoint_url)
        .config("spark.hadoop.fs.s3a.access.key", settings.aws_access_key_id)
        .config("spark.hadoop.fs.s3a.secret.key", settings.aws_secret_access_key)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", str(settings.minio_secure).lower())
        .config("spark.eventLog.enabled", "true")
        .config("spark.eventLog.dir", settings.spark_event_log_dir)
    )
    return configure_spark_with_delta_pip(builder).getOrCreate()


def spark_dependencies_available() -> bool:
    return (
        SparkSession is not None
        and configure_spark_with_delta_pip is not None
        and which("java") is not None
    )
