# TideTracker
# a Streamlit app version of a school project that reads tide-height and sunrise/sunset
# data for 2026, then lets the user filter by activity surf or swim, tide
# height, time window, and daylight conditions to see which days match on
# a calendar

# Frankie-Belle Taylor 09/07/26
# Dervived from previous versions of my TideTracker app project 

# WHAT IT DOES
# reads two data files, one with tide heights, one with sunrise and sunset times
# lets the user pick an activity, surf or swim
# lets the user set filters, a date, a tide height range, a time window, and daylight conditions
# checks every day in the chosen month against those filters
# shows a calendar where each day is marked as a match or not, with a star for the best days
# lets the user save their filters to a file and load them back later

# How the screen updates in Streamlit version
# streamlit has no persistent window, it reruns this whole file top to bottom on every click
# st.session_state is used to remember values between those reruns, such as which activity is picked
# each widget, like a dropdown or checkbox, is given a key, and its value lives in st.session_state under that key
# st.rerun() is called after certain actions to force an immediate redraw, such as switching screens

import csv
import os
import calendar as calmod
from datetime import datetime
import json
import streamlit as st

# GLOBAL CONSTANTS (UPPER_SNAKE_CASE)
COLOUR_SURF     = "#2e8b57"   # green
COLOUR_SWIM     = "#2f6fed"   # blue
COLOUR_BOTH     = "#8a4fff"   # purple
COLOUR_IDEAL    = "#f5b301"   # gold (kept, but ideal days are shown with a star, not gold)
COLOUR_NO_MATCH = "#33373e"   # grey
COLOUR_INACTIVE = "#555a63"   # inactive button grey

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

TIDES = ["{:.1f}".format(x / 10) for x in range(0, 31, 2)]
TIMES = ["{:02d}:00".format(h) for h in range(0, 24)]
YEARS = ["2026"]

STAR = "\u2605"

TIDE_FILE     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Point-Lonsdale_60730_2026.csv")
DAYLIGHT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Aireys_Inlet_Sunrise_and_Sunset.csv")


def parse_date(date_str):
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(str(date_str).strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError("Unrecognised date format: " + str(date_str))


def parse_time(time_str):
    s = str(time_str).strip()
    for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p"):
        try:
            return datetime.strptime(s, fmt).time()
        except ValueError:
            continue
    raise ValueError("Unrecognised time format: " + s)


def extract_year(date_str):
    return parse_date(date_str).year


def extract_month(date_str):
    return parse_date(date_str).month


def convert_to_decimal(value):
    return float(value)


def _minutes(t):
    return t.hour * 60 + t.minute


def find_closest_tide(tide_records, target_time):
    return min(
        tide_records,
        key=lambda rec: abs(_minutes(parse_time(rec["time"])) - _minutes(target_time)),
    )


def load_tide_data(file_path):
    if not os.path.exists(file_path):
        print("Tide file not found: " + file_path)
        return []

    readings = []
    with open(file_path, newline="") as f:
        for raw_line in f:
            line = raw_line.strip()
            if line == "" or line.startswith("#"):
                continue
            stamp, value = line.split(",")
            date_part = stamp[0:10]
            time_part = stamp[11:16]
            year_txt, month_txt, day_txt = date_part.split("-")
            iso_to_local = day_txt + "/" + month_txt + "/" + year_txt
            readings.append((iso_to_local, time_part, float(value)))

    raw_events = []
    for i in range(1, len(readings) - 1):
        prev_height = readings[i - 1][2]
        curr_height = readings[i][2]
        next_height = readings[i + 1][2]
        is_high = curr_height > prev_height and curr_height >= next_height
        is_low = curr_height < prev_height and curr_height <= next_height
        if is_high or is_low:
            date_str, time_str, height = readings[i]
            raw_events.append({
                "date": date_str,
                "time": time_str,
                "tide_height": round(height, 2),
                "kind": "high" if is_high else "low",
            })

    tide_records = []
    for event in raw_events:
        if tide_records and tide_records[-1]["kind"] == event["kind"]:
            last = tide_records[-1]
            keep_new = (event["kind"] == "high" and event["tide_height"] > last["tide_height"]) or \
                       (event["kind"] == "low" and event["tide_height"] < last["tide_height"])
            if keep_new:
                tide_records[-1] = event
        else:
            tide_records.append(event)
    return tide_records


def load_daylight_data(file_path):
    if not os.path.exists(file_path):
        print("Daylight file not found: " + file_path)
        return []

    daylight_records = []
    with open(file_path, newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            rise = datetime.strptime(row["rise_date"], "%Y-%m-%d %H:%M:%S")
            sett = datetime.strptime(row["set_date"], "%Y-%m-%d %H:%M:%S")
            daylight_records.append({
                "date": rise.strftime("%d/%m/%Y"),
                "sunrise_time": rise.strftime("%H:%M"),
                "sunset_time": sett.strftime("%H:%M"),
            })
    return daylight_records


def restrict_to_year(tide_records, daylight_records, selected_year):
    kept_tides = [r for r in tide_records if extract_year(r["date"]) == selected_year]
    kept_daylight = [r for r in daylight_records if extract_year(r["date"]) == selected_year]
    return kept_tides, kept_daylight


def collate_data(tide_records, daylight_records):
    unified_data = {}
    daylight_lookup = {r["date"]: r for r in daylight_records}
    for tide in tide_records:
        date_str = tide["date"]
        if date_str not in daylight_lookup:
            continue
        if date_str not in unified_data:
            unified_data[date_str] = {
                "date": date_str,
                "sunrise_time": daylight_lookup[date_str]["sunrise_time"],
                "sunset_time": daylight_lookup[date_str]["sunset_time"],
                "tide_records": [],
            }
        unified_data[date_str]["tide_records"].append(
            {"time": tide["time"], "tide_height": tide["tide_height"]}
        )
    return unified_data


class UserCriteria:
    def __init__(self):
        self.activity = None
        self.selected_year = None
        self.selected_month = None
        self.tide_min = None
        self.tide_max = None
        self.time_from = None
        self.time_to = None
        self.is_sunrise = False
        self.is_sunset = False
        self.is_after_sunrise = False
        self.is_before_sunset = False

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
        if name in MONTHS:
            return MONTHS.index(name) + 1
        return None

    # Copy the current widget values into this object, converting types
    # and doing the safety checks above along the way
          
    def read_from_values(self, activity, year_text, month_text, tide_min_text, tide_max_text,
                          time_from_text, time_to_text, is_sunrise, is_sunset,
                          is_after_sunrise, is_before_sunset):
        self.activity = activity
        self.selected_year = self._safe_int(year_text)
        self.selected_month = self._safe_month(month_text)
        self.tide_min = self._safe_float(tide_min_text)
        self.tide_max = self._safe_float(tide_max_text)
        self.time_from = self._safe_time(time_from_text)
        self.time_to = self._safe_time(time_to_text)
        self.is_sunrise = is_sunrise
        self.is_sunset = is_sunset
        self.is_after_sunrise = is_after_sunrise
        self.is_before_sunset = is_before_sunset

    def validate(self):
        problems = []
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

        if problems:
            return problems

        if self.activity not in ("surf", "swim"):
            problems.append("Activity must be 'surf' or 'swim'.")

        if not (1 <= self.selected_month <= 12):
            problems.append("Month must be between 1 and 12.")
        if not (0.0 <= self.tide_min <= 3.0) or not (0.0 <= self.tide_max <= 3.0):
            problems.append("Tide heights must be between 0.0 and 3.0 .")

        if self.tide_min > self.tide_max:
            problems.append("Minimum tide cannot be greater than maximum tide.")
        if self.time_from >= self.time_to:
            problems.append("From time must be earlier than To time.")
        if self.is_sunrise and self.is_sunset:
            problems.append("A tide cannot be at sunrise and at sunset at the same time.")

        return problems

    def save(self):
        file_name = self.activity + "_criteria_saved.json"
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
        try:
            with open(file_name, "w") as f:
                json.dump(data, f, indent=2)
            return "Criteria saved to " + file_name
        except OSError:
            return "Could not save criteria"

    def load(self):
        file_name = self.activity + "_criteria_saved.json"
        if not os.path.exists(file_name):
            return False
        with open(file_name) as f:
            data = json.load(f)
        self.activity = data["activity"]
        self.selected_year = data["selected_year"]
        self.selected_month = data["selected_month"]
        self.tide_min = data["tide_min"]
        self.tide_max = data["tide_max"]
        self.time_from = parse_time(data["time_from"])
        self.time_to = parse_time(data["time_to"])
        self.is_sunrise = data["is_sunrise"]
        self.is_sunset = data["is_sunset"]
        self.is_after_sunrise = data["is_after_sunrise"]
        self.is_before_sunset = data["is_before_sunset"]
        return True

    # Push the stored values back into the widgets by writing into
    # st.session_state under the same keys the widgets use
          # Streamlit widgets pick up their value from session_state on the next rerun

    def populate_widgets(self):
        st.session_state.current_activity = self.activity
        st.session_state.cmb_year = str(self.selected_year)
        st.session_state.cmb_month = MONTHS[self.selected_month - 1]
        st.session_state.cmb_tide_min = "{:.1f}".format(self.tide_min)
        st.session_state.cmb_tide_max = "{:.1f}".format(self.tide_max)
        st.session_state.cmb_time_from = self.time_from.strftime("%H:%M")
        st.session_state.cmb_time_to = self.time_to.strftime("%H:%M")
        st.session_state.var_sunrise = self.is_sunrise
        st.session_state.var_sunset = self.is_sunset
        st.session_state.var_after_sunrise = self.is_after_sunrise
        st.session_state.var_before_sunset = self.is_before_sunset


class ActivityFilter:
    def __init__(self):
        self.criteria = None
        self.match_days = {}

    def filter_and_rate(self, unified_data, criteria):
        self.criteria = criteria
        results = {}
        for date_str, day in unified_data.items():
            if extract_month(date_str) != criteria.selected_month:
                continue
            matched = []
            for tide in day["tide_records"]:
                tide_time = parse_time(tide["time"])
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
                if criteria.is_after_sunrise and tide_time < sunrise:
                    continue
                if criteria.is_before_sunset and tide_time > sunset:
                    continue
                if criteria.is_sunrise and tide_time != sunrise:
                    continue
                if criteria.is_sunset and tide_time != sunset:
                    continue
                matched.append(tide)
            if matched:
                results[date_str] = {
                    "tide_records": matched,
                    "sunrise_time": day["sunrise_time"],
                    "sunset_time": day["sunset_time"],
                }

        self.match_days = {}
        tide_range = criteria.tide_max - criteria.tide_min
        ideal_threshold = criteria.tide_max - (tide_range * 0.25)
        for date_str, day in results.items():
            best = find_closest_tide(day["tide_records"], criteria.time_from)
            self.match_days[date_str] = {
                "activity": criteria.activity,
                "tide_height": best["tide_height"],
                "tide_time": best["time"],
                "is_ideal": best["tide_height"] >= ideal_threshold,
            }
        return self.match_days

    def indicator_for(self, info):
        colour = COLOUR_SURF if self.criteria.activity == "surf" else COLOUR_SWIM
        symbol = STAR if info["is_ideal"] else ""
        return colour, symbol

# CLASS TideTrackerApp
# The main app
# Builds the two screens (criteria and calendar), holds
# program's shared state in st.session_state, and reacts to button presses

class TideTrackerApp:
    def __init__(self):
        # state for the whole app, kept in st.session_state so it lasts
        # from one rerun to the next
              # because Streamlit reruns the whole script on every interaction
              
        defaults = {
            "current_activity": None,
            "current_screen": "criteria_screen",
            "active_criteria": None,
            "current_match_days": None,
            "active_filter": None,
            "status_text": "Data sourced from Victoria (Australia) for Point Lonsdale. 
            Pick an activity, set your criteria, then Show calendar.",
            "pending_load": None,
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

        # loaded data, so the large tide file is only read once per run
        self._tide_records = None
        self._daylight_records = None

    # Switch which screen is currently shown.
    def show_screen(self, screen_name):
        st.session_state.current_screen = screen_name

    # Build the criteria screen and all of its controls
    def build_criteria_screen(self):
        if st.session_state.pending_load is not None:
            st.session_state.pending_load.populate_widgets()
            st.session_state.pending_load = None
                  
        header_col, status_col = st.columns([2, 3])
        header_col.title("Tide Tracker")
        status_col.write("")
        status_col.caption(st.session_state.status_text)

        # Activity card with the two activity buttons
        st.subheader("Activity")
        row = st.columns(2)
        surf_type = "primary" if st.session_state.current_activity == "surf" else "secondary"
        swim_type = "primary" if st.session_state.current_activity == "swim" else "secondary"
        if row[0].button("Surf", use_container_width=True, type=surf_type):
            self.on_activity_select("surf")
        if row[1].button("Swim", use_container_width=True, type=swim_type):
            self.on_activity_select("swim")

        # When card and Tide card, side by side
        when_col, tide_col = st.columns(2)
        with when_col:
            st.subheader("When")
            st.selectbox("Year", YEARS, key="cmb_year")
            st.selectbox("Month", MONTHS, index=2, key="cmb_month")
        with tide_col:
            st.subheader("Tide")
            st.selectbox("Minimum (m) ", TIDES, index=TIDES.index("0.8"), key="cmb_tide_min")
            st.selectbox("Maximum (m) ", TIDES, index=TIDES.index("1.6"), key="cmb_tide_max")

        # Time window card and Daylight conditions card
        time_col, light_col = st.columns(2)
        with time_col:
            st.subheader("Time window")
            st.selectbox("From", TIMES, index=TIMES.index("06:00"), key="cmb_time_from")
            st.selectbox("To", TIMES, index=TIMES.index("18:00"), key="cmb_time_to")
        with light_col:
            st.subheader("Daylight conditions")
            st.checkbox("At sunrise", key="var_sunrise")
            st.checkbox("At sunset", key="var_sunset")
            st.checkbox("After sunrise", key="var_after_sunrise")
            st.checkbox("Before sunset", key="var_before_sunset")

        # Action buttons
        actions = st.columns(3)
        if actions[0].button("Save criteria", use_container_width=True):
            self.on_save_criteria()
        if actions[1].button("Load criteria", use_container_width=True):
            self.on_load_criteria()
        if actions[2].button("Show calendar", use_container_width=True, type="primary"):
            self.on_show_calendar()

    # Record which activity is selected, the button colouring above reads
    # current_activity back out on the next draw to show which is active
          
    def on_activity_select(self, activity):
        st.session_state.current_activity = activity

    # Gather the current widget values from session_state and build a
    # UserCriteria object from them
          
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

    # Save criteria handler
          # validates first, never saves invalid criteria
          
    def on_save_criteria(self):
        criteria = self._read_criteria_from_widgets()
        problems = criteria.validate()
        if problems:
            st.session_state.status_text = "   ".join(problems)
            return
        st.session_state.status_text = criteria.save()

    # Load criteria handler
          # loads the file for the chosen activity and
    # fills the widgets with the saved values
          
    def on_load_criteria(self):
        if st.session_state.current_activity is None:
            st.session_state.status_text = "Choose Surf or Swim first, then Load criteria."
            return
        criteria = UserCriteria()
        criteria.activity = st.session_state.current_activity
        if criteria.load():
            st.session_state.pending_load = criteria
            st.session_state.status_text = "Criteria loaded for " + st.session_state.current_activity
            st.rerun()   # refresh so the reloaded widget values show immediately
        else:
            st.session_state.status_text = "No saved criteria found for " + st.session_state.current_activity

    # Load both data files once per run, so the large tide file isn't
    # re-read on every button press
          # Returns True if both are available 
          
    def _load_sources(self):
        if self._tide_records is None:
            self._tide_records = load_tide_data(TIDE_FILE)
        if self._daylight_records is None:
            self._daylight_records = load_daylight_data(DAYLIGHT_FILE)
        return len(self._tide_records) > 0 and len(self._daylight_records) > 0

    # The main flow when "Show calendar" is pressed validate the
    # criteria, load and filter the data, then switch to the calendar
    # screen
    def on_show_calendar(self):
        criteria = self._read_criteria_from_widgets()
        problems = criteria.validate()
        if problems:
            st.session_state.status_text = "   ".join(problems)
            return
        if not self._load_sources():
            st.session_state.status_text = "Could not read the data files, check the files"
            return
        st.session_state.status_text = ""
        st.session_state.active_criteria = criteria

        year = criteria.selected_year
        month = criteria.selected_month
        kept_tides, kept_daylight = restrict_to_year(self._tide_records, self._daylight_records, year)
        unified_data = collate_data(kept_tides, kept_daylight)
        af = ActivityFilter()
        match_days = af.filter_and_rate(unified_data, criteria)
        st.session_state.active_filter = af
        st.session_state.current_match_days = match_days

        if not match_days:
            st.session_state.status_text = "No matching days for these criteria - try widening them."

        self.show_screen("calendar_screen")
        st.rerun()   # redraw immediately so the calendar screen shows right away

    # Build the calendar screen
          
    def build_calendar_screen(self):
        criteria = st.session_state.active_criteria
        af = st.session_state.active_filter
        match_days = st.session_state.current_match_days

        topbar = st.columns([4, 1])
        topbar[0].subheader(MONTHS[criteria.selected_month - 1] + " " + str(criteria.selected_year))
        if topbar[1].button("Edit criteria"):
            self.show_screen("criteria_screen")
            st.rerun()

        head = st.columns(7)
        for i, weekday in enumerate(WEEKDAYS):
            head[i].markdown(f"**{weekday}**")

        self._render_calendar(criteria.selected_year, criteria.selected_month, match_days, af)
        self._build_legend()

    # Draw the month grid from the filtered results, week by week
          
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
                    detail = "{}m  {}".format(info["tide_height"], info["tide_time"])
                    self._draw_cell(row_cols[c], day, colour, symbol, detail)
                else:
                    self._draw_cell(row_cols[c], day, COLOUR_NO_MATCH, "X", "")

    # Draw one calendar cell
          # day number, a coloured badge showing the activity, and the matching tide detail underneath 
          
    def _draw_cell(self, column, day, colour, symbol, detail):
        with column.container(border=True):
            st.markdown(f"**{day}**")
            if colour == COLOUR_NO_MATCH:
                st.badge("No match", color="gray")
            else:
                activity_label = "Surf" if colour == COLOUR_SURF else "Swim"
                badge_colour = "green" if colour == COLOUR_SURF else "blue"
                if symbol:   # ideal day - use a distinct badge colour
                    st.badge(activity_label + " " + STAR, color="orange")
                else:
                    st.badge(activity_label, color=badge_colour)
            if detail:
                st.caption(detail)

    # Draw the colour key
    def _build_legend(self):
        st.write("")
        legend = st.columns(5)
        legend[0].badge("Surf", color="green")
        legend[1].badge("Swim", color="blue")
        legend[3].badge(STAR + " Ideal", color="orange")
        legend[4].badge("No match", color="gray")

    # Decide which screen to draw on this rerun.
    def run(self):
        if st.session_state.current_screen == "criteria_screen":
            self.build_criteria_screen()
        else:
            self.build_calendar_screen()


# create the app object and run it
if __name__ == "__main__":
    st.set_page_config(page_title="TideTracker", layout="wide")
    TideTrackerApp().run()
