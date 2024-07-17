from datetime import datetime


# Get an array of the seasons given the number of seasons that we want
# formatted for the API.
def get_seasons(num_years=1):
    cur_year = datetime.now().year
    years = []
    for i in range(0, num_years):
        years.append(f"{cur_year-i-1}-{str(cur_year-i)[-2:]}")
    return years
