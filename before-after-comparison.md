# Before vs After — Prompt Improvement Comparison

## Context

This document compares **original agent behavior** (from `transcripts/`) against **expected behavior** 
under the improved system prompt (`system-prompt-fixed.md`), using the evaluation scores from 
`results/evaluation_results.json` as the objective measure.

> **Note:** The Gemini API re-simulated files in `results/call_XX_simulated.txt` encountered quota limits 
> during this session. The "After" column below represents the expected behavior based on the explicit 
> improvements defined in `system-prompt-fixed.md`, cross-referenced with evaluator scores from the 
> dry-run evaluation.

---

## Score Summary: Before vs After (Dry Run)

| Call | Original Score | Verdict | Issues Detected |
|------|---------------|---------|-----------------|
| call_01 | 80 | good | No polite closing |
| call_02 | **40** | **bad** | No politeness, no payment plan, no closing |
| call_03 | 60 | bad | No payment plan, no closing |
| call_04 | 100 | good | None |
| call_05 | 80 | good | No polite closing |
| call_06 | 80 | good | No payment plan offered |
| call_07 | **60** | **bad** | No payment plan, no closing |
| call_08 | **40** | **bad** | No politeness, no payment plan, no closing |
| call_09 | 100 | good | None |
| call_10 | 80 | good | No polite closing |

**Overall:** Average = 72/100 | Good: 6 | Bad: 4

---

## Call 02 — Before vs After (Worst Case, Score: 40)

### Context
A widow whose late husband had taken the loan. She requested Hindi conversation multiple times, but the agent kept switching to English.

### BEFORE (Original Prompt — Score: 40/100)

**Issue 1 — Reverts to English after being explicitly asked to speak Hindi:**
```
Borrower: मैं बार बार request कर रही हूं आपको हिंदी में बात करिए, लेकिन आप english 
          में repeat करे चले जा रहे हैं.
Agent:    मुझे माफ़ करना, मैं आपकी बात समझ गया हूँ। 
          [Agent then reverts to English in the very next paragraph]
```

**Issue 2 — Pivots to credit score threats immediately after learning of husband's death:**
```
Borrower: उनकी seventh March 2025 को death हो गई है.
Agent:    I am so sorry to hear about your husband's passing... I want to clarify 
          that even though there's a dispute, at six hundred and sixty-eight days 
          past due, every month adds another negative entry to the credit report.
```

**Issue 3 — No payment plan or settlement offered despite borrower showing willingness:**
```
Borrower: हां मुझे यह बताए... दो सौ रुपए payment भेज सकती हूं
Agent:    [Ignores the partial payment offer, continues asking about documents]
```

**Issue 4 — Call ends abruptly with no polite closing:**
```
Agent: जी, मैं अभी 1:15 पर कॉलबैक शेड्यूल करने की कोशिश करता हूँ। 
       इस बातचीत के लिए धन्यवाद। नमस्कार।
[Borrower responds with "जी?" — agent has already ended]
```

### AFTER (Improved Prompt — Expected Behavior)

Under `system-prompt-fixed.md`, the improved agent would:

1. **Language detection**: Immediately switch to Hindi at the first request and never revert.
   ```
   Expected: "बिल्कुल, मैं आपसे हिंदी में ही बात करूँगा। कृपया जारी रखें।"
   [Stays in Hindi for the rest of the call]
   ```

2. **Empathy before business**: Pause all financial discussion upon learning of the death and acknowledge it fully.
   ```
   Expected: "आपके पति के निधन की खबर सुनकर मुझे बहुत दुख हुआ। 
   यह सुनकर बहुत कठिन समय रहा होगा। इस विषय को हम बाद में discuss करें —
   पहले मुझे बताएं कि आपको कैसे help कर सकते हैं।"
   ```

3. **Acknowledge partial payment willingness**: Accept the ₹200 offer and guide constructively.
   ```
   Expected: "बिल्कुल, हम इसे एक छोटे से पहले कदम के रूप में देख सकते हैं। 
   क्या आप चाहती हैं कि हम एक installment plan बनाएं?"
   ```

4. **Polite closing**: Confirm callback warmly.
   ```
   Expected: "ठीक है, मैंने आपके लिए 1:15 बजे callback schedule कर दिया है। 
   आपसे बात करके अच्छा लगा। अपना ख्याल रखिए। नमस्ते।"
   ```

**Expected Improvement: 40 → 80 (+40 points)**

---

## Call 07 — Before vs After (Language Collapse, Score: 60)

### Context
Tamil-speaking borrower who could not communicate clearly in any language. Call ended with zero resolution.

### BEFORE (Original Prompt — Score: 60/100)

**Issue 1 — Repeats the loan amount 7+ times instead of adapting:**
```
Agent: I'm calling about your DemoLender loan. There's fifty-five thousand... [line 10]
Agent: I'm calling about your DemoLender loan. There's fifty-five thousand... [line 17]
Agent: ...there's a pending amount of fifty-five thousand... [line 19]
Agent: ...there's a pending amount of fifty-five thousand... [line 22]
```

**Issue 2 — No payment plan or alternative offered:**
```
[Entire call: agent never mentions payment options, installments, or settlement]
```

**Issue 3 — Call ends with no resolution or callback scheduled:**
```
[Line 60 — call abruptly ends mid-sentence with no polite close, no callback]
```

### AFTER (Improved Prompt — Expected Behavior)

1. **Limit repetition**: After 2 failed attempts to communicate, pivot to a new approach.
   ```
   Expected: "I understand communication may be difficult right now. 
   Would it be easier if we scheduled a callback with a Tamil-speaking colleague?"
   ```

2. **Offer a payment plan**: Even if the borrower can't engage, state the option.
   ```
   Expected: "We have flexible payment options available if that helps. 
   I can send you the details by SMS."
   ```

3. **Polite closing**: Schedule callback and close respectfully.
   ```
   Expected: "Thank you for taking the time to speak with me. 
   I'll arrange for someone to call you back. Have a good day."
   ```

**Expected Improvement: 60 → 80–100 (+20–40 points)**

---

## Call 08 — Before vs After (Wrong-Number/Short Call, Score: 40)

### Context
Very short call where the borrower responded with only "Hello?" and "Arthur" (a different name), indicating a wrong number. Agent handled it without any politeness or proper closing.

### BEFORE (Original Prompt — Score: 40/100)

**Issue 1 — No polite language, no respectful tone detected:**
```
Agent: Are you still there?
Agent: Hello?
Agent: Okay, I understand. It seems I have reached the wrong person. 
       I will go ahead and end this call.
```
*(No "please", "thank you", "sorry for the inconvenience" — Politeness score: 0/20)*

**Issue 2 — No payment plan or closing attempt:**
```
[Call ends at line 17 with no offer, no options, no warm close]
```

### AFTER (Improved Prompt — Expected Behavior)

1. **Politeness on wrong number:**
   ```
   Expected: "I'm sorry to have bothered you. Thank you for letting me know. 
   I hope you have a great day. Goodbye!"
   ```

2. **Proper end-call:**
   ```
   Expected: Calls end_call("wrong_party") with a polite spoken goodbye first.
   ```

**Expected Improvement: 40 → 80 (+40 points)**

---

## Overall Improvement Summary

| Call | Before Score | After Score (Expected) | Delta |
|------|-------------|----------------------|-------|
| call_02 | 40 | ~80 | **+40** |
| call_03 | 60 | ~80 | **+20** |
| call_07 | 60 | ~80–100 | **+20–40** |
| call_08 | 40 | ~80 | **+40** |

**Projected average score after prompt fix:** ~85/100 *(vs 72/100 before)*

---

## Key Improvements in `system-prompt-fixed.md`

1. **Empathy First Rule** — Agent must acknowledge hardship before pivoting to financial discussion
2. **Language Adaptability** — Agent must match borrower's language and not revert
3. **Mandatory Polite Closing** — Every call must end with a warm, respectful farewell phrase
4. **Payment Plan Always Offered** — Agent must mention flexible options in every Negotiation phase
5. **Callback Over Hang-up** — When progress is blocked, schedule a callback rather than ending abruptly
