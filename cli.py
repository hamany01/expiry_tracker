import argparse
from pathlib import Path
from typing import List

import database


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Vehicle expiration tracker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize the database")
    init_parser.add_argument("--db", type=Path, default=database.DEFAULT_DB_PATH)

    # add command
    add_parser = subparsers.add_parser("add", help="Add a vehicle")
    add_parser.add_argument("name")
    add_parser.add_argument("plate_number")
    add_parser.add_argument("registration_expiry")
    add_parser.add_argument("insurance_expiry")
    add_parser.add_argument("--db", type=Path, default=database.DEFAULT_DB_PATH)

    # list command
    list_parser = subparsers.add_parser("list", help="List all vehicles")
    list_parser.add_argument("--db", type=Path, default=database.DEFAULT_DB_PATH)

    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        database.initialize(args.db)
    elif args.command == "add":
        database.add_vehicle(
            args.name,
            args.plate_number,
            args.registration_expiry,
            args.insurance_expiry,
            db_path=args.db,
        )
    elif args.command == "list":
        vehicles = database.get_all_vehicles(db_path=args.db)
        for vehicle in vehicles:
            print(
                f"{vehicle[0]} | {vehicle[1]} | {vehicle[2]} | {vehicle[3]}"
            )
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
