#!/usr/bin/env python3
"""Bulk retry failed documents by queuing ingest tasks."""

from sqlalchemy import text, create_engine

def get_failed_documents() -> list[tuple[str, str, str, str]]:
    """Fetch failed documents with their S3 keys."""
    db_url = "postgresql://gideon:FynbWI4dix30YGjioiY8kwg4962U3pwOMMpdUpipW6c=@localhost:5432/gideon"
    engine = create_engine(db_url)

    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id::text, filename, firm_id::text, matter_id::text
            FROM documents
            WHERE ingestion_status = 'failed'
            ORDER BY created_at DESC
        """))
        return [(row[0], row[1], row[2], row[3]) for row in result.fetchall()]

def queue_ingestion_tasks(docs: list[tuple[str, str, str, str]]) -> None:
    """Queue Celery ingest_document task for each failed document."""
    from app.workers.tasks.ingest_document import ingest_document
    from app.storage.s3 import S3StorageService

    for i, (doc_id, filename, firm_id, matter_id) in enumerate(docs, 1):
        try:
            extension = filename.split(".")[-1].lower() if "." in filename else "bin"
            s3_key = S3StorageService.object_key(firm_id, matter_id, doc_id, extension)

            task = ingest_document.delay(doc_id, s3_key)
            print(f"[{i}/{len(docs)}] ✓ Queued {doc_id} → {s3_key}")
        except Exception as e:
            print(f"[{i}/{len(docs)}] ✗ Error {doc_id}: {e}")

def main():
    print("Fetching failed documents...")
    docs = get_failed_documents()

    if not docs:
        print("No failed documents found.")
        return

    print(f"Found {len(docs)} failed documents.")
    queue_ingestion_tasks(docs)
    print("Done.")

if __name__ == "__main__":
    main()
