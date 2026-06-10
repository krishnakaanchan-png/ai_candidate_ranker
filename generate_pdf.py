from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf(filename="methodology.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=landscape(letter))
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    heading_style = styles["Heading1"]
    heading_style.textColor = colors.darkblue
    normal_style = styles["Normal"]
    normal_style.fontSize = 12
    normal_style.leading = 14

    story = []

    # Slide 1: Title
    story.append(Paragraph("Intelligent Candidate Discovery & Ranking", title_style))
    story.append(Spacer(1, 40))
    story.append(Paragraph("Team FitFinderAi - Methodology & Architecture", styles["Heading2"]))
    story.append(Spacer(1, 100))

    # Slide 2: Philosophy & Two-Phase Architecture
    story.append(Paragraph("1. Core Philosophy & Architecture", heading_style))
    story.append(Spacer(1, 10))
    text = (
        "To build a true AI system that understands contextual fit while adhering to the strict 5-minute CPU-only "
        "constraint, we designed a Two-Phase Hybrid Retrieval Architecture. "
        "Keywords are easily gamed, so instead we rely on dense vector embeddings for semantic matching, combined with "
        "hard behavioral and trajectory signals.<br/><br/>"
        "<b>Phase 1 (Offline):</b> All candidates are embedded using 'all-MiniLM-L6-v2' and stored in a highly optimized FAISS index.<br/>"
        "<b>Phase 2 (Online):</b> At runtime, we embed the core job description requirements, perform an instant semantic search to retrieve "
        "the Top 1,000 candidates, and apply our behavioral re-ranking algorithm to produce the final Top 100."
    )
    story.append(Paragraph(text, normal_style))
    story.append(Spacer(1, 40))

    # Slide 3: Honeypots and Constraints
    story.append(Paragraph("2. Constraint Enforcement & Honeypot Detection", heading_style))
    story.append(Spacer(1, 10))
    text = (
        "Before finalizing scores, our pipeline strictly enforces trajectory and authenticity checks:<br/>"
        "• <b>Honeypot Detection:</b> We actively filter profiles claiming 'expert' status with 0 months duration, or those whose single "
        "job experience duration drastically exceeds their total Years of Experience.<br/>"
        "• <b>Target YoE Bound:</b> Candidates outside the 4-15 Years of Experience range are filtered out. We grant a slight "
        "score boost for candidates inside the 5-9 YoE 'sweet spot' identified in the JD.<br/>"
        "• <b>Consulting Checks:</b> Candidates with purely services/consulting backgrounds (without product company exposure) "
        "are filtered based on explicit JD instructions."
    )
    story.append(Paragraph(text, normal_style))
    story.append(Spacer(1, 40))

    # Slide 4: Scoring Engine
    story.append(Paragraph("3. Hybrid Re-Ranking Scoring", heading_style))
    story.append(Spacer(1, 10))
    text = (
        "The final candidate score is a weighted combination (0.6 Semantic + 0.4 Behavioral):<br/>"
        "• <b>Semantic Score:</b> The cosine similarity derived from FAISS, matching the candidate's entire career corpus against the JD embedding.<br/>"
        "• <b>Behavioral Score:</b> Sourced from Redrob signals. It heavily weights recruiter response rate and interview completion rate, "
        "while applying penalties for extended notice periods (>60 days). This ensures we rank capable engineers who are actually available and engaged."
    )
    story.append(Paragraph(text, normal_style))
    story.append(Spacer(1, 40))

    # Slide 5: Performance
    story.append(Paragraph("4. Performance & Constraints", heading_style))
    story.append(Spacer(1, 10))
    text = (
        "By offloading embedding generation to the pre-computation phase, the runtime Stage 3 ranking step operates flawlessly "
        "within the 5-minute limit, requiring under 10 seconds and < 500MB RAM to search the FAISS index and score 100K candidates on a single CPU core."
    )
    story.append(Paragraph(text, normal_style))
    story.append(Spacer(1, 40))

    doc.build(story)

if __name__ == "__main__":
    generate_pdf()
