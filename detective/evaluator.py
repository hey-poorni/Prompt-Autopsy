"""
Evaluator for AI debt-collection call transcripts.
"""
import os
import glob

def load_transcripts(transcripts_dir="transcripts"):
    """
    Loads all transcript files (.txt or .md) from the specified directory.
    Returns a dictionary mapping the filename (without extension) to its content.
    """
    if not os.path.exists(transcripts_dir):
        print(f"Error: The directory '{transcripts_dir}' does not exist.")
        return {}
        
    if not os.path.isdir(transcripts_dir):
        print(f"Error: '{transcripts_dir}' is not a directory.")
        return {}

    transcripts = {}
    extensions = {".txt", ".md"}
    
    file_pattern = os.path.join(transcripts_dir, "*")
    for filepath in glob.glob(file_pattern):
        if os.path.isfile(filepath):
            filename = os.path.basename(filepath)
            name_without_ext, ext = os.path.splitext(filename)
            
            # Skip hidden files and filter by extension
            if filename.startswith('.') or ext.lower() not in extensions:
                continue
                
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    transcripts[name_without_ext] = f.read()
            except Exception as e:
                print(f"Warning: Could not read file {filepath}: {e}")
                
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
    agent_lines_original = [
        line.strip()
        for line in transcript.split('\n') 
        if line.startswith("Agent:")
    ]
    agent_lines = [
        str(line.split("Agent:", 1)[1].strip())
        for line in agent_lines_original
    ]
    agent_text = " ".join(agent_lines).lower()
    
    if not agent_lines:
        return {
            "score": 0,
            "issues": ["No Agent lines found in the transcript."],
            "verdict": "bad",
            "worst_messages": []
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
        
    # Analyze individual lines for bad behavior to find worst messages
    evaluated_messages = []
    
    # Define negative patterns
    aggressive_keywords = ["police", "arrest", "sue", "legal action", "lawsuit", "must pay now", "immediately", "court", "demand"]
    rude_keywords = ["don't care", "your problem", "shut up", "idiot", "not listening", "excuses", "nonsense", "liar"]
    inflexible_keywords = ["no other way", "only option", "pay in full", "refuse to", "unacceptable", "no choice", "can't help"]
    
    for i in range(len(agent_lines_original)):
        orig_line = agent_lines_original[i]
        line_lower = orig_line.lower()
        
        bad_score = 0
        reasons = []
        
        import re
        # Remove punctuation from the line for clean word boundary matching
        line_clean = re.sub(r'[^\w\s]', '', line_lower)
        line_padded = f" {line_clean} "
        
        if any(f" {w} " in line_padded for w in aggressive_keywords):
            bad_score += 3
            reasons.append("aggressive or threatening tone")
            
        if any(f" {w} " in line_padded for w in rude_keywords):
            bad_score += 3
            reasons.append("disrespectful language")
            
        if any(f" {w} " in line_padded for w in inflexible_keywords):
            bad_score += 2
            reasons.append("inflexible or demanding")
            
        if bad_score > 0:
            evaluated_messages.append({
                "message": orig_line,
                "reason": " and ".join(reasons),
                "bad_score": bad_score
            })
            
    # Sort by bad_score descending and pick top 3
    evaluated_messages.sort(key=lambda x: x["bad_score"], reverse=True)
    worst_messages = [
        {"message": str(msg["message"]), "reason": str(msg["reason"])} 
        for i, msg in enumerate(evaluated_messages) if i < 3
    ]

    verdict = "good" if score >= 80 else "bad"

    return {
        "score": score,
        "issues": issues,
        "verdict": verdict,
        "worst_messages": worst_messages
    }

def compare_verdicts(predicted_verdicts, verdicts_file="verdicts.json"):
    """
    Compares predicted verdicts with actual verdicts stored in the provided json file.
    
    returns: accuracy, correct_predictions, total_calls
    """
    import json
    
    try:
        with open(verdicts_file, 'r', encoding='utf-8') as f:
            file_data = json.load(f)
            actual_verdicts = file_data.get("verdicts", {})
    except Exception as e:
        print(f"Error loading {verdicts_file}: {e}")
        return 0, 0, 0
        
    correct_predictions = 0
    total_calls = 0
    
    for call_id, actual_data in actual_verdicts.items():
        actual_verdict = actual_data.get("verdict") if isinstance(actual_data, dict) else actual_data
        
        if call_id in predicted_verdicts:
            total_calls += 1
            if predicted_verdicts[call_id] == actual_verdict:
                correct_predictions += 1
                
    accuracy = correct_predictions / total_calls if total_calls > 0 else 0
    
    return accuracy, correct_predictions, total_calls
