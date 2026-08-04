"""
Database Management Command Line Interface.

Provides CLI commands for checking database readiness, initializing base metadata,
and performing administrative tasks.
"""

import argparse
import sys
import logging

from app.db.health import check_db_health
from app.db.init_db import init_db, wait_for_db

logger = logging.getLogger("db_cli")


def main() -> None:
    """
    Main entrypoint for administrative database CLI commands.
    """
    parser = argparse.ArgumentParser(description="Digital Biomarker Monitor DB Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: ping
    subparsers.add_parser("ping", help="Ping the database and return health status")

    # Command: wait
    wait_parser = subparsers.add_parser("wait", help="Block until database connection is ready")
    wait_parser.add_argument("--retries", type=int, default=30, help="Maximum retry attempts")
    wait_parser.add_argument("--delay", type=float, default=1.0, help="Delay between attempts in seconds")

    # Command: init
    subparsers.add_parser("init", help="Initialize database schema tables from metadata")

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if args.command == "ping":
        status = check_db_health()
        print(f"Status: {status.get('status')}")
        print(f"Latency: {status.get('latency_ms')} ms")
        print(f"Message: {status.get('message')}")
        if status.get("status") != "healthy":
            sys.exit(1)

    elif args.command == "wait":
        ready = wait_for_db(max_retries=args.retries, delay_seconds=args.delay)
        if not ready:
            sys.exit(1)

    elif args.command == "init":
        if wait_for_db(max_retries=5, delay_seconds=1.0):
            init_db()
        else:
            logger.error("Database unavailable. Metadata initialization aborted.")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()