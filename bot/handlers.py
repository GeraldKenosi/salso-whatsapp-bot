import re
from .knowledge_base import ORGANISATION, PROGRAMMES, FAQS, FAQ_KEYWORDS
from .session import get_or_create_user, update_user, is_registered

_registration_steps = {}
_menu_states = {}  # wa_id -> current menu name or None


# ── Menu definitions ──────────────────────────────────────────

MENUS = {
    "main": {
        "title": "MAIN MENU",
        "options": [
            ("About SALSO", "show_about"),
            ("Our Programmes", "menu:programmes"),
            ("FAQs", "menu:faq"),
            ("Contact Us", "show_contact"),
            ("Register / My Profile", "register"),
            ("Partners & Schools", "show_partners"),
        ],
    },
    "programmes": {
        "title": "PROGRAMMES",
        "options": [
            (p["title"], f"show_programme:{i}")
            for i, p in enumerate(PROGRAMMES)
        ] + [("Back to Main Menu", "menu:main")],
    },
    "faq": {
        "title": "FAQ TOPICS",
        "options": [
            (faq["question"][:60], f"show_faq:{i}")
            for i, faq in enumerate(FAQS)
        ] + [("Back to Main Menu", "menu:main")],
    },
}


def _format_menu(menu_name):
    """Build a menu string from its definition."""
    menu = MENUS[menu_name]
    lines = [f"*{menu['title']}*\n"]
    for i, (label, _) in enumerate(menu["options"], 1):
        lines.append(f"{i}. {label}")
    lines.append("\nReply with a number, or type your question freely.")
    return "\n".join(lines)


def _execute_action(wa_id, action, user):
    """Run a menu action and return (replies, new_menu)."""
    # --- direct content actions ---
    if action == "show_about":
        return _about_salso(), "main"
    if action == "show_contact":
        return _contact_info(), "main"
    if action == "show_partners":
        return _partners_info(), "main"
    if action == "register":
        _registration_steps[wa_id] = {"step": "name"}
        return ["Let's set up your profile.\n\nWhat is your full name?"], None
    if action.startswith("show_programme:"):
        idx = int(action.split(":", 1)[1])
        p = PROGRAMMES[idx]
        text = (
            f"*{p['title']}* ({p['short']})\n\n"
            f"{p['description']}\n\n"
            f"Reply *0* to go back to Programmes."
        )
        return [text], "programmes"
    if action.startswith("show_faq:"):
        idx = int(action.split(":", 1)[1])
        faq = FAQS[idx]
        text = f"*Q:* {faq['question']}\n\n*A:* {faq['answer']}"
        return [text], "faq"

    # --- menu navigation actions ---
    if action.startswith("menu:"):
        target = action.split(":", 1)[1]
        return [_format_menu(target)], target

    # fallback
    return [_format_menu("main")], "main"


# ── Main handler ──────────────────────────────────────────────

def _cancel_process(wa_id):
    """Cancel any in-progress process for this user."""
    if wa_id in _registration_steps:
        del _registration_steps[wa_id]
    _menu_states[wa_id] = "main"


def handle_message(wa_id, profile_name, message_text):
    user, is_new = get_or_create_user(wa_id, profile_name)

    text = message_text.strip()
    text_lower = text.lower()

    # Global escape: "menu" always goes to main menu, cancels anything in progress
    if text_lower in ["menu", "help", "options", "what can you do", "main menu", "home"]:
        _cancel_process(wa_id)
        return [_format_menu("main")]

    # Mid-registration -> continue
    if wa_id in _registration_steps:
        return _handle_registration(wa_id, message_text, user)

    # Greeting
    greeting_pattern = r"^(hi|hello|hey|howdy|good\s*(morning|afternoon|evening)|greetings|yo|h[o]+la)[\s!.]*$"
    if re.match(greeting_pattern, text_lower):
        return _handle_greeting(wa_id, user, is_new)

    # --- Determine response and menu state ---
    replies = None
    new_menu = None

    # Explicit command routing (still supported for power users)
    if text_lower in ["about", "info", "about salso", "about salo"]:
        replies = _about_salso() + ["", "Reply *0* for Main Menu."]
        new_menu = "main"

    elif text_lower in ["programmes", "programs", "work", "what we do", "our work"]:
        replies, new_menu = [_format_menu("programmes")], "programmes"

    elif text_lower in ["faq", "faqs", "questions"]:
        replies, new_menu = [_format_menu("faq")], "faq"

    elif text_lower in ["contact", "email", "call", "reach us"]:
        replies = _contact_info() + ["", "Reply *0* for Main Menu."]
        new_menu = "main"

    elif text_lower in ["register", "my details", "profile", "update"]:
        _registration_steps[wa_id] = {"step": "name"}
        return ["Let's set up your profile.\n\nWhat is your full name?"]

    elif text_lower in ["partners", "schools"]:
        replies = _partners_info() + ["", "Reply *0* for Main Menu."]
        new_menu = "main"

    elif text in ("0", "back", "exit", "go back"):
        replies, new_menu = [_format_menu("main")], "main"

    else:
        # Try number -> menu action or FAQ
        num_match = re.match(r"^(\d+)$", text)
        if num_match:
            num = int(num_match.group(1))
            current = _menu_states.get(wa_id)
            if current and current in MENUS:
                menu = MENUS[current]
                if 1 <= num <= len(menu["options"]):
                    _, action = menu["options"][num - 1]
                    replies, new_menu = _execute_action(wa_id, action, user)
            if replies is None and 1 <= num <= len(FAQS):
                faq = FAQS[num - 1]
                replies = [f"*Q:* {faq['question']}\n\n*A:* {faq['answer']}\n\n---\nReply *0* for Main Menu."]
                new_menu = None

        if replies is None:
            faq_reply = _try_faq_match(text_lower)
            if faq_reply:
                replies = [faq_reply]

    if replies is None:
        replies = _fallback()

    _menu_states[wa_id] = new_menu
    return replies


# ── Greeting ──────────────────────────────────────────────────

def _handle_greeting(wa_id, user, is_new):
    name = user.get("profile_name", "there")
    registered = is_registered(wa_id)

    if registered and user.get("name"):
        lines = [f"Welcome back, {user['name']}! 👋\n"]
    elif registered:
        lines = [f"Welcome back, {name}! 👋\n"]
    else:
        lines = [f"Hello {name}! Welcome to SALSO — The South African Learner Support Organisation. 👋\n"]

    lines.append(_format_menu("main"))
    _menu_states[wa_id] = "main"

    if not registered:
        lines.append(
            "Tip: Select option 5 to register so I can remember you next time!"
        )

    return lines


# ── Registration (asks name + email once, saves permanently) ──

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
        update_user(wa_id, email=text, registered=True)
        del _registration_steps[wa_id]
        _menu_states[wa_id] = "main"
        return [
            f"All set, {user.get('name', 'friend')}!\n\n"
            f"I'll remember you as:\n"
            f"  Name: {user.get('name')}\n"
            f"  Email: {text}\n\n"
            f"Reply with a number from the menu below, or just ask me anything!"
        ] + [_format_menu("main")]

    del _registration_steps[wa_id]
    _menu_states[wa_id] = "main"
    return [_format_menu("main")]


# ── Content functions ─────────────────────────────────────────

def _about_salso():
    org = ORGANISATION
    return [
        f"*{org['name']}*\n"
        f"_{org['tagline']}_\n\n"
        f"{org['description']}\n\n"
        f"Website: {org['website']}\n"
        f"Email: {org['email']} / {org['email2']}\n"
        f"Phone: {org['phone']} / {org['phone2']}\n"
        f"Address: {org['address']}\n\n"
        f"Reply *0* for Main Menu."
    ]


def _contact_info():
    org = ORGANISATION
    return [
        f"*Contact SALSO*\n\n"
        f"Email: {org['email']} / {org['email2']}\n"
        f"Phone: {org['phone']} / {org['phone2']}\n"
        f"Address: {org['address']}\n"
        f"Website: {org['website']}\n\n"
        f"Reply *0* for Main Menu."
    ]


def _partners_info():
    from .knowledge_base import PARTNERS, COLLABORATING_SCHOOLS
    lines = ["*Partners & Schools*\n"]
    lines.append("Partners:")
    for p in PARTNERS:
        lines.append(f"  - {p['name']} ({p['role']})")
    lines.append("\nCollaborating Schools:")
    for s in COLLABORATING_SCHOOLS:
        lines.append(f"  - {s}")
    lines.append("\nReply *0* for Main Menu.")
    return ["\n".join(lines)]


# ── FAQ matching ──────────────────────────────────────────────

def _try_faq_match(text):
    words = set(re.findall(r"[a-z]+", text.lower()))
    best_idx = None
    best_score = 0

    for word in words:
        if word in FAQ_KEYWORDS:
            for idx in FAQ_KEYWORDS[word]:
                q_words = set(re.findall(r"[a-z]+", FAQS[idx]["question"].lower()))
                overlap = len(words & q_words)
                if overlap > best_score:
                    best_score = overlap
                    best_idx = idx

    if best_idx is not None and best_score >= 1:
        faq = FAQS[best_idx]
        return f"*Q:* {faq['question']}\n\n*A:* {faq['answer']}\n\n---\nReply *0* for Main Menu."

    if "?" in text:
        return (
            "I'm not sure I have the answer to that. Try:\n"
            "- *faq* to see common questions\n"
            "- *contact* to reach SALSO directly"
        )

    return None


def _fallback():
    return [
        "I didn't quite understand that.\n\n"
        "Here's what I can do:\n"
        "- Type a number from the menu\n"
        "- Type *about*, *programmes*, *faq*, *contact*, *partners*\n"
        "- Type *menu* to see all options\n"
        "- Type *hi* to start over"
    ]
