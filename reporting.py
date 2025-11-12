"""
Standalone script for generating a daily report of book data changes.

This script connects to the MongoDB database, queries the 'changelog' collection
for all changes recorded in the last 24 hours, and exports the results into
either a JSON or CSV file.

This script is intended to be run automatically by a system scheduler (e.g., cron)
to provide daily updates.

Usage:
    python reporting.py [--format <json|csv>]
"""
import asyncio
import argparse
import csv
import json
from datetime import datetime, timedelta
import motor.motor_asyncio

# --- Database Configuration ---
# These settings should match the ones used in the Scrapy project.
MONGO_URI = "mongodb://127.0.0.1:27017"
MONGO_DATABASE = "books_db"
CHANGELOG_COLLECTION = "changelog"

async def get_daily_changes() -> list:
    """
    Connects to MongoDB and fetches all change log entries from the last 24 hours.

    Returns:
        A list of dictionaries, where each dictionary is a change log document.
    """
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DATABASE]
    
    # Calculate the datetime for 24 hours ago to filter recent changes.
    time_threshold = datetime.utcnow() - timedelta(hours=24)
    
    # Query the database for all documents newer than the threshold.
    cursor = db[CHANGELOG_COLLECTION].find(
        {"timestamp": {"$gte": time_threshold}},
        # Exclude the internal MongoDB '_id' field from the results for cleaner output.
        {"_id": 0}
    )
    
    changes = await cursor.to_list(length=None)
    client.close()
    return changes

def generate_json_report(changes: list, filename: str = "daily_report.json"):
    """
    Writes the list of change documents to a pretty-printed JSON file.

    Args:
        changes: A list of change log documents.
        filename: The name of the output file.
    """
    # Convert datetime objects to ISO 8601 strings, as datetime objects
    # are not directly serializable to JSON.
    for change in changes:
        if isinstance(change.get("timestamp"), datetime):
            change["timestamp"] = change["timestamp"].isoformat()

    with open(filename, "w") as f:
        json.dump(changes, f, indent=4)
    print(f"Successfully generated JSON report: {filename}")

def generate_csv_report(changes: list, filename: str = "daily_report.csv"):
    """
    Writes the list of change documents to a CSV file.

    Args:
        changes: A list of change log documents.
        filename: The name of the output file.
    """
    if not changes:
        print("No changes to report.")
        return

    # Define the headers for the CSV file in a logical order.
    fieldnames = ["timestamp", "book_id", "change_type", "field_changed", "old_value", "new_value"]
    
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(changes)
    print(f"Successfully generated CSV report: {filename}")

async def main():
    """
    The main entry point for the script.

    Parses command-line arguments to determine the output format and orchestrates
    the fetching of data and generation of the report.
    """
    parser = argparse.ArgumentParser(description="Generate a daily report of book data changes from the database.")
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "csv"],
        default="json",
        help="The output format for the report (default: json)."
    )
    args = parser.parse_args()

    print("Fetching changes from the last 24 hours...")
    changes = await get_daily_changes()

    if not changes:
        print("No changes found in the last 24 hours.")
        return

    if args.format == "json":
        generate_json_report(changes)
    elif args.format == "csv":
        generate_csv_report(changes)

if __name__ == "__main__":
    # Use asyncio.run() to execute the async main function.
    asyncio.run(main())
