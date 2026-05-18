import re
from .knowledge_base import ORGANISATION, PROGRAMMES, FAQS, FAQ_KEYWORDS
from .session import get_or_create_user, update_user, is_registered

# Track registration step for users who haven't completed it
_registration_steps = {}


def handle_message(wa_id, profile_name, message_text):
    """Main message handler. Returns a list of reply strings."""

    # Get or create user
    user, is_new = get_or_create_user(wa_id, profile_name)

    # If user is mid-registration, continue that flow
    if wa_id in _registration_steps:
        return _handle_registration(wa_id, message_text, user)

    # Check if user is saying hello / hi
    greeting_pattern = r"^(hi|hello|hey|howdy|good\s*(morning|afternoon|evening)|greetings|yo|h[o]+la)[\s!.]*$"
    if re.match(greeting_pattern, message_text.strip().lower()):
        return _handle_greeting(wa_id, user, is_new)

    # Command routing
    text = message_text.strip().lower()

    if text in ["menu", "help", "options", "what can you do"]:
        return [_show_menu()]

    if text in ["about", "info", "about salo", "about salso"]:
        return [_about_salo()]

    if text in ["programmes", "work", "what we do", "our work"]:
        return [_our_programmes()]

    if text in ["faq", "faqs", "questions", "help"]:
        return [_show_faqs()]

    if text in ["contact", "email", "call", "reach us"]:
        return [_contact_info()]

    if text in ["register", "my details", "profile", "update"]:
        _registration_steps[wa_id] = {"step": "name"}
        return [
            "Let's set up your profile.\n\n"
            "What is your full name?"
        ]

    # Try to match FAQ by keyword
    faq_reply = _try_faq_match(text)
    if faq_reply:
        return [faq_reply]

    return [_fallback()]


def _handle_greeting(wa_id, user, is_new):
    name = user.get("profile_name", "there")
    registered = is_registered(wa_id)

    if registered and user.get("name"):
        greeting = f"Welcome back, {user['name']}! 👋\n\n"
    elif registered:
        greeting = f"Welcome back, {name}! 👋\n\n"
    else:
        greeting = f"Hello {name}! Welcome to SALO — the Southern African Liaison Office. 👋\n\n"

    greeting += (
        "I can help you with:\n"
        "• ℹ️  About SALO — type *about*\n"
        "• 📋 Our Programmes — type *programmes*\n"
        "• ❓ FAQs — type *faq*\n"
        "• 📞 Contact Us — type *contact*\n"
        "• 📝 Register / My Profile — type *register*\n"
        "• 🆘 Menu — type *menu*\n\n"
        "What would you like to know?"
    )

    if not registered:
        _registration_steps[wa_id] = {"step": "name"}
        greeting += (
            "\n\n---\n"
            "Also, could you please tell me your *full name* so I can remember you?"
        )

    return [greeting]


def _handle_registration(wa_id, message_text, user):
    step_data = _registration_steps[wa_id]
    step = step_data.get("step")
    text = message_text.strip()

    if step == "name":
        update_user(wa_id, name=text)
        _registration_steps[wa_id]["step"] = "email"
        return [f"Thanks, {text}! What is your *email address*?"]

    if step == "email":
        if "@" not in text or "." not in text:
            return ["That doesn't look like a valid email. Please enter a valid email address (e.g. name@example.com)."]
        update_user(wa_id, email=text)
        _registration_steps[wa_id]["step"] = "organisation"
        return [
            f"Great! Got it.\n\n"
            f"Which *organisation* are you with (or are you an individual interested in SALO's work)?"
        ]

    if step == "organisation":
        update_user(wa_id, organisation=text, registered=True)
        _registration_steps[wa_id]["step"] = "role"
        return [
            f"Excellent! And finally, what best describes your *role*?\n\n"
            f"Options: Student / Researcher / NGO Worker / Government / Media / Other"
        ]

    if step == "role":
        update_user(wa_id, role=text)
        del _registration_steps[wa_id]
        return [
            f"✅ You're all set, {user.get('name', 'friend')}!\n\n"
            f"Here's what I have saved:\n"
            f"• Name: {user.get('name')}\n"
            f"• Email: {user.get('email')}\n"
            f"• Organisation: {user.get('organisation')}\n"
            f"• Role: {text}\n\n"
            f"Type *menu* to see what I can help you with, or just ask me anything about SALO!"
        ]

    del _registration_steps[wa_id]
    return ["Something went wrong. Type *menu* to start over."]


def _about_salo():
    org = ORGANISATION
    text = (
        f"📍 *{org['name']}*\n"
        f"_{org['tagline']}_\n\n"
        f"{org['description']}\n\n"
        f"🌐 {org['website']}\n"
        f"📧 {org['email']}\n\n"
        f"Type *programmes* to learn about our work, or *faq* for common questions."
    )
    return [text]


def _our_programmes():
    lines = ["📋 *SALO's Key Programmes:*\n"]
    for i, p in enumerate(PROGRAMMES, 1):
        lines.append(f"{i}. *{p['title']}*")
        lines.append(f"   {p['description']}\n")
    lines.append("Type *about* for general info, or *faq* for common questions.")
    return ["\n".join(lines)]


def _show_faqs():
    lines = ["❓ *Frequently Asked Questions:*\n"]
    for i, faq in enumerate(FAQS, 1):
        lines.append(f"{i}. {faq['question']}")
    lines.append("\nReply with a number (1-{}) to see the answer.".format(len(FAQS)))
    lines.append("Or just type your question freely!")
    return ["\n".join(lines)]


def _show_menu():
    return [
        "*📋 MENU*\n\n"
        "Type any of these:\n\n"
        "• *about* — About SALO\n"
        "• *programmes* — Our work & programmes\n"
        "• *faq* — Frequently asked questions\n"
        "• *contact* — Contact information\n"
        "• *register* — Set up / update your profile\n"
        "• *hi* — Start over\n\n"
        "Or just ask me anything about SALO!"
    ]


def _contact_info():
    return [
        "📞 *Contact SALO*\n\n"
        f"📧 Email: {ORGANISATION['email']}\n"
        f"🌐 Website: {ORGANISATION['website']}\n\n"
        "For general enquiries, feedback, or partnership opportunities, "
        "email us and we'll get back to you."
    ]


def _try_faq_match(text):
    """Try to find a matching FAQ based on keywords in the user's message."""
    # Check if user typed a number (FAQ index)
    num_match = re.match(r"^(\d+)$", text.strip())
    if num_match:
        idx = int(num_match.group(1)) - 1
        if 0 <= idx < len(FAQS):
            faq = FAQS[idx]
            return f"*Q:* {faq['question']}\n\n*A:* {faq['answer']}"

    # Keyword matching
    words = set(re.findall(r"[a-z]+", text.lower()))
    best_idx = None
    best_score = 0

    for word in words:
        if word in FAQ_KEYWORDS:
            for idx in FAQ_KEYWORDS[word]:
                # Count how many of the user's words match this FAQ's question
                q_words = set(re.findall(r"[a-z]+", FAQS[idx]["question"].lower()))
                overlap = len(words & q_words)
                if overlap > best_score:
                    best_score = overlap
                    best_idx = idx

    if best_idx is not None and best_score >= 1:
        faq = FAQS[best_idx]
        return f"*Q:* {faq['question']}\n\n*A:* {faq['answer']}\n\n---\nType *faq* for more questions."

    # If user asked a question-like thing but we couldn't match
    if "?" in text:
        return (
            "I'm not sure I have the answer to that. Try:\n"
            "• *faq* — See common questions\n"
            "• *contact* — Reach SALO directly\n"
            "• *about* — Learn about SALO"
        )

    return None


def _fallback():
    return [
        "I didn't quite understand that. 🤔\n\n"
        "Here's what I can help with:\n"
        "• *about* — About SALO\n"
        "• *programmes* — Our work\n"
        "• *faq* — FAQs\n"
        "• *contact* — Reach us\n"
        "• *register* — Set up your profile\n"
        "• *menu* — Show all options\n\n"
        "Or just type *hi* to start over!"
    ]
