from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LakeForge Control Plane"
    app_env: str = "development"
    debug: bool = True

    database_url: str = "postgresql+psycopg://lakeforge:lakeforge@localhost:5432/lakeforge"

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "lakeforge"
    minio_secure: bool = False

    spark_app_name: str = "LakeForge Spark"
    spark_master_url: str = "spark://localhost:7077"
    spark_warehouse_dir: str = "s3a://lakeforge/managed/"
    spark_event_log_dir: str = "file:/tmp/spark-events"
    aws_access_key_id: str = "minioadmin"
    aws_secret_access_key: str = "minioadmin"
    s3_endpoint_url: str = "http://localhost:9000"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="LAKEFORGE_")


settings = Settings()
