import streamlit as st
import openai
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import datetime, timedelta
import time

# API keys
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# In-memory storage for progress tracking
progress_data = {
    "questions_solved": {
        "Behavioral": 0, "Technical": 0, "Situational": 0, "Case Study": 0, "Problem Solving": 0, "All": 0
    },
    "mock_interviews_taken": 0,
    "feedback_provided": 0,
    "tips_retrieved": 0
}

def get_llm(model_choice):
    if model_choice == "Gemini" or model_choice == "Groq":
        return ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY)
    elif model_choice == "OpenAI":
        return None
    else:
        raise ValueError("Unsupported model choice.")

def generate_questions(model_choice, role, question_type, num_questions, difficulty):
    prompt = (
        f"Generate {num_questions} {difficulty} {question_type.lower()} interview questions for the role of {role}. "
        f"Only include {question_type.lower()} questions."
    )
    if model_choice == "OpenAI":
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip().split("\n")
    elif model_choice == "Gemini" or model_choice == "Groq":
        llm = get_llm(model_choice)
        response = llm.invoke(prompt)
        return response.content.split("\n")
    else:
        raise ValueError("Unsupported model choice.")

def get_feedback_and_suggestion(model_choice, question, answer):
    prompt = f"Provide feedback on the following answer for the question: '{question}'. Suggest the most eligible answer."
    if model_choice == "OpenAI":
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    elif model_choice == "Gemini" or model_choice == "Groq":
        llm = get_llm(model_choice)
        response = llm.invoke(prompt)
        return response.content
    else:
        raise ValueError("Unsupported model choice.")

def show_welcome_message():
    st.markdown("""
        <div style="
            text-align: center;
            padding: 20px;
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            font-size: 24px;
            font-weight: bold;
        ">
            Welcome to ProPrep - Your Ultimate Interview Preparation Platform!
        </div>
    """, unsafe_allow_html=True)
    time.sleep(4)  # Display for 4 seconds

def practice_questions():
    st.header("📝 Practice Questions")

    roles = ["Software Engineer", "Data Scientist", "Product Manager", "Designer", "Business Analyst"]
    domains = ["Behavioral", "Technical", "Situational", "Case Study", "Problem Solving"]
    
    role = st.selectbox("Select Role", roles)
    domain = st.selectbox("Select Domain", domains)
    num_questions = st.slider("Number of Questions", min_value=1, max_value=5, value=1)
    model_choice = st.selectbox("Choose Model", ["OpenAI", "Gemini", "Groq"])

    if st.button("Get Practice Question"):
        question = generate_questions(model_choice, role, domain, num_questions, "Medium")[0]  # Get a single question
        st.write(f"**Question:** {question}")

        # Timer for 60 seconds
        countdown_end = datetime.now() + timedelta(seconds=60)
        st.write("You have 60 seconds to answer the question.")
        
        while datetime.now() < countdown_end:
            remaining_time = countdown_end - datetime.now()
            if remaining_time <= timedelta(seconds=10):
                st.write(f"**Time Remaining:** {str(remaining_time).split('.')[0]}")
            time.sleep(1)
        
        answer = st.text_area("Your Answer")
        if st.button("Submit Answer"):
            if not answer:
                st.error("Please enter an answer to receive feedback.")
            else:
                with st.spinner("Providing feedback..."):
                    feedback_and_suggestion = get_feedback_and_suggestion(model_choice, question, answer)
                    st.markdown(f"### Feedback and Suggestions")
                    st.write(feedback_and_suggestion)
                    progress_data["feedback_provided"] += 1

def schedule_mock_interview():
    st.header("🎥 Schedule a Mock Interview")
    st.write("Fill in the details below to schedule your mock interview.")
    
    date = st.date_input("Select Date", min_value=datetime.now().date())
    time_slot = st.time_input("Select Time", value=datetime.now().time())
    email = st.text_input("Enter Your Email")

    if st.button("Schedule Interview"):
        if not email:
            st.error("Please enter your email address.")
        else:
            # This is a placeholder. Implement email sending or calendar integration as needed.
            st.success(f"Mock interview scheduled for {date} at {time_slot}. An email confirmation will be sent to {email}.")
            progress_data["mock_interviews_taken"] += 1

def connect_resources():
    st.header("🔗 Connect with Resources")
    st.write("Here are some useful resources to help you with your interview preparation:")

    resources = {
        "Interview Preparation Guide": "https://in.indeed.com/career-advice/interviewing/interview-preparation",
        "Technical Interview Questions": "https://www.techinterviewhandbook.org/coding-interview-prep",
        "Behavioral Interview Tips": "https://www.themuse.com/advice/behavioral-interview-questions-answers-examples",
        "Mock Interview Platforms": "https://www.preplaced.in/?utm_source=google&utm_medium=cpc&utm_campaign=21494461844&utm_content=167960354791&utm_term=online%20mock%20interview&gad_source=1&gclid=CjwKCAjw_Na1BhAlEiwAM-dm7GsqvdVRJeToj3CJXGuD-4uqtAcCbRv_YPXb63Z_6EaeGR5VQahlJxoCCowQAvD_BwE",
        "Online Courses": "https://www.coursera.org/browse/information-technology"
    }
    for resource_name, resource_link in resources.items():
        st.markdown(f"- [{resource_name}]({resource_link})")

def generate_questions_from_job_description():
    st.header("💼 Generate Questions from Job Description")

    job_description = st.text_area("Paste Job Description Here", height=150)
    model_choice = st.selectbox("Choose Model", ["OpenAI", "Gemini", "Groq"])

    if st.button("Generate Questions"):
        questions = generate_questions(model_choice, "Job Role", "All", 5, "Medium")  # Placeholder for job description
        st.write("### Generated Questions")
        for idx, question in enumerate(questions):
            st.write(f"**{idx + 1}.** {question}")

        # Removed correct answers from here

        progress_data["questions_solved"]["All"] += 1

def main():
    st.set_page_config(page_title="ProPrep - Interview Preparation", layout="wide")
    show_welcome_message()

    menu = ["Generate Questions", "Practice Questions", "Track Progress", "Schedule Mock Interview", "Connect with Resources", "Generate Questions from Job Description"]
    choice = st.sidebar.selectbox("Select an Option", menu)

    if choice == "Generate Questions":
        st.header("🔍 Generate Interview Questions")
        role = st.selectbox("Select Role", ["Software Engineer", "Data Scientist", "Product Manager", "Designer", "Business Analyst"])
        question_type = st.selectbox("Select Question Type", ["Behavioral", "Technical", "Situational", "Case Study", "Problem Solving"])
        difficulty = st.selectbox("Select Difficulty", ["Easy", "Medium", "Hard"])
        num_questions = st.slider("Number of Questions", min_value=1, max_value=10, value=5)
        model_choice = st.selectbox("Choose Model", ["OpenAI", "Gemini", "Groq"])

        if st.button("Generate Questions"):
            questions = generate_questions(model_choice, role, question_type, num_questions, difficulty)
            st.write("### Generated Questions")
            for idx, question in enumerate(questions):
                st.write(f"**{idx + 1}.** {question}")

            # Removed correct answers from here

            progress_data["questions_solved"][question_type] += num_questions

    elif choice == "Practice Questions":
        practice_questions()

    elif choice == "Track Progress":
        st.header("📊 Track Your Progress")
        st.write("Here's your detailed progress data:")
        st.markdown(f"""
        <div style="
            border: 2px solid #2196F3;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
            background-color: #f9f9f9;
            font-size: 16px;
            color: #333;
        ">
            <p><strong>Behavioral Questions Solved:</strong> {progress_data['questions_solved']['Behavioral']}</p>
            <p><strong>Technical Questions Solved:</strong> {progress_data['questions_solved']['Technical']}</p>
            <p><strong>Situational Questions Solved:</strong> {progress_data['questions_solved']['Situational']}</p>
            <p><strong>Case Study Questions Solved:</strong> {progress_data['questions_solved']['Case Study']}</p>
            <p><strong>Problem Solving Questions Solved:</strong> {progress_data['questions_solved']['Problem Solving']}</p>
            <p><strong>Total Questions Solved:</strong> {progress_data['questions_solved']['All']}</p>
            <p><strong>Mock Interviews Taken:</strong> {progress_data['mock_interviews_taken']}</p>
            <p><strong>Feedback Provided:</strong> {progress_data['feedback_provided']}</p>
            <p><strong>Tips Retrieved:</strong> {progress_data['tips_retrieved']}</p>
        </div>
        """, unsafe_allow_html=True)

    elif choice == "Schedule Mock Interview":
        schedule_mock_interview()

    elif choice == "Connect with Resources":
        connect_resources()

    elif choice == "Generate Questions from Job Description":
        generate_questions_from_job_description()

if __name__ == "__main__":
    main()













