visual_logs = []

def visual_log(message: str, level: str = "INFO"):
    color_map = {
        "INFO": "#66B2FF",
        "SUCCESS": "#77DD77",
        "WARNING": "orange",
        "ERROR": "red"
    }
    color = color_map.get(level, "black")
    visual_logs.append(f"<span style='color:{color};'>[{level}] {message}</span>")
    if len(visual_logs) > 20:
        visual_logs.pop(0)

def display_logs(st):
    st.subheader("📝 Journaux d'activité")
    for log in visual_logs:
        st.markdown(log, unsafe_allow_html=True)