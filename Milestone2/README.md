# FreightQuote AI — Milestone 2
Full-Stack AI/ML Integration & Advanced Security Engine

## What Milestone 2 adds on top of Milestone 1
Milestone 1 delivered the User Authentication module — JWT session handling, a
Streamlit login UI, SQLite credential storage, and Gmail-based OTP verification.

Milestone 2 unifies that security gateway with the multi-agent ML core and the LLM
Copilot, and adds three hardening layers on top of it:

1. **Progressive account lockout** — 3 failed logins locks the account for 5 minutes,
   4 failed logins locks it for 15 minutes, and a 5th failed attempt locks the account
   permanently until an Administrator unlocks it from the Admin Dashboard.
2. **Dynamic password strength verification** — passwords under 5 characters are
   blocked outright; 5–9 characters is allowed but flagged "Average"; 10+ characters
   is flagged "Good". This runs live on both the registration form and the
   password-reset form.
3. **A fully functional Admin Dashboard** — Add / Delete / Unlock user lifecycle
   controls, an LLM Activity Monitor (queries per user), and an ML Model Card tab
   showing each agent's champion algorithm and metric.

On top of the security layer, three autonomous ML agents (Pricing, Route Delay,
Carrier Compliance) each compare 5+ algorithms per Kaggle dataset pair and save a
champion model. A Qwen2.5-3B-Instruct (4-bit) LLM Copilot then synthesizes the three
agents' numeric outputs into a plain-English recommendation, a "Debate View" showing
each agent's independent take, and a structured JSON audit action.

## Features built
- Login / Registration / Forgot Password (Gmail OTP) gating all other pages
- Progressive lockout (5 / 15 min / permanent) — `auth.py`
- OTP resend cooldown (60s → 3min → 5min → 1hr) — `auth.py`
- Password strength checker (Weak / Average / Good) — `auth.py`
- Agent 1: Dynamic Pricing (regression, R² ≥ 0.90 target) — `train_ml_freight.py`
- Agent 2: Route Delay Classifier (ROC-AUC optimized) — `train_ml_freight.py`
- Agent 3: Carrier Compliance Sentinel (ROC-AUC optimized) — `train_ml_freight.py`
- AI Copilot powered by Qwen2.5-3B-Instruct (4-bit, bitsandbytes) — `llm_engine_freight.py`
- Debate View + structured JSON audit action synthesis — `llm_engine_freight.py`
- Admin Dashboard: Add / Delete / Unlock users, LLM Activity Monitor, ML Model Card — `admin_dash.py`

## Tech stack
- **Frontend:** Streamlit
- **Auth:** PyJWT, bcrypt, SQLite
- **ML:** scikit-learn, joblib, kagglehub
- **LLM:** HuggingFace Transformers, bitsandbytes (4-bit quantization), Qwen2.5-3B-Instruct
- **Tunnel:** pyngrok
- **Notebook:** Google Colab (T4 GPU)

## Indian port coverage
| Port | Code | Region |
|---|---|---|
| Jawaharlal Nehru Port (Mumbai) | JNPT | West Coast |
| Mundra Port | MUNDRA | West Coast (Gujarat) |
| Chennai Port | CHENNAI | East Coast |
| Cochin Port | COCHIN | South-West Coast (Kerala) |

## How to run
1. Open `FreightQuote_AI_Milestone2.ipynb` in Google Colab.
2. **Runtime → Change runtime type → T4 GPU → Save.**
3. Add the Colab Secrets listed below (🔑 icon in the left sidebar), toggling
   notebook access ON for each.
4. Run all cells top to bottom. The last cell prints the public ngrok URL.
5. Sign in with your `ADMIN_EMAIL_ID` / `ADMIN_PASSWORD` secret (or the default
   `infosys@ai` / `admin@123` if those secrets aren't set).

### Colab Secrets setup
| Secret | How to get it | Used for |
|---|---|---|
| `JWT_SECRET_KEY` | Any long random string you make up | Signs/verifies session tokens |
| `ADMIN_EMAIL_ID` | Any email you choose (default: `infosys@ai`) | Bootstraps the Admin account |
| `ADMIN_PASSWORD` | Any password meeting the strength rule | Bootstraps the Admin account |
| `NGROK_AUTHTOKEN` | ngrok.com → dashboard → Authtoken | Public HTTPS URL for the Streamlit app |
| `HF_TOKEN` | HuggingFace → Settings → Access Tokens | Loads Qwen2.5-3B-Instruct (4-bit) |
| `EMAIL_ID` (optional) | Your Gmail address | Sends real OTP emails |
| `EMAIL_PASSWORD` (optional) | Gmail → 2-Step Verification → App Passwords | Authenticates Gmail SMTP |
| `KAGGLE_USERNAME` / `KAGGLE_KEY` (optional) | kaggle.com → Settings → API → Create New Token | Trains on real Kaggle data instead of synthetic |

### Kaggle API setup (optional but recommended)
1. Log in at kaggle.com → profile picture → **Settings → API → Create New Token**.
2. This downloads `kaggle.json` containing your username and key.
3. Add both as Colab Secrets (`KAGGLE_USERNAME`, `KAGGLE_KEY`) — the notebook reads
   them and sets the environment variables automatically. **The notebook still works
   without this**, falling back to a seeded synthetic data generator.

## Screenshots
See the `screenshots/` folder:
- `01_home_page.png` — Home / KPI dashboard
- `02_ai_copilot.png` — AI Copilot prompt + response
- `03_pricing_calculator.png` — Agent 1 input + predicted cost
- `04_ml_model_card.png` — Admin → ML Model Card (R²/ROC-AUC for all agents)
- `05_admin_user_actions.png` — Admin → Add / Delete / Unlock user
- `06_lockout_and_otp_cooldown.png` — Triggered lockout message + OTP cooldown message
