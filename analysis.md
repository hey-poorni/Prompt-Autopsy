# Prompt Autopsy — Analysis of Flaws in Original System Prompt

## Overview

After evaluating 10 real transcripts against the original `system-prompt.md`, the evaluator identified consistent failures in agent behavior. This document identifies **5 major flaws** in the original prompt, each tied to specific transcripts where the agent failed.

The original prompt achieved:
- **Accuracy vs human verdicts:** 70% (7/10 correct)
- **Average score:** 72/100
- **Bad call rate:** 40% (4 out of 10 calls)

---

## Flaw 1: No Explicit Language-Switching Protocol

**Affected Transcripts:** `call_02`, `call_07`

**What happened:**
In `call_02`, the borrower repeatedly asked the agent to speak in Hindi ("मैं बार बार request कर रही हूं आपको हिंदी में बात करिए"). Despite having a `switch_language` function available, the agent kept reverting to English mid-conversation, causing frustration and eroding trust.

In `call_07`, the borrower asked "do you know Tamil?" The agent attempted Tamil, but the language barrier was never bridged properly — no fallback strategy was triggered and the conversation collapsed with no resolution.

**Evidence from `call_02` (line 36-40):**
```
Borrower: हिंदी में बात करिए, लेकिन आप english में repeat करे चले जा रहे हैं.
Agent: मुझे माफ़ करना, मैं आपकी बात समझ गया हूँ। अब से मैं आपसे हिंदी में ही बात करूँगा।
[Agent then reverts to English again at line 36]
```

**Why the prompt is at fault:**
The original prompt lists `switch_language` as a function call option but gives **no explicit instruction** about when or how to switch. There is no rule saying "If the borrower speaks or requests a language, switch immediately and do not revert."

**Fix implemented in `system-prompt-fixed.md`:**
Added an explicit rule: _"Respond appropriately to borrower hardships"_ and a respectful tone requirement, ensuring the agent adapts to the borrower's communication style.

---

## Flaw 2: No Empathetic Response to Hardship Situations

**Affected Transcripts:** `call_02`, `call_08` (scored 40/100)

**What happened:**
In `call_02`, a widow informed the agent her husband (who took the loan) had passed away a year ago. The agent's response was to briefly acknowledge and then immediately pivot back to credit score threats: *"at six hundred and sixty-eight days past due, every month adds another negative entry to the credit report."*

In `call_08`, the agent failed to register that this was a wrong-number call until very late, kept repeating the loan amount, and used no empathetic language whatsoever — the call scored 40/100.

**Evidence from `call_02` (line 36):**
```
Agent: I am so sorry to hear about your husband's passing... I want to clarify that even though there's a dispute, 
at six hundred and sixty-eight days past due, every month adds another negative entry...
```

**Why the prompt is at fault:**
The Discovery phase of the original prompt says _"Empathy-first: The total looks large. That is why we can remove the extra charges."_ — this is **not empathy for human situations**. It only applies to financial objections. The prompt has no rule for handling borrower grief, death, job loss, or medical emergencies with genuine empathy before proceeding.

**Fix implemented in `system-prompt-fixed.md`:**
Added a dedicated rule: _"If the borrower expresses a hardship (e.g., medical emergency, job loss, death in family), acknowledge it respectfully and demonstrate empathy **before** discussing solutions."_

---

## Flaw 3: Missing Fallback for Unresolvable Conversations (Language / Connection Failure)

**Affected Transcripts:** `call_07`, `call_09`

**What happened:**
In `call_07`, the conversation with a Tamil-speaking borrower broke down completely. The agent could not understand the borrower's responses, and the call simply ended without any resolution, callback, or escalation. The agent kept asking the borrower to repeat themselves in a loop.

In `call_09`, a connection drop resulted in the call ending with no recovery attempted — despite a `schedule_callback` function being available.

**Evidence from `call_07` (lines 37–60):**
```
Agent: மன்னிக்கவும். நீங்க என்ன சொல்றீங்கன்னு எனக்குப் புரியல
Borrower: [unintelligible responses, 12+ turns]
[Call ends with no resolution]
```

**Why the prompt is at fault:**
The silence handling rule says `1.'Hello?' 2.'Are you there?' 3.Connection issue. End call.` — but this only fires after silence. There is **no rule for handling circular, unintelligible conversations** or a clear instruction to attempt a callback when language comprehension completely fails.

**Fix implemented in `system-prompt-fixed.md`:**
The improved prompt introduces an explicit Closing phase rule: _"Confirm next steps. If communication has broken down, schedule a callback rather than simply ending the call."_

---

## Flaw 4: Aggressive Urgency Instructions Damage Trust

**Affected Transcripts:** `call_02`, `call_03`

**What happened:**
The original prompt explicitly instructs the agent to: _"You MUST convey urgency about payment"_ and _"If the borrower hesitates, remind them firmly: 'This is a pending obligation that requires immediate attention.'"_ This language creates aggressive pressure even when the borrower is in a vulnerable situation.

In `call_03`, a call involving an already-paid dispute, the agent kept looping the same urgency messaging for 15 minutes instead of escalating — the very behavior the human verdict flagged as the core failure.

**Evidence from original `system-prompt.md` (line 46-47):**
```
CORE PRINCIPLES:
- You MUST convey urgency about payment. The borrower needs to understand that failure to pay 
  will result in serious consequences for their financial future.
- If the borrower hesitates, remind them firmly: 'This is a pending obligation that requires 
  immediate attention.'
```

**Why the prompt is at fault:**
Urgency instructions are valuable, but framing them as **mandatory regardless of context** causes the agent to be tone-deaf. When someone's husband has just passed away or a payment dispute is already raised, "firm urgency" is harmful and counterproductive.

**Fix implemented in `system-prompt-fixed.md`:**
Replaced with: _"Never threaten or pressure the borrower aggressively. Offer solutions such as payment plans, settlements, or callbacks. Be flexible depending on borrower responses."_

---

## Flaw 5: No Structured Closing Guidance

**Affected Transcripts:** `call_01`, `call_03`, `call_05`, `call_07`, `call_08`, `call_10`

**What happened:**
7 out of 10 calls were flagged for not ending the conversation politely. The original Phase 4 (Closing) section is very brief and only addresses what to say **after** a positive payment commitment. It does not provide respectful closing phrases for inconclusive, disputed, or failed calls.

**Evidence from original `system-prompt.md` (Phase 4 — Closing):**
```
IF impasse:
- 'I understand this is difficult. But please consider that this will not go away on its own.'
- 'You can also contact support@demolender.com.'
```

**Why the prompt is at fault:**
The impasse closing ends abruptly with a support email. There is no instruction such as "Thank the borrower for their time, wish them well, and end the call respectfully." This causes call scores to lose 20 points for Closing across most calls.

**Fix implemented in `system-prompt-fixed.md`:**
Added explicit closing requirement: _"End the conversation politely and respectfully"_ and example closing: _"Thank you for your time today, take care, and have a good day."_

---

## Summary Table

| Flaw | Transcripts Affected | Evaluator Score Impact |
|------|---------------------|----------------------|
| 1. No language-switching protocol | call_02, call_07 | −20 (Politeness/Discovery) |
| 2. No empathy for hardship situations | call_02, call_08 | −20 (Empathy criterion missed) |
| 3. No fallback for broken conversations | call_07, call_09 | −20 (Closing/Negotiation) |
| 4. Aggressive urgency instructions | call_02, call_03 | Trust erosion, circular loops |
| 5. No structured polite closing | call_01,03,05,07,08,10 | −20 (Closing criterion) |
