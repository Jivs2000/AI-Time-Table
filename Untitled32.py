#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import random

# Function to generate the timetable
def generate_timetable(teachers_data, num_periods=5):
    """
    Generates timetables for two sections based on teacher availability.

    Args:
        teachers_data (dict): A dictionary containing teacher information for each section.
                              Example: {"Section 1": [{"name": "Alice", "days": ["Monday"]}], ...}
        num_periods (int): The number of periods per day.

    Returns:
        dict: A dictionary containing pandas DataFrames for each section's timetable.
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    sections = ["Section 1", "Section 2"]

    # Initialize empty DataFrames for each section's timetable
    timetables = {section: pd.DataFrame(index=days, columns=[f"Period {i+1}" for i in range(num_periods)]) for section in sections}

    # Prepare a dictionary to quickly look up teachers available on specific days for each section
    teachers_available_per_day_section = {section: {day: [] for day in days} for section in sections}
    for section_name, teachers_list in teachers_data.items():
        for teacher_info in teachers_list:
            name = teacher_info['name']
            available_days = teacher_info['days']
            for day in available_days:
                if day in teachers_available_per_day_section[section_name]:
                    teachers_available_per_day_section[section_name][day].append(name)

    # Iterate through each day and period to assign teachers
    for day in days:
        # This set tracks teachers already assigned in the *current period* across both sections
        # to prevent a teacher from being in two places at once.
        teachers_assigned_in_current_period = set()

        for period_idx in range(num_periods):
            # --- Assign for Section 1 ---
            assigned_s1 = False
            # Get teachers available for Section 1 on this specific day
            available_s1_teachers = list(teachers_available_per_day_section["Section 1"][day])
            random.shuffle(available_s1_teachers) # Shuffle to randomize assignment preference

            for teacher in available_s1_teachers:
                # Check if the teacher is not already assigned in this period (across both sections)
                if teacher not in teachers_assigned_in_current_period:
                    timetables["Section 1"].loc[day, f"Period {period_idx+1}"] = teacher
                    teachers_assigned_in_current_period.add(teacher) # Mark teacher as busy for this period
                    assigned_s1 = True
                    break
            if not assigned_s1:
                timetables["Section 1"].loc[day, f"Period {period_idx+1}"] = "Free" # No suitable teacher found

            # --- Assign for Section 2 ---
            assigned_s2 = False
            # Get teachers available for Section 2 on this specific day
            available_s2_teachers = list(teachers_available_per_day_section["Section 2"][day])
            random.shuffle(available_s2_teachers) # Shuffle to randomize assignment preference

            for teacher in available_s2_teachers:
                # Check if the teacher is not already assigned in this period (across both sections)
                if teacher not in teachers_assigned_in_current_period:
                    timetables["Section 2"].loc[day, f"Period {period_idx+1}"] = teacher
                    teachers_assigned_in_current_period.add(teacher) # Mark teacher as busy for this period
                    assigned_s2 = True
                    break
            if not assigned_s2:
                timetables["Section 2"].loc[day, f"Period {period_idx+1}"] = "Free" # No suitable teacher found

    return timetables

# --- Streamlit UI ---
st.set_page_config(layout="wide") # Use wide layout for better display of tables
st.title("College Timetable Generator 🗓️")
st.markdown("Enter teacher details and their availability for two sections to generate a basic timetable.")

# Initialize session state variables to store teacher data
if 'teachers_section1' not in st.session_state:
    st.session_state.teachers_section1 = []
if 'teachers_section2' not in st.session_state:
    st.session_state.teachers_section2 = []

days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

st.sidebar.header("Add Teachers and Availability")

# --- Section 1 Teacher Input ---
st.sidebar.subheader("Section 1 Teachers")
# Loop through the list of teachers in session state to display input fields
for i, teacher in enumerate(st.session_state.teachers_section1):
    with st.sidebar.expander(f"Teacher {i+1} (Section 1)"):
        # Use unique keys for each widget to prevent issues with dynamic lists
        teacher['name'] = st.text_input(f"Name (S1, T{i+1})", value=teacher.get('name', ''), key=f"name_s1_{i}")
        teacher['days'] = st.multiselect(f"Available Days (S1, T{i+1})", days_of_week, default=teacher.get('days', []), key=f"days_s1_{i}")
# Button to add a new teacher input row for Section 1
if st.sidebar.button("Add Teacher for Section 1"):
    st.session_state.teachers_section1.append({'name': '', 'days': []})

st.sidebar.markdown("---") # Separator

# --- Section 2 Teacher Input ---
st.sidebar.subheader("Section 2 Teachers")
# Loop through the list of teachers in session state to display input fields
for i, teacher in enumerate(st.session_state.teachers_section2):
    with st.sidebar.expander(f"Teacher {i+1} (Section 2)"):
        # Use unique keys for each widget
        teacher['name'] = st.text_input(f"Name (S2, T{i+1})", value=teacher.get('name', ''), key=f"name_s2_{i}")
        teacher['days'] = st.multiselect(f"Available Days (S2, T{i+1})", days_of_week, default=teacher.get('days', []), key=f"days_s2_{i}")
# Button to add a new teacher input row for Section 2
if st.sidebar.button("Add Teacher for Section 2"):
    st.session_state.teachers_section2.append({'name': '', 'days': []})

st.sidebar.markdown("---") # Separator

# --- Generate Timetables Button ---
if st.sidebar.button("Generate Timetables 🚀"):
    # Filter out any teacher entries where the name is empty
    valid_teachers_s1 = [t for t in st.session_state.teachers_section1 if t['name'].strip() != '']
    valid_teachers_s2 = [t for t in st.session_state.teachers_section2 if t['name'].strip() != '']

    if not valid_teachers_s1 and not valid_teachers_s2:
        st.error("Please add at least one teacher for either section to generate timetables.")
    else:
        # Combine valid teacher data for the generation function
        teacher_data_for_generation = {
            "Section 1": valid_teachers_s1,
            "Section 2": valid_teachers_s2
        }
        # Call the timetable generation function
        timetables = generate_timetable(teacher_data_for_generation)

        # Display the generated timetables
        st.header("Timetable for Section 1")
        st.dataframe(timetables["Section 1"], use_container_width=True) # Display DataFrame with full width

        st.header("Timetable for Section 2")
        st.dataframe(timetables["Section 2"], use_container_width=True) # Display DataFrame with full width

        st.success("Timetables generated successfully! ✨")
