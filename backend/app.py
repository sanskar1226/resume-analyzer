from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
import re

app = Flask(__name__)
CORS(app)

# ----------------------------
# Extract text
# ----------------------------
def extract_text(file):
    if file.filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    return file.read().decode("utf-8", errors="ignore")


# ----------------------------
# Clean text
# ----------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)

    stopwords = {
        "and","or","the","a","an","to","of","in","for","on","with",
        "is","are","was","were","this","that","it","as","by","at",
        "we","you","they","he","she","will","can","should",
        "from","into","our","your","their",
        "required","responsibilities","job","role","using"
    }

    words = []
    for w in text.split():
        if len(w) <= 3:
            continue
        if w in stopwords:
            continue

        # normalize
        if w.endswith("ing"):
            w = w[:-3]
        elif w.endswith("ed"):
            w = w[:-2]
        elif w.endswith("s"):
            w = w[:-1]

        words.append(w)

    return words


# ----------------------------
# Synonym mapping
# ----------------------------
def normalize_words(words):
    mapping = {
        "retail": "sales",
        "sale": "sales",
        "selling": "sales",

        "graphic": "design",
        "graphics": "design",
        "designer": "design",

        "branding": "marketing",
        "brand": "marketing",
        "market": "marketing",

        "customer": "customer",
        "service": "customer",

        "inventory": "inventory",
        "stock": "inventory",

        "display": "display",
        "visual": "display",

        "communication": "communication",
        "interaction": "communication"
    }

    return [mapping.get(w, w) for w in words]


# ----------------------------
# Analyze resume
# ----------------------------
def analyze_resume(resume_text, job_desc):
    r_words = normalize_words(clean_text(resume_text))
    j_words = normalize_words(clean_text(job_desc))

    r_set = set(r_words)
    j_set = set(j_words)

    # TF-IDF similarity
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([
        " ".join(r_words),
        " ".join(j_words)
    ])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    matched = list(r_set & j_set)
    missing = list(j_set - r_set)

    # keyword score
    keyword_score = len(matched) / len(j_set) if j_set else 0

    # 🔥 FINAL IMPROVED SCORING
    final_score = (similarity * 0.4 + keyword_score * 0.6) * 100

    # boost for short resumes
    if final_score < 70:
        final_score = final_score * 1.3

    # cap at 100
    final_score = min(final_score, 100)

    return {
        "score": round(final_score, 2),
        "matched": sorted(matched)[:10],
        "missing": sorted(missing)[:10]
    }


# ----------------------------
# API
# ----------------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["resume"]
    job_desc = request.form["job"]

    text = extract_text(file)
    result = analyze_resume(text, job_desc)

    return jsonify(result)


# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    app.run(port=5000)