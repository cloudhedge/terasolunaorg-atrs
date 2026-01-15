"""Background task for generating reservation history reports"""

import csv
import os
from datetime import datetime
from pathlib import Path

from ..repositories import ReservationRepository


async def generate_reservation_history_report(
    ctx: dict,
    membership_number: str,
    output_dir: str = "/tmp/atrs/reports",
) -> str:
    """
    Generate CSV report of member's reservation history.

    This replaces the JMS-based async report generation from the Java app.

    Args:
        ctx: arq context containing database connection
        membership_number: Member to generate report for
        output_dir: Directory to save report

    Returns:
        Path to generated CSV file
    """
    db = ctx["db"]
    reservation_repo = ReservationRepository(db)

    # Get reservation history
    history = await reservation_repo.find_all_by_membership_number_for_report(
        membership_number
    )

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reservation_history_{membership_number}_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)

    # Write CSV
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            "Reserve No",
            "Reserve Date",
            "Total Fare",
            "Representative Name",
            "Departure Date",
            "Flight Name",
            "Departure Airport",
            "Arrival Airport",
        ])

        # Data rows
        for row in history:
            writer.writerow([
                row.reserve_no,
                row.reserve_date.strftime("%Y/%m/%d"),
                f"{row.total_fare:,}",
                f"{row.rep_family_name} {row.rep_given_name}",
                row.departure_date.strftime("%Y/%m/%d"),
                row.flight_name,
                row.dep_airport_name,
                row.arr_airport_name,
            ])

    return filepath
