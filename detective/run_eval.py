"""
Script to run evaluations on transcripts.
"""
import os
import sys
import json

# Ensure the script's directory is in sys.path so it works seamlessly and linters can find 'evaluator'
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from evaluator import load_transcripts, evaluate_transcript  # type: ignore

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
    
    # Compare with verdicts.json if it exists
    verdicts_path = os.path.join(repo_root, "verdicts.json")
    if not os.path.exists(verdicts_path):
        verdicts_path = os.path.join(transcripts_dir, "verdicts.json")
        
    if os.path.exists(verdicts_path):
        from evaluator import compare_verdicts  # type: ignore
        
        # Extract verdict strings from the results dictionary
        predicted_verdicts = {k: v["verdict"] for k, v in results.items()}
        
        accuracy, correct_predictions, total_calls = compare_verdicts(predicted_verdicts, verdicts_path)
        print("\n--- Accuracy Report ---")
        print(f"Total Calls Evaluated vs Verdicts: {total_calls}")
        print(f"Correct Predictions: {correct_predictions}")
        print(f"Accuracy: {accuracy:.2%}")

if __name__ == "__main__":
    main()
