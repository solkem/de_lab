def managed_table_location(bucket: str, catalog: str, schema: str, table: str) -> str:
    return f"s3a://{bucket}/managed/catalog={catalog}/schema={schema}/table={table}/"

