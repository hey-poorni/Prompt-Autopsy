# Prompt Autopsy - AI Debt-Collection Evaluator

## 1. Project Overview
**Prompt Autopsy** is an analytical pipeline designed to evaluate and improve the behavior of an AI debt-collection voice agent. AI agents handling sensitive tasks like education loan repayment must navigate complex conversations across multiple phases (Opening, Discovery, Negotiation, Closing). 

This project analyzes historical conversation transcripts to identify prompt flaws, explain failure points, and iteratively improve the agent's core system prompt for better compliance and effectiveness.

## 2. Project Workflow
The system follows a structured, iterative improvement pipeline:

**Transcripts → Conversation Evaluation → Prompt Diagnosis → Prompt Improvement → Re-evaluation**

- **Transcripts:** Raw, historical conversation logs between the borrower and the AI agent.
- **Conversation Evaluation:** Automated scoring and analysis of the agent's performance based on established criteria.
- **Prompt Diagnosis:** Identifying specific instances where the agent's responses failed, explaining *why*, and tracing it back to the system prompt.
- **Prompt Improvement:** Resolving identified flaws by updating the system prompt (`system-prompt-fixed.md`).
- **Re-evaluation:** Resimulating and re-testing the improved prompt against the historical transcripts to measure accuracy and behavioral improvements.

## 3. Features
- **Transcript Evaluation & Scoring:** Automatically grades the AI agent's performance in real conversational scenarios.
- **Flaw Identification:** Pinpoints problematic agent responses and violations of required conversational phases.
- **Failure Explanation:** Provides detailed explanations of why specific responses failed contextually.
- **Prompt Debugging:** Diagnoses structural or logical issues within the initial system prompt.
- **Automated Pipeline:** End-to-end evaluation pipeline that runs across large datasets of transcripts.
- **Accuracy Comparison:** Validates the pipeline's findings against a ground-truth dataset (`verdicts.json`).
- **Summary Reports:** Automatically generates comprehensive text and JSON reports of the evaluation metrics.

## 4. Project Structure
```text
project-root/
├── detective/               # Tools for evaluating current transcripts (`evaluator.py`)
├── pipeline/                # Automated pipeline scripts (`run_pipeline.py`)
├── surgeon/                 # Tools for rewriting prompts and resimulating calls (`resimulate.py`)
├── results/                 # Output directories for reports and simulated calls
├── transcripts/             # Directory storing raw call transcript logs
├── verdicts.json            # Ground-truth human annotations for accuracy testing
├── system-prompt.md         # The original, flawed AI system prompt
├── system-prompt-fixed.md   # The debugged, improved AI system prompt
└── README.md                # Project documentation
```

## 5. Setup Instructions
To run this project locally, follow these steps:

**Step 1 – Clone the repository**
```bash
git clone https://github.com/yourusername/prompt-autopsy.git
cd prompt-autopsy
```

**Step 2 – Create a virtual environment and install dependencies**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```
*(Note: Ensure you have `google-generativeai` installed if not in a requirements file: `pip install google-generativeai`)*

**Step 3 – Prepare transcripts folder**
Ensure that your historical call transcripts are placed inside the `transcripts/` directory as `.txt` files.

**Step 4 – Configure API keys**
Create a `.env` file in the root directory and add your Google Gemini API key:
```env
GOOGLE_API_KEY="your_api_key_here"
```

## 6. How to Run the Pipeline
To execute the automated evaluation pipeline, run the following command from the project root:

```bash
python pipeline/run_pipeline.py --prompt system-prompt.md --transcripts transcripts/
```

**What this does:**
1. Loads the specified system prompt and reads all `.txt` files in the transcripts directory.
2. Uses an LLM to evaluate the effectiveness of the prompt against the outcomes of the calls.
3. Calculates scores, identifies common failures, and suggests actionable prompt improvements.
4. Generates an output report in the `results/` folder.

## 7. Output
When the pipeline completes, it generates insightful data and outputs:
- **Evaluation Scores:** A calculated average performance score across all analyzed calls.
- **Good vs. Bad Calls:** A clear breakdown of successful interactions versus failed interactions.
- **Accuracy Calculation:** Matches the AI evaluator's findings against manual human annotations (`verdicts.json`).
- **Common Issues Summary:** An aggregated list of frequent behavioral failures identified across the dataset.
- **Result Files:** A `pipeline_report.json` and customized summaries saved to the `results/` folder.

## 8. Prompt Debugging Section
A core focus of this project is prompt engineering and debugging. The pipeline first analyzes the baseline `system-prompt.md` to identify logic gaps, overly rigid constraints, or ambiguous instructions. Based on the evaluation outputs, profound improvements and safeguards are engineered into a new prompt, which is stored securely in `system-prompt-fixed.md`. Resimulating the calls with this corrected prompt yields demonstrably better AI compliance.

## 9. Example Output
```text
==============================
PIPELINE SUMMARY REPORT
==============================
Prompt: system-prompt.md
Avg Score: 68.50
Good Calls: 7
Bad Calls: 3

Common Issues:
- Failed to attempt settlement negotiation before closing.
- Ignored borrower's mention of recent unemployment.

Full report saved to: results\pipeline_report.json

--- Prompt Improvement Suggestions ---
  1. Add explicit instructions for empathetic listening during the Discovery phase.
  2. Implement a mandatory "Offer Installment Plan" step before entering Closing.
```

## 10. Author
**Shri Poornima Alagarsamy**  
*AI/ML Engineer | Prompt Engineer*  
Passionate about building safe, effective, and highly controllable AI agents to solve complex human-in-the-loop problems.
