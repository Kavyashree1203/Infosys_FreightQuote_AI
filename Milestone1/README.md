# Milestone 1 — User Authentication Module

**Infosys Springboard Internship 7.0 · Batch 1 · Milestone 1**

## About This Milestone

This milestone builds a complete user authentication module for **Infosys FreightQuote** — a smart logistics quotation and authentication portal. It covers user signup, login, password recovery (via security question or email OTP), a session-protected user dashboard, and a separate admin dashboard, all built as a single Streamlit app and served publicly through ngrok while running inside Google Colab.

## Features Built

- **Login Page** — Username/Email + Password, both mandatory. On success, a JWT session token is issued and the user is taken to the Dashboard. On failure, a single generic error is shown (it never reveals whether the username or the password was wrong).
- **Signup Page** — Username, Email, Password, Confirm Password, Security Question (chosen from a fixed list), and Security Answer — all mandatory. Usernames must be unique; duplicate signups are rejected with a clear message.
- **Forgot Password Page** — Two recovery routes on the same page:
  - **Security Question route** — enter your username, answer the question you set at signup, then set a new password.
  - **Email OTP route** — enter your registered email, receive a 6-digit one-time code by email, verify it, then set a new password.
  - Both routes enforce the same password rule as Signup.
- **JWT Session Handling** — A JWT is issued only at Login and stored in Streamlit's session state. The Dashboard checks for a valid JWT before rendering; Signup and password resets always route back to Login instead of issuing a session directly.
- **Field Validation**
  - No form submits while a mandatory field is empty.
  - Email must be shaped like `ab@cd.ef` (at least 2 letters before the `@`, at least 2 letters between the `@` and the dot, at least 2 letters after the final dot).
  - Password must be at least 8 characters and include an uppercase letter, a lowercase letter, a number, and a special symbol. Confirm Password must match exactly.
- **User Dashboard** — Welcomes the logged-in user by name, confirms JWT authentication, shows basic account details, and includes a Logout action that clears the session and returns to Login.
- **Admin Dashboard** — A separate login using an admin username/password defined directly in code (not a signup account). Once logged in, it lists every registered user's username and email — password data is never displayed. It isn't linked in the navigation; it's reached only through a hidden URL flag (`?admin=1`) to keep it out of the public-facing UI.

## Tech Stack

| Layer | Technology |
| --- | --- |
| UI / App framework | [Streamlit](https://streamlit.io/) |
| Session tokens | [PyJWT](https://pyjwt.readthedocs.io/) |
| Public URL tunnel | [ngrok](https://ngrok.com/) (via `pyngrok`) |
| OTP delivery | Gmail SMTP (`smtplib`, Gmail App Password) |
| User storage | Local JSON file (`users.json`) — sufficient for a Colab demo |
| Password / answer hashing | SHA-256 (`hashlib`) |
| Secrets management | Google Colab Secrets |

## Project Structure

## How to Run

1. Open `Milestone1.ipynb` in **Google Colab**.
2. Set up the required secrets under **Colab Secrets** (key icon in the left sidebar), and toggle notebook access **on** for each:

   | Secret Name | Value |
   | --- | --- |
   | `JWT_SECRET` | Any long random string used to sign session tokens |
   | `NGROK_AUTHTOKEN` | Your personal ngrok Authtoken |
   | `EMAIL_PASSWORD` | A Gmail **App Password** (requires 2-Step Verification enabled) |
   | `EMAIL_ADDRESS` | The Gmail address that will send OTP emails |

3. Run all cells from top to bottom (**Runtime → Run all**, or restart the runtime first if re-running).
4. The last cell prints a public **ngrok URL** — open it in your browser to use the app.
5. To reach the Admin Dashboard, open the same URL with `?admin=1` appended, e.g. `https://your-ngrok-url/?admin=1`.

## Security Notes

- No secrets (email address, JWT secret, ngrok token, admin password) are hard-coded in the notebook — all are read from Colab Secrets at runtime.
- Passwords and security answers are stored as SHA-256 hashes, never in plain text.
- OTPs expire after 5 minutes and are single-use.

## Screenshots

_Add screenshots to a `screenshots/` folder in this directory, then link them below (one below the other):_

### Login
![Login](screenshots/login.png)

### Signup
![Signup](screenshots/signup.png)

### Forgot Password — Security Question
![Forgot Password - Security Question](screenshots/forgot-security-question.png)

### Forgot Password — Email OTP
![Forgot Password - OTP](screenshots/forgot-otp.png)

### OTP Email
![OTP Email](screenshots/otp-email.png)

### User Dashboard
![User Dashboard](screenshots/user-dashboard.png)

### Admin Dashboard
![Admin Dashboard](screenshots/admin-dashboard.png)

---
*Infosys Springboard 7.0 — Batch 1 — Milestone 1*
