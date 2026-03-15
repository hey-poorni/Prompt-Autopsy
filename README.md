# Prompt Autopsy - AI Debt-Collection Call Evaluator

This project analyzes transcripts of an AI debt-collection voice agent used for education loan repayment calls. The conversations typically follow phases like Opening, Discovery, Negotiation, and Closing.

## Goal
The goal of the project is to evaluate how well the AI agent handles these conversations, identify failures caused by issues in the system prompt, and experiment with improved prompts to see if the agent behavior improves. The project also includes a pipeline to test prompts against multiple transcripts and analyze the results.

## Structure
- `detective/`: Tools for evaluating current transcripts.
- `surgeon/`: Tools for rewriting prompts and resimulating calls.
- `pipeline/`: Pipeline for testing new prompts across datasets.
- `results/`: Directory for output and generated analysis.
- `transcripts/`: Directory for storing call transcript logs to evaluate.
