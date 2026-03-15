"""
Evaluator for AI debt-collection call transcripts.
"""
import os
import glob

def load_transcripts(transcripts_dir="transcripts"):
    """
    Loads all transcript text files from the specified directory.
    Returns a dictionary mapping the filename (without extension) to its content.
    """
    transcripts = {}
    
    file_pattern = os.path.join(transcripts_dir, "*")
    for filepath in glob.glob(file_pattern):
        if os.path.isfile(filepath):
            filename = os.path.basename(filepath)
            name_without_ext, _ = os.path.splitext(filename)
            
            # Skip hidden files like .gitkeep
            if filename.startswith('.'):
                continue
                
            with open(filepath, 'r', encoding='utf-8') as f:
                transcripts[name_without_ext] = f.read()
                
    return transcripts

def evaluate_transcript(transcript):
    """
    Scores an AI debt collection call based on a rule-based detection approach.
    
    Returns:
    {
        "score": int (0-100),
        "issues": list,
        "verdict": "good" or "bad"
    }
    """
    score = 0
    issues = []
    
    transcript_lower = transcript.lower()
    
    # Extract only the Agent's lines to avoid scoring based on the Borrower's words
    agent_lines = [
        str(line.split("Agent:", 1)[1].strip())
        for line in transcript.split('\n') 
        if line.startswith("Agent:")
    ]
    agent_text = " ".join(agent_lines).lower()
    
    if not agent_lines:
        return {
            "score": 0,
            "issues": ["No Agent lines found in the transcript."],
            "verdict": "bad"
        }

    # 1. Empathy (20 points): Agent acknowledges borrower problems.
    empathy_keywords = ["understand", "sorry to hear", "apologize", "difficult", "hardship", "make sense", "rough time", "empathize"]
    if any(keyword in agent_text for keyword in empathy_keywords):
        score += 20
    else:
        issues.append("Agent failed to show empathy or acknowledge borrower problems.")

    # 2. Politeness (20 points): Agent tone must be respectful.
    politeness_keywords = ["please", "thank you", "appreciate", "kindly", "thanks", "respect"]
    if any(keyword in agent_text for keyword in politeness_keywords):
        score += 20
    else:
        issues.append("Agent lacked politeness or respectful tone.")

    # 3. Discovery (20 points): Agent asks about borrower situation.
    discovery_keywords = ["current situation", "what happened", "reason", "why", "circumstances", "able to pay", "can you tell me"]
    # Check for keywords or basic question asking
    if any(keyword in agent_text for keyword in discovery_keywords) or "?" in agent_text:
        score += 20
    else:
        issues.append("Agent failed to ask about the borrower's situation (Discovery phase missing).")

    # 4. Negotiation (20 points): Agent offers payment plan or settlement.
    negotiation_keywords = ["payment plan", "settlement", "installments", "options", "offer", "discount", "split", "pay over time", "waive", "flexibility"]
    if any(keyword in agent_text for keyword in negotiation_keywords):
        score += 20
    else:
        issues.append("Agent did not offer a payment plan or settlement options.")

    # 5. Closing (20 points): Agent ends conversation politely.
    closing_keywords = ["have a good day", "goodbye", "bye", "take care", "thank you for your time", "reach out if", "call back"]
    # Usually closing is at the end, but we broadly check the agent's text or specifically the last few lines
    start_idx = max(0, len(agent_lines) - 3)
    last_few_agent_lines_list = []
    for i in range(start_idx, len(agent_lines)):
        last_few_agent_lines_list.append(agent_lines[i])
    last_few_agent_lines = " ".join(last_few_agent_lines_list).lower()
    if any(keyword in last_few_agent_lines for keyword in closing_keywords):
        score += 20
    else:
        issues.append("Agent did not end the conversation politely.")

    verdict = "good" if score >= 80 else "bad"

    return {
        "score": score,
        "issues": issues,
        "verdict": verdict
    }
