import streamlit as st
from datetime import datetime, timedelta, date
import json
import os
import uuid
import calendar
from streamlit_autorefresh import st_autorefresh

# Dark Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: #1a1a1a;
        color: #ffffff;
    }
    
    .compact-card {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        background: #2d2d2d;
        border-left: 4px solid;
    }
    
    .corner-timer {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #2d2d2d;
        padding: 1rem 2rem;
        border-radius: 8px;
        color: #ffffff;
        border: 1px solid #404040;
        z-index: 999;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    
    .progress-container {
        margin: 1rem 0;
        padding: 0.5rem;
    }
    
    .calendar-day {
        width: 100% !important;
        height: 60px !important;
        margin: 2px 0 !important;
    }
    
    .reminder-item {
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid;
        background: #2d2d2d;
        border-radius: 4px;
    }
    
    .notes-container {
        border-left: 4px solid;
        padding: 1rem;
        margin: 1rem 0;
        background: #2d2d2d;
        border-radius: 8px;
    }
    
    .notes-preview {
        padding: 1rem;
        background: #1a1a1a;
        border-radius: 8px;
        border: 1px solid #404040;
        margin: 1rem 0;
        color: #ffffff;
    }
    
    .notes-editor {
        margin: 1rem 0;
    }
    
    .notes-toolbar {
        margin-bottom: 1rem;
    }
    
    .formatting-help {
        font-size: 0.8em;
        color: #a0a0a0;
        padding: 0.5rem;
        background: #2d2d2d;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .upcoming-event {
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        background: #2d2d2d;
    }
    
    .stTextInput input, .stTextArea textarea {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
    }
    
    .stSelectbox select {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
    }
    
    .stDateInput input {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
    }
    
    .stTimeInput input {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
    }
    
    .stButton button {
        background-color: #4f8bf9;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
    }
    
    .stButton button:hover {
        background-color: #3b6bb8;
        color: white;
    }
    
    .stProgress > div > div > div {
        background-color: #4f8bf9 !important;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    session_defaults = {
        'current_activity': None,
        'start_time': None,
        'logs': [],
        'reminders': [],
        'calendar_events': [],
        'activities': {},
        'notes': [],
        'calendar_view': date.today(),
        'selected_date': None,
        'selected_notebook': None
    }
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def load_data():
    os.makedirs('data', exist_ok=True)
    try:
        if os.path.exists('data/activities.json'):
            with open('data/activities.json', 'r') as f:
                st.session_state.activities = json.load(f)
        else:
            st.session_state.activities = {
                'gym': {'name': '🏋 Gym', 'duration': None, 'color': '#4a90e2'},
                'study': {'name': '📚 Study', 'duration': None, 'color': '#00cec9'},
                'shower': {'name': '🚿 Shower', 'duration': None, 'color': '#fd79a8'},
                'cycle': {'name': '🚴 Leisure', 'duration': 3*3600, 'color': '#fdcb6e'},
                'course': {'name': '💻 Course', 'duration': 2*3600, 'color': '#6c5ce7'}
            }
        
        if os.path.exists('data/reminders.json'):
            with open('data/reminders.json', 'r') as f:
                st.session_state.reminders = json.load(f)
        
        if os.path.exists('data/calendar_events.json'):
            with open('data/calendar_events.json', 'r') as f:
                st.session_state.calendar_events = json.load(f)
        
        if os.path.exists('data/notes.json'):
            with open('data/notes.json', 'r') as f:
                st.session_state.notes = json.load(f)
        
        if os.path.exists('data/logs.json'):
            with open('data/logs.json', 'r') as f:
                st.session_state.logs = json.load(f)
                
    except Exception as e:
        st.error(f"Data error: {str(e)}")

def save_data():
    try:
        with open('data/activities.json', 'w') as f:
            json.dump(st.session_state.activities, f)
        with open('data/reminders.json', 'w') as f:
            json.dump(st.session_state.reminders, f, default=str)
        with open('data/calendar_events.json', 'w') as f:
            json.dump(st.session_state.calendar_events, f, default=str)
        with open('data/notes.json', 'w') as f:
            json.dump(st.session_state.notes, f)
        with open('data/logs.json', 'w') as f:
            json.dump(st.session_state.logs, f)
    except Exception as e:
        st.error(f"Save error: {str(e)}")

def format_duration(seconds):
    hours, rem = divmod(seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{int(hours):02d}h {int(minutes):02d}m {int(seconds):02d}s"

def get_today_summary():
    today = datetime.now().strftime("%Y-%m-%d")
    summary = {key: {'total': 0, 'completed': False} for key in st.session_state.activities}
    
    for log in st.session_state.logs:
        if log['date'] == today:
            for key, act in st.session_state.activities.items():
                if act['name'] == log['activity']:
                    summary[key]['total'] += log['duration']
                    if log['completed']:
                        summary[key]['completed'] = True
    
    if st.session_state.current_activity:
        current_key = st.session_state.current_activity
        elapsed = (datetime.now() - st.session_state.start_time).total_seconds()
        summary[current_key]['total'] += elapsed
    
    return summary

def show_dashboard():
    st.markdown("## 📊 Today's Progress Dashboard")
    summary = get_today_summary()
    
    with st.expander("➕ Add New Activity", expanded=False):
        with st.form(key='add_activity_form'):
            col1, col2 = st.columns([1, 4])
            with col1:
                emoji = st.text_input("Emoji", max_chars=3)
            with col2:
                name = st.text_input("Activity Name")
            color = st.color_picker("Color", value="#4a90e2")
            target = st.number_input("Target Duration (0 for no target)", min_value=0, value=0, step=1)
            target_unit = st.selectbox("Time Unit", ["Hours", "Minutes", "None"])
            
            if st.form_submit_button("Add Activity"):
                if name and emoji:
                    key = f"{name.lower().replace(' ', '')}{str(uuid.uuid4())[:4]}"
                    duration = target * 3600 if target_unit == "Hours" else target * 60
                    duration = duration if target_unit != "None" and target > 0 else None
                    
                    st.session_state.activities[key] = {
                        'name': f"{emoji} {name}",
                        'duration': duration,
                        'color': color
                    }
                    save_data()
                    st.rerun()
                else:
                    st.error("Please provide both emoji and activity name")

    with st.expander("🗑 Manage Activities", expanded=False):
        st.write("Delete existing activities here:")
        for key in list(st.session_state.activities.keys()):
            activity = st.session_state.activities[key]
            col1, col2 = st.columns([4, 1])
            with col1:
                duration_info = format_duration(activity['duration']) if activity['duration'] else "No target duration"
                st.markdown(f"""
                    <div style="padding: 0.5rem 0; border-bottom: 1px solid #eee;">
                        <div style="font-weight: 500; color: {activity['color']}">{activity['name']}</div>
                        <div style="font-size: 0.8rem; color: #666">{duration_info}</div>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("Delete", key=f"delete_{key}"):
                    if st.session_state.current_activity == key:
                        stop_activity()
                    del st.session_state.activities[key]
                    save_data()
                    st.rerun()
        if not st.session_state.activities:
            st.info("No activities to manage")

    st.markdown("## 🎯 Target Progress")
    for key in st.session_state.activities:
        activity = st.session_state.activities[key]
        if activity['duration']:
            total = summary[key]['total']
            duration = activity['duration']
            progress = min(total / duration, 1.0)
            st.markdown(f"""
            <div class="progress-container">
                <div style="color: {activity['color']}; margin-bottom: 0.5rem; font-size: 1rem">
                    {activity['name']}
                </div>
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="flex-grow: 1; background: #f0f0f0; border-radius: 4px;">
                        <div style="width: {progress*100}%; 
                                  background-color: {activity['color']}; 
                                  height: 12px; 
                                  border-radius: 4px;
                                  transition: width 0.3s ease;">
                        </div>
                    </div>
                    <div style="font-size: 0.9rem; color: #666;">
                        {format_duration(total)} / {format_duration(duration)}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("## 🕒 Activity Cards")
    cols = st.columns(len(st.session_state.activities))
    for i, key in enumerate(st.session_state.activities):
        activity = st.session_state.activities[key]
        with cols[i]:
            total_time = summary[key]['total']
            st.markdown(f"""
            <div class='compact-card' style='border-color: {activity['color']}'>
                <div>
                    <h4 style='margin: 0; color: {activity['color']}; font-size: 1.1rem'>{activity['name']}</h4>
                    <div style='margin: 0.5rem 0'>
                        <div style='font-size: 0.9rem; color: #666'>Total Time</div>
                        <div style='font-size: 1rem; font-weight: 500'>{format_duration(total_time)}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def show_corner_timer():
    if st.session_state.current_activity:
        elapsed = (datetime.now() - st.session_state.start_time).total_seconds()
        activity = st.session_state.activities[st.session_state.current_activity]
        timer_text = f"⏱ {activity['name']} - {format_duration(elapsed)}"
        st.markdown(f"""
        <div class="corner-timer">
            {timer_text}
        </div>
        """, unsafe_allow_html=True)

def activity_controls():
    st.markdown("## 🎯 Start Activity")
    cols = st.columns(2)
    activity_keys = list(st.session_state.activities.keys())
    for i, key in enumerate(activity_keys):
        activity = st.session_state.activities[key]
        with cols[i % 2]:
            is_active = st.session_state.current_activity == key
            if st.button(
                f"{'🛑 Stop' if is_active else '▶ Start'} {activity['name']}",
                key=f"btn_{key}",
                type="primary" if is_active else "secondary"
            ):
                if is_active:
                    stop_activity()
                else:
                    start_activity(key)

def start_activity(key):
    stop_activity()
    st.session_state.current_activity = key
    st.session_state.start_time = datetime.now()
    save_data()

def stop_activity():
    if st.session_state.current_activity:
        key = st.session_state.current_activity
        duration = (datetime.now() - st.session_state.start_time).total_seconds()
        activity = st.session_state.activities[key]
        completed = activity['duration'] and duration >= activity['duration']
        
        log_entry = {
            'activity': activity['name'],
            'date': datetime.now().strftime("%Y-%m-%d"),
            'start_time': st.session_state.start_time.isoformat(),
            'duration': duration,
            'completed': completed
        }
        st.session_state.logs.append(log_entry)
        st.session_state.current_activity = None
        save_data()
        st.rerun()

def reminders_tab():
    st.header("🔔 Reminders Manager")
    with st.expander("➕ Add New Reminder", expanded=True):
        new_reminder = st.text_input("Reminder text")
        col1, col2 = st.columns(2)
        with col1:
            due_date = st.date_input("Due date")
        with col2:
            due_time = st.time_input("Due time")
        
        if st.button("Add Reminder") and new_reminder:
            reminder_id = str(uuid.uuid4())
            st.session_state.reminders.append({
                'id': reminder_id,
                'text': new_reminder,
                'due': datetime.combine(due_date, due_time).isoformat(),
                'completed': False
            })
            save_data()
            st.rerun()
    
    st.subheader("Active Reminders")
    if not st.session_state.reminders:
        st.info("No reminders added yet!")
        return
    
    for reminder in st.session_state.reminders:
        due_date = datetime.fromisoformat(reminder['due'])
        is_overdue = datetime.now() > due_date if not reminder['completed'] else False
        
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;
                        border-left: 4px solid {'#ef4444' if is_overdue else '#4a90e2'}">
                <div style="{'color: #ef4444' if is_overdue else 'color: #2d3436'}">
                    {reminder['text']}
                </div>
                <div style="color: #666; font-size: 0.9rem">
                    ⏰ Due: {due_date.strftime('%b %d, %Y %I:%M %p')}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("✕", key=f"del_{reminder['id']}"):
                st.session_state.reminders.remove(reminder)
                save_data()
                st.rerun()

def calendar_tab():
    st.header("📅 Calendar Events")
    
    # Upcoming Events Section
    st.subheader("🗓 Next 7 Days' Events")
    today = datetime.today().date()
    upcoming_events = sorted(
        [e for e in st.session_state.calendar_events 
         if datetime.fromisoformat(e['due']).date() >= today],
        key=lambda x: datetime.fromisoformat(x['due'])
    )[:7]

    if upcoming_events:
        cols = st.columns(7)
        for i, event in enumerate(upcoming_events):
            with cols[i % 7]:
                event_date = datetime.fromisoformat(event['due']).date()
                event_time = datetime.fromisoformat(event['due']).strftime("%I:%M %p")
                days_until = (event_date - today).days
                
                st.markdown(f"""
                    <div style="padding: 0.5rem; margin: 0.25rem 0; 
                                background: {event.get('color', '#f8f9fa')};
                                border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.1rem; font-weight: 500;">{event_date.day}</div>
                        <div style="font-size: 0.8rem;">{event_date.strftime('%a')}</div>
                        <div style="font-size: 0.9rem; margin-top: 0.5rem;">{event['text'][:15]}{'...' if len(event['text']) >15 else ''}</div>
                        <div style="color: #666; font-size: 0.8rem">
                            {event_time}<br>
                            {days_until}d
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown("---")
    else:
        st.info("No upcoming events in the next 7 days")
        st.markdown("---")

    # Calendar Navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Previous Month"):
            new_date = st.session_state.calendar_view - timedelta(days=1)
            st.session_state.calendar_view = new_date.replace(day=1)
    with col2:
        st.markdown(f"### {st.session_state.calendar_view.strftime('%B %Y')}")
    with col3:
        if st.button("Next Month →"):
            next_month = st.session_state.calendar_view.replace(day=28) + timedelta(days=4)
            st.session_state.calendar_view = next_month.replace(day=1)
    
    # Calendar Grid
    cal = calendar.Calendar()
    month_days = cal.monthdatescalendar(
        st.session_state.calendar_view.year,
        st.session_state.calendar_view.month
    )
    
    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                day_events = [e for e in st.session_state.calendar_events 
                            if datetime.fromisoformat(e['due']).date() == day]
                is_today = day == date.today()
                is_current_month = day.month == st.session_state.calendar_view.month
                
                btn_label = f"{day.day}\n{len(day_events)*'•'}"
                if st.button(btn_label, 
                           key=f"day_{day}",
                           disabled=not is_current_month):
                    st.session_state.selected_date = day
                
                st.markdown(f"""
                    <style>
                        button[data-testid="baseButton-secondary"][disabled] {{
                            background-color: {'#e3f2fd' if is_today else '#f8f9fa'} !important;
                            border-color: {'#2196f3' if is_today else '#dee2e6'} !important;
                            color: {'#000' if is_current_month else '#9e9e9e'} !important;
                        }}
                    </style>
                """, unsafe_allow_html=True)
    
    # Date-Specific Event Management
    if st.session_state.get('selected_date'):
        selected_date = st.session_state.selected_date
        st.subheader(f"🗓 {selected_date.strftime('%b %d, %Y')} Events")
        
        date_events = [e for e in st.session_state.calendar_events 
                      if datetime.fromisoformat(e['due']).date() == selected_date]
        
        if date_events:
            for event in date_events:
                col1, col2 = st.columns([4, 1])
                with col1:
                    due_time = datetime.fromisoformat(event['due']).strftime("%I:%M %p")
                    st.markdown(f"""
                        <div class="reminder-item" style="border-color: {event.get('color', '#4a90e2')}">
                            <div style="font-weight: 500;">{event['text']}</div>
                            <div style="color: #666; font-size: 0.9rem">
                                ⏰ {due_time} • {event.get('color', '#4a90e2')}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("✕", key=f"cal_del_{event['id']}"):
                        st.session_state.calendar_events.remove(event)
                        save_data()
                        st.rerun()
        else:
            st.info("No events for this date")
        
        with st.form(key='calendar_event_form'):
            st.markdown("#### Add New Event")
            event_text = st.text_input("Event description")
            event_time = st.time_input("Event time")
            event_color = st.color_picker("Event color", value="#ff6b6b")
            
            if st.form_submit_button("➕ Add Event"):
                if event_text:
                    event_id = str(uuid.uuid4())
                    due_datetime = datetime.combine(selected_date, event_time)
                    st.session_state.calendar_events.append({
                        'id': event_id,
                        'text': event_text,
                        'due': due_datetime.isoformat(),
                        'color': event_color
                    })
                    save_data()
                    st.rerun()
                else:
                    st.error("Event description cannot be empty")

def notes_tab():
    st.header("📝 Notes Notebooks")
    
    # Custom CSS for Notes Tab
    st.markdown("""
    <style>
        .notebook-card {
            padding: 1rem;
            margin: 0.5rem 0;
            border: 2px solid #4a90e2;
            border-radius: 10px;
            background: white;
            transition: transform 0.2s;
        }
        .notebook-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 2px 8px rgba(74, 144, 226, 0.2);
        }
        .editor-container {
            border: 2px solid #4a90e2;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            background: #2d3436;
        }
        .editor-container textarea {
            background-color: #2d3436 !important;
            color: white !important;
            border: 1px solid #4a90e2 !important;
            border-radius: 8px !important;
            padding: 1rem !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 16px !important;
        }
        .preview-container {
            border: 2px solid #4a90e2;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            background: #f8f9fa;
            color: #2d3436;
        }
        .formatting-help {
            color: #ffffff;
            background: #404040;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        .save-button {
            background: #4a90e2 !important;
            color: white !important;
            border: none !important;
            padding: 0.5rem 1.5rem !important;
            border-radius: 8px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Create New Notebook
    with st.expander("➕ Create New Notebook", expanded=False):
        with st.form("new_notebook_form"):
            col1, col2 = st.columns([2, 1])
            with col1:
                name = st.text_input("Notebook Name")
            with col2:
                color = st.color_picker("Color", "#4a90e2")
            if st.form_submit_button("Create Notebook"):
                if name:
                    new_notebook = {
                        'id': str(uuid.uuid4()),
                        'name': name,
                        'color': color,
                        'content': "",
                        'created': datetime.now().isoformat()
                    }
                    st.session_state.notes.append(new_notebook)
                    save_data()
                    st.session_state.selected_notebook = new_notebook['id']
                    st.rerun()
                else:
                    st.error("Please enter a notebook name")

    # Notebooks Grid View
    if st.session_state.notes:
        st.subheader("Your Notebooks")
        cols = st.columns(3)
        for idx, notebook in enumerate(st.session_state.notes):
            with cols[idx % 3]:
                with st.container():
                    st.markdown(f"""
                    <div class="notebook-card" style="border-left: 4px solid {notebook['color']}">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h3 style="margin: 0; color: {notebook['color']}">{notebook['name']}</h3>
                            <button onclick="window.confirmDelete('{notebook['id']}')" 
                                    style="border: none; background: none; color: #ff4444;">✕</button>
                        </div>
                        <div style="color: #666; font-size: 0.9em; margin-top: 0.5rem;">
                            {notebook['content'][:50] + '...' if notebook['content'] else 'Empty notebook'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("Open", key=f"open_{notebook['id']}"):
                        st.session_state.selected_notebook = notebook['id']
                        st.rerun()

        st.markdown("---")
        
    # Notebook Editor
    if st.session_state.selected_notebook:
        notebook = next(n for n in st.session_state.notes if n['id'] == st.session_state.selected_notebook)
        
        with st.container():
            st.markdown(f"### ✏ Editing: {notebook['name']}")
            
            # Formatting Help
            st.markdown("""
            <div class="formatting-help">
                <strong>Formatting Help:</strong><br>
                • Bold: *text* &nbsp;&nbsp;• Italic: text &nbsp;&nbsp;• Bullets: - item<br>
                • Headers: # H1 &nbsp;&nbsp;## H2 &nbsp;&nbsp;### H3<br>
                • Links: [text](url) &nbsp;&nbsp;• Code: code or code block
            </div>
            """, unsafe_allow_html=True)
            
            # Editor
            with st.container():
                new_content = st.text_area(
                    "Edit your notes:",
                    value=notebook['content'],
                    height=400,
                    key=f"editor_{notebook['id']}",
                    label_visibility="collapsed"
                )
            
            # Save Button
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("💾 Save Changes", 
                           key=f"save_{notebook['id']}", 
                           use_container_width=True,
                           type="primary"):
                    notebook['content'] = new_content
                    save_data()
                    st.toast("Changes saved successfully!", icon="✅")
            
            # Preview
            st.markdown("### 📄 Preview")
            with st.container():
                st.markdown(f'<div class="preview-container">{new_content}</div>', 
                          unsafe_allow_html=True)
            
            # Delete Button
            st.markdown("---")
            if st.button("🗑 Delete This Notebook", 
                        type="primary", 
                        key=f"del_{notebook['id']}",
                        use_container_width=True):
                st.session_state.notes.remove(notebook)
                save_data()
                st.session_state.selected_notebook = None
                st.rerun()
    else:
        st.info("Select a notebook from the grid above or create a new one")

    # JavaScript for delete confirmation
    st.markdown("""
    <script>
    function confirmDelete(notebookId) {
        if (confirm('Are you sure you want to delete this notebook?')) {
            window.streamlitApi.sendMessage('delete_notebook', {id: notebookId});
        }
    }
    </script>
    """, unsafe_allow_html=True)

def reset_tab():
    st.header("🔄 Reset Data")
    st.warning("This action will permanently delete all your data!")
    if st.button("⚠ Reset All Data"):
        try:
            os.remove('data/logs.json')
            os.remove('data/reminders.json')
            os.remove('data/activities.json')
            os.remove('data/calendar_events.json')
            os.remove('data/notes.json')
        except:
            pass
        st.session_state.clear()
        st.rerun()

def main():
    init_session_state()
    load_data()
    
    st.title("Productivity Master")
    show_corner_timer()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Dashboard & Activities", 
        "Reminders", 
        "Calendar Events",
        "Notes",
        "Reset Data"
    ])
    
    with tab1:
        show_dashboard()
        activity_controls()
    with tab2:
        reminders_tab()
    with tab3:
        calendar_tab()
    with tab4:
        notes_tab()
    with tab5:
        reset_tab()

    if st.session_state.current_activity:
        st_autorefresh(interval=1000, key="timer_refresh")

if __name__ == "__main__":
    main()