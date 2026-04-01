import streamlit as st

def apply_custom_styles():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Hide default Streamlit header/footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stSelectbox label {
    color: #94a3b8 !important;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] select {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    color: #f1f5f9 !important;
    font-family: 'Inter', monospace !important;
}
[data-testid="stSidebar"] .stMarkdown h2 {
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b !important;
    border-bottom: 1px solid #334155;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

/* Hero Title */
.hero-title {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.25rem;
}
.hero-sub {
    font-size: 1rem;
    color: #64748b;
    margin-bottom: 2rem;
}

/* Step Headers */
.step-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1rem;
    margin-top: 1.5rem;
}
.step-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 600;
    flex-shrink: 0;
}
.step-badge-active {
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    color: white;
    }
.step-badge-done {
    background: #dcfce7;
    color: #166534;
}
.step-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1e293b;
}

/* Card Container */
.card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* FAQ Cards */
.faq-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 0.75rem;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.faq-card:hover {
    border-color: #93c5fd;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.08);
}
.faq-q {
    padding: 1rem 1.25rem;
    font-size: 0.95rem;
    font-weight: 600;
    color: #1e293b;
    background: #f8fafc;
    display: flex;
    align-items: center;
    gap: 10px;
}
.faq-a {
    padding: 1rem 1.25rem;
    font-size: 0.9rem;
    color: #475569;
    line-height: 1.7;
    border-top: 1px solid #f1f5f9;
}
.faq-source {
    padding: 0.5rem 1.25rem 0.75rem;
    font-size: 0.75rem;
    color: #94a3b8;
}

/* Category Badges */
.cat-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    margin-left: auto;
    flex-shrink: 0;
}
.cat-teal { background: #dcfce7; color: #166534; }
.cat-blue { background: #dbeafe; color: #1e40af; }
.cat-amber { background: #fef3c7; color: #92400e; }
.cat-purple { background: #f3e8ff; color: #6b21a8; }
.cat-red { background: #fee2e2; color: #991b1b; }

/* Metrics Row */
.metrics-row {
    display: flex;
    gap: 12px;
    margin: 1rem 0;
}
.metric-card {
    flex: 1;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    text-align: center;
}
.metric-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1e293b;
}
.metric-label {
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 2px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Buttons */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.02em;
    transition: opacity 0.2s;
}
.stButton > button[kind="primary"]:hover {
    opacity: 0.9;
}

/* Download Buttons Row */
.dl-row {
    display: flex;
    gap: 8px;
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)
