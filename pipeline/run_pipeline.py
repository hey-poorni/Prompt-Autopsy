import os
import sys
import json
import argparse
from pathlib import Path
from collections import Counter
import time

# Add project root to sys.path
_repo_root = Path(__file__).parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

# Import existing logic
from detective.evaluator import load_transcripts, evaluate_transcript # type: ignore
from surgeon.resimulate import extract_borrower_messages, resimulate_conversation # type: ignore

def main():
    parser = argparse.ArgumentParser(description="AI Prompt Evaluation Pipeline")
    parser.add_argument("--prompt", type=str, required=True, help="Path to the system prompt markdown file")
    parser.add_argument("--transcripts", type=str, required=True, help="Path to the folder containing transcript text files")
    parser.add_argument("--output", type=str, default="results/pipeline_report.json", help="Path to save the final report")
    
    args = parser.parse_args()
    
    prompt_path = Path(args.prompt)
    transcripts_dir = Path(args.transcripts)
    output_path = Path(args.output)
    
    if not prompt_path.exists():
        print(f"Error: Prompt file {prompt_path} not found.")
        return
    if not transcripts_dir.exists():
        print(f"Error: Transcripts directory {transcripts_dir} not found.")
        return

    # 1. Load system prompt
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_prompt = f.read()

    # 2. Load all transcripts
    # Ensure transcripts_dir is absolute relative to project root for robustness
    if not transcripts_dir.is_absolute():
        transcripts_dir = (_repo_root / transcripts_dir).resolve()

    print(f"Resolved transcripts folder path: {transcripts_dir}")
    
    # Use the existing function but ensures we pass the correct absolute path
    transcripts = load_transcripts(str(transcripts_dir))
    
    if not transcripts:
        print(f"Error: No valid transcript files (.txt, .md) found in '{transcripts_dir}'.")
        print("Please check the folder path and ensure it contains the correct files.")
        return

    print(f"Loaded transcripts: {len(transcripts)}")
    print(f"Detected filenames: {', '.join(transcripts.keys())}")
    print("Starting simulation and evaluation...")

    results = []
    total_score: float = 0
    good_calls: int = 0
    bad_calls: int = 0
    all_issues: list[str] = []

    for call_id, original_content in transcripts.items():
        print(f"Processing {call_id}...")
        
        # 3. Simulate agent responses using LLM
        borrower_msgs = extract_borrower_messages(original_content)
        new_transcript = resimulate_conversation(borrower_msgs, system_prompt)
        
        if new_transcript.startswith("ERROR"):
            print(f"  Simulation failed for {call_id}: {new_transcript}")
            continue

        # 4. & 5. Evaluate results
        eval_result = evaluate_transcript(new_transcript)
        
        # Track stats
        total_score = total_score + eval_result["score"] # type: ignore
        if eval_result.get("verdict") == "good":
            good_calls = good_calls + 1 # type: ignore
        else:
            bad_calls = bad_calls + 1 # type: ignore
            
        current_issues = eval_result.get("issues", [])
        all_issues.extend(current_issues)
        
        # Add a small delay to avoid hitting rate limits too quickly
        time.sleep(1)
        
        results.append({
            "call_id": call_id,
            "score": eval_result["score"],
            "verdict": eval_result["verdict"],
            "issues": eval_result["issues"],
            "simulated_transcript": new_transcript
        })

    # 6. Generate summary report
    num_processed = len(results)
    avg_score = total_score / num_processed if num_processed > 0 else 0
    common_issues = [issue for issue, count in Counter(all_issues).most_common(5)]

    report = {
        "summary": {
            "prompt_used": str(prompt_path),
            "total_calls_processed": num_processed,
            "average_score": avg_score,
            "good_calls": good_calls,
            "bad_calls": bad_calls,
            "common_issues": common_issues
        },
        "details": results
    }

    # Save final report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    print("\n" + "="*30)
    print("PIPELINE SUMMARY REPORT")
    print("="*30)
    print(f"Prompt: {prompt_path.name}")
    print(f"Avg Score: {avg_score:.2f}")
    print(f"Good Calls: {good_calls}")
    print(f"Bad Calls: {bad_calls}")
    print(f"Common Issues: {', '.join(common_issues) if common_issues else 'None'}")
    print(f"Full report saved to: {output_path}")

if __name__ == "__main__":
    main()

