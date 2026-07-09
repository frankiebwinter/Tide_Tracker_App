# TideTracker
# reads real data from the two CSV files in this folder (won't fully function when run outside of my pycharm folder)
# The two files attached in the folder are the only ones that can be read

# I REFERRED TO:
# https://docs.python.org/3/library/calendar.html
# For information

# I REFERRED TO:
# my own previous code

# I chose JSON because it stores my mixed criteria (text, numbers, True/False)
# in a structured, human-readable form that Python can write and read back with one line each
# (json.dump, json.load), with no parsing code of my own

# Tide Tracker Application
# Frankie-Belle Taylor 01/06/2026
# Frankie-Belle Taylor 02/06/2026
# Frankie-Belle Taylor 05/06/2026
# Frankie-Belle Taylor 08/06/26
# Frankie-Belle Taylor 12/06/26
# Frankie-Belle Taylor 15/06/26
# Frankie-Belle Taylor 16/06/26
# Frankie-Belle Taylor 19/06/26
# Frankie-Belle Taylor 22/06/26

# OVERVIEW
# This application helps users find suitable days for surfing or swimming
# by filtering tide and daylight data against user-defined criteria
# Users set preferences (tide height range, time window, daylight conditions)
# on a criteria screen, then view matching days highlighted on a calendar
# A layering feature allows two activities to be compared on the same calendar
# Results will be able to be saved, loaded (and maybe exported)



# DATA SOURCES
# "Point-Lonsdale_60730_2026.csv" - Bureau of Meteorology tide predictions for Point Lonsdale,
# one height reading every 6 minutes for all of 2026
# A CSV was chosen because it is plain text, easy to read line by line, and is the format the data was supplied in.
# "Aireys_Inlet_Sunrise_and_Sunset.csv" - daily sunrise/sunset times for 2026. Chosen for the
# same reasons
# it is the nearest official daylight data for this area of the coast

# NAMING CONVENTIONS APPLIED
# snake_case for variables, functions and methods (e.g. tide_records, load_tide_data)
# PascalCase for classes (UserCriteria, ActivityFilter, TideTrackerApp)
# UPPER_SNAKE_CASE for constants (COLOUR_SURF, TIDE_FILE)
# GUI controls are prefixed by type: cmb_ (combo box), btn_ (button), lbl_ (label), var_ (a
#  tk variable for a checkbox).
# A leading underscore marks helpers used only inside their own class or this file (e.g. _minutes,
# _card, _load_sources)

import csv
import os
import calendar as calmod
from datetime import datetime
import streamlit as st
import json

# GLOBAL CONSTANTS (UPPER_SNAKE_CASE)
# These never change while the program runs
# str data type, a hex colour code is text used by the GUI to paint a cell
COLOUR_SURF     = "#2e8b57"   # green
COLOUR_SWIM     = "#2f6fed"   # blue
COLOUR_BOTH     = "#8a4fff"   # purple
COLOUR_IDEAL    = "#f5b301"   # gold (kept, but ideal days are shown with a star, not gold)
COLOUR_NO_MATCH = "#33373e"   # grey
COLOUR_INACTIVE = "#555a63"   # inactive button grey

# list of str: fixed labels reused by the GUI and for converting a month name to its number
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# list of str: the values offered in the drop-down boxes.
# TIDES is built with a loop and arithmetic so I don't have to type each value by hand
# The [] part below is a list comprehension, it runs the for-loop and collects each result into a
# list in one line
# range(0, 31, 2) gives 0,2,4, etc
# x / 10 turns those into 0.0 format
# "{:.1f}".format makes each into text with one decimal place
TIDES = ["{:.1f}".format(x / 10) for x in range(0, 31, 2)]   # "0.0","0.2",..."3.0"  (x/10 = arithmetic)
# one entry per hour 0-23, formatted as two digits plus ":00" ("00:00") etc
TIMES = ["{:02d}:00".format(h) for h in range(0, 24)]
# only 2026 is offered because both data files cover 2026 only (range matched to the data).
YEARS = ["2026"]

STAR = "\u2605"   # str: the star symbol shown on an ideal day

# str constants naming the two data files, kept in one place so they are easy to change.
TIDE_FILE     = "Point-Lonsdale_60730_2026.csv"
DAYLIGHT_FILE = "Aireys_Inlet_Sunrise_and_Sunset.csv"

# Small fuctions used across the program
# Pulled out so the logic reads clearly and the
# same conversion is not repeated
def parse_date(date_str):
    # Turn a "DD/MM/YYYY" date string into a date object so its parts can be read
    # The data might use a few different layouts, so we try each known format in turn. strptime
    # "string parse time" reads the text using one format, if that format does not fit it raises
    # ValueError, which we catch and then try the next format
    # If none fit, we raise our own error
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(str(date_str).strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError("Unrecognised date format: " + str(date_str))


def parse_time(time_str):
    # Turn an "HH:MM" string into a time object so two times can be compared with
    # Same try-each-format idea as parse_date above
    s = str(time_str).strip()
    for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p"):
        try:
            return datetime.strptime(s, fmt).time()
        except ValueError:
            continue
    raise ValueError("Unrecognised time format: " + s)


def extract_year(date_str):
    # int: the year of a date string.
    return parse_date(date_str).year


def extract_month(date_str):
    # int: the month of a date string.
    return parse_date(date_str).month


def convert_to_decimal(value):
    # float: a tide-height text turned into a number in metres
    return float(value)


def _minutes(t):
    # int: a time expressed as minutes since midnight
    # Arithmetic operators used here
    # so two times can be compared as plain numbers
    return t.hour * 60 + t.minute

def find_closest_tide(tide_records, target_time):
    # Return the record whose time is nearest target_time
    # This is the tide rated for the day
    # min() looks at every record and keeps the "smallest" one
    # The key= tells min() what counts as small
    # lambda is just a tiny function with no name
    # this one takes one record and returns how far its time is from target_time in minutes
    # abs() drops the sign so "10 minutes before" and "10 minutes after" both score 10
    # min() returns the record with the smallest score

    return min(
        tide_records,
        key=lambda rec: abs(_minutes(parse_time(rec["time"])) - _minutes(target_time)),
    )

# DATA SOURCE FUNCTION: load tide data from the CSV.
# The file holds one height every 6 minutes
# that is far more detail than a calendar needs, so this function reduces the readings to the HIGH and LOW tides, which is what a surfer/swimmer actually cares about
# Returns a list of record dictionaries
# still editing this section 19/06/26

def load_tide_data(file_path):
    # existence check on the data source
    # if the file is missing, report it and return an empty list rather than crashing
    if not os.path.exists(file_path):
        print("Tide file not found: " + file_path)
        return []

    readings = []   # list of date_str, time_str, height in file order
    with open(file_path, newline="") as f:
        # iteration, read the file one line at a time
        for raw_line in f:
            line = raw_line.strip()
            # selection, skip blank lines and the leading comment line in the file
            if line == "" or line.startswith("#"):
                continue
            stamp, value = line.split(",")
            # split cuts the line at the comma into two pieces, the timestamp and the height.
            # The clock time shown is already local Victorian time, so the date and HH:MM are taken straight from the text
            # Slicing takes a range of characters by position

            date_part = stamp[0:10]
            time_part = stamp[11:16]
            year_txt, month_txt, day_txt = date_part.split("-")   # split the date into 3 parts
            iso_to_local = day_txt + "/" + month_txt + "/" + year_txt   # rewrite as DD/MM/YYYY
            readings.append((iso_to_local, time_part, float(value)))    # type conversion

    # A HIGH tide is a reading higher than the one before and not lower than
    # the one after, a LOW tide is the opposite
    # The loop looks at each reading together with the ones before and after
    # If the middle reading is the highest of the three it is a peak, and if it is the lowest it is a low
    # start at 1 and stop one early so every reading has one on either side

    raw_events = []
    for i in range(1, len(readings) - 1):
        prev_height = readings[i - 1][2]
        curr_height = readings[i][2]
        next_height = readings[i + 1][2]
        is_high = curr_height > prev_height and curr_height >= next_height
        is_low = curr_height < prev_height and curr_height <= next_height
        if is_high or is_low:                 # selection
            date_str, time_str, height = readings[i]
            raw_events.append({
                "date": date_str,                       # str
                "time": time_str,                       # str
                "tide_height": round(height, 2),        # float (rounded to 2 dp)
                # "A if test else B" picks one of two values: "high" when is_high is true, else "low".
                "kind": "high" if is_high else "low",   # str
            })

    # the 6-minute data sometimes wobbles around a bit
    # This pass keeps a clean sequence of low, high
    # My dad suggested doing this restriction
    tide_records = []
    for event in raw_events:                  # iteration
        # tide_records[-1] means the last event
        # If it is the same kind, keep only the stronger one instead of both
        if tide_records and tide_records[-1]["kind"] == event["kind"]:
            last = tide_records[-1]
            # the \ at the end just continues this one condition onto the next line
            keep_new = (event["kind"] == "high" and event["tide_height"] > last["tide_height"]) or \
                       (event["kind"] == "low" and event["tide_height"] < last["tide_height"])
            if keep_new:
                tide_records[-1] = event      # replace the weaker same-kind event
            # else, ignore the duplicate event
        else:
            tide_records.append(event)
    return tide_records

# Data source function
# load sunrise/sunset data from the CSV
# Returns a list of record dictionaries

def load_daylight_data(file_path):
    # existence check on the data source.
    if not os.path.exists(file_path):
        print("Daylight file not found: " + file_path)
        return []

    daylight_records = []
    with open(file_path, newline="") as csv_file:
        # csv.DictReader reads each row into a dictionary keyed by the column headings, so columns can be read by name
        reader = csv.DictReader(csv_file)
        for row in reader:                    # iteration over the rows
            # The rise_date, set_date columns hold a full date-and-time stamp
            # Only the date and the HH:MM clock time are needed
            rise = datetime.strptime(row["rise_date"], "%Y-%m-%d %H:%M:%S")
            sett = datetime.strptime(row["set_date"], "%Y-%m-%d %H:%M:%S")
            daylight_records.append({
                "date": rise.strftime("%d/%m/%Y"),       # str
                "sunrise_time": rise.strftime("%H:%M"),  # str
                "sunset_time": sett.strftime("%H:%M"),   # str
            })
    return daylight_records

# Keep only the records for the chosen year (the data is 2026, but this keeps the design general).
def restrict_to_year(tide_records, daylight_records, selected_year):
    # These list comprehensions read "keep record r for every r in the list, but only if its year
    # matches selected_year
    # The "if" at the end filters out the rest
    kept_tides = [r for r in tide_records if extract_year(r["date"]) == selected_year]
    kept_daylight = [r for r in daylight_records if extract_year(r["date"]) == selected_year]
    return kept_tides, kept_daylight


# Merge the tide and daylight lists into one dictionary keyed by date, so each day carries its sunrise, sunset and all of its tides together
# A dictionary lookup is built first so matching a tide to its day is fast
def collate_data(tide_records, daylight_records):
    unified_data = {}
    # This is a dictionary comprehension
    # it builds a quick lookup table mapping each date to its
    # daylight record, so a day's sunrise/sunset can be found instantly by date instead of searching
    daylight_lookup = {r["date"]: r for r in daylight_records}
    for tide in tide_records:                 # iteration
        date_str = tide["date"]
        if date_str not in daylight_lookup:   # selection, skip a tide with no daylight entry
            continue
        if date_str not in unified_data:
            unified_data[date_str] = {
                "date": date_str,
                "sunrise_time": daylight_lookup[date_str]["sunrise_time"],
                "sunset_time": daylight_lookup[date_str]["sunset_time"],
                "tide_records": [],           # list to collect this day's tides
            }
        unified_data[date_str]["tide_records"].append(
            {"time": tide["time"], "tide_height": tide["tide_height"]}
        )
    return unified_data

# CLASS UserCriteria
# Encapsulates everything the user can choose
# It reads those choices off the screen, converts them to the right data types, and validates them
class UserCriteria:
    def __init__(self):
        # Attributes start empty so "missing" can be told apart from "0"

        self.activity = None          # str  "surf"/"swim"
        self.selected_year = None     # int
        self.selected_month = None    # int 1-12
        self.tide_min = None          # float metres
        self.tide_max = None          # float metres
        self.time_from = None         # time
        self.time_to = None           # time
        self.is_sunrise = False       # bool
        self.is_sunset = False        # bool
        self.is_after_sunrise = False # bool
        self.is_before_sunset = False # bool

    # Each tries to convert the text and returns None if it cannot
    # These WERE NOT in my pseudocode, I added them in last minute because I hadn't validated proper;y
    # 19/06/26
    def _safe_int(self, text):
        try:
            return int(text)
        except (ValueError, TypeError):
            return None

    def _safe_float(self, text):
        try:
            return float(text)
        except (ValueError, TypeError):
            return None

    def _safe_time(self, text):
        try:
            return parse_time(text)
        except (ValueError, TypeError):
            return None

    def _safe_month(self, name):
        # Convert a month name to its number 1-12
        if name in MONTHS:
            return MONTHS.index(name) + 1
        return None

    # Copy the GUI values into this object, converting types

    def read_from_screen(self, app):
        self.activity = app.current_activity
        self.selected_year = self._safe_int(app.cmb_year.get())
        self.selected_month = self._safe_month(app.cmb_month.get())
        self.tide_min = self._safe_float(app.cmb_tide_min.get())
        self.tide_max = self._safe_float(app.cmb_tide_max.get())
        self.time_from = self._safe_time(app.cmb_time_from.get())
        self.time_to = self._safe_time(app.cmb_time_to.get())
        # BooleanVar.get() already returns a bool
        self.is_sunrise = app.var_sunrise.get()
        self.is_sunset = app.var_sunset.get()
        self.is_after_sunrise = app.var_after_sunrise.get()
        self.is_before_sunset = app.var_before_sunset.get()

    # Returns a list of problem messages
    # empty means all good
    def validate(self):
        problems = []

        # Existence and type checks
        # read_from_screen stored None for anything missing or of the wrong type, so a None here means the value is absent or could not be converted.
        if self.activity is None:
            problems.append("Choose Surf or Swim (no activity selected).")
        if self.selected_year is None:
            problems.append("Year is missing or not a whole number.")
        if self.selected_month is None:
            problems.append("Month is missing or not recognised.")
        if self.tide_min is None or self.tide_max is None:
            problems.append("Both tide heights must be set to a number.")
        if self.time_from is None or self.time_to is None:
            problems.append("Both From and To times must be valid times.")

        # if anything essential is still missing, stop now so the range checks below do not run on a None value
        if problems:
            return problems

        # type check
        # activity must be exactly one of the two allowed words
        if self.activity not in ("surf", "swim"):
            problems.append("Activity must be 'surf' or 'swim'.")

        # range checks
        if not (1 <= self.selected_month <= 12):
            problems.append("Month must be between 1 and 12.")
        if not (0.0 <= self.tide_min <= 3.0) or not (0.0 <= self.tide_max <= 3.0):
            problems.append("Tide heights must be between 0.0 and 3.0 metres.")

        # logic checks, the values exist and are in range, but must also make sense together
        if self.tide_min > self.tide_max:
            problems.append("Minimum tide cannot be greater than maximum tide.")
        if self.time_from >= self.time_to:
            problems.append("From time must be earlier than To time.")
        if self.is_sunrise and self.is_sunset:
            problems.append("A tide cannot be at sunrise and at sunset at the same time.")

        return problems

 # Added on 22/06/26
 # Save the current criteria to a JSON file named after the activity
    def save(self):
        # filename built from the activity so surf and swim stay separate
        file_name = self.activity + "_criteria_saved.json"
        # every value gathered into one dictionary, times stored as text
        data = {
            "activity": self.activity,
            "selected_year": self.selected_year,
            "selected_month": self.selected_month,
            "tide_min": self.tide_min,
            "tide_max": self.tide_max,
            "time_from": self.time_from.strftime("%H:%M"),
            "time_to": self.time_to.strftime("%H:%M"),
            "is_sunrise": self.is_sunrise,
            "is_sunset": self.is_sunset,
            "is_after_sunrise": self.is_after_sunrise,
            "is_before_sunset": self.is_before_sunset,
        }
        # write the file, return a message either way
        try:
            with open(file_name, "w") as f:
                json.dump(data, f, indent=2)
            return "Criteria saved to " + file_name
        except OSError:
            return "Could not save criteria"

    # ADDED: load saved criteria for this activity back into the object
    def load(self):
        file_name = self.activity + "_criteria_saved.json"
        # no file means nothing to load, tell the caller to stop
        if not os.path.exists(file_name):
            return False
        with open(file_name) as f:
            data = json.load(f)
        self.activity = data["activity"]
        self.selected_year = data["selected_year"]
        self.selected_month = data["selected_month"]
        self.tide_min = data["tide_min"]
        self.tide_max = data["tide_max"]
        self.time_from = parse_time(data["time_from"])   # text back into a time
        self.time_to = parse_time(data["time_to"])
        self.is_sunrise = data["is_sunrise"]
        self.is_sunset = data["is_sunset"]
        self.is_after_sunrise = data["is_after_sunrise"]
        self.is_before_sunset = data["is_before_sunset"]
        return True

    # Push the stored values back into the on-screen widgets
    def populate_widgets(self, app):
        app.on_activity_select(self.activity)
        app.cmb_year.set(str(self.selected_year))
        app.cmb_month.set(MONTHS[self.selected_month - 1])      # number back to month name
        app.cmb_tide_min.set("{:.1f}".format(self.tide_min))
        app.cmb_tide_max.set("{:.1f}".format(self.tide_max))
        app.cmb_time_from.set(self.time_from.strftime("%H:%M"))
        app.cmb_time_to.set(self.time_to.strftime("%H:%M"))
        app.var_sunrise.set(self.is_sunrise)
        app.var_sunset.set(self.is_sunset)
        app.var_after_sunrise.set(self.is_after_sunrise)
        app.var_before_sunset.set(self.is_before_sunset)

# CLASS ActivityFilter
# Encapsulates the filtering and rating
# Given the unified data and the criteria it produces the match_days dictionary the calendar draws from
class ActivityFilter:
    def __init__(self):
        self.criteria = None
        self.match_days = {}

    # Keep matching tides, then rate each matching day
    def filter_and_rate(self, unified_data, criteria):
        self.criteria = criteria
        results = {}
        for date_str, day in unified_data.items():        # iteration over each day
            if extract_month(date_str) != criteria.selected_month:   # selection: wrong month
                continue
            matched = []
            for tide in day["tide_records"]:              # iteration over the day's tides
                tide_time = parse_time(tide["time"])
                # selection and comparison operators
                # reject tides outside the range or window
                # a tide that fails any test below is never added to matched
                if tide["tide_height"] < criteria.tide_min:
                    continue
                if tide["tide_height"] > criteria.tide_max:
                    continue
                if tide_time < criteria.time_from:
                    continue
                if tide_time > criteria.time_to:
                    continue
                sunrise = parse_time(day["sunrise_time"])
                sunset = parse_time(day["sunset_time"])
                # optional daylight rules, only applied when the matching checkbox is ticked
                if criteria.is_after_sunrise and tide_time < sunrise:
                    continue
                if criteria.is_before_sunset and tide_time > sunset:
                    continue
                if criteria.is_sunrise and tide_time != sunrise:
                    continue
                if criteria.is_sunset and tide_time != sunset:
                    continue
                matched.append(tide)
            if matched:                                   # keep the day only if a tide matched
                results[date_str] = {
                    "tide_records": matched,
                    "sunrise_time": day["sunrise_time"],
                    "sunset_time": day["sunset_time"],
                }

        # Rate each matching day
        # The top quarter of the chosen range counts as "ideal"
        # tide_range and ideal_threshold are local variables

        self.match_days = {}
        tide_range = criteria.tide_max - criteria.tide_min
        ideal_threshold = criteria.tide_max - (tide_range * 0.25)
        for date_str, day in results.items():
            best = find_closest_tide(day["tide_records"], criteria.time_from)
            self.match_days[date_str] = {
                "activity": criteria.activity,
                "tide_height": best["tide_height"],
                "tide_time": best["time"],
                "is_ideal": best["tide_height"] >= ideal_threshold,   # bool result of a comparison
            }
        return self.match_days

    # Choose the colour and symbol for one matching day.
    def indicator_for(self, info):
        # Each line uses "value_if_true if test else value_if_false"
        # The first picks green for surf or blue for swim
        # the second shows a star only when the day is ideal, otherwise no symbol
        colour = COLOUR_SURF if self.criteria.activity == "surf" else COLOUR_SWIM
        symbol = STAR if info["is_ideal"] else ""
        return colour, symbol
class TideTrackerApp:
    def __init__(self):
        # State for whole app
        defaults = {
            "current_activity": None,
            "active_criteria": None,
            "current_match_days": None,
            "active_filter": None,
            "current_screen": "criteria_screen",
            "status_text": "Pick an activity, set your criteria, then Show calendar",
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

        # Loaded once
        self._tide_records = None
        self._daylight_records = None

    def show_screen(self, screen_name):
        st.session_state.current_screen = screen_name

    def build_criteria_screen(self):
        header_col, status_col = st.columns([2, 3])
        header_col.title("Tide Tracker")
        status_col.write("")
        status_col.caption(st.session_state.status_text)

        # Activity
        st.subheader("Activity")
        row = st.columns(2)

        surf_type = (
            "primary"
            if st.session_state.current_activity == "surf"
            else "secondary"
        )
        swim_type = (
            "primary"
            if st.session_state.current_activity == "swim"
            else "secondary"
        )

        if row[0].button("Surf", use_container_width=True, type=surf_type):
            self.on_activity_select("surf")

        if row[1].button("Swim", use_container_width=True, type=swim_type):
            self.on_activity_select("swim")

        # When / Tide
        when_col, tide_col = st.columns(2)

        with when_col:
            st.subheader("When")
            st.selectbox("Year", YEARS, key="cmb_year")
            st.selectbox("Month", MONTHS, index=2, key="cmb_month")

        with tide_col:
            st.subheader("Tide")
            st.selectbox(
                "Minimum",
                TIDES,
                index=TIDES.index("0.8"),
                key="cmb_tide_min",
            )
            st.selectbox(
                "Maximum",
                TIDES,
                index=TIDES.index("1.6"),
                key="cmb_tide_max",
            )

        # Time / Daylight
        time_col, light_col = st.columns(2)

        with time_col:
            st.subheader("Time window")
            st.selectbox(
                "From",
                TIMES,
                index=TIMES.index("06:00"),
                key="cmb_time_from",
            )
            st.selectbox(
                "To",
                TIMES,
                index=TIMES.index("18:00"),
                key="cmb_time_to",
            )

        with light_col:
            st.subheader("Daylight conditions")
            st.checkbox("At sunrise", key="var_sunrise")
            st.checkbox("At sunset", key="var_sunset")
            st.checkbox("After sunrise", key="var_after_sunrise")
            st.checkbox("Before sunset", key="var_before_sunset")

        # Buttons
        actions = st.columns(3)

        if actions[0].button("Save criteria", use_container_width=True):
            self.on_save_criteria()

        if actions[1].button("Load criteria", use_container_width=True):
            self.on_load_criteria()

        if actions[2].button(
            "Show calendar",
            use_container_width=True,
            type="primary",
        ):
            self.on_show_calendar()

    def on_activity_select(self, activity):
        st.session_state.current_activity = activity

    def _read_criteria_from_widgets(self):
        criteria = UserCriteria()

        criteria.read_from_values(
            st.session_state.current_activity,
            st.session_state.cmb_year,
            st.session_state.cmb_month,
            st.session_state.cmb_tide_min,
            st.session_state.cmb_tide_max,
            st.session_state.cmb_time_from,
            st.session_state.cmb_time_to,
            st.session_state.var_sunrise,
            st.session_state.var_sunset,
            st.session_state.var_after_sunrise,
            st.session_state.var_before_sunset,
        )

        return criteria

    def on_save_criteria(self):
        criteria = self._read_criteria_from_widgets()
        problems = criteria.validate()

        if problems:
            st.session_state.status_text = "   ".join(problems)
            return

        st.session_state.status_text = criteria.save()

    def on_load_criteria(self):
        if st.session_state.current_activity is None:
            st.session_state.status_text = (
                "Choose Surf or Swim first, then Load criteria."
            )
            return

        criteria = UserCriteria()
        criteria.activity = st.session_state.current_activity

        if criteria.load():
            criteria.populate_widgets()
            st.session_state.status_text = (
                "Criteria loaded for "
                + st.session_state.current_activity
            )
            st.rerun()
        else:
            st.session_state.status_text = (
                "No saved criteria found for "
                + st.session_state.current_activity
            )

    def _load_sources(self):
        if self._tide_records is None:
            self._tide_records = load_tide_data(TIDE_FILE)

        if self._daylight_records is None:
            self._daylight_records = load_daylight_data(DAYLIGHT_FILE)

        return (
            len(self._tide_records) > 0
            and len(self._daylight_records) > 0
        )

    def on_show_calendar(self):
        criteria = self._read_criteria_from_widgets()

        problems = criteria.validate()

        if problems:
            st.session_state.status_text = "   ".join(problems)
            return

        if not self._load_sources():
            st.session_state.status_text = (
                "Could not read the data files, check the files"
            )
            return

        st.session_state.status_text = ""
        st.session_state.active_criteria = criteria

        year = criteria.selected_year
        month = criteria.selected_month

        kept_tides, kept_daylight = restrict_to_year(
            self._tide_records,
            self._daylight_records,
            year,
        )

        unified_data = collate_data(kept_tides, kept_daylight)

        af = ActivityFilter()
        match_days = af.filter_and_rate(unified_data, criteria)

        st.session_state.active_filter = af
        st.session_state.current_match_days = match_days

        if not match_days:
            st.session_state.status_text = (
                "No matching days for these criteria - try widening them."
            )

        self.show_screen("calendar_screen")
        st.rerun()

    def build_calendar_screen(self):
        criteria = st.session_state.active_criteria
        af = st.session_state.active_filter
        match_days = st.session_state.current_match_days

        topbar = st.columns([4, 1])

        topbar[0].subheader(
            MONTHS[criteria.selected_month - 1]
            + " "
            + str(criteria.selected_year)
        )

        if topbar[1].button("Edit criteria"):
            self.show_screen("criteria_screen")
            st.rerun()

        head = st.columns(7)

        for i, weekday in enumerate(WEEKDAYS):
            head[i].markdown(f"**{weekday}**")

        self._render_calendar(
            criteria.selected_year,
            criteria.selected_month,
            match_days,
            af,
        )

        self._build_legend()

    def _render_calendar(self, year, month, match_days, af):
        cal = calmod.Calendar(firstweekday=0)

        for week in cal.monthdayscalendar(year, month):
            row_cols = st.columns(7)

            for c, day in enumerate(week):
                if day == 0:
                    continue

                date_str = "{:02d}/{:02d}/{}".format(day, month, year)

                if date_str in match_days:
                    info = match_days[date_str]
                    colour, symbol = af.indicator_for(info)
                    detail = "{}m {}".format(
                        info["tide_height"],
                        info["tide_time"],
                    )
                    self._draw_cell(
                        row_cols[c],
                        day,
                        colour,
                        symbol,
                        detail,
                    )
                else:
                    self._draw_cell(
                        row_cols[c],
                        day,
                        COLOUR_NO_MATCH,
                        "X",
                        "",
                    )

    def _draw_cell(self, column, day, colour, symbol, detail):
        with column.container(border=True):
            st.markdown(f"**{day}**")

            if colour == COLOUR_NO_MATCH:
                st.badge("No match", color="gray")
            else:
                activity_label = (
                    "Surf"
                    if colour == COLOUR_SURF
                    else "Swim"
                )

                badge_colour = (
                    "green"
                    if colour == COLOUR_SURF
                    else "blue"
                )

                if symbol:
                    st.badge(
                        activity_label + " " + STAR,
                        color="orange",
                    )
                else:
                    st.badge(
                        activity_label,
                        color=badge_colour,
                    )

            if detail:
                st.caption(detail)

    def _build_legend(self):
        st.write("")
        legend = st.columns(5)

        legend[0].badge("Surf", color="green")
        legend[1].badge("Swim", color="blue")
        legend[2].badge("Both", color="violet")
        legend[3].badge(STAR + " Ideal", color="orange")
        legend[4].badge("No match", color="gray")

    def run(self):
        if st.session_state.current_screen == "criteria_screen":
            self.build_criteria_screen()
        else:
            self.build_calendar_screen()


if __name__ == "__main__":
    st.set_page_config(
        page_title="TideTracker",
        layout="wide",
    )

    TideTrackerApp().run()

