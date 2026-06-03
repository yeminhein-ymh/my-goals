from __future__ import annotations

from datetime import date, datetime

import streamlit as st


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


def init_state() -> None:
    st.session_state.setdefault("view", "Goals")
    st.session_state.setdefault("notes", {})
    st.session_state.setdefault("coach_messages", [
        {
            "role": "assistant",
            "content": "Hi, I am your goal coach. Ask me what to focus on today, how to plan the week, or how to reduce overload.",
        }
    ])

    for goal in GOALS:
        for task in goal["tasks"]:
            st.session_state.setdefault(f"task_{task['id']}", False)
        for habit in goal["habits"]:
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

    views = ["Goals", "Schedule", "Phases", "Coach"]
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
        task_tab, habit_tab, milestone_tab, notes_tab = st.tabs(["Tasks", "Habits", "Milestones", "Notes"])

        with task_tab:
            st.markdown(f"<div class='mini-label'>Daily time: {goal['dailyTime']}</div>", unsafe_allow_html=True)
            for task in goal["tasks"]:
                st.checkbox(task["text"], key=f"task_{task['id']}")
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

    cols = st.columns(4)
    cols[0].metric("Active goals", "4")
    cols[1].metric("Task progress", f"{total_done}/{total_tasks}")
    cols[2].metric("Daily focus", "3h")
    cols[3].metric("Total runway", "6mo")

    st.write("")
    for goal in GOALS:
        render_goal_card(goal)


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
    else:
        render_coach()


if __name__ == "__main__":
    main()
