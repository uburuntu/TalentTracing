# pages/3_Liked_Professions.py
from openai import OpenAI
import streamlit as st
import instructor
from groq import Groq
from pydantic import BaseModel
from shared_utils import init_session_state, render_sidebar

st.set_page_config(page_icon="💼", page_title="Liked Professions", layout="centered")


class ChatResponse(BaseModel):
    """Model for career advice chat responses"""

    content: str
    tone: str = "friendly"
    focus_areas: list[str] = []


def get_suggested_questions(title: str) -> list[str]:
    """Get list of suggested questions for a profession"""
    return [
        "What education or training do I need?",
        "What's a typical work day like?",
        "What skills are most important?",
        "What companies are hiring?",
        "What's the salary range?",
        "What are the challenges?",
    ]


def render_question_buttons(title: str, container):
    """Render suggested questions as buttons in a grid"""
    questions = get_suggested_questions(title)

    # Calculate number of rows needed (2 buttons per row)
    BUTTONS_PER_ROW = 2
    num_rows = (len(questions) + BUTTONS_PER_ROW - 1) // BUTTONS_PER_ROW

    # Create buttons grid
    for row_idx in range(num_rows):
        cols = container.columns(BUTTONS_PER_ROW)
        start_idx = row_idx * BUTTONS_PER_ROW
        end_idx = min(start_idx + BUTTONS_PER_ROW, len(questions))

        for col_idx, question in enumerate(questions[start_idx:end_idx]):
            if cols[col_idx].button(
                f"❓ {question}",
                key=f"q_button_{title}_{start_idx + col_idx}",
                use_container_width=True,
            ):
                return question
    return None


def get_profession_chat_response(
    profession_title: str, question: str, groq_api_key: str
) -> str:
    client = instructor.from_groq(Groq(api_key=groq_api_key), mode=instructor.Mode.JSON)

    prompt = f"""As a career counselor specialized in {profession_title}, provide detailed, 
    practical answers to questions about this career. Base your responses on real-world experience 
    and current industry knowledge. Keep answers relevant and engaging for teenagers. 
    Respond in markdown format, make text readable by formatting. Make UK specific answers.

    Previous context:
    {st.session_state.liked_professions[profession_title].daily_life_example}

    Question: {question}"""

    with st.status("Getting answer...", expanded=True):
        response = client.chat.completions.create(
            model=st.session_state.model,
            response_model=ChatResponse,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": question},
            ],
            temperature=0.7,
        )

    return response.content


def render_chat_interface(title, prof):
    """Render chat interface for a specific profession"""
    st.header(title)
    st.write(prof.explanation)

    # col1, col2 = st.columns(2)
    st.info("📅 **A Day in the Life:**\n" + prof.daily_life_example)

    # # Generate and display profession image
    # if "profession_image" not in st.session_state:
    #     st.session_state.profession_image = {}

    # if title in st.session_state.profession_image:
    #     col2.image(st.session_state.profession_image[title])
    # else:
    #     with col2.status("Generating profession visualization...", expanded=True):
    #         client = OpenAI(api_key=st.secrets["openai"]["api_key"])
    #         prompt = f"A realistic photo showing a day in the life of a {title} at work, professional setting, natural lighting"
    #         response = client.images.generate(
    #             model="dall-e-2", prompt=prompt, size="256x256", style="natural"
    #         )
    #         st.session_state.profession_image[title] = response.data[0].url

    # Initialize chat history for this profession if not exists
    if f"chat_history_{title}" not in st.session_state:
        st.session_state[f"chat_history_{title}"] = []
        # Add initial welcome message
        st.session_state[f"chat_history_{title}"].append(
            {
                "role": "assistant",
                "content": f"""Hi! 👋 I'm your advisor for {title} career. 
            Feel free to ask me anything about this path! 
            Choose a question below or type your own:""",
            }
        )

    # Display chat messages
    messages = st.session_state[f"chat_history_{title}"]

    # Chat container
    chat_container = st.container()
    with chat_container:
        for msg in messages:
            with st.chat_message(
                msg["role"], avatar="👤" if msg["role"] == "user" else "🧑‍💼"
            ):
                st.markdown(msg["content"])

    # Show question buttons
    with st.container():
        selected_question = render_question_buttons(title, st.container())
        if selected_question:
            # Add user message
            st.session_state[f"chat_history_{title}"].append(
                {"role": "user", "content": selected_question}
            )

            # Get and add assistant response
            response = get_profession_chat_response(
                title, selected_question, st.secrets["groq"]["api_key"]
            )
            st.session_state[f"chat_history_{title}"].append(
                {"role": "assistant", "content": response}
            )
            st.rerun()

    # Chat input
    if prompt := st.chat_input(
        f"Ask anything about {title} career...", key=f"chat_input_{title}"
    ):
        # Add user message
        st.session_state[f"chat_history_{title}"].append(
            {"role": "user", "content": prompt}
        )

        # Get and add assistant response
        with st.chat_message("assistant", avatar="🧑‍💼"):
            response = get_profession_chat_response(
                title, prompt, st.secrets["groq"]["api_key"]
            )
            st.markdown(response)
            st.session_state[f"chat_history_{title}"].append(
                {"role": "assistant", "content": response}
            )
        st.rerun()


def main():
    init_session_state()
    render_sidebar()

    st.title("💛 Your Liked Professions")

    if not st.session_state.get("liked_professions"):
        st.info(
            "You haven't liked any professions yet! Go back to the professions page to explore options."
        )
        if st.button("View All Matching Professions"):
            st.switch_page("pages/2_Matching_Professions.py")
        return

    # Profession selector
    profession_titles = list(st.session_state.liked_professions.keys())
    if len(profession_titles) > 1:
        selected_profession = st.selectbox(
            "Select a profession to chat about:",
            profession_titles,
            index=0,
            format_func=lambda x: f"{x}",
        )
    else:
        selected_profession = profession_titles[0]

    # Render chat interface for selected profession
    prof = st.session_state.liked_professions[selected_profession]
    render_chat_interface(selected_profession, prof)


if __name__ == "__main__":
    main()
