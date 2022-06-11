import datetime


def year(request):
    """Computes current year."""
    return {
        'year': datetime.date.today().year
    }
