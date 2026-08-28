from app.core.config import settings
from app.database.database import SessionLocal
from app.services.index_service import index_files


def main() -> None:
    db = SessionLocal()

    try:
        result = index_files(
            db=db,
            root_path=settings.index_root_path,
        )

        print()
        print("Index completed")
        print("-------------------------")
        print(f"Root path        : {settings.index_root_path}")
        print(f"Status           : {result.status}")
        print(f"Scanned files    : {result.scanned_files}")
        print(f"New files        : {result.new_files}")
        print(f"Updated files    : {result.updated_files}")
        print(f"Inactive files   : {result.inactive_files}")
        print(f"Skipped files    : {result.skipped_files}")
        print(f"Errors           : {result.error_count}")

    finally:
        db.close()


if __name__ == "__main__":
    main()