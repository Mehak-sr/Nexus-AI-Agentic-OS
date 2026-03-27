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

# --- VOICE ALERT FUNCTION ---
def trigger_voice(text):
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
        trigger_voice(f"Warning. Critical failure detected in {problem_task['Task']}")
        return True
    return False

def self_correction_agent(problem_task):
    add_log("🔄 Self-Correction", f"Re-routing '{problem_task['Task']}' to Backup AI.")
    for t in st.session_state.tasks:
        if t["id"] == problem_task["id"]:
            t["Owner"] = "🤖 Backup-Agent"
            t["Status"] = "Fixed & Processing"
    
    trigger_voice("Self correction protocol initiated. Task has been reassigned.")
    add_log("🔔 Alert Agent", "Notification sent to Manager.")

# --- UI HEADER ---
st.title("🧠 Nexus AI: Agentic Command Center")
st.markdown("---")

input_text = st.text_area("Step 1: Paste Meeting Transcript", height=100, placeholder="Example: Rahul needs to finish the report today.")

# --- MAIN UI DISPLAY COLUMNS ---
col1, col2 = st.columns([2, 1])

with col1:
    dashboard_placeholder = st.empty() 
    if not st.session_state.tasks:
        with dashboard_placeholder.container():
            st.subheader("📊 Task Manager Dashboard")
            st.info("Awaiting meeting transcript to generate task objects...")
    else:
        with dashboard_placeholder.container():
            st.subheader("📊 Task Manager Dashboard")
            st.table(pd.DataFrame(st.session_state.tasks))

with col2:
    st.subheader("📜 Audit Agent (Live Log)")
    # This placeholder allows us to update the log in real-time
    log_placeholder = st.empty() 
    
    # Show existing logs if any
    with log_placeholder.container():
        for log in st.session_state.audit_log[:10]:
            st.write(f"**{log['Time']}** [{log['Agent']}] {log['Status']}")
            st.caption(log['Action'])

# --- PIPELINE LOGIC ---
if st.button("🚀 Start Agent Pipeline"):
    # Function to refresh the log window manually during the loop
    def update_ui():
        with log_placeholder.container():
            for log in st.session_state.audit_log[:10]:
                st.write(f"**{log['Time']}** [{log['Agent']}] {log['Status']}")
                st.caption(log['Action'])
        with dashboard_placeholder.container():
            st.subheader("📊 Task Manager Dashboard")
            st.table(pd.DataFrame(st.session_state.tasks))

    # PHASE 1: EXTRACTION
    st.session_state.tasks = extraction_agent(input_text)
    update_ui()
    
    add_log("⚙️ System", "Initial extraction complete. Monitoring workloads...")
    update_ui()
    
    time.sleep(3) 

    # PHASE 2: MONITORING & CORRECTION
    problem = monitoring_agent()
    update_ui()
    
    if failure_detection_agent(problem):
        update_ui()
        trigger_voice(f"Warning. Failure detected in {problem['Task']}. Reassigning.")
        time.sleep(2) 
        
        self_correction_agent(problem)
        update_ui()
            
        st.success("✅ Self-Correction Successful: System Stabilized.")
    else:
        add_log("✅ Audit Agent", "All tasks verified and healthy.")
        update_ui()
        trigger_voice("Workflow processed successfully.")

# Bottom: Simulation Feature
st.markdown("---")
if st.button("⚠️ Simulate Manual Failure"):
    trigger_voice("Emergency Alert. Task deadline missed. Escalating to management.")
    add_log("🔄 Self-Correction", "Manual escalation triggered.")
    st.error("Manual Failure Simulation Active.")
    # Quick refresh for manual button
    with log_placeholder.container():
        for log in st.session_state.audit_log[:10]:
            st.write(f"**{log['Time']}** [{log['Agent']}] {log['Status']}")
            st.caption(log['Action'])