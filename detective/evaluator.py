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

class TranscriptEvaluator:
    def __init__(self):
        pass
    
    def evaluate(self, transcript_path):
        pass
