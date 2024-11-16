import streamlit as st
import instructor
from groq import Groq
import time
from models import AssessmentResponse
from shared_utils import init_session_state, render_sidebar


st.set_page_config(page_icon="📝", page_title="Career Assessment", layout="centered")


def get_llm_response(user_input, groq_api_key):
    client = instructor.from_groq(Groq(api_key=groq_api_key), mode=instructor.Mode.JSON)

    system_prompt = """You are a friendly career guidance counselor conducting an assessment with a teenager. 
    Your goal is to gather information about their Abilities, Interests, Knowledge, and Skills (AIKS).

    Guidelines:
    1. Ask engaging questions that are easy for teens to answer
    2. Always provide 2-5 example options they can choose from, don't suggest "Other" vague options, it must be copy-pastable
    3. Keep the tone casual and encouraging
    4. Acknowledge and build upon their previous answers
    5. Use examples and scenarios teens can relate to

    Current AIKS Data:
    {aiks_data}

    Chat History:
    {chat_history}"""

    with st.status("Thinking about your response...", expanded=True) as status:
        status.update(label="Analyzing your interests...")
        response = client.chat.completions.create(
            model=st.session_state.model,
            response_model=AssessmentResponse,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.7,
        )
        status.update(label="Preparing suggestions...", state="complete")

    return response


def process_user_input(user_input):
    # Add user message to chat history first for immediate feedback
    st.session_state.chat_history.append(
        {"role": "user", "content": user_input, "timestamp": time.time()}
    )

    # Get LLM response
    response = get_llm_response(user_input, st.secrets["groq"]["api_key"])

    # Update AIKS data
    for category, items in response.aiks_updates.dict().items():
        if category != "suggested_options":
            st.session_state.aiks_data[category].extend(items)
            st.session_state.aiks_data[category] = list(
                set(st.session_state.aiks_data[category])
            )

    # Add assistant response to chat history
    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": response.next_question,
            "options": response.suggested_options,
            "timestamp": time.time(),
        }
    )

    st.session_state.current_question += 1


def render_suggested_options(options, message_timestamp, container):
    """
    Render suggestion buttons in rows with max 3 columns per row.
    Args:
        options: List of option strings
        message_timestamp: Timestamp for unique keys
        container: Streamlit container to render in
    Returns:
        Selected option or None
    """
    if not options:
        return None

    # Calculate number of rows needed
    COLS_PER_ROW = 3
    num_rows = (len(options) + COLS_PER_ROW - 1) // COLS_PER_ROW

    # Process each row
    for row_idx in range(num_rows):
        # Get options for this row
        start_idx = row_idx * COLS_PER_ROW
        end_idx = min(start_idx + COLS_PER_ROW, len(options))
        row_options = options[start_idx:end_idx]

        # Create columns for this row
        cols = container.columns(len(row_options))

        # Create buttons in the columns
        for col_idx, (col, option) in enumerate(zip(cols, row_options)):
            abs_idx = start_idx + col_idx
            unique_key = f"opt_{message_timestamp}_{abs_idx}"

            if col.button(f"📌 {option}", key=unique_key):
                return option

    return None


def main():
    init_session_state()
    render_sidebar()

    st.title("📝 Career Assessment")
    st.write("""Let's have a casual chat about what interests you! Feel free to share as much or as little as you're comfortable with.
    You can move to viewing career matches at any time.""")

    # Chat container for message history
    chat_container = st.container()

    with chat_container:
        # Display chat history
        for idx, message in enumerate(st.session_state.chat_history):
            is_last_message = idx == len(st.session_state.chat_history) - 1

            if message["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant", avatar="🧑‍💼"):
                    st.write(message["content"])
                    # Show suggested options only for the last assistant message
                    if "options" in message and is_last_message:
                        selected_option = render_suggested_options(
                            message["options"],
                            message.get("timestamp", time.time()),
                            st.container(),
                        )
                        if selected_option:
                            process_user_input(selected_option)
                            st.rerun()

    # Chat input
    if prompt := st.chat_input(
        "Type your answer or choose from the suggestions above..."
    ):
        process_user_input(prompt)
        st.rerun()

    # Initialize chat with first question if empty
    if not st.session_state.chat_history:
        initial_prompt = """Hi! 👋 I'm your career guidance counselor. I'd love to learn more about you 
        to help find careers that match your interests and strengths. 
        Let's start with your interests! What do you enjoy the most?
        Here are some examples:
        """

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": initial_prompt,
                "options": [
                    "I like building, fixing, or working with my hands",
                    "I enjoy solving problems and learning how things work",
                    "I love creating art, music, or writing",
                    "I like helping, teaching, or supporting others",
                    "I'm interested in leading, managing, or starting projects",
                ],
                "timestamp": time.time(),
            }
        )
        st.rerun()


if __name__ == "__main__":
    main()
