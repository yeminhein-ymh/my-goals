from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

import streamlit as st

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    gspread = None
    Credentials = None


GOALS = [
    {
        "id": "coursework",
        "title": "Coursework Reassessment",
        "icon": "📚",
        "color": "#E24B4A",
        "bg": "#FCEBEB",
        "deadline": "2025-06-08",
        "phase": "URGENT",
        "target": "Complete 2 courseworks",
        "dailyTime": "8:30-10 PM study block",
        "tasks": [
            {"id": "cw1", "text": "Coursework 1 - outline & draft"},
            {"id": "cw2", "text": "Coursework 1 - write & revise"},
            {"id": "cw3", "text": "Coursework 1 - submit"},
            {"id": "cw4", "text": "Coursework 2 - outline & draft"},
            {"id": "cw5", "text": "Coursework 2 - write & revise"},
            {"id": "cw6", "text": "Coursework 2 - submit"},
        ],
        "habits": [
            {"id": "h_cw1", "text": "Study session (8:30-10 PM)"},
            {"id": "h_cw2", "text": "Review notes (morning)"},
        ],
        "milestones": ["CW1 draft done", "CW1 submitted", "CW2 draft done", "CW2 submitted"],
    },
    {
        "id": "fitness",
        "title": "Lose 5 kg in 3 Months",
        "icon": "💪",
        "color": "#1D9E75",
        "bg": "#E1F5EE",
        "deadline": "2025-08-29",
        "phase": "Month 1-3",
        "target": "-5 kg by end of August",
        "dailyTime": "1h (6-7 AM)",
        "tasks": [
            {"id": "ft1", "text": "Set up meal tracking app"},
            {"id": "ft2", "text": "Plan weekly workout schedule"},
            {"id": "ft3", "text": "First weigh-in (baseline)"},
            {"id": "ft4", "text": "Reach -2 kg milestone"},
            {"id": "ft5", "text": "Reach -3.5 kg milestone"},
            {"id": "ft6", "text": "Reach -5 kg goal"},
        ],
        "habits": [
            {"id": "h_ft1", "text": "Morning workout (30 min)"},
            {"id": "h_ft2", "text": "Track meals / calories"},
            {"id": "h_ft3", "text": "8 glasses of water"},
        ],
        "milestones": ["Workout routine set", "-1 kg", "-2.5 kg", "-5 kg"],
    },
    {
        "id": "youtube",
        "title": "Solar Tech YouTube + Social",
        "icon": "☀️",
        "color": "#BA7517",
        "bg": "#FAEEDA",
        "deadline": "2025-11-29",
        "phase": "Month 2-6",
        "target": "Regular income from content",
        "dailyTime": "8:30-10 PM rotation + Sunday batch",
        "tasks": [
            {"id": "yt1", "text": "Set up YouTube channel"},
            {"id": "yt2", "text": "Create Facebook & TikTok pages"},
            {"id": "yt3", "text": "Film first YouTube video"},
            {"id": "yt4", "text": "Post first TikTok/Facebook reel"},
            {"id": "yt5", "text": "Reach 100 YouTube subscribers"},
            {"id": "yt6", "text": "First monetisation milestone"},
        ],
        "habits": [
            {"id": "h_yt1", "text": "Post short-form content (TikTok/FB)"},
            {"id": "h_yt2", "text": "Sunday batch-create content"},
            {"id": "h_yt3", "text": "Engage with comments/community"},
        ],
        "milestones": ["Channel live", "10 videos posted", "100 subscribers", "First $50 earned"],
    },
    {
        "id": "trading",
        "title": "Stock & Options Trading",
        "icon": "📈",
        "color": "#534AB7",
        "bg": "#EEEDFE",
        "deadline": "2025-11-29",
        "phase": "Month 1-6",
        "target": "$100-150/day profit",
        "dailyTime": "8:30-10 PM rotation",
        "tasks": [
            {"id": "tr1", "text": "Choose a trading platform / broker"},
            {"id": "tr2", "text": "Complete beginner options course"},
            {"id": "tr3", "text": "Start paper trading (simulated)"},
            {"id": "tr4", "text": "Track 30 paper trades"},
            {"id": "tr5", "text": "First real trade (small amount)"},
            {"id": "tr6", "text": "Consistent $50/day paper profit"},
        ],
        "habits": [
            {"id": "h_tr1", "text": "30 min trading study"},
            {"id": "h_tr2", "text": "Review market pre-open"},
            {"id": "h_tr3", "text": "Log trade in journal"},
        ],
        "milestones": ["Paper trading started", "30 trades logged", "Profitable week (paper)", "$50/day consistent"],
    },
]

PHASES = [
    {
        "label": "Now -> 8 Jun",
        "color": "#FCEBEB",
        "textColor": "#A32D2D",
        "desc": "EMERGENCY: Coursework only. Exercise daily.",
    },
    {
        "label": "Jun -> Jul",
        "color": "#E6F1FB",
        "textColor": "#185FA5",
        "desc": "LAUNCH: Start YouTube, paper trade, habits locked.",
    },
    {
        "label": "Jul -> Aug",
        "color": "#EAF3DE",
        "textColor": "#3B6D11",
        "desc": "ACCELERATE: Weight goal hit, 8+ YT videos, small real trades.",
    },
    {
        "label": "Sep -> Nov",
        "color": "#FAEEDA",
        "textColor": "#854F0B",
        "desc": "SCALE: Social income growing, trading consistency building.",
    },
]

DAYS = ["M", "T", "W", "T", "F", "S", "S"]
DATA_FILE = Path(__file__).with_name("goal_progress.json")
SHEET_TAB = "goal_progress"


def days_until(date_str: str) -> int:
    target = datetime.strptime(date_str, "%Y-%m-%d").date()
    return max((target - date.today()).days, 0)


def deadline_label(date_str: str) -> str:
    target = datetime.strptime(date_str, "%Y-%m-%d").date()
    delta = (target - date.today()).days
    if delta > 0:
        return f"{delta}d left"
    if delta == 0:
        return "due today"
    return f"{abs(delta)}d overdue"


def all_task_ids() -> list[str]:
    return [task["id"] for goal in GOALS for task in goal["tasks"]]


def all_habit_day_keys() -> list[str]:
    return [
        f"{habit['id']}_{day_index}"
        for goal in GOALS
        for habit in goal["habits"]
        for day_index in range(7)
    ]


def default_data() -> dict:
    return {
        "tasks": {task_id: False for task_id in all_task_ids()},
        "habits": {habit_key: False for habit_key in all_habit_day_keys()},
        "daily_logs": {},
        "notes": {},
        "history": {},
    }


def today_key() -> str:
    return date.today().isoformat()


def daily_task_state_key(task_id: str, day: str | None = None) -> str:
    return f"daily_task_{day or today_key()}_{task_id}"


def daily_habit_state_key(habit_id: str, day: str | None = None) -> str:
    return f"daily_habit_{day or today_key()}_{habit_id}"


def daily_log_from_session(day: str | None = None) -> dict:
    day = day or today_key()
    return {
        "tasks": {
            task["id"]: bool(st.session_state.get(daily_task_state_key(task["id"], day), False))
            for goal in GOALS
            for task in goal["tasks"]
        },
        "habits": {
            habit["id"]: bool(st.session_state.get(daily_habit_state_key(habit["id"], day), False))
            for goal in GOALS
            for habit in goal["habits"]
        },
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }


def daily_log_counts(day: str | None = None) -> tuple[int, int, int]:
    day = day or today_key()
    log = st.session_state.get("daily_logs", {}).get(day, {})
    task_values = log.get("tasks", {})
    habit_values = log.get("habits", {})
    total = sum(len(goal["tasks"]) + len(goal["habits"]) for goal in GOALS)
    done = sum(1 for value in task_values.values() if value) + sum(1 for value in habit_values.values() if value)
    pct = round((done / total) * 100) if total else 0
    return done, total, pct


def google_sheet_configured() -> bool:
    return (
        gspread is not None
        and Credentials is not None
        and "gcp_service_account" in st.secrets
        and "google_sheet_id" in st.secrets
    )


def get_goal_worksheet():
    if not google_sheet_configured():
        return None

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=scopes,
    )
    client = gspread.authorize(credentials)
    workbook = client.open_by_key(st.secrets["google_sheet_id"])
    try:
        worksheet = workbook.worksheet(SHEET_TAB)
    except gspread.WorksheetNotFound:
        worksheet = workbook.add_worksheet(title=SHEET_TAB, rows=1000, cols=4)
        worksheet.update("A1:D1", [["record_type", "record_key", "payload_json", "updated_at"]])
    return worksheet


def data_from_google_sheet() -> dict | None:
    worksheet = get_goal_worksheet()
    if worksheet is None:
        return None

    rows = worksheet.get_all_records()
    data = default_data()
    for row in rows:
        record_type = row.get("record_type")
        record_key = str(row.get("record_key", ""))
        payload = row.get("payload_json")
        if not payload:
            continue
        try:
            value = json.loads(payload)
        except (TypeError, json.JSONDecodeError):
            continue

        if record_type == "task" and record_key:
            data["tasks"][record_key] = bool(value)
        elif record_type == "habit" and record_key:
            data["habits"][record_key] = bool(value)
        elif record_type == "daily_logs":
            data["daily_logs"] = value if isinstance(value, dict) else {}
        elif record_type == "notes":
            data["notes"] = value if isinstance(value, dict) else {}
        elif record_type == "history":
            data["history"] = value if isinstance(value, dict) else {}

    return data


def save_to_google_sheet(data: dict) -> bool:
    worksheet = get_goal_worksheet()
    if worksheet is None:
        return False

    rows = [["record_type", "record_key", "payload_json", "updated_at"]]
    updated_at = datetime.now().isoformat(timespec="seconds")
    for task_id, is_done in data["tasks"].items():
        rows.append(["task", task_id, json.dumps(bool(is_done)), updated_at])
    for habit_key, is_done in data["habits"].items():
        rows.append(["habit", habit_key, json.dumps(bool(is_done)), updated_at])
    rows.append(["daily_logs", "all", json.dumps(data["daily_logs"], ensure_ascii=False), updated_at])
    rows.append(["notes", "all", json.dumps(data["notes"], ensure_ascii=False), updated_at])
    rows.append(["history", "all", json.dumps(data["history"], ensure_ascii=False), updated_at])

    worksheet.clear()
    worksheet.update("A1", rows)
    return True


def load_data() -> dict:
    data = default_data()
    try:
        sheet_data = data_from_google_sheet()
        if sheet_data is not None:
            st.session_state["storage_backend"] = "Google Sheets"
            return sheet_data
    except Exception as exc:
        st.session_state["storage_backend"] = "Local JSON fallback"
        st.session_state["storage_error"] = f"Google Sheets load failed: {exc}"

    if DATA_FILE.exists():
        try:
            saved = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            data["tasks"].update(saved.get("tasks", {}))
            data["habits"].update(saved.get("habits", {}))
            data["daily_logs"] = saved.get("daily_logs", {})
            data["notes"] = saved.get("notes", {})
            data["history"] = saved.get("history", {})
        except (OSError, json.JSONDecodeError):
            st.warning("Saved progress could not be read. Starting with a clean local state.")
    return data


def current_progress_snapshot() -> dict:
    total_tasks = len(all_task_ids())
    completed_tasks = sum(1 for task_id in all_task_ids() if st.session_state.get(f"task_{task_id}", False))
    total_habits = len(all_habit_day_keys())
    completed_habits = sum(
        1
        for habit_key in all_habit_day_keys()
        if st.session_state.get(f"habit_{habit_key}", False)
    )
    today_done, today_total, today_percent = daily_log_counts()
    return {
        "date": date.today().isoformat(),
        "completed_tasks": completed_tasks,
        "total_tasks": total_tasks,
        "completed_habits": completed_habits,
        "total_habits": total_habits,
        "today_done": today_done,
        "today_total": today_total,
        "today_percent": today_percent,
        "task_percent": round((completed_tasks / total_tasks) * 100) if total_tasks else 0,
        "habit_percent": round((completed_habits / total_habits) * 100) if total_habits else 0,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }


def data_from_session() -> dict:
    data = {
        "tasks": {task_id: bool(st.session_state.get(f"task_{task_id}", False)) for task_id in all_task_ids()},
        "habits": {
            habit_key: bool(st.session_state.get(f"habit_{habit_key}", False))
            for habit_key in all_habit_day_keys()
        },
        "daily_logs": st.session_state.get("daily_logs", {}),
        "notes": st.session_state.get("notes", {}),
        "history": st.session_state.get("history", {}),
    }
    data["daily_logs"][today_key()] = daily_log_from_session()
    st.session_state["daily_logs"] = data["daily_logs"]
    data["history"][date.today().isoformat()] = current_progress_snapshot()
    return data


def save_progress() -> None:
    data = data_from_session()
    st.session_state["history"] = data["history"]
    try:
        if save_to_google_sheet(data):
            st.session_state["storage_backend"] = "Google Sheets"
            st.session_state["last_saved_at"] = f"{datetime.now().strftime('%d %b %Y, %I:%M %p')} to Google Sheets"
            return
    except Exception as exc:
        st.session_state["storage_backend"] = "Local JSON fallback"
        st.session_state["storage_error"] = f"Google Sheets save failed: {exc}"

    try:
        DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        st.session_state["last_saved_at"] = f"{datetime.now().strftime('%d %b %Y, %I:%M %p')} to local JSON"
    except OSError as exc:
        st.session_state["last_saved_at"] = f"Save failed: {exc}"


def init_state() -> None:
    if "data_loaded" not in st.session_state:
        saved = load_data()
        for task_id, is_done in saved["tasks"].items():
            st.session_state[f"task_{task_id}"] = bool(is_done)
        for habit_key, is_done in saved["habits"].items():
            st.session_state[f"habit_{habit_key}"] = bool(is_done)
        st.session_state["daily_logs"] = saved.get("daily_logs", {})
        today_log = st.session_state["daily_logs"].get(today_key(), {})
        for task_id, is_done in today_log.get("tasks", {}).items():
            st.session_state[daily_task_state_key(task_id)] = bool(is_done)
        for habit_id, is_done in today_log.get("habits", {}).items():
            st.session_state[daily_habit_state_key(habit_id)] = bool(is_done)
        st.session_state["notes"] = saved["notes"]
        st.session_state["history"] = saved["history"]
        st.session_state["data_loaded"] = True

    st.session_state.setdefault("view", "Goals")
    st.session_state.setdefault("notes", {})
    st.session_state.setdefault("daily_logs", {})
    st.session_state.setdefault("history", {})
    st.session_state.setdefault("last_saved_at", "Not saved yet")
    st.session_state.setdefault("storage_backend", "Google Sheets" if google_sheet_configured() else "Local JSON")
    st.session_state.setdefault("storage_error", "")
    st.session_state.setdefault("coach_messages", [
        {
            "role": "assistant",
            "content": "Hi, I am your goal coach. Ask me what to focus on today, how to plan the week, or how to reduce overload.",
        }
    ])

    for goal in GOALS:
        for task in goal["tasks"]:
            st.session_state.setdefault(f"task_{task['id']}", False)
            st.session_state.setdefault(daily_task_state_key(task["id"]), False)
        for habit in goal["habits"]:
            st.session_state.setdefault(daily_habit_state_key(habit["id"]), False)
            for day_index in range(7):
                st.session_state.setdefault(f"habit_{habit['id']}_{day_index}", False)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --ink: #1f2328;
            --muted: #757883;
            --line: #ececec;
            --paper: #ffffff;
            --wash: #fafaf8;
        }

        .stApp {
            background: var(--wash);
            color: var(--ink);
            font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .block-container {
            max-width: 920px;
            padding-top: 3rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3, p {
            letter-spacing: 0;
        }

        div[data-testid="stMetric"] {
            background: #fff;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 12px 14px;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.55rem;
            font-weight: 800;
        }

        .topbar {
            background: #fff;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 18px 18px;
            margin-top: 4px;
            margin-bottom: 14px;
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 16px;
            min-height: 82px;
            overflow: visible;
        }

        .brand-title {
            font-size: 1.25rem;
            font-weight: 800;
            line-height: 1.3;
            padding-top: 2px;
        }

        .brand-subtitle {
            color: var(--muted);
            font-size: 0.78rem;
            margin-top: 4px;
        }

        .brand-context {
            color: var(--muted);
            font-size: 0.78rem;
            margin-top: 8px;
            text-align: right;
        }

        @media (max-width: 720px) {
            .block-container {
                padding-top: 3.5rem;
            }

            .topbar {
                flex-direction: column;
                min-height: 112px;
            }

            .brand-context {
                text-align: left;
                margin-top: 0;
            }
        }

        .urgent {
            background: #FCEBEB;
            border: 1px solid #E24B4A;
            border-radius: 8px;
            padding: 13px 15px;
            margin: 12px 0 16px;
        }

        .urgent-title {
            color: #A32D2D;
            font-weight: 800;
            font-size: 0.9rem;
        }

        .urgent-copy {
            color: #B94747;
            font-size: 0.8rem;
            margin-top: 3px;
        }

        .goal-card {
            background: #fff;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 15px 16px;
            margin-bottom: 12px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.035);
        }

        .goal-head {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }

        .goal-icon {
            width: 44px;
            height: 44px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.45rem;
            flex: 0 0 auto;
        }

        .goal-title {
            font-weight: 800;
            font-size: 1rem;
        }

        .pill {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 3px 9px;
            font-size: 0.68rem;
            font-weight: 800;
            margin-left: 6px;
            vertical-align: 2px;
        }

        .meta-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            color: var(--muted);
            font-size: 0.78rem;
            margin-top: 4px;
        }

        .progress-shell {
            background: #f0f0f0;
            border-radius: 999px;
            height: 7px;
            overflow: hidden;
            margin: 10px 0 4px;
        }

        .progress-fill {
            height: 100%;
            border-radius: 999px;
        }

        .target-box {
            border-radius: 8px;
            padding: 10px 12px;
            margin-top: 8px;
            font-size: 0.82rem;
        }

        .mini-label {
            color: var(--muted);
            font-size: 0.78rem;
            margin-bottom: 6px;
        }

        .phase-card {
            border-radius: 8px;
            padding: 13px 15px;
            margin-bottom: 12px;
            border: 1px solid rgba(0,0,0,0.06);
        }

        .schedule-cell {
            border-radius: 8px;
            padding: 8px 6px;
            min-height: 42px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            font-size: 0.75rem;
            font-weight: 600;
            color: #3f4147;
            border: 1px solid rgba(0,0,0,0.04);
        }

        .schedule-time {
            color: var(--muted);
            font-size: 0.75rem;
            line-height: 1.25;
            display: flex;
            align-items: center;
        }

        .chat-assistant, .chat-user {
            border-radius: 8px;
            padding: 10px 12px;
            margin: 8px 0;
            line-height: 1.45;
            font-size: 0.9rem;
        }

        .chat-assistant {
            background: #f3f3f5;
            color: #222;
            margin-right: 12%;
        }

        .chat-user {
            background: #534AB7;
            color: #fff;
            margin-left: 12%;
        }

        button[kind="secondary"] {
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def progress_for_goal(goal: dict) -> tuple[int, int, int]:
    done = sum(1 for task in goal["tasks"] if st.session_state[f"task_{task['id']}"])
    total = len(goal["tasks"])
    pct = round((done / total) * 100) if total else 0
    return done, total, pct


def render_header() -> None:
    overall_days = days_until("2025-11-29")
    subtitle = f"{overall_days} days remaining" if overall_days else "Timeline ready for your next reset"
    st.markdown(
        f"""
        <div class="topbar">
          <div>
            <div class="brand-title">My 6-Month System</div>
            <div class="brand-subtitle">{subtitle}</div>
          </div>
          <div class="brand-context">Coursework · Fitness · Content · Trading</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    views = ["Goals", "Schedule", "Phases", "Progress", "Coach"]
    st.session_state["view"] = st.segmented_control(
        "View",
        views,
        selection_mode="single",
        default=st.session_state["view"],
        label_visibility="collapsed",
    )


def render_goal_card(goal: dict) -> None:
    done, total, pct = progress_for_goal(goal)
    st.markdown(
        f"""
        <div class="goal-card" style="border-color: {goal['color']}33;">
          <div class="goal-head">
            <div class="goal-icon" style="background:{goal['bg']};">{goal['icon']}</div>
            <div>
              <div class="goal-title">
                {goal['title']}
                <span class="pill" style="background:{goal['bg']}; color:{goal['color']};">{goal['phase']}</span>
              </div>
              <div class="meta-row">
                <span>{done}/{total} tasks</span>
                <span>{deadline_label(goal['deadline'])}</span>
                <span>{goal['dailyTime']}</span>
              </div>
            </div>
          </div>
          <div class="progress-shell">
            <div class="progress-fill" style="width:{pct}%; background:{goal['color']};"></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Open tracker", expanded=False):
        today_tab, task_tab, habit_tab, milestone_tab, notes_tab = st.tabs(["Today", "Tasks", "Habits", "Milestones", "Notes"])

        with today_tab:
            st.markdown(f"<div class='mini-label'>Daily record for {date.today().strftime('%d %b %Y')}</div>", unsafe_allow_html=True)
            st.markdown("**Today's tasks**")
            for task in goal["tasks"]:
                st.checkbox(
                    task["text"],
                    key=daily_task_state_key(task["id"]),
                    on_change=save_progress,
                )

            st.markdown("**Today's habits**")
            for habit in goal["habits"]:
                st.checkbox(
                    habit["text"],
                    key=daily_habit_state_key(habit["id"]),
                    on_change=save_progress,
                )

            if st.button("Save today's tracker", key=f"save_today_{goal['id']}", use_container_width=True):
                save_progress()
                st.success("Today's tracker has been saved.")
                st.rerun()

        with task_tab:
            st.markdown(f"<div class='mini-label'>Daily time: {goal['dailyTime']}</div>", unsafe_allow_html=True)
            for task in goal["tasks"]:
                st.checkbox(task["text"], key=f"task_{task['id']}", on_change=save_progress)
            st.markdown(
                f"""
                <div class="target-box" style="background:{goal['bg']};">
                    <strong style="color:{goal['color']};">Target:</strong> {goal['target']}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with habit_tab:
            header_cols = st.columns([2.8, 1, 1, 1, 1, 1, 1, 1])
            header_cols[0].caption("Habit")
            for index, day_name in enumerate(DAYS, 1):
                header_cols[index].caption(day_name)

            for habit in goal["habits"]:
                cols = st.columns([2.8, 1, 1, 1, 1, 1, 1, 1])
                cols[0].markdown(f"<div style='font-size:0.82rem; padding-top:7px;'>{habit['text']}</div>", unsafe_allow_html=True)
                for day_index in range(7):
                    cols[day_index + 1].checkbox(
                        "done",
                        key=f"habit_{habit['id']}_{day_index}",
                        label_visibility="collapsed",
                        on_change=save_progress,
                    )
            st.caption("Mark each day as complete to build the weekly rhythm.")

        with milestone_tab:
            completed_milestones = min(len(goal["milestones"]), pct // 25)
            for index, milestone in enumerate(goal["milestones"], 1):
                status = "Done" if index <= completed_milestones else "Next"
                st.markdown(f"**{index}. {milestone}** · {status}")

        with notes_tab:
            note_key = f"note_input_{goal['id']}"
            st.text_input("Add a note or reflection", key=note_key, placeholder="Log wins, blockers, ideas...")
            if st.button("Add note", key=f"add_note_{goal['id']}"):
                note = st.session_state[note_key].strip()
                if note:
                    st.session_state["notes"].setdefault(goal["id"], []).insert(
                        0,
                        {"text": note, "date": date.today().strftime("%d %b %Y")},
                    )
                    st.session_state[note_key] = ""
                    save_progress()
                    st.rerun()

            notes = st.session_state["notes"].get(goal["id"], [])
            if not notes:
                st.caption("No notes yet.")
            for note in notes:
                st.info(f"{note['text']}\n\n{note['date']}")


def render_dashboard() -> None:
    urgent_days = days_until("2025-06-08")
    urgent_line = (
        f"{urgent_days} days until coursework deadline (8 June)"
        if urgent_days
        else "Coursework deadline has passed. Use this tracker to reset the plan."
    )
    st.markdown(
        f"""
        <div class="urgent">
            <div class="urgent-title">URGENT: {urgent_line}</div>
            <div class="urgent-copy">Protect the 8:30-10 PM study block and keep the 6-7 AM exercise routine simple.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    total_done = 0
    total_tasks = 0
    for goal in GOALS:
        done, total, _ = progress_for_goal(goal)
        total_done += done
        total_tasks += total
    today_done, today_total, today_percent = daily_log_counts()

    cols = st.columns(4)
    cols[0].metric("Active goals", "4")
    cols[1].metric("Task progress", f"{total_done}/{total_tasks}")
    cols[2].metric("Today recorded", f"{today_done}/{today_total}", f"{today_percent}%")
    cols[3].metric("Total runway", "6mo")
    st.caption(
        f"Storage: {st.session_state.get('storage_backend', 'Local JSON')} · "
        f"Last saved: {st.session_state.get('last_saved_at', 'Not saved yet')}"
    )
    if st.session_state.get("storage_error"):
        st.warning(st.session_state["storage_error"])

    st.write("")
    for goal in GOALS:
        render_goal_card(goal)


def render_progress() -> None:
    st.subheader("Progress Record")
    st.caption("Daily task and habit progress is saved to Google Sheets when configured, with local JSON as a fallback.")

    snapshot = current_progress_snapshot()
    cols = st.columns(4)
    cols[0].metric("Today recorded", f"{snapshot['today_done']}/{snapshot['today_total']}")
    cols[1].metric("Today progress", f"{snapshot['today_percent']}%")
    cols[2].metric("Goal tasks done", f"{snapshot['completed_tasks']}/{snapshot['total_tasks']}")
    cols[3].metric("Weekly habits done", f"{snapshot['completed_habits']}/{snapshot['total_habits']}")

    if st.button("Save today's progress now", use_container_width=True):
        save_progress()
        st.success("Today's progress has been saved.")
        st.rerun()

    st.caption(
        f"Storage: {st.session_state.get('storage_backend', 'Local JSON')} · "
        f"Last saved: {st.session_state.get('last_saved_at', 'Not saved yet')}"
    )
    if st.session_state.get("storage_error"):
        st.warning(st.session_state["storage_error"])

    data = data_from_session()
    backup_json = json.dumps(data, indent=2)
    st.download_button(
        "Download progress backup",
        data=backup_json,
        file_name=f"goal_progress_backup_{date.today().isoformat()}.json",
        mime="application/json",
        use_container_width=True,
    )

    history = st.session_state.get("history", {})
    if not history:
        st.info("No saved daily history yet. Tick a task or habit, or use the save button above.")
        return

    st.write("")
    st.markdown("**Daily History**")
    for day, row in sorted(history.items(), reverse=True):
        st.markdown(
            f"- **{day}** · Today: {row.get('today_done', 0)}/{row.get('today_total', 0)} "
            f"({row.get('today_percent', 0)}%) · Goal tasks: {row.get('completed_tasks', 0)}/{row.get('total_tasks', 0)} "
            f"· Weekly habits: {row.get('completed_habits', 0)}/{row.get('total_habits', 0)}"
        )


def render_schedule() -> None:
    st.subheader("Weekly Schedule")
    st.caption("Weekday routine with the 8:30-10:00 PM study block allocated across coursework, Solar Tech YouTube, and stock trading.")

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    rows = [
        ("6:00-7:00 AM", ["Exercise", "Exercise", "Exercise", "Exercise", "Exercise", "Exercise", "Rest"], ["#EAF3DE"] * 6 + ["#f5f5f5"]),
        ("7:30-9:00 AM", ["Travel to work", "Travel to work", "Travel to work", "Travel to work", "Travel to work", "Home / errands", "Home / rest"], ["#E6F1FB"] * 5 + ["#fafafa"] * 2),
        ("9:00 AM-6:00 PM", ["Day job", "Day job", "Day job", "Day job", "Day job", "YT filming", "Content batch"], ["#f0f0f0"] * 5 + ["#FAEEDA"] * 2),
        ("6:00-7:30 PM", ["Travel home", "Travel home", "Travel home", "Travel home", "Travel home", "Free time", "Week reset"], ["#E6F1FB"] * 5 + ["#fafafa", "#E6F1FB"]),
        ("7:30-8:30 PM", ["Dinner", "Dinner", "Dinner", "Dinner", "Dinner", "Dinner", "Dinner"], ["#fff4df"] * 7),
        ("8:30-10:00 PM", ["Coursework", "Solar Tech YouTube", "Stock trading", "Coursework", "Stock trading review", "Solar Tech batch", "Coursework / weekly plan"], ["#FCEBEB", "#FAEEDA", "#EEEDFE", "#FCEBEB", "#EEEDFE", "#FAEEDA", "#FCEBEB"]),
    ]

    header = st.columns([1.25, 1, 1, 1, 1, 1, 1, 1])
    header[0].write("")
    for index, day_name in enumerate(days, 1):
        header[index].markdown(f"**{day_name}**")

    for time_label, slots, colors in rows:
        cols = st.columns([1.25, 1, 1, 1, 1, 1, 1, 1])
        cols[0].markdown(f"<div class='schedule-time'>{time_label}</div>", unsafe_allow_html=True)
        for index, slot in enumerate(slots):
            cols[index + 1].markdown(
                f"<div class='schedule-cell' style='background:{colors[index]};'>{slot}</div>",
                unsafe_allow_html=True,
            )


def render_phases() -> None:
    st.subheader("6-Month Phase Plan")
    st.caption("Phase in your goals so the system stays realistic.")

    for index, phase in enumerate(PHASES, 1):
        st.markdown(
            f"""
            <div class="phase-card" style="background:{phase['color']};">
                <div style="font-weight:800; color:{phase['textColor']}; margin-bottom:4px;">
                    {index}. {phase['label']}
                </div>
                <div style="font-size:0.9rem;">{phase['desc']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    cols = st.columns(4)
    for col, goal in zip(cols, GOALS):
        col.markdown(
            f"""
            <div class="goal-card" style="min-height:132px;">
                <div style="font-size:1.5rem;">{goal['icon']}</div>
                <div style="font-weight:800; margin-top:5px;">{goal['title']}</div>
                <div class="meta-row">{goal['phase']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def coach_reply(prompt: str) -> str:
    text = prompt.lower()
    if "today" in text or "focus" in text:
        return (
            "Today, choose one main win: protect the 8:30-10 PM block for the most urgent coursework task, "
            "then do a 10-minute reset note before bed. Keep fitness tiny if the day is packed: a walk still counts."
        )
    if "trading" in text or "option" in text:
        return (
            "For trading, stay in learning mode first: finish one beginner module, paper trade only, and log every setup. "
            "Do not judge the system from one trade; judge it after 30 logged paper trades."
        )
    if "youtube" in text or "content" in text or "tiktok" in text:
        return (
            "For Solar Tech content, batch the hard part on Sunday: 3 hooks, 1 short script, 1 filmed explainer. "
            "Start with simple topics like bills, panels, batteries, and common homeowner questions."
        )
    if "overwhelmed" in text or "stress" in text:
        return (
            "Shrink the plan for the next 24 hours. Pick one coursework task, one body task, and one admin task. "
            "Everything else becomes optional until the urgent pressure drops."
        )
    return (
        "A practical next step: rank the four goals by deadline pressure, then commit to one visible action today. "
        "Coursework gets priority, fitness stays lightweight, and content/trading can live in small scheduled blocks."
    )


def render_coach() -> None:
    st.subheader("Goal Coach")
    st.caption("Local coaching prompts for your four-goal system.")

    for message in st.session_state["coach_messages"]:
        klass = "chat-user" if message["role"] == "user" else "chat-assistant"
        st.markdown(f"<div class='{klass}'>{message['content']}</div>", unsafe_allow_html=True)

    with st.form("coach_form", clear_on_submit=True):
        prompt = st.text_input("Ask your coach anything", placeholder="What should I do today?")
        submitted = st.form_submit_button("Send")
        if submitted and prompt.strip():
            st.session_state["coach_messages"].append({"role": "user", "content": prompt.strip()})
            st.session_state["coach_messages"].append({"role": "assistant", "content": coach_reply(prompt)})
            st.rerun()

    cols = st.columns(4)
    quick_prompts = ["What should I do today?", "How to start trading?", "YouTube tips?", "I'm feeling overwhelmed"]
    for col, prompt in zip(cols, quick_prompts):
        if col.button(prompt, use_container_width=True):
            st.session_state["coach_messages"].append({"role": "user", "content": prompt})
            st.session_state["coach_messages"].append({"role": "assistant", "content": coach_reply(prompt)})
            st.rerun()


def main() -> None:
    st.set_page_config(page_title="My 6-Month Goal System", page_icon="🎯", layout="wide")
    init_state()
    inject_css()
    render_header()

    view = st.session_state["view"]
    if view == "Goals":
        render_dashboard()
    elif view == "Schedule":
        render_schedule()
    elif view == "Phases":
        render_phases()
    elif view == "Progress":
        render_progress()
    else:
        render_coach()


if __name__ == "__main__":
    main()
