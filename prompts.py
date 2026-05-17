from langchain_core.prompts import PromptTemplate


generate_questions_prompt = PromptTemplate(
    template = """
      You are an expert technical interviewer.

      Generate 5 high-quality interview questions
      Based on
      1. expeirence: {experience}
      2. job role: {job_role}

      Cover a mix of these topics:
      - LLMs
      - Prompt Engineering
      - RAG
      - Embeddings and Vector Databases
      - AI Agents
      - LangChain and LangGraph
      - MCP (Model Context Protocol)
      - Function Calling and Tool Use
      - Evaluation and Observability
      - Guardrails and AI Safety
      - FastAPI and Streaming APIs
      - Redis and Background Workers
      - Docker, Kubernetes, and Cloud Deployment
      - Security and Cost Optimization
      - Production System Design

      Use this difficulty in progressive way

      Return only valid JSON in this format:

        {{
        [{{
        "question": "Question 1",
        "answer": "" # please leave the answer blank, we only need the questions
        "feedback": "" # please leave the feedback blank, we only need the questions  
        }},
        {{
        "question": "Question 2",
        "answer": "" # please leave the answer blank, we only need the questions
        "feedback": "" # please leave the feedback blank, we only need the questions  
        }},

        ]
  
        }}
      Ensure the questions are practical, production-focused, and test both conceptual understanding and hands-on experience.
      """,
    input_variables = ["job_role", "experience"]
    )



answer_prompt = PromptTemplate(
    template ="""You are an expert technical interviewer evaluating a candidate's answer.
INPUT:
Question: {question}
Candidate's Answer: {answer}


Provide a detailed evaluation including:
1. Technical accuracy (1-10)
2. Completeness of answer (1-10)
3. Clarity of explanation (1-10)
4. Specific feedback and suggestions
5. Overall score (1-10)


Format your response as OUTPUT FORMAT: TEXT

""",
    input_variables=["question", "answer"]
)



final_prompt = PromptTemplate(
    input_variables=["candidate_name", "role", "interview_date", "question_evaluations"],
    template="""
You are an expert technical interview report generator for Senior Generative AI Developer interviews.

Your task is to compile all interview question evaluations into a professional and structured final assessment report.

Input Data:
- # data = list(zip(questions, answer,answer_feedback))
- Question Evaluations:
  {data}

Your Responsibilities:
1. Aggregate scores across all questions.
2. Calculate:
   - average_score
   - highest_scoring_categories
   - weakest_categories
   - performance_by_difficulty
3. Summarize:
   - technical strengths
   - technical gaps
   - communication skills
   - architecture and system design ability
   - production readiness
4. Provide a hiring recommendation.

Hiring Recommendation Rules:
- 90–100: Strong Hire
- 80–89: Hire
- 70–79: Lean Hire
- 60–69: Lean No Hire
- 50–59: No Hire
- Below 50: Strong No Hire

Return ONLY valid JSON in the following format:

{{
  "summary": {{
    "total_questions": 10,
    "average_score": 84.6,
    "highest_scoring_categories": [
      "RAG",
      "System Design"
    ],
    "weakest_categories": [
      "Guardrails",
      "MCP"
    ],
    "performance_by_difficulty": {{
      "Easy": 88.5,
      "Medium": 84.2,
      "Hard": 81.7,
      "Expert": 79.4
    }}
  }},
  "strengths": [
    "Strong production experience with RAG and AI agents",
    "Excellent system design and scalability thinking",
    "Clear and structured communication"
  ],
  "areas_for_improvement": [
    "Needs deeper understanding of guardrails and evaluation frameworks",
    "Could improve knowledge of MCP and advanced observability"
  ],
  "overall_assessment": {{
    "technical_depth": "Excellent",
    "system_design": "Strong",
    "communication": "Excellent",
    "production_readiness": "High"
  }},
  "hiring_recommendation": {{
    "decision": "Hire",
    "confidence": "High",
    "reason": "Candidate demonstrated strong end-to-end GenAI development expertise and solid architectural thinking."
  }}
}}

Important Instructions:
- Return only valid JSON.
- Do not include markdown, explanations, or additional text.
- Ensure all numeric scores are calculated from the provided evaluations.
- Keep the report concise, professional, and suitable for hiring managers and technical leadership.
""",
     input_variable = ["data"]
)