# # Build an AI Resume Screener with Python & Llama 3

# ### Installing Ollama and connecting it with Python. Opening in terminal

get_ipython().system('ollama pull llama3')
get_ipython().system('pip install ollama pymupdf')


# ### Step 1: The Reader

import fitz

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


# ### Step 2: The Brain

import ollama

def screen_resume (resume_text, job_description):
    prompt = f"""
    You are a Senior Technical Recruiter with 20 years of experience.
    Your goal is to objectively evaluate a candidate based on a Job |

    JOB DESCRIPTION:
    {job_description}

    CANDIDATE RESUME:
    {resume_text}

    TASK:
    Analyze the resume against the job description. Look for key skills, experience levels and project relevance. 
    Be strict but fair. "React" matches "React.js". "AWS" matches "Amazon Web Services".

    OUTPUT FORMAT:
    Provide the response in valid JSON format only. Do not add any conversational text. 
    structure:
    {{
        "candidate_name": "extract name",
        "match_score":"0-100",
        "key_strenghts": ["list of 3 key strengths"],
        missing_critical_skills": ["List of missing skills"],
        "recommendation": "Interview" or "Reject",
        "reasoning": "A 2-sentence summary of why."
    }}
    """ 

    response = ollama.chat(model='llama3', messages=[
        {'role': 'user', 'content': prompt},
    ])

    return response ['message']['content']


# ### Step 3: The Execution

import json

# 1. Define the Job Description (The Standard)
job_description = """ 
We are looking for a Junior Data Scientist.
Must have:
- Python (Pandas, NumPy, Scikit-Learn)
- Experience with SQL
- Basic understanding of Machine Learning algorithms
- Good communication skills
Nice to have:
- Experience with AWS or Cloud deployment
- Knowledge of NLP
"""

# 2. Load the Resume (The Input)
try:
    resume_text = extract_text_from_pdf("/Users/diegomanssur/Desktop/DataSciencetoAI/AIResumeScreener/DiegoManssur_DataAnalyst_2026.pdf")
    print (f"Resume loaded. Length: {len(resume_text)} characters.")
except Exception as e:
    print (f"Error loading resume:{e}")
    exit()

# 3. The Screening/Processing
print("AI is analyzing the candidate...(this may take a few seconds on a local hardware)")
result_json_string = screen_resume(resume_text, job_description)

#4. Parse and Display Results
try:
    #Cleaning up JSON blocks wrapped by LLM.
    clean_json = result_json_string.replace("```json", "").replace("```", "").strip()
    result_data = json.loads (clean_json)

    print("\n--- SCREENING REPORT ---")
    print(f"Candidate: {result_data.get('candidate_name', 'Unknown')}")
    print(f"Score: {result_data.get('match_score')}/100")
    print(f"Decision: {result_data.get('recommendation').upper()}")

    reasoning = result_data.get('reasoning', [])
    if isinstance(reasoning, list):
        reasoning_text = ' '.join(reasoning)
    else:
        reasoning_text = reasoning

    # Split by periods and create tabbed output
    sentences = [s.strip() for s in reasoning_text.split('.') if s.strip()]
    if sentences:
        print("Reasoning:")
        for sentence in sentences:
            print(f"\t• {sentence}.")

    print(f"Missing Skills: {', '.join(result_data.get('missing_critical_skills', []))}")

except json.JSONDecodeError:
    print("Failed to pase JSON. Raw output:")
    print(result_json_string)
    



# 
