"""
FitFinderAi — Professional Methodology Deck Generator
Generates a polished, consulting-grade PDF presentation.
"""
import math
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.utils import ImageReader
import os

# ── Design Tokens ──────────────────────────────────────────────
W, H = 1280, 720

BG_DARK   = HexColor("#0B1120")
BG_CARD   = Color(0.06, 0.10, 0.18, 1)
ACCENT    = HexColor("#38BDF8")   # sky-400
ACCENT2   = HexColor("#818CF8")   # indigo-400
ACCENT3   = HexColor("#34D399")   # emerald-400
WARN      = HexColor("#FB923C")   # orange-400
WHITE     = Color(1, 1, 1, 1)
MUTED     = Color(0.65, 0.70, 0.78, 1)
DIVIDER   = Color(1, 1, 1, 0.08)
CARD_BG   = Color(0.08, 0.12, 0.22, 0.92)
CARD_STROKE = Color(1, 1, 1, 0.10)

FONT_SANS = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_ITAL = "Helvetica-Oblique"

# ── Drawing Helpers ────────────────────────────────────────────
def draw_bg(c, bg_path=None):
    """Dark gradient background with optional image overlay."""
    if bg_path and os.path.exists(bg_path):
        c.drawImage(bg_path, 0, 0, width=W, height=H, preserveAspectRatio=False)
        # Darken overlay so text pops
        c.setFillColor(Color(0.04, 0.07, 0.13, 0.55))
        c.rect(0, 0, W, H, fill=1, stroke=0)
    else:
        c.setFillColor(BG_DARK)
        c.rect(0, 0, W, H, fill=1, stroke=0)
    # Subtle top accent line
    c.setStrokeColor(ACCENT)
    c.setLineWidth(3)
    c.line(0, H - 3, W, H - 3)

def draw_footer(c, page_num, total):
    """Consistent footer bar with logo text and page number."""
    c.setFillColor(Color(0, 0, 0, 0.35))
    c.rect(0, 0, W, 40, fill=1, stroke=0)
    c.setFont(FONT_BOLD, 13)
    c.setFillColor(ACCENT)
    c.drawString(30, 14, "FitFinderAi")
    c.setFillColor(MUTED)
    c.setFont(FONT_SANS, 11)
    c.drawString(140, 14, "Intelligent Candidate Discovery & Ranking")
    c.drawRightString(W - 30, 14, f"{page_num} / {total}")

def draw_card(c, x, y, w, h, fill=CARD_BG, stroke=CARD_STROKE, radius=12):
    c.saveState()
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)
    c.restoreState()

def draw_pill(c, x, y, text, bg=ACCENT, fg=BG_DARK, font_size=12):
    """Rounded pill / badge."""
    c.saveState()
    tw = c.stringWidth(text, FONT_BOLD, font_size)
    pw, ph = tw + 24, font_size + 12
    c.setFillColor(bg)
    c.roundRect(x, y, pw, ph, ph / 2, fill=1, stroke=0)
    c.setFillColor(fg)
    c.setFont(FONT_BOLD, font_size)
    c.drawString(x + 12, y + 6, text)
    c.restoreState()
    return pw

def text(c, s, x, y, font=FONT_SANS, size=18, color=WHITE, align="left"):
    c.setFont(font, size)
    c.setFillColor(color)
    if align == "center":
        c.drawCentredString(x, y, s)
    elif align == "right":
        c.drawRightString(x, y, s)
    else:
        c.drawString(x, y, s)

def draw_arrow(c, x1, y1, x2, y2, color=ACCENT, width=3, head=10):
    """Arrow with triangular head."""
    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)
    angle = math.atan2(y2 - y1, x2 - x1)
    c.translate(x2, y2)
    c.rotate(math.degrees(angle))
    p = c.beginPath()
    p.moveTo(0, 0)
    p.lineTo(-head, head / 2)
    p.lineTo(-head, -head / 2)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()

def draw_circle_icon(c, cx, cy, r, color, label):
    """Circle with centered single character."""
    c.saveState()
    c.setFillColor(color)
    c.circle(cx, cy, r, fill=1, stroke=0)
    c.setFillColor(BG_DARK)
    c.setFont(FONT_BOLD, int(r * 1.1))
    c.drawCentredString(cx, cy - r * 0.35, label)
    c.restoreState()

def wrap_lines(text_str, max_chars=60):
    """Simple word-wrap."""
    words = text_str.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > max_chars:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        lines.append(cur)
    return lines

TOTAL_PAGES = 8

# ── SLIDE BUILDERS ─────────────────────────────────────────────
def slide_title(c, bg):
    draw_bg(c, bg)
    # Centered content
    text(c, "FitFinderAi", W / 2, 440, FONT_BOLD, 72, ACCENT, "center")
    # Thin rule
    c.setStrokeColor(Color(1, 1, 1, 0.25))
    c.setLineWidth(1)
    c.line(W / 2 - 220, 420, W / 2 + 220, 420)
    text(c, "Intelligent Candidate Discovery & Ranking", W / 2, 370, FONT_SANS, 30, WHITE, "center")
    text(c, "Redrob Hackathon — Methodology & Architecture", W / 2, 320, FONT_ITAL, 20, MUTED, "center")
    # Team
    text(c, "Team FitFinderAi  •  Kaanchan Krishna", W / 2, 230, FONT_SANS, 18, MUTED, "center")
    draw_footer(c, 1, TOTAL_PAGES)

def slide_problem(c, bg):
    draw_bg(c, bg)
    text(c, "The Problem", 80, 640, FONT_BOLD, 42, ACCENT)
    c.setStrokeColor(ACCENT); c.setLineWidth(3)
    c.line(80, 625, 330, 625)

    # Left column — pain points
    draw_card(c, 60, 200, 540, 380)
    text(c, "Why keyword matching fails", 90, 530, FONT_BOLD, 24, WARN)
    bullets = [
        "Recruiters review 100s of profiles, still miss the right person.",
        "Keyword filters can't understand contextual fit or career arcs.",
        "Good candidates get buried; keyword-stuffers rise to the top.",
        "Behavioral signals (responsiveness, completion rates) are ignored.",
        "No way to catch honeypot / fabricated profiles automatically.",
    ]
    y = 485
    for b in bullets:
        draw_circle_icon(c, 108, y + 4, 8, WARN, "!")
        for i, line in enumerate(wrap_lines(b, 48)):
            text(c, line, 130, y - i * 20, FONT_SANS, 17, WHITE if i == 0 else MUTED)
        y -= 55

    # Right column — our answer
    draw_card(c, 680, 200, 540, 380)
    text(c, "Our approach", 710, 530, FONT_BOLD, 24, ACCENT3)
    answers = [
        ("Semantic Understanding", "Dense vector embeddings capture meaning, not keywords."),
        ("Behavioral Intelligence", "Redrob platform signals measure real-world engagement."),
        ("Strict Guardrails", "Honeypot detection + JD red-flag disqualifications."),
        ("Blazing Speed", "100K candidates ranked in < 10 seconds on CPU."),
    ]
    y = 480
    for title, desc in answers:
        draw_circle_icon(c, 708, y + 4, 8, ACCENT3, "✓")
        text(c, title, 730, y, FONT_BOLD, 17, WHITE)
        text(c, desc, 730, y - 22, FONT_SANS, 15, MUTED)
        y -= 62

    draw_footer(c, 2, TOTAL_PAGES)

def slide_architecture(c, bg):
    draw_bg(c, bg)
    text(c, "Two-Phase Architecture", 80, 640, FONT_BOLD, 42, ACCENT)
    c.setStrokeColor(ACCENT); c.setLineWidth(3)
    c.line(80, 625, 490, 625)

    # ── Phase 1 card ──
    draw_card(c, 60, 120, 520, 460)
    draw_pill(c, 80, 530, "PHASE 1 — OFFLINE", ACCENT2, WHITE)
    items = [
        ("1", "Load 100K candidates from JSONL"),
        ("2", "Extract text: Title → Skills → Career History"),
        ("3", "Embed via all-MiniLM-L6-v2 (384-dim)"),
        ("4", "Normalize vectors for cosine similarity"),
        ("5", "Build FAISS IndexFlatIP (Inner Product)"),
        ("6", "Persist index + metadata pickle to disk"),
    ]
    y = 480
    for num, desc in items:
        draw_circle_icon(c, 105, y + 4, 14, ACCENT2, num)
        text(c, desc, 130, y - 2, FONT_SANS, 17, WHITE)
        y -= 52

    # ── Arrow ──
    draw_arrow(c, 600, 350, 680, 350, ACCENT, 4, 14)
    text(c, "FAISS", 620, 370, FONT_BOLD, 14, ACCENT, "center")
    text(c, "Index", 620, 330, FONT_BOLD, 14, ACCENT, "center")

    # ── Phase 2 card ──
    draw_card(c, 700, 120, 520, 460)
    draw_pill(c, 720, 530, "PHASE 2 — ONLINE (< 10s)", ACCENT3, BG_DARK)
    items = [
        ("1", "Parse & embed the Job Description"),
        ("2", "Query FAISS → Top 10,000 semantic matches"),
        ("3", "Apply hard filters (YoE, Honeypots, Red Flags)"),
        ("4", "Compute behavioral score from Redrob signals"),
        ("5", "Fuse: 60% Semantic + 40% Behavioral"),
        ("6", "Output Top 100 ranked candidates to CSV"),
    ]
    y = 480
    for num, desc in items:
        draw_circle_icon(c, 745, y + 4, 14, ACCENT3, num)
        text(c, desc, 770, y - 2, FONT_SANS, 17, WHITE)
        y -= 52

    draw_footer(c, 3, TOTAL_PAGES)

def slide_semantic(c, bg):
    draw_bg(c, bg)
    text(c, "Semantic Embedding Pipeline", 80, 640, FONT_BOLD, 42, ACCENT)
    c.setStrokeColor(ACCENT); c.setLineWidth(3)
    c.line(80, 625, 540, 625)

    # Flow diagram: boxes with arrows
    boxes = [
        (80, 380, 200, 100, "Raw\nCandidate\nJSON", MUTED),
        (340, 380, 200, 100, "Text\nExtraction\n& Cleaning", ACCENT2),
        (600, 380, 200, 100, "SentenceTransformer\nall-MiniLM-L6-v2\n(384-dim)", ACCENT),
        (860, 380, 200, 100, "Normalized\nVector\nEmbedding", ACCENT3),
        (1060, 330, 160, 200, "FAISS\nIndexFlatIP\n(100K vectors)", WARN),
    ]
    for bx, by, bw, bh, label, col in boxes:
        draw_card(c, bx, by, bw, bh, fill=Color(0.08, 0.12, 0.22, 0.95))
        c.setStrokeColor(col); c.setLineWidth(2)
        c.roundRect(bx, by, bw, bh, 10, fill=0, stroke=1)
        lines = label.split("\n")
        for i, ln in enumerate(lines):
            text(c, ln, bx + bw / 2, by + bh - 25 - i * 22, FONT_BOLD if i == 0 else FONT_SANS,
                 15 if i == 0 else 13, col if i == 0 else WHITE, "center")

    # Arrows between boxes
    for i in range(len(boxes) - 1):
        x1 = boxes[i][0] + boxes[i][2]
        x2 = boxes[i + 1][0]
        mid_y = boxes[i][1] + boxes[i][3] / 2
        draw_arrow(c, x1 + 5, mid_y, x2 - 5, mid_y, Color(1, 1, 1, 0.4), 2, 8)

    # Detail card below
    draw_card(c, 60, 80, 1160, 250)
    text(c, "Key Design Decision: Text Ordering", 100, 280, FONT_BOLD, 22, ACCENT)
    details = [
        "• The model has a 256-token context window. We deliberately order text as: Title → Summary → Skills → Career History.",
        "• This ensures high-value skill keywords are always embedded before potential truncation of verbose job descriptions.",
        "• Embeddings are L2-normalized so FAISS Inner Product = Cosine Similarity. No post-processing required.",
        "• Batch encoding at 256 samples/batch with progress bar for the full 100K corpus (~4 min on Apple M-series).",
    ]
    y = 240
    for d in details:
        text(c, d, 100, y, FONT_SANS, 16, WHITE)
        y -= 35

    draw_footer(c, 4, TOTAL_PAGES)

def slide_constraints(c, bg):
    draw_bg(c, bg)
    text(c, "Guardrails & Honeypot Detection", 80, 640, FONT_BOLD, 42, ACCENT)
    c.setStrokeColor(ACCENT); c.setLineWidth(3)
    c.line(80, 625, 580, 625)

    # Three filter cards
    cards = [
        ("Honeypot Detection", WARN, [
            "'Expert' proficiency with 0 months duration → REJECT",
            "Skill duration > total YoE + 5 years → REJECT",
            "Single job > total YoE + 2 years → REJECT",
        ]),
        ("Hard Boundary Filters", ACCENT2, [
            "Years of Experience < 4 → REJECT",
            "Years of Experience > 15 → REJECT",
            "Sweet-spot boost: 5-9 YoE → +0.05 bonus",
        ]),
        ("JD Red Flag Disqualifications", HexColor("#F87171"), [
            "Consulting-only career (TCS/Wipro/Infosys…) → REJECT",
            "Pure researcher without Vector DB experience → REJECT",
            "LangChain-only without model/eval knowledge → REJECT",
        ]),
    ]

    x = 60
    for title, color, items in cards:
        draw_card(c, x, 140, 370, 430)
        # Colored top accent bar
        c.setFillColor(color)
        c.roundRect(x, 540, 370, 30, 12, fill=1, stroke=0)
        c.setFillColor(Color(0, 0, 0, 0.6))
        c.roundRect(x, 140, 370, 400, 12, fill=1, stroke=0)
        # Re-draw card content
        draw_card(c, x, 140, 370, 400, fill=CARD_BG)
        text(c, title, x + 20, 500, FONT_BOLD, 20, color)
        # Divider
        c.setStrokeColor(Color(1, 1, 1, 0.1)); c.setLineWidth(1)
        c.line(x + 20, 485, x + 350, 485)
        y = 450
        for item in items:
            # Split on arrow
            if "→" in item:
                parts = item.split("→")
                cond = parts[0].strip()
                action = "→ " + parts[1].strip()
                for ln in wrap_lines(cond, 38):
                    text(c, ln, x + 30, y, FONT_SANS, 15, WHITE)
                    y -= 22
                text(c, action, x + 30, y, FONT_BOLD, 15, color)
                y -= 40
            else:
                text(c, item, x + 30, y, FONT_SANS, 15, WHITE)
                y -= 30
        x += 400

    draw_footer(c, 5, TOTAL_PAGES)

def slide_scoring(c, bg):
    draw_bg(c, bg)
    text(c, "Hybrid Scoring Engine", 80, 640, FONT_BOLD, 42, ACCENT)
    c.setStrokeColor(ACCENT); c.setLineWidth(3)
    c.line(80, 625, 440, 625)

    # Formula banner
    draw_card(c, 160, 520, 960, 70, fill=Color(0.06, 0.10, 0.20, 0.95))
    c.setStrokeColor(ACCENT); c.setLineWidth(2)
    c.roundRect(160, 520, 960, 70, 12, fill=0, stroke=1)
    text(c, "Final Score  =  Semantic × 0.6  +  Behavioral × 0.4  +  YoE Bonus",
         W / 2, 545, FONT_BOLD, 28, ACCENT, "center")

    # Semantic column
    draw_card(c, 60, 120, 560, 360)
    draw_pill(c, 80, 430, "60%  SEMANTIC MATCH", ACCENT, BG_DARK)
    sem_items = [
        ("Source", "FAISS cosine similarity (Inner Product on normalized vectors)"),
        ("Input", "Candidate career corpus vs. curated JD query embedding"),
        ("Model", "all-MiniLM-L6-v2 — 384 dimensions, 256 token context"),
        ("Why it works", "Captures meaning: 'ML Engineer' matches 'Machine Learning"),
        ("", "Developer' even without exact keyword overlap"),
    ]
    y = 385
    for label, desc in sem_items:
        if label:
            text(c, label, 90, y, FONT_BOLD, 15, ACCENT)
            text(c, desc, 200, y, FONT_SANS, 15, WHITE)
        else:
            text(c, desc, 200, y, FONT_SANS, 15, WHITE)
        y -= 32

    # Behavioral column
    draw_card(c, 660, 120, 560, 360)
    draw_pill(c, 680, 430, "40%  BEHAVIORAL SIGNALS", ACCENT3, BG_DARK)
    beh_items = [
        ("Recruiter Response Rate", "×40 weight", ACCENT3),
        ("Interview Completion Rate", "×30 weight", ACCENT3),
        ("Profile Completeness", "×10 weight", ACCENT2),
        ("GitHub Activity Score", "×10 weight", ACCENT2),
        ("Open to Work Flag", "+5 flat bonus", ACCENT),
        ("Notice Period > 60 days", "-10 penalty", WARN),
    ]
    y = 385
    for label, weight, col in beh_items:
        text(c, "●", 690, y, FONT_BOLD, 14, col)
        text(c, label, 715, y, FONT_SANS, 15, WHITE)
        text(c, weight, 1060, y, FONT_BOLD, 14, col, "right")
        # Subtle separator
        c.setStrokeColor(DIVIDER); c.setLineWidth(0.5)
        c.line(690, y - 10, 1190, y - 10)
        y -= 38

    draw_footer(c, 6, TOTAL_PAGES)

def slide_performance(c, bg):
    draw_bg(c, bg)
    text(c, "Performance & Constraints", 80, 640, FONT_BOLD, 42, ACCENT)
    c.setStrokeColor(ACCENT); c.setLineWidth(3)
    c.line(80, 625, 520, 625)

    # Metric cards — top row
    metrics = [
        ("100,000", "Candidates\nSearched", ACCENT),
        ("< 10 sec", "End-to-End\nCPU Runtime", ACCENT3),
        ("~500 MB", "Peak RAM\nUsage", ACCENT2),
        ("100%", "Submission\nValidated", WARN),
    ]
    x = 60
    for val, label, col in metrics:
        draw_card(c, x, 380, 270, 190)
        # Colored top edge
        c.setFillColor(col)
        c.roundRect(x, 555, 270, 15, 8, fill=1, stroke=0)
        text(c, val, x + 135, 490, FONT_BOLD, 48, col, "center")
        for i, ln in enumerate(label.split("\n")):
            text(c, ln, x + 135, 440 - i * 22, FONT_SANS, 18, MUTED, "center")
        x += 300

    # Constraint compliance
    draw_card(c, 60, 60, 1160, 270)
    text(c, "Competition Constraint Compliance", 100, 280, FONT_BOLD, 24, ACCENT)
    c.setStrokeColor(DIVIDER); c.setLineWidth(1)
    c.line(100, 265, 1180, 265)

    checks = [
        ("5-minute wall-clock limit", "PASS — executes in ~10 seconds", True),
        ("CPU-only (no GPU)", "PASS — runs on Apple M-series CPU", True),
        ("No network calls at runtime", "PASS — all data is local/precomputed", True),
        ("16 GB RAM cap", "PASS — peak usage ~500 MB", True),
        ("Exactly 100 ranked candidates", "PASS — validated by validate_submission.py", True),
        ("Honeypot detection", "PASS — multi-signal heuristic detection", True),
    ]
    y = 235
    for label, status, passed in checks:
        col = ACCENT3 if passed else HexColor("#F87171")
        text(c, "✓" if passed else "✗", 110, y, FONT_BOLD, 18, col)
        text(c, label, 140, y, FONT_SANS, 16, WHITE)
        text(c, status, 580, y, FONT_SANS, 16, MUTED)
        y -= 30

    draw_footer(c, 7, TOTAL_PAGES)

def slide_closing(c, bg):
    draw_bg(c, bg)

    # Big centered thank-you
    text(c, "Thank You", W / 2, 460, FONT_BOLD, 72, ACCENT, "center")
    c.setStrokeColor(Color(1, 1, 1, 0.25)); c.setLineWidth(1)
    c.line(W / 2 - 180, 440, W / 2 + 180, 440)
    text(c, "Built with semantic intelligence, not keyword tricks.", W / 2, 390, FONT_ITAL, 24, MUTED, "center")

    # Contact / links
    draw_card(c, 340, 180, 600, 160)
    text(c, "Kaanchan Krishna", W / 2, 300, FONT_BOLD, 22, WHITE, "center")
    text(c, "krishnakaanchan@gmail.com  •  +91 90442 77353", W / 2, 265, FONT_SANS, 17, MUTED, "center")
    text(c, "github.com/krishnakaanchan-png/ai_candidate_ranker", W / 2, 230, FONT_SANS, 16, ACCENT, "center")

    draw_footer(c, 8, TOTAL_PAGES)


# ── Main ───────────────────────────────────────────────────────
def main():
    bg_path = os.path.join(os.path.dirname(__file__), "deck_bg.png")
    if not os.path.exists(bg_path):
        bg_path = None

    out = os.path.join(os.path.dirname(__file__) or ".", "methodology.pdf")
    c = canvas.Canvas(out, pagesize=(W, H))

    slides = [
        slide_title,
        slide_problem,
        slide_architecture,
        slide_semantic,
        slide_constraints,
        slide_scoring,
        slide_performance,
        slide_closing,
    ]
    for slide_fn in slides:
        slide_fn(c, bg_path)
        c.showPage()

    c.save()
    print(f"Deck saved → {out}  ({len(slides)} slides)")

if __name__ == "__main__":
    main()
