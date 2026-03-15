"""
Script to run evaluations on transcripts.
"""
import os
import sys
import json

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detective.evaluator import load_transcripts, evaluate_transcript

def main():
    # Setup path relative to the script location assuming it's run from repo root
    # Use abspath to reliably find the project root whether run from inside `detective/` or from repo root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    
    transcripts_dir = os.path.join(repo_root, "transcripts")
    results_dir = os.path.join(repo_root, "results")
    
    transcripts = load_transcripts(transcripts_dir)
    results = {}
    
    for call_id, content in transcripts.items():
        eval_result = evaluate_transcript(content)
        results[call_id] = eval_result
        
    os.makedirs(results_dir, exist_ok=True)
    output_path = os.path.join(results_dir, "evaluation_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
        
    print(f"Evaluations completed. Results saved to {output_path}")

if __name__ == "__main__":
    main()
