import openai
import pandas as pd
import os
import streamlit as st
import pandas as pd
import json
import re

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("The OPENAI_API_KEY environment variable is not set.")


def load_inputs(resume_path, job_roles_csv_path):
    """Load resume, personal info, and job roles CSV from files."""
    with open(resume_path, "r") as f:
        resume = f.read()
    job_roles_df = pd.read_csv(job_roles_csv_path)
    job_roles_csv = job_roles_df.to_csv(index=False)
    return resume, job_roles_csv


def create_prompt(resume, job_roles_csv):
    """Construct the prompt for the AI agent including the schema and input data."""
    base_prompt = (
        "You are a highly experienced job compatibility expert. I will provide the following inputs:\n\n"
        "Plaintext Resume: This contains my work experience, education, skills, and other relevant details.\n"
        "Additional Personal Information: Any extra details that might influence job matching.\n"
        "Job Roles Data: A CSV file with detailed information about various job positions.\n\n"
        "Your Task:\n"
        "Analyze the provided inputs and generate a JSON object following the schema below. Each job role in the JSON must include a calculated "
        "compatibilityScore that indicates the likelihood of my success in that role based on my resume and additional data.\n\n"
        "Please ensure that your analysis:\n"
        "- Considers all relevant details from my resume and additional information.\n"
        "- Appropriately weights skills, experience, and qualifications against the job requirements.\n"
        "- Outputs the result strictly as a JSON object conforming to the provided schema.\n\n"
        "You should not give me any other output other than the json file. No padding no text just the json file"
        "JSON Schema:\n"
        "{\n"
        '  "name": "job_listing",\n'
        '  "strict": true,\n'
        '  "schema": {\n'
        '    "type": "object",\n'
        '    "properties": {\n'
        '      "jobs": {\n'
        '        "type": "array",\n'
        '        "description": "A list of job postings.",\n'
        '        "items": {\n'
        '          "type": "object",\n'
        '          "properties": {\n'
        '            "jobTitle": {\n'
        '              "type": "string",\n'
        '              "description": "The title of the job."\n'
        "            },\n"
        '            "url": {\n'
        '              "type": "string",\n'
        '              "description": "The link to the job listing."\n'
        "            },\n"
        '            "company": {\n'
        '              "type": "string",\n'
        '              "description": "The name of the company offering the job."\n'
        "            },\n"
        '            "location": {\n'
        '              "type": "string",\n'
        '              "description": "The location where the job is based."\n'
        "            },\n"
        '            "requirements": {\n'
        '              "type": "string",\n'
        '              "description": "The requirements needed to qualify for the job."\n'
        "            },\n"
        '            "compatibilityScore": {\n'
        '              "type": "number",\n'
        '              "description": "A score indicating the compatibility of the applicant with the job."\n'
        "            },\n"
        '            "notes": {\n'
        '              "type": "string",\n'
        '              "description": "Additional notes related to the job."\n'
        "            }\n"
        "          },\n"
        '          "required": [\n'
        '            "jobTitle",\n'
        '            "company",\n'
        '            "location",\n'
        '            "requirements",\n'
        '            "compatibilityScore",\n'
        '            "notes"\n'
        "          ],\n"
        '          "additionalProperties": false\n'
        "        }\n"
        "      }\n"
        "    },\n"
        '    "required": [\n'
        '      "jobs"\n'
        "    ],\n"
        '    "additionalProperties": false\n'
        "  }\n"
        "}\n"
    )

    # Append the inputs to the prompt for context
    full_prompt = (
        f"{base_prompt}\n---\n"
        f"Resume and personal info:\n{resume}\n\n"
        f"Job Roles CSV:\n{job_roles_csv}\n"
    )
    return full_prompt


def query_ai_agent(prompt):
    """Send the prompt to the AI agent and return the JSON response."""
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful AI agent."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,  # Deterministic response for consistency
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    # Define paths to your input files
    resume_path = "output.txt"
    job_roles_csv_path = "job_roles.csv"

    # Load input data from files
    resume, job_roles_csv = load_inputs(resume_path, job_roles_csv_path)

    # Create the full prompt for the AI agent
    prompt = create_prompt(resume, job_roles_csv)

    # Query the AI agent and print the result
    result = query_ai_agent(prompt)

    if not result:
        raise Exception("Error generating response in the correct format")

    json_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", result, re.DOTALL)
    if json_match:
        result = json_match.group(1)

    data = json.loads(result)
    df = pd.DataFrame(data["jobs"])

    st.markdown(
        """
        <style>
            .stTable {
                width: 100vw;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # st.write(df[["jobTitle", "company", "compatibilityScore"]])
    st.write(df)
