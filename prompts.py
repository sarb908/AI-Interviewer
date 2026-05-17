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