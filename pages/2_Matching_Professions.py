import streamlit as st
import instructor
from groq import Groq
from models import ProfessionResponse
from shared_utils import init_session_state, render_sidebar

st.set_page_config(page_icon="💼", page_title="Matching Professions", layout="centered")


def generate_professions(groq_api_key):
    # Check if we already have professions generated
    if "generated_professions" in st.session_state:
        return st.session_state.generated_professions

    client = instructor.from_groq(Groq(api_key=groq_api_key), mode=instructor.Mode.JSON)

    aiks_data = st.session_state.aiks_data
    aiks_summary = "\n".join(
        [
            f"{category.title()}: " + ", ".join(items)
            for category, items in aiks_data.items()
        ]
    )

    with st.spinner("Generating profession matches..."):
        response = client.chat.completions.create(
            model=st.session_state.model,
            response_model=ProfessionResponse,
            messages=[
                {
                    "role": "system",
                    "content": """You are a career advisor assistant. Generate detailed profession matches 
                    based on the user's AIKS profile. For each profession, include a day-in-the-life 
                    example that would appeal to teenagers.""",
                },
                {
                    "role": "user",
                    "content": f"""Based on the following assessment data, suggest the top 5-10 professions 
                    that would be most fulfilling for this person. For each profession, provide:
                    1. A realistic day-in-the-life example
                    2. A brief explanation of the career
                    3. Required skills and education
                    4. How it aligns with their AIKS profile

                    Assessment Data:
                    {aiks_summary}""",
                },
            ],
            temperature=0.7,
        )

        # Store in session state to avoid regenerating
        st.session_state.generated_professions = response.professions
        return response.professions


def handle_feedback(profession_title: str, feedback_value: bool, profession_data: dict):
    """Handle feedback updates using boolean feedback value"""
    if "profession_feedback" not in st.session_state:
        st.session_state.profession_feedback = {}

    st.session_state.profession_feedback[profession_title] = feedback_value

    # Update liked professions based on feedback
    if feedback_value:  # True means thumbs up
        if "liked_professions" not in st.session_state:
            st.session_state.liked_professions = {}
        st.session_state.liked_professions[profession_title] = profession_data
    else:
        # Remove from liked professions if feedback is negative
        st.session_state.liked_professions.pop(profession_title, None)


def profession_card(prof, idx):
    """Render a single profession card"""
    col1, col2 = st.columns([5, 1])

    with col1:
        st.subheader(prof.title)

    with col2:
        # Get current feedback value from session state
        current_feedback = st.session_state.get("profession_feedback", {}).get(
            prof.title, None
        )

        feedback = st.feedback(
            "thumbs",
            key=f"feedback_{idx}_{prof.title}",
        )

        # Handle feedback changes
        if feedback is not None and feedback != current_feedback:
            handle_feedback(prof.title, feedback, prof)

            if feedback:  # If thumbs up
                st.toast(f"✅ Saved {prof.title}")

    st.write(prof.explanation)

    # Day in the Life section
    st.info("📅 **A Day in the Life:**\n" + prof.daily_life_example)

    # Expandable details section
    with st.expander("See Details"):
        st.write("**Required Skills:**")
        for skill in prof.required_skills:
            st.write(f"- {skill}")

        st.write("**Alignment with Your Profile:**")
        for category, alignments in prof.aiks_alignment.items():
            st.write(f"*{category.title()}:* {', '.join(alignments)}")


def main():
    init_session_state()
    render_sidebar()

    st.title("💼 Your Matching Professions")
    st.write("Explore the options below and react with likes ")

    # Assessment summary
    # with st.expander("Your Assessment Summary"):
    #     for category, items in st.session_state.aiks_data.items():
    #         st.write(f"**{category.title()}:** {', '.join(items)}")

    col1, col2 = st.columns(2)

    # Initialize or get professions
    if "generated_professions" not in st.session_state or col1.button(
        "Find New Matches"
    ):
        professions = generate_professions(st.secrets["groq"]["api_key"])
    else:
        professions = st.session_state.generated_professions

    if len(st.session_state.get("liked_professions", {})) > 0:
        if col2.button("View Liked Professions"):
            st.switch_page("pages/3_Liked_Professions.py")

    st.divider()

    # Display professions
    if professions:
        # Filters
        # st.subheader("Filter Professions")
        # col1, col2 = st.columns(2)
        # with col1:
        #     show_liked_only = st.checkbox("Show liked careers only", value=False)
        # with col2:
        #     sort_by = st.selectbox("Sort by:", ["Relevance", "Title A-Z", "Liked First"], index=0)

        # # Apply filters
        # filtered_professions = professions
        # if show_liked_only:
        #     liked_titles = set(st.session_state.get("liked_professions", {}).keys())
        #     filtered_professions = [p for p in professions if p.title in liked_titles]
        #
        # if sort_by == "Title A-Z":
        #     filtered_professions = sorted(filtered_professions, key=lambda x: x.title)
        # elif sort_by == "Liked First":
        #     filtered_professions = sorted(
        #         filtered_professions,
        #         key=lambda x: st.session_state.get("profession_feedback", {}).get(x.title, False),
        #         reverse=True,
        #     )
        filtered_professions = professions

        # Display professions
        for idx, prof in enumerate(filtered_professions):
            profession_card(prof, idx)
            st.divider()


if __name__ == "__main__":
    main()
