# analysis/utils.py
from textblob import TextBlob
from sentence_transformers import SentenceTransformer, util
import numpy as np
import re
import string
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


try:
    nltk.data.find("tokenizers/punkt")
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("punkt", quiet=True)
    nltk.download("wordnet", quiet=True)
    nltk.download("omw-1.4", quiet=True)

lemmatizer = WordNetLemmatizer()
model = SentenceTransformer('all-MiniLM-L6-v2')  # loaded once

# --- Normalization helpers ---
CONTRACTIONS = {
    "can't": "cannot", "won't": "will not", "don't": "do not", "didn't": "did not",
    "i'm": "i am", "i've": "i have", "i'd": "i would", "it's": "it is", "they're": "they are",
    "we're": "we are", "you're": "you are", "isn't": "is not", "aren't": "are not",
    "couldn't": "could not", "shouldn't": "should not", "wouldn't": "would not"
}
PUNCTUATION_TABLE = str.maketrans('', '', string.punctuation)


def normalize_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.lower()
    # expand common contractions
    for k, v in CONTRACTIONS.items():
        s = s.replace(k, v)
    # remove extra whitespace
    s = re.sub(r'\s+', ' ', s).strip()
    # remove punctuation for token-matching but keep for other checks if needed
    return s


def lemmatized_tokens(s: str):
    s = normalize_text(s)
    toks = word_tokenize(s)
    return [lemmatizer.lemmatize(t) for t in toks]


def contains_lemma_any(s: str, lemmas):
    toks = lemmatized_tokens(s)
    return any(l in toks for l in lemmas)


# --- Pattern sets (expandable) ---
FALLBACK_PATTERNS = [
    r"\bdo not know\b", r"\bdoesn't know\b", r"\bdo n't know\b", r"\bnot sure\b",
    r"\bunable\b", r"\bcan not\b", r"\bcannot\b", r"\bcan't\b", r"\bno idea\b",
    r"\bi have no\b", r"\bi'm not able\b", r"\bi am not able\b", r"\bnot available\b",
    r"\bunknown\b", r"\bno information\b", r"\bi don't have that\b", r"\bcan't help\b"
]

EMPATHY_PHRASES = [
    "sorry to hear", "i'm sorry", "i am sorry", "i understand", "i can imagine", "that must be",
    "i'm here to help", "i am here to help", "happy to help", "glad to help", "appreciate",
    "sorry about", "apologize", "i apologize", "thanks for sharing"
]

CLOSURE_PHRASES = [
    "anything else", "is there anything", "let me know", "glad i could help", "happy to help",
    "thank you", "thanks", "if you need", "feel free to", "have a great", "goodbye"
]

RESOLUTION_PATTERNS = [
    r"\bresolved\b", r"\bfixed\b", r"\bcompleted\b", r"\bclosed\b", r"\bshipped\b",
    r"\bdelivered\b", r"\brefund\b", r"\breturned\b", r"\bcancelled\b", r"\bcancelled\b",
    r"\brefunded\b", r"\bissue solved\b", r"\bticket closed\b"
]

FACTUAL_KEYWORDS = ["order", "id", "tracking", "date", "number", "price", "invoice", "amount", "ref", "reference"]


# --- Regex helpers ---
def regex_any_match(text: str, patterns):
    text = normalize_text(text)
    for p in patterns:
        if re.search(p, text):
            return True
    return False


# --- Core analysis ---
def analyze_conversation(messages):
    """
    Analyzes messages list like:
        [{"sender": "user", "message": "Hi"}, ...]
    Returns dictionary with the required parameters (10 fields).
    """
    # basic separation
    user_msgs = [m['message'] for m in messages if m['sender'] == 'user']
    ai_msgs = [m['message'] for m in messages if m['sender'] == 'ai']

    if not user_msgs and not ai_msgs:
        return {"error": "empty conversation"}

    # --- 1) Clarity score (AI responses) ---
    # Use TextBlob subjectivity + average sentence length heuristic.
    clarity_vals = []
    for msg in ai_msgs:
        txt = normalize_text(msg)
        blob = TextBlob(txt)
        subjectivity = abs(blob.sentiment.subjectivity)  # 0.0 objective -> better clarity
        # length factor: super short replies (<=3 tokens) are less clear if they don't answer
        token_count = len(word_tokenize(txt))
        length_penalty = 0.0
        if token_count <= 3:
            length_penalty = 0.15
        clarity = max(0.0, 1.0 - subjectivity - length_penalty)
        clarity_vals.append(clarity)
    clarity_score = round(float(np.mean(clarity_vals)) if clarity_vals else 0.0, 2)

    # --- 2) Relevance score ---
    # Match each user message to the next AI reply (or nearest following AI reply).
    relevance_scores = []
    # Build index of messages to map user->next ai
    for idx, m in enumerate(messages):
        if m['sender'] != 'user':
            continue
        # find next ai message after this user message
        next_ai = None
        for j in range(idx + 1, len(messages)):
            if messages[j]['sender'] == 'ai':
                next_ai = messages[j]['message']
                break
        if next_ai:
            u_emb = model.encode(m['message'], convert_to_tensor=True)
            a_emb = model.encode(next_ai, convert_to_tensor=True)
            sim = util.cos_sim(u_emb, a_emb).item()
            relevance_scores.append(sim)
    relevance_score = round(float(np.mean(relevance_scores)) if relevance_scores else 0.0, 2)

    # --- 3) Accuracy score ---
    # Heuristic: if AI contains factual tokens (order/tracking/ids/dates/numbers) it's likely more accurate
    factual_count = 0
    for msg in ai_msgs:
        txt = normalize_text(msg)
        # numeric patterns (order number, digits, tracking)
        if re.search(r"\b\d{3,}\b", txt):  # numbers with >=3 digits (IDs, amounts)
            factual_count += 1
            continue
        # tracking-like tokens
        if any(k in txt for k in FACTUAL_KEYWORDS):
            factual_count += 1
            continue
        # date-like
        if re.search(r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b", txt):
            factual_count += 1
            continue
    # base 0.5 baseline + 0.1 per factual message (cap 1.0)
    accuracy_score = round(min(1.0, 0.5 + 0.1 * factual_count), 2)

    # --- 4) Completeness score ---
    # If AI asks clarifying questions (many '?') completeness is lower.
    complete_count = 0
    clarification_count = 0
    for msg in ai_msgs:
        txt = normalize_text(msg)
        # closure phrase presence indicates completeness
        if any(phrase in txt for phrase in CLOSURE_PHRASES):
            complete_count += 1
        # messages that are questions indicate clarifying follow-ups
        if "?" in msg or txt.strip().startswith("can you") or txt.strip().startswith("could you") or txt.strip().startswith("please"):
            clarification_count += 1
    # completeness: more closure phrases add, more clarif reduce it
    completeness_score = 0.6 + 0.1 * complete_count - 0.08 * clarification_count
    completeness_score = round(max(0.0, min(1.0, completeness_score)), 2)

    # --- 5) Empathy score ---
    # Check phrases and lemmatized tokens for empathetic language
    empathy_hits = 0
    for msg in ai_msgs:
        txt = normalize_text(msg)
        if regex_any_match(txt, [re.escape(p) for p in EMPATHY_PHRASES]):
            empathy_hits += 1
        else:
            # lemmatized token-level fallback
            if contains_lemma_any(txt, ["sorry", "understand", "help", "apologize", "appreciate", "regret"]):
                empathy_hits += 1
    empathy_score = round(min(1.0, 0.4 + 0.12 * empathy_hits), 2)

    # --- 6) Sentiment (user) ---
    user_pols = []
    for msg in user_msgs:
        txt = normalize_text(msg)
        user_pols.append(TextBlob(txt).sentiment.polarity)
    avg_pol = float(np.mean(user_pols)) if user_pols else 0.0
    if avg_pol > 0.2:
        sentiment = "positive"
    elif avg_pol < -0.2:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    # --- 7) Fallback frequency (robust detection) ---
    fallback_count = 0
    for msg in ai_msgs:
        txt = normalize_text(msg)
        # direct regex patterns (covers many variants and contractions)
        if regex_any_match(txt, FALLBACK_PATTERNS):
            fallback_count += 1
            continue
        # detect "I don't have information" style using lemmatized tokens
        if contains_lemma_any(txt, ["not", "no"]) and contains_lemma_any(txt, ["know", "have", "information", "access"]):
            fallback_count += 1
            continue
        # "unable to" / "can't" with verbs like "help" or "find"
        if re.search(r"(unable|cannot|can not|cannot) .* (help|find|access|provide|retrieve)", txt):
            fallback_count += 1
            continue

    # --- 8) Resolution detection (robust) ---
    resolved = False
    for msg in ai_msgs:
        txt = normalize_text(msg)
        if regex_any_match(txt, RESOLUTION_PATTERNS):
            resolved = True
            break
        # also detect phrases like "your order .* has been shipped/delivered"
        if re.search(r"order .* (shipped|delivered|dispatched|on the way|will arrive|arrive tomorrow|out for delivery)", txt):
            resolved = True
            break

    # --- 9) Escalation need ---
    escalation_needed = False
    # escalate if unresolved AND user sentiment negative OR many fallbacks
    if (not resolved and sentiment == "negative") or fallback_count >= 2:
        escalation_needed = True

    # --- 10) Overall score ---
    metric_list = [clarity_score, relevance_score, accuracy_score, completeness_score, empathy_score]
    overall_score = round(float(np.mean(metric_list)), 2)

    return {
        "clarity_score": clarity_score,
        "relevance_score": relevance_score,
        "accuracy_score": accuracy_score,
        "completeness_score": completeness_score,
        "empathy_score": empathy_score,
        "sentiment": sentiment,
        "resolution": resolved,
        "escalation_needed": escalation_needed,
        "fallback_count": int(fallback_count),
        "overall_score": overall_score
    }
