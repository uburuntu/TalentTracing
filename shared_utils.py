# shared_utils.py
import streamlit as st


def init_session_state():
    if "model" not in st.session_state:
        st.session_state.model = "llama-3.2-90b-text-preview"

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "aiks_data" not in st.session_state:
        st.session_state.aiks_data = {
            "abilities": [],
            "interests": [],
            "knowledge": [],
            "skills": [],
        }
    if "assessment_complete" not in st.session_state:
        st.session_state.assessment_complete = False
    if "current_question" not in st.session_state:
        st.session_state.current_question = 0
    if "liked_professions" not in st.session_state:
        st.session_state.liked_professions = {}


def render_sidebar():
    with st.sidebar:
        # User Profile Section
        st.title("👤 Your Profile")

        # AIKS Data visualization
        aiks_data = st.session_state.aiks_data

        # Helper function to create emoji bullets
        def format_list_items(items):
            return (
                "\n".join([f"• {item}" for item in items])
                if items
                else "None identified yet"
            )

        # Abilities Section
        with st.expander("Abilities", expanded=True, icon="💪"):
            if aiks_data["abilities"]:
                st.markdown(format_list_items(aiks_data["abilities"]))
            else:
                st.caption("No abilities identified yet")

        # Interests Section
        with st.expander("Interests", expanded=True, icon="🌟"):
            if aiks_data["interests"]:
                st.markdown(format_list_items(aiks_data["interests"]))
            else:
                st.caption("No interests identified yet")

        # Knowledge Section
        with st.expander("Knowledge", expanded=True, icon="🧠"):
            if aiks_data["knowledge"]:
                st.markdown(format_list_items(aiks_data["knowledge"]))
            else:
                st.caption("No knowledge areas identified yet")

        # Skills Section
        with st.expander("Skills", expanded=True, icon="🛠️"):
            if aiks_data["skills"]:
                st.markdown(format_list_items(aiks_data["skills"]))
            else:
                st.caption("No skills identified yet")

        st.divider()

        # Liked Professions Section
        st.title("💼 Liked Professions")
        liked_profs = st.session_state.get("liked_professions", {})
        if liked_profs:
            for title in liked_profs.keys():
                st.markdown(f"✨ {title}")
        else:
            st.caption("No liked professions yet")

        st.divider()

        # Debug Information (collapsed by default)
        with st.expander("🔧 Debug Information", expanded=False):
            st.subheader("System Settings")

            # Model selection at the top
            st.session_state["model"] = st.selectbox(
                "Choose LLM Model",
                [
                    "llama-3.2-90b-text-preview",
                    "llama-3.2-90b-vision-preview",
                    "llama-3.2-11b-text-preview",
                    "llama-3.2-11b-vision-preview",
                    "llama-3.2-1b-preview",
                    "llama-3.2-3b-preview",
                    "llama3-70b-8192",
                    "llama3-8b-8192",
                ],
                index=0,
            )

            st.divider()

            st.subheader("Session State")
            st.json(
                {
                    k: v
                    for k, v in st.session_state.items()
                    if k not in ["liked_professions", "chat_history"]
                }
            )
