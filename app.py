import streamlit as st
import pandas as pd
import datetime
import streamlit.components.v1 as components

# --- SYSTEM SETUP ---
st.set_page_config(page_title="AI Multi-Agent System", layout="wide")

if "audit_log" not in st.session_state:
    st.session_state.audit_log = []
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# --- NEW FEATURE: VOICE ALERT FUNCTION ---
def trigger_voice(text):
    # This creates a hidden JavaScript snippet that uses the Browser's Speech API
    js_code = f"""
    <script>
    var msg = new SpeechSynthesisUtterance('{text}');
    window.speechSynthesis.speak(msg);
    </script>
    """
    components.html(js_code, height=0)

def add_log(agent, message, status="ℹ️"):
    st.session_state.audit_log.insert(0, {
        "Time": datetime.datetime.now().strftime("%H:%M:%S"),
        "Agent": agent,
        "Action": message,
        "Status": status
    })

# --- AGENT DEFINITIONS ---

def extraction_agent(text):
    add_log("📝 Extractor", "Scanning transcript for tasks...")
    new_tasks = []
    if "report" in text.lower():
        new_tasks.append({"id": 1, "Task": "Financial Report", "Owner": "Rahul", "Deadline": "Today", "Status": "Pending"})
    if "client" in text.lower():
        new_tasks.append({"id": 2, "Task": "Client Call", "Owner": "Sarah", "Deadline": "2 Hours", "Status": "Pending"})
    return new_tasks

def monitoring_agent():
    add_log("📡 Monitoring", "Checking task pulse and deadlines...")
    for t in st.session_state.tasks:
        if t["Deadline"] == "Today" and t["Status"] == "Pending":
            return t
    return None

def failure_detection_agent(problem_task):
    if problem_task:
        add_log("⚠️ Failure Detector", f"CRITICAL: '{problem_task['Task']}' is at risk!", "❌")
        # VOICE ALERT 1
        trigger_voice(f"Warning. Critical failure detected in {problem_task['Task']}")
        return True
    return False

def self_correction_agent(problem_task):
    add_log("🔄 Self-Correction", f"Re-routing '{problem_task['Task']}' to Backup AI.")
    for t in st.session_state.tasks:
        if t["id"] == problem_task["id"]:
            t["Owner"] = "🤖 Backup-Agent"
            t["Status"] = "Fixed & Processing"
    
    # VOICE ALERT 2
    trigger_voice("Self correction protocol initiated. Task has been reassigned.")
    add_log("🔔 Alert Agent", "Notification sent to Manager.")

# --- UI LAYOUT ---
st.title("🧠 Nexus AI: Agentic Command Center" )
st.markdown("---")

input_text = st.text_area("Step 1: Paste Meeting Transcript", height=100, placeholder="Example: Rahul needs to finish the report today.")

if st.button("🚀 Start Agent Pipeline"):
    st.session_state.tasks = extraction_agent(input_text)
    problem = monitoring_agent()
    if failure_detection_agent(problem):
        self_correction_agent(problem)
    else:
        add_log("✅ Audit Agent", "All tasks verified and healthy.")
        trigger_voice("Workflow processed successfully.")

# Main Dashboard Display
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("📊 Task Manager Dashboard")
    if st.session_state.tasks:
        st.table(pd.DataFrame(st.session_state.tasks))
    else:
        st.write("No active tasks.")

with col2:
    st.subheader("📜 Audit Agent (Live Log)")
    for log in st.session_state.audit_log[:10]:
        st.write(f"**{log['Time']}** [{log['Agent']}] {log['Status']}")
        st.caption(log['Action'])

# Bottom: Simulation Feature
st.markdown("---")
if st.button("⚠️ Simulate Manual Failure"):
    trigger_voice("Emergency Alert. Task deadline missed. Escalating to management.")
    add_log("🔄 Self-Correction", "Manual escalation triggered.")
    st.error("Manual Failure Simulation Active.")