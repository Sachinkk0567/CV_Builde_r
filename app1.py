import streamlit as st
from google import genai
from config import API_KEY

from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

client = genai.Client(api_key=API_KEY)

st.set_page_config(
    page_title="AI Resume Builder",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Resume Builder")

st.sidebar.title("Settings")

model_name = st.sidebar.selectbox(
    "Select Model",
    [
        "gemini-3.5-flash",
        "gemini-2.0-flash",
        "gemini-flash-latest",
        "gemini-pro-latest"
    ]
)

resume_type = st.sidebar.selectbox(
    "Resume Type",
    [
        "Fresher",
        "Experienced",
        "ATS Friendly"
    ]
)

photo = st.file_uploader(
    "Upload Profile Photo (Optional)",
    type=["jpg", "jpeg", "png"]
)

with st.form("resume"):

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    address = st.text_area("Address")

    objective = st.text_area("Career Objective")

    education = st.text_area("Education")

    skills = st.text_area("Skills")

    projects = st.text_area("Projects")

    experience = st.text_area("Experience")

    certifications = st.text_area("Certifications")

    achievements = st.text_area("Achievements")

    languages = st.text_input("Languages")

    generate = st.form_submit_button("Generate Resume")

if generate:

    prompt = f"""
Create a professional {resume_type} resume.

Name:
{name}

Email:
{email}

Phone:
{phone}

Address:
{address}

Career Objective:
{objective}

Education:
{education}

Skills:
{skills}

Projects:
{projects}

Experience:
{experience}

Certifications:
{certifications}

Achievements:
{achievements}

Languages:
{languages}

Use proper headings.
Use bullet points.
Return only the resume.
"""

    with st.spinner("Generating Resume..."):

        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )

    resume = response.text

    st.success("Resume Generated Successfully")

    if photo:
        st.image(photo, width=150)

    st.markdown(resume)

    # Download TXT

    st.download_button(
        "Download TXT",
        resume,
        "resume.txt",
        "text/plain"
    )

    # Create Word File

    doc = Document()

    doc.add_heading("Resume", level=1)

    doc.add_paragraph(resume)

    doc.save("resume.docx")

    with open("resume.docx", "rb") as file:

        st.download_button(
            "Download Word",
            file,
            "resume.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    # Create PDF

    styles = getSampleStyleSheet()

    pdf = SimpleDocTemplate("resume.pdf")

    story = []

    for line in resume.split("\n"):
        story.append(Paragraph(line, styles["BodyText"]))

    pdf.build(story)

    with open("resume.pdf", "rb") as file:

        st.download_button(
            "Download PDF",
            file,
            "resume.pdf",
            "application/pdf"
        )