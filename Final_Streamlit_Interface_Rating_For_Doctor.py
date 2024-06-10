import streamlit as st
import pandas as pd
from datetime import datetime
import random

# Load data from the provided Excel file
@st.cache
def load_data():
    file_path = "Fully_Updated_English_Prompt.xlsx"
    data = pd.read_excel(file_path, sheet_name="Sheet1")
    data = data.rename(columns={
        "Formula name": "scenario_category",
        "English Prompt Scenario": "scenario",
        "English_Answers": "answer",
        "Added_Question_Scenario": "modified_question",
        "Added_Question_Answers": "modified_answer"
    })
    return data

data = load_data()
all_scenarios = data.to_dict(orient='records')

# Initialize session state variables if not already initialized
if 'selected_prompts' not in st.session_state:
    st.session_state.selected_prompts = random.sample(all_scenarios, 5)
if 'phase_3_prompts' not in st.session_state:
    st.session_state.phase_3_prompts = random.sample([s for s in all_scenarios if s not in st.session_state.selected_prompts], 5)

# Sign-Up Session
def render_sign_up():
    st.title("Medsense Survey Interface Rating from Doctor")
    st.subheader("Sign-Up")
    name = st.text_input("Name")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Sign Up"):
        if not name or not username or not password:
            st.error("Please fill all the fields")
        else:
            st.session_state.user = {"name": name, "username": username, "password": password}
            st.success(f"Welcome, {name}!")
            st.session_state.page = 'phase_1'

# Phase 1: Initial Prompt Generation
def render_phase_1():
    st.subheader("Phase 1: Initial Prompt Evaluation")
    selected_scenario = random.choice(all_scenarios)
    st.info(f"**Scenario Category:** {selected_scenario['scenario_category']}")
    st.info(f"**Example of the Scenario:**  {selected_scenario['scenario']}")
    prompt_question = st.text_input("Enter your initial prompt question:")
    prompt_response = st.text_area("Enter your response/answers for the initial prompt:")

    if st.button('Submit Initial Response'):
        st.session_state.initial_responses = st.session_state.get('initial_responses', [])
        st.session_state.initial_responses.append({
            'user': st.session_state.user['username'],
            'phase': 'Phase 1',
            'scenario': selected_scenario['scenario'],
            'prompt_question': prompt_question,
            'prompt_response': prompt_response,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.success('Initial response submitted!')
        
        if len(st.session_state.initial_responses) >= 10:  # Assuming 10 submissions per Phase 1
            st.session_state.page = 'phase_2'
        else:
            st.experimental_rerun()

# Phase 2: Evaluate Randomized Scenarios
def render_phase_2():
    st.subheader("Phase 2: Evaluate Randomized Scenarios")
    if 'current_scenario_index' not in st.session_state:
        st.session_state.current_scenario_index = 0
        st.session_state.responses = []

    prompt = st.session_state.selected_prompts[st.session_state.current_scenario_index]
    #st.markdown(f"### Scenario: {prompt['scenario_category']}")
    with st.container():
        #st.write(f"**Scenario Category:** {prompt['scenario_category']}")
        st.write(f"**Original Question:** {prompt['scenario']}")
        st.write(f"**Original Answer:** {prompt['answer']}")
        rating_orig = st.slider('Rate the original answer:', 1, 5, key=f"rating_orig_{prompt['scenario']}")
        response_orig = st.text_area("Your Answer on the original prompt (The answer supposed to be):", key=f"response_orig_{prompt['scenario']}")

        st.write(f"**Modified Question:** {prompt['modified_question']}")
        st.write(f"**Modified Answer:** {prompt['modified_answer']}")
        rating_mod = st.slider('Rate the modified answer:', 1, 5, key=f"rating_mod_{prompt['scenario']}")
        response_mod = st.text_area("Your Answer on the modified prompt (The answer supposed to be):", key=f"response_mod_{prompt['scenario']}")

    if st.button('Next Scenario'):
        st.session_state.responses.append({
            'user': st.session_state.user['username'],
            'scenario': prompt['scenario'],
            'original_rating': rating_orig,
            'original_response': response_orig,
            'modified_rating': rating_mod,
            'modified_response': response_mod,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        if st.session_state.current_scenario_index < len(st.session_state.selected_prompts) - 1:
            st.session_state.current_scenario_index += 1
        else:
            save_data_to_files(st.session_state.responses, "Phase_2_3_Responses")
            st.success("Thank you for completing all scenarios.")
            st.session_state.page = 'phase_3'

# Phase 3: Similar to Phase 1 but with different scenarios
def render_phase_3():
    st.subheader("Phase 3: Create Prompts for New Scenarios")
    if 'current_phase_3_index' not in st.session_state:
        st.session_state.current_phase_3_index = 0
        st.session_state.phase_3_responses = []

    prompt = st.session_state.phase_3_prompts[st.session_state.current_phase_3_index]
    st.markdown(f"### Example of the Scenario: {prompt['scenario']}")
    prompt_question = st.text_input("Enter your prompt question for this scenario:", key=f"prompt_question_phase3_{prompt['scenario']}")
    prompt_response = st.text_area("Enter your response to the prompt:", key=f"prompt_response_phase3_{prompt['scenario']}")

    if st.button('Next Scenario (Phase 3)'):
        st.session_state.phase_3_responses.append({
            'user': st.session_state.user['username'],
            'scenario': prompt['scenario'],
            'prompt_question': prompt_question,
            'prompt_response': prompt_response,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        if st.session_state.current_phase_3_index < len(st.session_state.phase_3_prompts) - 1:
            st.session_state.current_phase_3_index += 1
        else:
            save_data_to_files(st.session_state.phase_3_responses, "Phase_2_3_Responses")
            st.success("Thank you for completing all scenarios.")
            st.session_state.page = 'completed'

    feedback = st.text_area("General feedback on the scenarios:")
    satisfaction = st.slider("Overall satisfaction with the process:", 1, 5, 3)

    if st.button("Submit Feedback"):
        feedback_data = {
            'user': st.session_state.user['username'],
            'phase': 'Phase 3',
            'feedback': feedback,
            'satisfaction': satisfaction,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_data_to_files([feedback_data], "Phase_2_3_Responses")
        st.success("Thank you for your feedback!")

# Function to save data
def save_data_to_files(data, filename):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    for entry in data:
        entry['timestamp'] = timestamp

    # Save to Excel
    df = pd.DataFrame(data)
    df.to_excel(f'{filename}.xlsx', index=False)
    
    # Save to TXT
    with open(f'{filename}.txt', 'a') as file:
        for entry in data:
            file.write(f"{entry}\n")

# Navigation and session state management
st.sidebar.title("Navigation")
if 'user' not in st.session_state:
    st.session_state.page = 'sign_up'

st.sidebar.button("Go to Sign Up", on_click=lambda: st.session_state.update({"page": "sign_up"}))
st.sidebar.button("Go to Phase 1", on_click=lambda: st.session_state.update({"page": "phase_1"}))
st.sidebar.button("Go to Phase 2", on_click=lambda: st.session_state.update({"page": "phase_2"}))
st.sidebar.button("Go to Phase 3", on_click=lambda: st.session_state.update({"page": "phase_3"}))

if 'page' not in st.session_state:
    st.session_state.page = 'sign_up'

if st.session_state.page == 'sign_up':
    render_sign_up()
elif st.session_state.page == 'phase_1':
    render_phase_1()
elif st.session_state.page == 'phase_2':
    render_phase_2()
elif st.session_state.page == 'phase_3':
    render_phase_3()
else:
    st.write("Thank you for participating in the study!")
