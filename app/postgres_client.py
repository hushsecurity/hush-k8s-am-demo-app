import hashlib
import logging
import os
import time

import psycopg2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "goatdb")
POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
STATIC_SECRET = os.getenv("STATIC_SECRET")
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "15"))


def log_static_secret_status() -> None:
    if not STATIC_SECRET:
        logging.warning("STATIC_SECRET was not injected")
        return

    secret_hash = hashlib.sha256(STATIC_SECRET.encode("utf-8")).hexdigest()[:8]
    logging.info("Static secret injected (hash prefix: %s)", secret_hash)


def validate_required_env() -> None:
    if POSTGRES_USERNAME and POSTGRES_PASSWORD:
        return

    logging.error(
        "Missing injected postgres credentials (POSTGRES_USERNAME / POSTGRES_PASSWORD). "
        "Hush AccessPolicy may not have been reconciled before this pod was admitted. "
        "Delete this pod so it is re-created after the policy is active."
    )
    raise SystemExit(1)


def validate_database_access() -> None:
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USERNAME,
        password=POSTGRES_PASSWORD,
    )

    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]

        cursor.execute("SELECT name, email FROM users ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()

    conn.close()
    logging.info("Validated DB access. users=%s latest=%s", count, row)


def main() -> None:
    validate_required_env()
    log_static_secret_status()

    while True:
        try:
            validate_database_access()
        except Exception as exc:
            logging.error("DB validation failed: %s", exc)

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
