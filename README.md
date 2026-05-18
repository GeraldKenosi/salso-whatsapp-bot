# SALSO WhatsApp Bot

An intelligent WhatsApp chatbot for **The South African Learner Support Organisation (SALSO)** built with Python, Flask, and Twilio.

## Features

- **ℹ️ About SALSO** — Organisation info, mission, and background
- **📋 Programmes** — Learn about SALSO's 4 core programmes (Breaking Barriers, Salubrious, CAP, No Shame)
- **❓ Smart FAQs** — Keyword-matching answers to 15+ common questions
- **📞 Contact** — Direct contact details including phone, email, and address
- **👤 One-time Registration** — User enters name/email/organisation/role once after saying "Hi", bot remembers them forever
- **🆘 Menu** — Full command reference

## Architecture

```
                    ┌─────────────┐
                    │  WhatsApp   │
                    │  (User)     │
                    └──────┬──────┘
                           │ Message
                           ▼
              ┌──────────────────────────┐
              │       Twilio API         │
              │  (WhatsApp Sandbox/Prod) │
              └────────────┬─────────────┘
                           │ HTTP POST
                           ▼
              ┌──────────────────────────┐
              │   Flask Web App (app.py) │
              │  POST /whatsapp webhook  │
              └────────────┬─────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ handlers │ │knowledge │ │ session  │
        │  .py     │ │ _base.py │ │   .py    │
        └──────────┘ └──────────┘ └──────────┘
                                        │
                                        ▼
                                  ┌──────────┐
                                  │ users.json│
                                  │ (persist) │
                                  └──────────┘
```

## Quick Start (Local Testing)

### 1. Install Python 3.9+

```bash
python --version
```

### 2. Set up the project

```bash
cd salso-wa-bot
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Get Twilio Credentials

1. Sign up for a free Twilio account at https://www.twilio.com
2. Go to **Console Dashboard** → copy your **Account SID** and **Auth Token**
3. Go to **Messaging > Try it out > Send a WhatsApp message**
4. Connect your WhatsApp number to the Twilio Sandbox
5. Copy the sandbox number (default: `+14155238886`)

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in:
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
```

### 5. Run the bot

```bash
python app.py
```

The bot will start on `http://0.0.0.0:5000`.

### 6. Expose with ngrok (for Twilio webhook)

In a new terminal:

```bash
ngrok http 5000
```

Copy the ngrok HTTPS URL (e.g. `https://abc123.ngrok.io`).

### 7. Configure Twilio Webhook

1. Go to **Twilio Console > Messaging > Sandbox > WhatsApp Sandbox Settings**
2. Set **WHEN A MESSAGE COMES IN** to: `https://your-ngrok-url.ngrok.io/whatsapp`
3. Set Method to **HTTP POST**
4. Click **Save**

### 8. Test

Send a WhatsApp message to the sandbox number from your phone:
- `Hi` — starts the conversation
- `About` — learn about SALSO
- `Programmes` — see our work
- `FAQ` — common questions
- `Contact` — reach us
- `Register` — update your profile

## Deployment with Your Own Domain (bot.salso.org.za)

You own **salso.org.za** — Twilio and Meta will trust your domain, no extra verification needed.

### Step-by-step: Render + bot.salso.org.za (Free, 30 minutes)

#### Step 1 — Push code to GitHub

Create a new repository on GitHub (public or private):

```bash
# In the salso-wa-bot folder
git init
git add .
git commit -m "Initial commit — SALSO WhatsApp Bot"
git remote add origin https://github.com/YOUR_USERNAME/salso-whatsapp-bot.git
git push -u origin main
```

Make sure `.env` is NOT committed (it's in `.gitignore`). Use `.env.example` as the template.

#### Step 2 — Deploy to Render

1. Go to **[https://dashboard.render.com](https://dashboard.render.com)** and sign up (free, no credit card needed)
2. Click **New +** → **Web Service**
3. Connect your GitHub account and select the `salso-whatsapp-bot` repo
4. Fill in the form:

| Field | Value |
|---|---|
| **Name** | `salso-whatsapp-bot` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:\$PORT` |
| **Plan** | **Free** |

5. Under **Environment Variables**, add these:

| Key | Value |
|---|---|
| `TWILIO_ACCOUNT_SID` | Your Twilio Account SID (from console.twilio.com) |
| `TWILIO_AUTH_TOKEN` | Your Twilio Auth Token |
| `TWILIO_WHATSAPP_NUMBER` | `+14155238886` (sandbox) or your approved WhatsApp number |

6. Click **Create Web Service**

Wait 2-3 minutes. Render will build and deploy. You'll get a URL like:
```
https://salso-whatsapp-bot.onrender.com
```

Test it: `https://salso-whatsapp-bot.onrender.com/health` → `{"status": "ok"}`

#### Step 3 — Connect your domain

1. In Render dashboard → web service → **Settings** tab
2. Scroll to **Custom Domain**
3. Enter: `bot.salso.org.za`
4. Click **Add Domain**
5. Render shows you a CNAME target

#### Step 4 — Update DNS

Add a CNAME record at your domain registrar:

| Field | Value |
|---|---|
| **Type** | `CNAME` |
| **Name** | `bot` |
| **Target** | Render CNAME target (e.g. `salso-whatsapp-bot.onrender.com`) |
| **TTL** | `3600` |

DNS propagation takes 5-30 minutes. Render provisions free SSL (Let's Encrypt) automatically.

#### Step 5 — Connect Twilio to your domain

1. Go to **[Twilio Console > Messaging > Try it out > Send a WhatsApp message](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)**
2. Scroll to **Sandbox Settings**
3. Set **WHEN A MESSAGE COMES IN** to: `https://bot.salso.org.za/whatsapp`
4. Set Method to **HTTP POST**
5. Click **Save**

That's it! Twilio forwards all WhatsApp messages to `https://bot.salso.org.za/whatsapp`.

#### Step 6 — Test

From your phone, send a WhatsApp message to the Twilio sandbox number:

```
Hi
```

Then try:
- `About` → SALSO info
- `Programmes` → our programmes
- `FAQ` → common questions
- `Contact` → contact details

---

### Going Live (Production — WhatsApp Business)

When you're ready to move beyond the sandbox:

1. **Register your business** at https://business.facebook.com using `salso.org.za` as your business domain
2. **Apply for WhatsApp Business API** through Twilio Console → Messaging → WhatsApp → Senders
3. Once approved, Twilio will give you a dedicated WhatsApp phone number
4. Update `TWILIO_WHATSAPP_NUMBER` in Render's environment variables to your new number
5. Update the Twilio webhook URL if needed

The domain `bot.salso.org.za` stays the same — no code changes needed.

---

### Alternative: Deploy on your own VPS

If you already have a server hosting `salso.org.za`:

1. SSH into your server
2. Copy the bot files to `/var/www/salso-whatsapp-bot/`
3. Set up a systemd service or Docker container
4. Configure Nginx reverse proxy:

```nginx
server {
    listen 443 ssl;
    server_name bot.salso.org.za;

    ssl_certificate /etc/letsencrypt/live/bot.salso.org.za/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bot.salso.org.za/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

5. Get SSL cert: `sudo certbot --nginx -d bot.salso.org.za`
6. Set Twilio webhook to `https://bot.salso.org.za/whatsapp`

## User Flow

```
User: Hi
Bot: Welcome! Could you please tell me your full name?
User: John Doe
Bot: Thanks, John! What is your email address?
User: john@salso.org.za
Bot: Great! Which organisation are you with?
User: SALSO
Bot: Excellent! What best describes your role?
User: Volunteer
Bot: ✅ You're all set, John!

--- Next conversation ---

User: Hi
Bot: Welcome back, John! 👋
     I can help you with:
     • About SALSO — type "about"
     • Programmes — type "programmes"
     • FAQ — type "faq"
     ...

User: about
Bot: 📍 The South African Learner Support Organisation...
```

## Price Breakdown

### Development / Testing (ZERO cost)

| Item | Cost |
|------|------|
| Twilio Account | Free |
| Twilio WhatsApp Sandbox | Free (unlimited test messages) |
| ngrok (local tunnel) | Free |
| Python / Flask | Open-source (free) |
| **Total** | **$0.00** |

### Production — Low Volume (<1,000 messages/month)

| Item | Cost |
|------|------|
| Twilio WhatsApp (outbound) | $0.005/message × ~500 = **$2.50** |
| Twilio WhatsApp (inbound) | $0.005/message × ~500 = **$2.50** |
| Hosting (Render free tier) | **$0.00** |
| Domain (already own salso.org.za) | **$0.00** |
| **Monthly Total** | **~$5.00** |

### Production — Medium Volume (<10,000 messages/month)

| Item | Cost |
|------|------|
| Twilio WhatsApp (~5,000 msgs) | **~$50.00** |
| Hosting (Render Pro, $7/month) | **$7.00** |
| **Monthly Total** | **~$57.00** |

## Files

| File | Purpose |
|------|---------|
| `app.py` | Flask web app with Twilio webhook endpoint |
| `bot/handlers.py` | Message routing, registration flow, menu logic |
| `bot/knowledge_base.py` | SALSO info, programmes, FAQs, keyword map |
| `bot/session.py` | User persistence (JSON file) |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variable template |
| `data/users.json` | User data (auto-created, gitignored) |

## Customisation

- **Add FAQs**: Edit `FAQS` list and `FAQ_KEYWORDS` map in `bot/knowledge_base.py`
- **Add programmes**: Edit `PROGRAMMES` list in `bot/knowledge_base.py`
- **Change registration fields**: Edit `_handle_registration()` in `bot/handlers.py`
- **Add new commands**: Add a new `if text in [...]` block in `handle_message()` and a corresponding `_function()`
