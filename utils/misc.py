"""
This file contains miscellaneous utility functions!
"""

# =================
# DECLARING METHODS
# =================
# Below, we'll declare all of the utility functions.


def abbreviate_month(month: str) -> str:
    """
    This utility function converts months to their abbreviated form.

    Args:
        - month (str): The full name of the month.

    Returns:
        The abbreviated form of the month.
    """
    month_abbreviations = {
        "January": "Jan",
        "February": "Feb",
        "March": "Mar",
        "April": "Apr",
        "May": "May",
        "June": "Jun",
        "July": "Jul",
        "August": "Aug",
        "September": "Sep",
        "October": "Oct",
        "November": "Nov",
        "December": "Dec",
    }
    return month_abbreviations.get(month, "")
