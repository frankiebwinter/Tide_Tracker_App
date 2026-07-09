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

# CONTEXT
# similarly to my pseudocode, I was playing around with Custom Tkinter in my own time with 'for fun' project,
# I implemented what I learnt for this school project

# NOTES 01/06/26
# I spent a lot of the double fiddling around with the daylight hour CSVs so didn't get much actual coding done
# I successfully downloaded CSV of sunrise and sunset times from Geoscience Aus as planned
# However, I have realised (that I didn't realise in designing) that I need to download the CSV files per individual year
# The two options for download are for a single day, or annual
# This will change my 'year selection' button, but I'm not sure quite how it will change yet
# I may need to download multiple year files so that the user still has a choice, and this will mean I will be
# dealing with more separate CSV files than I anticipated

# NOTES 01/06/26
# I spent this time defining all my constants and thinking some things through

# NOTES 05/06/26
# 05/06 I don't have access to the tide CSVs yet because I can only access these through my dad
# The tide files are NOT publicly available, so I have to work on some other things like the GUI layout
# I will hopefully gain access to the CSVs I need next week
# I have laid out some of the key buttons, checkboxes etc but without any commands yet
# I will add in the commands later
# None of this 'works' yet per say, but it is just setting up
# I have been referring to my pseudocode throughout

# NOTES 15/06/26
# added in the parsing sections, which I had referenced in my pseudocode but hadn't implemented yet
# Added to init section of Tide Application Class

# TO BE IMPLEMENTED
# I don't like how i'v laid things out using the self._card
# I want to change this and use some other word not card
# SHOULD I USE Calendar module (import it? import calendar?)
# Need to work a lot more on calendar section very messy at the moment

# REFLECTION: I have been being a little slow motion with my coding, but I am confident that
# In coming weeks I will get a lot of fast progress since I have spent so long this week organising things and thinking things through

# Notes 8/06/26 (Referring to a previous version of code, which is in my google drive folder)
# got my rough draft actually running
# Previous version would not run at all, because several buttons had empty "command=" arguments, two helper methods (_card, _combo) were
# used but never written, the calendar helpers were accidentally nested inside another method, and
# the calendar module was referred to by the wrong name
# fixed those so the program actually launches
# launches: the criteria screen shows, the activity buttons work, and "Show calendar" switches to

# Notes 12/06/26 (Referring to previous version of code, which is in my google drive folder)
# built on my previous version, which got the GUI running but only showed a fixed sample calendar
# made calendar so it is driven by the user's actual choices: when "Show calendar" is pressed
# the program reads the criteria, filters some in-memory sample tide data, rates each matching day,
# and colours the calendar accordingly
# There are still no data files the tide and daylight data are hardcoded sample values

# NOTES 19/06/26
# I still have some parts unfinished, like the 'Save' button
# Like I eliminated the PDF function, I may have to eliminate these features in not finished
# I finally implemented with actual data sources
# Because I only got the files from my dad in the last few days I couldn't do this earlier
# I may be slightly behind because of this delay, and should have sourced the files earlier

# NOTES 22/06/26
# I implemented the 'save' and 'load' functionalities
# I just directly implemented these based on my pseudocode, with very few alterations

# DATA SOURCES
# "Point-Lonsdale_60730_2026.csv" - Bureau of Meteorology tide predictions for Point Lonsdale,
# one height reading every 6 minutes for all of 2026
# A CSV was chosen because it is plain text, easy to read line by line, and is the format the data was supplied in.
# "Aireys_Inlet_Sunrise_and_Sunset.csv" - daily sunrise/sunset times for 2026. Chosen for the
# same reasons
# it is the nearest official daylight data for this area of the coast

# DATA TYPES USED
# String: dates "DD/MM/YYYY", clock times "HH:MM", activity names, GUI labels. Text is used
# because these are read from a CSV/combo box as text and are easiest to display and compare
# Numeric int: year, month (1-12), minutes-since-midnight
# Whole numbers so int is best
# Numeric float: tide heights in metres
# Height is fractional so float is best
# Boolean: the four daylight checkboxes
# tick is a yes/no value, so bool

# DATA STRUCTURES USED
# Constants in UPPER_SNAKE_CASE (lists/strings that never change) for colours, month names, etc
# Arrays for ordered collections of records (every tide reading, every tide event)
# Dictionaries used as records to keep all the facts about one day or one tide together under
# named keys

# NAMING CONVENTIONS APPLIED
# snake_case for variables, functions and methods (e.g. tide_records, load_tide_data)
# PascalCase for classes (UserCriteria, ActivityFilter, TideTrackerApp)
# UPPER_SNAKE_CASE for constants (COLOUR_SURF, TIDE_FILE)
# GUI controls are prefixed by type: cmb_ (combo box), btn_ (button), lbl_ (label), var_ (a
#  tk variable for a checkbox).
# A leading underscore marks helpers used only inside their own class or this file (e.g. _minutes,
# _card, _load_sources)

# OBJECT-ORIENTED PRINCIPLES APPLIED
# Encapsulation: each class keeps its own data and the methods that act on it (UserCriteria holds
# the user's choices
# ActivityFilter holds the filtering/rating)
# Abstraction: small helper methods/functions hide detail behind a clear name
# Inheritance: TideTrackerApp inherits from customtkinter's CTk window class
# Also loading, filtering, rating and drawing are separated so each can be changed alone.

# VALIDATION
# All user input is checked for existence, type and range
# Also logic checked

import csv
import os
import calendar as calmod
from datetime import datetime
import customtkinter as ctk
import json

# appearance settings from the customtkinter docs
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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

# CLASS TideTrackerApp
# The main window
# Inherits from customtkinter's CTk
# It builds the two screens, holds the program's global/shared state, and reacts to the buttons

class TideTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TideTracker")
        self.geometry("980x760")
        self.minsize(860, 640)

        # state the whole app
        # act like global variables

        self.current_activity = None     # str
        self.active_criteria = None      # UserCriteria
        self.current_match_days = None   # dict
        self.active_filter = None        # ActivityFilter
        self.current_screen = "criteria_screen"   # str

        #  loaded data so the large tide file is only read once

        self._tide_records = None        # list or None until loaded
        self._daylight_records = None    # list or None until loaded

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.criteria_screen = self.build_criteria_screen(self.container)
        self.calendar_screen = self.build_calendar_screen(self.container)
        self.criteria_screen.grid(row=0, column=0, sticky="nsew")
        self.calendar_screen.grid(row=0, column=0, sticky="nsew")
        self.show_screen("criteria_screen")

    # Raise whichever screen should be visible.
    def show_screen(self, screen_name):
        if screen_name == "criteria_screen":
            self.criteria_screen.tkraise()
        else:
            self.calendar_screen.tkraise()
        self.current_screen = screen_name

    # build a titled "card" frame for a group of controls
    def _card(self, parent, title):
        card = ctk.CTkFrame(parent, corner_radius=12)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold")
                     ).pack(anchor="w", padx=16, pady=(12, 4))
        return card

    #  add a labelled drop-down to a card and return the combo box
    def _combo(self, parent, label, values, default):
        rowf = ctk.CTkFrame(parent, fg_color="transparent")
        rowf.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(rowf, text=label, width=80, anchor="w").pack(side="left")
        combo = ctk.CTkComboBox(rowf, values=values)
        combo.set(default)
        combo.pack(side="left", fill="x", expand=True)
        return combo

    # Build the criteria screen and all of its GUI controls
    def build_criteria_screen(self, parent):
        screen = ctk.CTkFrame(parent, fg_color="transparent")

        header = ctk.CTkFrame(screen, height=70)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="Tide Tracker", font=ctk.CTkFont(size=24, weight="bold")
                     ).pack(side="left", padx=24, pady=16)
        # lbl_ prefix marks a label control
        # this one shows hints and validation messages
        self.lbl_status = ctk.CTkLabel(header, text="Pick an activity, set your criteria, then Show calendar.",
                                       text_color="#8b929c", font=ctk.CTkFont(size=13))
        self.lbl_status.pack(side="left", pady=16)

        body = ctk.CTkFrame(screen, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=16)
        body.grid_columnconfigure((0, 1), weight=1)

        # Activity card with the two activity buttons
        activity = self._card(body, "Activity")
        activity.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        row = ctk.CTkFrame(activity, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 12))
        self.btn_surf = ctk.CTkButton(row, text="Surf", height=46,
                                      fg_color=COLOUR_INACTIVE, hover_color=COLOUR_SURF,
                                      font=ctk.CTkFont(size=15, weight="bold"),
                                      # command needs a function to call WHEN the button is clicked
                                      # lambda makes a tiny no-name function that, when clicked, calls on_activity_select("surf")
                                      # Writing on_activity_select("surf")
                                      # lambda also lets me pass the "surf"/"swim" argument
                                      command=lambda: self.on_activity_select("surf"))

        self.btn_swim = ctk.CTkButton(row, text="Swim", height=46,
                                      fg_color=COLOUR_INACTIVE, hover_color=COLOUR_SWIM,
                                      font=ctk.CTkFont(size=15, weight="bold"),
                                      command=lambda: self.on_activity_select("swim"))
        self.btn_surf.pack(side="left", expand=True, fill="x", padx=(0, 8))
        self.btn_swim.pack(side="left", expand=True, fill="x", padx=(8, 0))

        # When card, year and month combo boxes
        when = self._card(body, "When")
        when.grid(row=1, column=0, sticky="ew", padx=(0, 7), pady=(0, 14))
        self.cmb_year = self._combo(when, "Year", YEARS, YEARS[0])
        self.cmb_month = self._combo(when, "Month", MONTHS, "March")

        # Tide card, minimum and maximum height combo boxes
        tide = self._card(body, "Tide")
        tide.grid(row=1, column=1, sticky="ew", padx=(7, 0), pady=(0, 14))
        self.cmb_tide_min = self._combo(tide, "Minimum", TIDES, "0.8")
        self.cmb_tide_max = self._combo(tide, "Maximum", TIDES, "1.6")

        # Time window card
        time_card = self._card(body, "Time window")
        time_card.grid(row=2, column=0, sticky="ew", padx=(0, 7), pady=(0, 14))
        self.cmb_time_from = self._combo(time_card, "From", TIMES, "06:00")
        self.cmb_time_to = self._combo(time_card, "To", TIMES, "18:00")

        # Daylight conditions card
        # four checkboxes backed by BooleanVars
        light = self._card(body, "Daylight conditions")
        light.grid(row=2, column=1, sticky="ew", padx=(7, 0), pady=(0, 14))
        self.var_sunrise = ctk.BooleanVar()
        self.var_sunset = ctk.BooleanVar()
        self.var_after_sunrise = ctk.BooleanVar()
        self.var_before_sunset = ctk.BooleanVar()
        # This loops over a list of pairs
        # Each time round, Python unpacks the pair into text and var
        # one CTkCheckBox is built per line without repeating the code
        for text, var in [("At sunrise", self.var_sunrise),
                          ("At sunset", self.var_sunset),
                          ("After sunrise", self.var_after_sunrise),
                          ("Before sunset", self.var_before_sunset)]:
            ctk.CTkCheckBox(light, text=text, variable=var).pack(anchor="w", padx=16, pady=4)
        ctk.CTkLabel(light, text="").pack(pady=2)

        # Action buttons
        actions = ctk.CTkFrame(body, fg_color="transparent")
        actions.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        actions.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkButton(actions, text="Save criteria", height=44,
                      fg_color="transparent", border_width=2,
                      command=self.on_save_criteria).grid(row=0, column=0, sticky="ew", padx=4)
        self.btn_load = ctk.CTkButton(actions, text="Load criteria", height=44,
                                      fg_color="transparent", border_width=2,
                                      command=self.on_load_criteria)
        self.btn_load.grid(row=0, column=1, sticky="ew", padx=4)
        ctk.CTkButton(actions, text="Show calendar", height=44,
                      font=ctk.CTkFont(weight="bold"),
                      command=self.on_show_calendar).grid(row=0, column=2, sticky="ew", padx=4)
        return screen

# I haven't done the Save or load criteria part fully yet
    # this is so its absence doesn't mess up the rest of my code when it runs
    # def on_save_placeholder(self):
    #     self.lbl_status.configure(text="Save criteria: not finished yet")
    #
    # def on_load_placeholder(self):
    #     self.lbl_status.configure(text="Load criteria: not finished yet")

        # Added on 22/06/26
        # Save criteria handler, reads the screen, validates, then saves

    def on_save_criteria(self):
        criteria = UserCriteria()
        criteria.read_from_screen(self)
        problems = criteria.validate()  # never save invalid criteria
        if problems:
            self.lbl_status.configure(text="   ".join(problems))
            return
        self.lbl_status.configure(text=criteria.save())

        # Added on 22/06/26
        # oad criteria handler, loads the file for the chosen activity and fills the screen
    def on_load_criteria(self):
        if self.current_activity is None:  # need an activity to know which file
            self.lbl_status.configure(text="Choose Surf or Swim first, then Load criteria.")
            return
        criteria = UserCriteria()
        criteria.activity = self.current_activity
        if criteria.load():  # load() returns True or False
            criteria.populate_widgets(self)
            self.active_criteria = criteria
            self.lbl_status.configure(text="Criteria loaded for " + self.current_activity)
        else:
            self.lbl_status.configure(text="No saved criteria found for " + self.current_activity)

    # Load both data files once
    # Returns True if both are available
    def _load_sources(self):
        if self._tide_records is None:
            self._tide_records = load_tide_data(TIDE_FILE)
        if self._daylight_records is None:
            self._daylight_records = load_daylight_data(DAYLIGHT_FILE)
        # existence check on the data sources
        return len(self._tide_records) > 0 and len(self._daylight_records) > 0

    # The main flow when "Show calendar" is pressed
    def on_show_calendar(self):
        # read the criteria and convert types
        criteria = UserCriteria()
        criteria.read_from_screen(self)
        # validate if there are problems, show them and stay on this screen
        problems = criteria.validate()
        if problems:
            self.lbl_status.configure(text="   ".join(problems))
            return
        # make sure the data files are present
        if not self._load_sources():
            self.lbl_status.configure(
                text="Could not read the data files, check the files")
            return
        self.lbl_status.configure(text="")
        self.active_criteria = criteria

        # restrict to the chosen year, collate, then filter and rate
        year = criteria.selected_year
        month = criteria.selected_month
        kept_tides, kept_daylight = restrict_to_year(self._tide_records, self._daylight_records, year)
        unified_data = collate_data(kept_tides, kept_daylight)
        af = ActivityFilter()
        match_days = af.filter_and_rate(unified_data, criteria)
        self.active_filter = af
        self.current_match_days = match_days

        # completeness check, warning if no day matched
        if not match_days:
            self.lbl_status.configure(text="No matching days for these criteria - try widening them.")

        # draw the calendar and switch to it
        self.lbl_month_title.configure(text=MONTHS[month - 1] + " " + str(year))
        self._render_calendar(year, month, match_days, af)
        self.show_screen("calendar_screen")

    # Build the calendar screen
    def build_calendar_screen(self, parent):
        screen = ctk.CTkFrame(parent, fg_color="transparent")

        topbar = ctk.CTkFrame(screen)
        topbar.pack(fill="x", padx=20, pady=(16, 4))
        self.lbl_month_title = ctk.CTkLabel(topbar, text="March 2026",
                                            font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_month_title.pack(side="left", padx=8)
        ctk.CTkButton(topbar, text="Edit criteria", width=120,
                      command=lambda: self.show_screen("criteria_screen")).pack(side="right", padx=8)

        head = ctk.CTkFrame(screen, fg_color="transparent")
        head.pack(fill="x", padx=20, pady=(8, 4))
        for i, weekday in enumerate(WEEKDAYS):    # iteration to build the 7 column headers
            head.grid_columnconfigure(i, weight=1, uniform="day")
            ctk.CTkLabel(head, text=weekday, text_color="#8b929c",
                         font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=i, sticky="ew")

        self.calendar_frame = ctk.CTkFrame(screen, fg_color="transparent")
        self.calendar_frame.pack(fill="both", expand=True, padx=20)

        self._build_legend(screen)
        return screen

    # Draw the month grid from the filtered results
    def _render_calendar(self, year, month, match_days, af):
        for widget in self.calendar_frame.winfo_children():   # iteration: clear old cells
            widget.destroy()
        for i in range(7):
            self.calendar_frame.grid_columnconfigure(i, weight=1, uniform="cell")
        for i in range(6):
            self.calendar_frame.grid_rowconfigure(i, weight=1, uniform="cellr")

        cal = calmod.Calendar(firstweekday=0)   # weeks start on Monday
        # monthdayscalendar gives the month as weeks
        # a 0 means no day in the cell
        # enumerate gives a counter with each item
        # r is the week's row number, c is the column
        # The outer loop walks down the weeks (rows), the inner loop walks across the 7 days (columns)
        for r, week in enumerate(cal.monthdayscalendar(year, month)):     # nested iteration
            for c, day in enumerate(week):
                if day == 0:
                    continue
                date_str = "{:02d}/{:02d}/{}".format(day, month, year)
                if date_str in match_days:                # selecting matched vs not matched
                    info = match_days[date_str]
                    colour, symbol = af.indicator_for(info)
                    detail = "{}m  {}".format(info["tide_height"], info["tide_time"])
                    self._draw_cell(r, c, day, colour, symbol, detail)
                else:
                    self._draw_cell(r, c, day, COLOUR_NO_MATCH, "X", "")

    # Draw one calendar cell
    def _draw_cell(self, row, col, day, colour, symbol, detail):
        cell = ctk.CTkFrame(self.calendar_frame, fg_color=colour, corner_radius=10)
        cell.grid(row=row, column=col, sticky="nsew", padx=3, pady=3)
        cell.grid_propagate(False)
        ctk.CTkLabel(cell, text=str(day), text_color="white",
                     font=ctk.CTkFont(size=14, weight="bold")).place(x=8, y=4)
        if symbol:
            ctk.CTkLabel(cell, text=symbol, text_color="white",
                         font=ctk.CTkFont(size=22)).place(relx=0.5, rely=0.42, anchor="center")
        if detail:
            ctk.CTkLabel(cell, text=detail, text_color="white",
                         font=ctk.CTkFont(size=10)).place(relx=0.5, rely=0.82, anchor="center")

    # Draw the colour key
    def _build_legend(self, parent):
        legend = ctk.CTkFrame(parent, fg_color="transparent")
        legend.pack(fill="x", padx=20, pady=12)
        items = [(COLOUR_SURF, "Surf"), (COLOUR_SWIM, "Swim"),
                 (COLOUR_BOTH, "Both"), (COLOUR_SURF, STAR + " Ideal"),
                 (COLOUR_NO_MATCH, "X No match")]
        for colour, label in items:           # iteration to build each legend part
            chip = ctk.CTkFrame(legend, fg_color="transparent")
            chip.pack(side="left", padx=10)
            ctk.CTkLabel(chip, text="   ", fg_color=colour, corner_radius=4).pack(side="left", padx=(0, 6))
            ctk.CTkLabel(chip, text=label, text_color="#c4c9d2").pack(side="left")

    # Record the chosen activity and recolour the buttons
    def on_activity_select(self, activity):
        self.current_activity = activity
        if activity == "surf":
            self.btn_surf.configure(fg_color=COLOUR_SURF)
            self.btn_swim.configure(fg_color=COLOUR_INACTIVE)
            self.btn_load.configure(fg_color=COLOUR_SURF)
        else:
            self.btn_swim.configure(fg_color=COLOUR_SWIM)
            self.btn_surf.configure(fg_color=COLOUR_INACTIVE)
            self.btn_load.configure(fg_color=COLOUR_SWIM)

#  create the app object and start the GUI event loop
if __name__ == "__main__":
    TideTrackerApp().mainloop()

