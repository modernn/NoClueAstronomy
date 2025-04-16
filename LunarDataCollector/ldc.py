import requests
from bs4 import BeautifulSoup
import sqlite3

URL = "https://eclipse.gsfc.nasa.gov/LEcat5/LE2001-2100.html"

def scrape_eclipse_data():
    response = requests.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    # The page has multiple <pre> tags. We want the one that actually
    # contains the table of eclipses (with lines beginning in e.g. '09651').
    pre_tags = soup.find_all("pre")
    
    data_lines = []
    for pre in pre_tags:
        # Split into lines
        lines = pre.get_text().splitlines()
        # Look for lines that appear to be valid data lines (start with a digit after stripping).
        # We'll collect them into data_lines if they match.
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            # Check if the first character is a digit
            if stripped[0].isdigit():
                data_lines.append(stripped)
    
    records = []
    for line in data_lines:
        # The lines in NASA’s table typically have 18 “columns” when split on whitespace.
        # But we must be careful with the day/month/year vs. time fields, etc.
        # Let’s just do a normal split and see if we get enough tokens.
        tokens = line.split()
        
        # The table columns are (with typical indices):
        #   0 CatNum
        #   1 Year
        #   2 Month
        #   3 Day
        #   4 Time
        #   5 ΔT
        #   6 Luna#
        #   7 Saros#
        #   8 Ecl.Type
        #   9 QSE
        #   10 Gamma
        #   11 Mag1
        #   12 Mag2
        #   13 Pen (m)
        #   14 Par (m)
        #   15 Tot (m)
        #   16 Lat
        #   17 Lng
        
        if len(tokens) < 18:
            # If the line doesn't have at least 18 tokens, skip it.
            continue
        
        cat_num         = tokens[0]
        # Combine year, month, day into a single string: "2001 Jan 09"
        calendar_date   = " ".join(tokens[1:4])  # e.g. "2001 Jan 09"
        greatest_eclipse= tokens[4]             # e.g. "20:21:40"
        delta_t         = tokens[5]             # e.g. "64"
        luna_num        = tokens[6]
        saros_num       = tokens[7]
        eclipse_type    = tokens[8]             # e.g. "T"
        qse             = tokens[9]             # e.g. "p-"
        gamma           = tokens[10]
        mag1            = tokens[11]
        mag2            = tokens[12]
        pen             = tokens[13]            # e.g. "311.0" or "-"
        par             = tokens[14]            # e.g. "196.3" or "-"
        total           = tokens[15]            # e.g. "61.0" or "-"
        lat             = tokens[16]
        lng             = tokens[17]

        records.append((
            cat_num, calendar_date, greatest_eclipse, delta_t,
            luna_num, saros_num, eclipse_type, qse,
            gamma, mag1, mag2, pen, par, total, lat, lng
        ))

    return records

def create_database(records, db_name="eclipse_data.db"):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    # Create the eclipses table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS eclipses (
            cat_num TEXT,
            calendar_date TEXT,
            greatest_eclipse TEXT,
            delta_t TEXT,
            luna_num TEXT,
            saros_num TEXT,
            eclipse_type TEXT,
            qse TEXT,
            gamma TEXT,
            mag1 TEXT,
            mag2 TEXT,
            pen TEXT,
            par TEXT,
            total TEXT,
            lat TEXT,
            lng TEXT
        )
    """)
    
    # Insert the records into the database
    cur.executemany("""
        INSERT INTO eclipses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, records)
    
    conn.commit()
    conn.close()

def main():
    records = scrape_eclipse_data()
    print(f"Found {len(records)} data lines that look like eclipses.")
    create_database(records)
    print(f"Inserted {len(records)} records into eclipse_data.db")

if __name__ == "__main__":
    main()
