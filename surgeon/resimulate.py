import os
import sys
import json
import glob
import google.generativeai as genai
from pathlib import Path

# Add project root to sys.path to allow imports from detective
repo_root = Path(__file__).parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from detective.evaluator import load_transcripts  # type: ignore

def load_improved_prompt(prompt_path="system-prompt-fixed.md"):
    """Loads the improved system prompt from the markdown file."""
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def extract_borrower_messages(transcript_text):
    """Extracts only the Borrower's messages from the transcript text."""
    borrower_messages = []
    for line in transcript_text.split('\n'):
        if line.startswith("Borrower:"):
            msg = line.replace("Borrower:", "").strip()
            if msg:
                borrower_messages.append(msg)
    return borrower_messages

def resimulate_conversation(borrower_messages, system_prompt):
    """
    Simulates a conversation using Gemini. 
    The agent follows the system prompt and responds to sequential borrower messages.
    """
    # Configure Generative AI
    # Try to load API key from environment or .env file
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        # Fallback: Check for .env file manually
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            with open(env_path, "r") as f:
                for line in f:
                    if line.startswith("GOOGLE_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break

    if not api_key:
        return "ERROR: GOOGLE_API_KEY not found in environment variables or .env file."

    genai.configure(api_key=api_key)
    
    # Check for available models and pick a suitable one
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = 'models/gemini-1.5-flash'
    if target_model not in available_models:
        # Try to find something similar or fallback
        flash_models = [m for m in available_models if 'flash' in m]
        if flash_models:
            target_model = flash_models[0]
        else:
            target_model = 'models/gemini-pro' # Absolute fallback

    model = genai.GenerativeModel(target_model, system_instruction=system_prompt)
    
    chat = model.start_chat(history=[])
    simulated_transcript = []

    # 1. Agent makes the first move (Opening)
    try:
        response = chat.send_message("Please start the call.")
        agent_msg = response.text.strip()
        simulated_transcript.append(f"Agent: {agent_msg}")
    except Exception as e:
        return f"ERROR during initial agent response with {target_model}: {e}"


    # 2. Sequential turns
    for borrower_msg in borrower_messages:
        simulated_transcript.append(f"Borrower: {borrower_msg}")
        try:
            response = chat.send_message(borrower_msg)
            agent_msg = response.text.strip()
            simulated_transcript.append(f"Agent: {agent_msg}")
        except Exception as e:
            simulated_transcript.append(f"ERROR during agent response to '{borrower_msg}': {e}")
            break
            
    return "\n".join(simulated_transcript)

def main():
    repo_root = Path(__file__).parent.parent
    prompt_path = repo_root / "system-prompt-fixed.md"
    transcripts_dir = repo_root / "transcripts"
    results_dir = repo_root / "results"
    
    if not prompt_path.exists():
        print(f"Error: {prompt_path} not found.")
        return

    system_prompt = load_improved_prompt(prompt_path)
    transcripts = load_transcripts(str(transcripts_dir))
    
    if not transcripts:
        print("No transcripts found to resimulate.")
        return

    print(f"Starting resimulation for {len(transcripts)} calls...")
    
    for call_id, content in transcripts.items():
        print(f"Resimulating {call_id}...")
        borrower_msgs = extract_borrower_messages(content)
        
        new_transcript = resimulate_conversation(borrower_msgs, system_prompt)
        
        output_file = results_dir / f"{call_id}_simulated.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(new_transcript)
        
        print(f"Saved to {output_file}")

if __name__ == "__main__":
    main()

