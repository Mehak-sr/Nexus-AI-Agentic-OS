import streamlit as st
import pandas as pd
import datetime
import streamlit.components.v1 as components
import time

# --- SYSTEM SETUP ---
st.set_page_config(page_title="Nexus AI | Agentic OS", layout="wide")

if "audit_log" not in st.session_state:
    st.session_state.audit_log = []
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "time_saved" not in st.session_state:
    st.session_state.time_saved = 0
if "ratings" not in st.session_state:
    st.session_state.ratings = {} # Dynamic rating storage

# --- CORE FUNCTIONS ---
def trigger_voice(text):
    js_code = f"<script>var msg = new SpeechSynthesisUtterance('{text}'); window.speechSynthesis.speak(msg);</script>"
    components.html(js_code, height=0)

def add_log(agent, message, status="ℹ️"):
    st.session_state.audit_log.insert(0, {
        "Time": datetime.datetime.now().strftime("%H:%M:%S"),
        "Agent": agent,
        "Action": message,
        "Status": status
    })

def update_rating(name, adjustment):
    current = st.session_state.ratings.get(name, 5.0)
    st.session_state.ratings[name] = round(max(0.0, min(5.0, current + adjustment)), 1)

# --- DYNAMIC AGENTIC LOGIC ---
def extraction_agent(text):
    add_log("📝 Extractor", "Analyzing temporal constraints and urgency...")
    new_tasks = []
    trigger_verbs = ["needs to", "will handle", "must finish", "is assigned to", "to lead"]
    
    # NEW: Keywords that imply the task must happen NOW/SOON
    urgent_keywords = ["today", "2 hours", "3 hours", "hr", "tonight", "immediately", "now"]
    
    sentences = text.replace("!", ".").replace("?", ".").split(".")
    
    for sentence in sentences:
        for verb in trigger_verbs:
            if verb in sentence.lower():
                parts = sentence.lower().split(verb)
                words_before = parts[0].strip().split()
                if not words_before: continue
                name = words_before[-1].capitalize()
                task_raw = parts[1].strip().capitalize()
                
                # NEW: Advanced Deadline Detection
                deadline = "Pending"
                is_urgent = False
                for word in urgent_keywords:
                    if word in sentence.lower():
                        # Capture the specific time mentioned (e.g., '2 hours')
                        if "hour" in sentence.lower() or "hr" in sentence.lower():
                            deadline = "Urgent (Sub-24h)"
                        elif "minute" in sentence.lower() or "min" in sentence.lower():
                            deadline = "Urgent"
                        elif "seconds" in sentence.lower() or "sec" in sentence.lower():
                            deadline = "Urgent"
                        else:
                            deadline = "Today"
                        is_urgent = True
                        break
                
                if name not in st.session_state.ratings:
                    st.session_state.ratings[name] = 5.0
                
                new_tasks.append({
                    "id": len(new_tasks) + 1,
                    "Task": task_raw,
                    "Owner": name,
                    "Deadline": deadline,
                    "Is_Urgent": is_urgent, # Secret flag for the detector
                    "Rating": f"{st.session_state.ratings[name]} ⭐",
                    "Status": "Pending"
                })
                st.session_state.time_saved += 15
                break 
    return new_tasks

def self_correction_agent(problem_task):
    owner = problem_task['Owner']
    add_log("🔄 Self-Correction", f"SLA Violation by {owner}. Downgrading reliability score.")
    update_rating(owner, -0.5)
    
    for t in st.session_state.tasks:
        if t["id"] == problem_task["id"]:
            t["Owner"] = "🤖 Backup-Agent"
            t["Rating"] = 4.5
            t["Status"] = "Fixed & Processing"
    
    st.toast(f"🤖 AI TAKEOVER: {problem_task['Task']} reassigned!", icon="🚀")
    trigger_voice(f"Self correction protocol initiated. Performance rating for {owner} has been downgraded.")

# --- UI DISPLAY ---
st.title("🧠 Nexus AI: Autonomous Agentic OS")

m1, m2, m3 = st.columns(3)
m1.metric("Active Agents", "4", "Ready")
m2.metric("System Health", "100%" if not st.session_state.tasks else "Optimized")
m3.metric("Human Time Saved", f"{st.session_state.time_saved} Mins", "⚡ Efficiency")

st.markdown("---")
input_text = st.text_area("Step 1: Paste Any Meeting Transcript", height=100, 
                          placeholder="Try: 'Alice needs to fix the server today.'")

col1, col2 = st.columns([2, 1])

with col1:
    dashboard_placeholder = st.empty()
    if not st.session_state.tasks:
        dashboard_placeholder.info("Awaiting input to generate dynamic dashboard...")
    else:
        dashboard_placeholder.table(pd.DataFrame(st.session_state.tasks))

with col2:
    st.subheader("📜 Audit Agent")
    if st.session_state.audit_log:
        csv = pd.DataFrame(st.session_state.audit_log).to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Audit History", data=csv, file_name="nexus_audit.csv", mime="text/csv")
    log_placeholder = st.empty()

# --- RUN PIPELINE ---
if st.button("🚀 Start Agent Pipeline"):
    def update_ui():
        with log_placeholder.container():
            for log in st.session_state.audit_log[:8]:
                st.write(f"**[{log['Agent']}]** {log['Status']} - {log['Action']}")
        dashboard_placeholder.table(pd.DataFrame(st.session_state.tasks))

    st.session_state.tasks = extraction_agent(input_text)
    update_ui()
    time.sleep(7) # Demo pause

    for t in st.session_state.tasks:
        # Now it checks the "Is_Urgent" flag instead of just the word "Today"
        if t["Is_Urgent"] and "Agent" not in t["Owner"]:
            add_log("⚠️ Failure Detector", f"SLA Risk: {t['Owner']} has an urgent deadline!", "❌")
            trigger_voice(f"Warning. {t['Owner']} has an immediate deadline. Initiating autonomous backup.")
            update_ui()
            time.sleep(7)
            self_correction_agent(t)
            update_ui()

# --- MANUAL SIMULATOR ---
st.markdown("---")
if st.button("🚨 Simulate Global Failure"):
    trigger_voice("Emergency Alert. Manual intervention triggered. Task deadline missed.")
    add_log("🔄 Self-Correction", "Manual escalation triggered by operator.", "🚨")
    st.error("Global Failure Simulation Active.")