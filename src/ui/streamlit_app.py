"""
Travel Chatbot Demo — Streamlit Frontend (Redesigned)
Run:  streamlit run streamlit_app.py
Requires: pip install streamlit requests
"""

import streamlit as st
import requests
import json

st.set_page_config(
    page_title="Travel Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=DM+Mono:wght@300;400&family=Outfit:wght@300;400;500;600&display=swap');

:root {
    --bg-deep:    #0d090a;
    --bg-card:    #1a1014;
    --plum-dark:  #361f27;
    --plum-mid:   #521945;
    --rose:       #912f56;
    --mint:       #eaf2ef;
    --mint-dim:   rgba(234,242,239,0.55);
    --mint-faint: rgba(234,242,239,0.08);
    --rose-glow:  rgba(145,47,86,0.35);
    --border:     rgba(145,47,86,0.25);
}

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    background-color: var(--bg-deep) !important;
    color: var(--mint) !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2rem 2.5rem 4rem !important;
    max-width: 1100px !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a0d12 0%, #0d090a 100%) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--mint) !important; }

.sidebar-logo {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    color: var(--mint) !important;
    margin-bottom: 0.15rem;
}
.sidebar-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--mint-dim) !important;
    margin-bottom: 1.5rem;
}

[data-testid="stTextInput"] input {
    background: var(--mint-faint) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--mint) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    padding: 0.6rem 0.8rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--rose) !important;
    box-shadow: 0 0 0 2px var(--rose-glow) !important;
}
[data-testid="stTextInput"] label {
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--mint-dim) !important;
    font-family: 'DM Mono', monospace !important;
}

.status-connected {
    display: flex; align-items: center; gap: 8px;
    background: rgba(234,242,239,0.06);
    border: 1px solid rgba(234,242,239,0.15);
    border-radius: 30px;
    padding: 8px 16px;
    font-size: 0.78rem;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.05em;
    margin: 0.5rem 0 1rem;
}
.status-connected .dot { width:8px; height:8px; border-radius:50%; background:#4ade80;
    box-shadow: 0 0 8px #4ade80; flex-shrink:0; }
.status-error {
    display: flex; align-items: center; gap: 8px;
    background: rgba(145,47,86,0.15);
    border: 1px solid var(--border);
    border-radius: 30px;
    padding: 8px 16px;
    font-size: 0.78rem;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.05em;
    margin: 0.5rem 0 1rem;
}
.status-error .dot { width:8px; height:8px; border-radius:50%; background:var(--rose); flex-shrink:0; }

[data-testid="stButton"] button {
    width: 100% !important;
    background: transparent !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--mint-dim) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.06em !important;
    padding: 0.55rem 1rem !important;
    transition: all 0.2s ease !important;
    text-align: left !important;
}
[data-testid="stButton"] button:hover {
    border-color: var(--rose) !important;
    color: var(--mint) !important;
    background: var(--rose-glow) !important;
}

.example-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--mint-dim);
    margin: 1.2rem 0 0.6rem;
}

.page-header {
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
}
.page-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.8rem;
    font-weight: 300;
    letter-spacing: -0.01em;
    line-height: 1.1;
    color: var(--mint) !important;
    margin-bottom: 0.3rem;
}
.page-title span { color: var(--rose); }
.page-tagline {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--mint-dim);
}

.user-msg {
    display: flex;
    justify-content: flex-end;
    margin: 1rem 0 0.5rem;
}
.user-bubble {
    background: linear-gradient(135deg, var(--plum-mid), var(--rose));
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    max-width: 70%;
    font-size: 0.95rem;
    line-height: 1.5;
    color: var(--mint) !important;
    font-family: 'Outfit', sans-serif;
    font-weight: 400;
    box-shadow: 0 4px 20px var(--rose-glow);
}

.bot-row {
    display: flex;
    justify-content: flex-start;
    margin: 0.5rem 0 0.25rem;
    gap: 12px;
    align-items: flex-start;
}
.bot-avatar {
    width: 34px; height: 34px; border-radius: 50%;
    background: linear-gradient(135deg, var(--plum-dark), var(--plum-mid));
    border: 1px solid var(--border);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; flex-shrink: 0; margin-top: 2px;
}
.bot-text-bubble {
    background: rgba(53,31,39,0.5);
    border: 1px solid var(--border);
    border-radius: 4px 18px 18px 18px;
    padding: 12px 18px;
    font-size: 0.95rem;
    line-height: 1.6;
    color: var(--mint) !important;
    font-family: 'Outfit', sans-serif;
    margin-bottom: 10px;
    max-width: 75%;
}

.output-card {
    background: var(--mint-faint);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin: 0 0 1.5rem 46px;
}

.metrics-row {
    display: flex; gap: 10px; margin-bottom: 14px; flex-wrap: wrap;
}
.metric-chip {
    background: rgba(145,47,86,0.15);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 6px 14px;
    display: flex; flex-direction: column; gap: 2px;
    min-width: 110px;
}
.metric-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--rose);
}
.metric-value {
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    color: var(--mint);
}

.domain-badge {
    display: inline-flex; align-items: center; gap: 5px;
    border-radius: 20px; padding: 3px 12px;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem; letter-spacing: 0.06em;
    margin-bottom: 12px;
}
.badge-hotel      { background:rgba(59,130,246,0.15); border:1px solid rgba(59,130,246,0.3); color:#93c5fd; }
.badge-restaurant { background:rgba(34,197,94,0.12);  border:1px solid rgba(34,197,94,0.3);  color:#86efac; }
.badge-taxi       { background:rgba(234,179,8,0.12);  border:1px solid rgba(234,179,8,0.3);  color:#fde047; }
.badge-attraction { background:rgba(168,85,247,0.12); border:1px solid rgba(168,85,247,0.3); color:#d8b4fe; }
.badge-unknown    { background:rgba(234,242,239,0.06); border:1px solid var(--border); color:var(--mint-dim); }

.slot-section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--mint-dim); margin: 10px 0 5px;
}
.slot-table { width: 100%; border-collapse: collapse; }
.slot-table td {
    padding: 6px 10px; font-family: 'DM Mono', monospace;
    font-size: 0.78rem; border-bottom: 1px solid rgba(145,47,86,0.12);
}
.slot-table td:first-child { color: var(--rose); width: 38%; }
.slot-table td:last-child  { color: var(--mint); }
.slot-table tr:last-child td { border-bottom: none; }

.missing-tag {
    display: inline-flex; align-items: center; gap: 4px;
    background: rgba(145,47,86,0.2); border: 1px solid rgba(145,47,86,0.4);
    border-radius: 6px; padding: 3px 10px;
    font-family: 'DM Mono', monospace; font-size: 0.68rem; color: #f9a8c9; margin: 2px;
}

[data-testid="stExpander"] {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    margin-top: 8px !important;
}
[data-testid="stExpander"] summary {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important; color: var(--mint-dim) !important;
}

[data-testid="stChatInput"] {
    background: var(--plum-dark) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: var(--mint) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.9rem !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--mint-dim) !important; }

hr { border-color: var(--border) !important; margin: 1rem 0 !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: var(--plum-mid); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "prefill" not in st.session_state:
    st.session_state.prefill = ""


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">✈ Travel NLU</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Mistral-7B · LoRA Fine-tuned</div>', unsafe_allow_html=True)

    api_url = st.text_input("KAGGLE NGROK API URL", placeholder="https://reconvene-sprawl-modified.ngrok-free.dev")

    if api_url:
        try:
            r = requests.get(f"{api_url}/health", timeout=5)
            if r.status_code == 200:
                st.markdown('<div class="status-connected"><div class="dot"></div>API connected</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-error"><div class="dot"></div>Unhealthy response</div>', unsafe_allow_html=True)
        except Exception:
            st.markdown('<div class="status-error"><div class="dot"></div>Cannot reach API</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-error"><div class="dot"></div>No URL entered</div>', unsafe_allow_html=True)

    st.markdown("---")

    if st.button("↺  Reset Dialogue State"):
        if api_url:
            try:
                requests.post(f"{api_url}/reset", timeout=10)
                st.session_state.messages = []
                st.rerun()
            except Exception as e:
                st.error(f"Reset failed: {e}")

    st.markdown('<div class="example-label">✦ Example prompts</div>', unsafe_allow_html=True)
    examples = [
        "I need a cheap hotel in the north with free parking.",
        "Find me an Italian restaurant in the centre.",
        "I need a taxi from the hotel to the train station by 7 pm.",
        "Find me a museum to visit in the centre.",
        "Book a table for 2 people on Friday at 7 pm.",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex[:25]}"):
            st.session_state.prefill = ex


# ── Helper: natural language response ────────────────────────────────────────
SLOT_LABELS = {
    "people": "how many people",
    "day": "which day",
    "stay": "how many nights",
    "time": "what time",
    "departure": "where you're departing from",
    "destination": "your destination",
    "leave_at_or_arrive_by": "what time you'd like to leave or arrive by",
    "area": "which area",
    "price_range": "your budget",
    "food": "the cuisine type",
}

def generate_chat_response(output: dict) -> str:
    if not output:
        return "Sorry, I couldn't understand that. Could you try rephrasing?"
    domain  = output.get("domain", "unknown")
    action  = output.get("next_action", "fallback")
    missing = output.get("missing_slots", [])
    slots   = output.get("slots", {})
    domain_slots  = slots.get(domain, {})
    search  = domain_slots.get("search_slots",  {})
    booking = domain_slots.get("booking_slots", {})

    if action == "fallback":
        return "I'm not sure I understood that. Are you looking for a hotel, restaurant, taxi, or attraction?"
    if action == "ask_missing_slot" and missing:
        label = SLOT_LABELS.get(missing[0], missing[0].replace("_", " "))
        return f"I'd be happy to help with that! Could you tell me {label}?"
    if action == "search_hotel":
        parts = []
        if search.get("area"):        parts.append(f"in the {search['area']}")
        if search.get("price_range"): parts.append(f"with a {search['price_range']} price range")
        if search.get("parking"):     parts.append("with free parking")
        if search.get("internet"):    parts.append("with internet")
        return f"Got it! Searching for hotels {', '.join(parts) if parts else 'matching your preferences'}."
    if action == "search_restaurant":
        parts = []
        if search.get("food"): parts.append(f"{search['food']} cuisine")
        if search.get("area"): parts.append(f"in the {search['area']}")
        return f"Looking for a {' '.join(parts) if parts else 'restaurant'} for you."
    if action == "book_restaurant":
        parts = []
        if booking.get("people"): parts.append(f"{booking['people']} people")
        if booking.get("day"):    parts.append(f"on {booking['day']}")
        if booking.get("time"):   parts.append(f"at {booking['time']}")
        return f"I'll book a restaurant table for {' '.join(parts) if parts else 'your requested time'}."
    if action == "book_hotel":
        parts = []
        if booking.get("people"): parts.append(f"{booking['people']} guests")
        if booking.get("day"):    parts.append(f"from {booking['day']}")
        if booking.get("stay"):   parts.append(f"for {booking['stay']} nights")
        return f"I'll arrange a hotel booking for {' '.join(parts) if parts else 'your requested dates'}."
    if action == "book_taxi":
        dep = booking.get("departure", "your location")
        dst = booking.get("destination", "your destination")
        t   = booking.get("leave_at") or booking.get("arrive_by", "")
        time_str = f" {'arriving by' if booking.get('arrive_by') else 'leaving at'} {t}" if t else ""
        return f"I'll book a taxi from {dep} to {dst}{time_str}."
    if action == "search_attraction":
        parts = []
        if search.get("type"): parts.append(search["type"])
        if search.get("area"): parts.append(f"in the {search['area']}")
        return f"Searching for a {' '.join(parts) if parts else 'attraction'} for you."
    return f"Understood! I'll help you with your {domain} request."


# ── Helper: domain badge ──────────────────────────────────────────────────────
DOMAIN_ICONS = {"hotel": "🏨", "restaurant": "🍽️", "taxi": "🚕", "attraction": "🎡"}

def domain_badge_html(domain):
    icon = DOMAIN_ICONS.get(domain, "❓")
    cls  = f"badge-{domain}" if domain in DOMAIN_ICONS else "badge-unknown"
    return f'<span class="domain-badge {cls}">{icon} {domain}</span>'


# ── Helper: render structured card ───────────────────────────────────────────
def render_structured_card(output: dict):
    if not output or not isinstance(output, dict):
        return
    domain      = output.get("domain", "unknown")
    intent      = output.get("intent", "—")
    next_action = output.get("next_action", "—")
    missing     = output.get("missing_slots", [])
    slots = output.get("slots") or {}

    html = '<div class="output-card">'
    html += '<div class="metrics-row">'
    for label, val in [("Domain", domain), ("Intent", intent), ("Next Action", next_action)]:
        html += f'<div class="metric-chip"><div class="metric-label">{label}</div><div class="metric-value">{val}</div></div>'
    html += '</div>'
    html += domain_badge_html(domain)

    for dom, slot_block in slots.items():
        if not isinstance(slot_block, dict):
            continue
        search_slots  = {k: v for k, v in slot_block.get("search_slots",  {}).items() if v}
        booking_slots = {k: v for k, v in slot_block.get("booking_slots", {}).items() if v}
        if search_slots:
            html += '<div class="slot-section-label">Search slots</div><table class="slot-table">'
            for k, v in search_slots.items():
                html += f'<tr><td>{k}</td><td>{v}</td></tr>'
            html += '</table>'
        if booking_slots:
            html += '<div class="slot-section-label">Booking slots</div><table class="slot-table">'
            for k, v in booking_slots.items():
                html += f'<tr><td>{k}</td><td>{v}</td></tr>'
            html += '</table>'

    if missing:
        html += '<div class="slot-section-label">Missing slots</div>'
        html += "".join(f'<span class="missing-tag">⚠ {s}</span>' for s in missing)

    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-title">Travel <span>Assistant</span></div>
    <div class="page-tagline">✦ NLU Demo &nbsp;·&nbsp; Fine-tuned Mistral-7B &nbsp;·&nbsp; Hotel · Restaurant · Taxi · Attraction</div>
</div>
""", unsafe_allow_html=True)


# ── Render existing chat history ──────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg"><div class="user-bubble">{msg["content"]}</div></div>',
                    unsafe_allow_html=True)
    else:
        st.markdown(f'''
        <div class="bot-row">
            <div class="bot-avatar">✈</div>
            <div class="bot-text-bubble">{msg["text"]}</div>
        </div>''', unsafe_allow_html=True)
        if msg.get("normalized_output"):
            render_structured_card(msg["normalized_output"])

            with st.expander("🔬 Debug details"):
                st.markdown("**Raw model output**")
                st.code(msg.get("raw", ""), language="json")

                st.markdown("**Policy decision**")
                st.json(msg.get("policy_decision", {}))

                st.markdown("**Tool result**")
                st.json(msg.get("tool_result", {}))

                st.markdown("**Dialogue state**")
                st.json(msg.get("dialogue_state", {}))


# ── Chat input ────────────────────────────────────────────────────────────────
prefill = st.session_state.pop("prefill", "")
prompt  = st.chat_input("Type a travel request… e.g. 'I need a cheap hotel in the north'")
if not prompt and prefill:
    prompt = prefill

if prompt:
    if not api_url:
        st.error("Please enter your ngrok API URL in the sidebar first.")
        st.stop()

    api_url = api_url.strip().rstrip("/")

    # Show user message immediately
    st.markdown(
        f'<div class="user-msg"><div class="user-bubble">{prompt}</div></div>',
        unsafe_allow_html=True
    )
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.spinner("Thinking..."):
        try:
            resp = requests.post(
                f"{api_url}/chat",
                json={"message": prompt},
                timeout=180
            )

            # If backend returns an error page/text, show it clearly
            if resp.status_code != 200:
                st.error(f"Backend returned status {resp.status_code}")
                st.code(resp.text[:2000])
                st.stop()

            data = resp.json()

            # Support both new and old backend response formats
            chat_text = (
                data.get("response")
                or data.get("chat_response")
                or "Sorry, I could not generate a response."
            )

            normalized_output = (
                data.get("normalized_output")
                or data.get("output")
                or {}
            )

            policy_decision = data.get("policy_decision") or {}
            tool_result = data.get("tool_result") or {}
            dialogue_state = data.get("dialogue_state") or {}
            raw = data.get("raw_model_output") or data.get("raw") or ""

            # Show bot response
            st.markdown(f'''
            <div class="bot-row">
                <div class="bot-avatar">✈</div>
                <div class="bot-text-bubble">{chat_text}</div>
            </div>
            ''', unsafe_allow_html=True)

            # Show structured output
            render_structured_card(normalized_output)

            # Show debug exactly like notebook
            with st.expander("🔬 Debug details"):
                st.markdown("**Raw model output**")
                st.code(raw, language="json")

                st.markdown("**Normalized output**")
                st.json(normalized_output)

                st.markdown("**Policy decision**")
                st.json(policy_decision)

                st.markdown("**Tool result**")
                st.json(tool_result)

                st.markdown("**Dialogue state**")
                st.json(dialogue_state)

            # Save bot turn to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "text": chat_text,
                "normalized_output": normalized_output,
                "policy_decision": policy_decision,
                "tool_result": tool_result,
                "dialogue_state": dialogue_state,
                "raw": raw,
            })

        except requests.exceptions.Timeout:
            st.error("Request timed out. The model may still be generating.")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect. Is the Kaggle notebook API still running?")
        except Exception as e:
            st.error(f"Streamlit error: {e}")