"""
admin_dash.py
Admin Dashboard — Section 9 of the Milestone 2 spec.
Rendered only when the logged-in user's role == 'Admin' (checked in app.py).
"""

import streamlit as st
import db
from ui_theme import card_start, card_end


def render():
    card_start("🛡️ Admin Dashboard")

    tab_users, tab_models = st.tabs(["User Lifecycle", "ML Model Card"])

    # ---------------- User Lifecycle: Add / Delete / Unlock ----------------
    with tab_users:
        st.subheader("Add User")
        with st.form("add_user_form", clear_on_submit=True):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Initial Password", type="password")
            new_role = st.selectbox("Role", ["Admin", "Logistics Manager", "User"])
            submitted = st.form_submit_button("Add User")
            if submitted:
                if not all([new_username, new_email, new_password]):
                    st.warning("All fields are required.")
                else:
                    db.create_user(
                        new_username, new_email, new_password,
                        security_question="What is your favourite pet's name?",
                        security_answer="reset-me",
                        role=new_role,
                    )
                    st.success(f"✅ User '{new_username}' created with role '{new_role}'.")
                    st.rerun()

        st.markdown("---")
        st.subheader("Existing Users")
        users = db.get_all_users()

        for u in users:
            cols = st.columns([2, 2, 1.5, 1.5, 1.5, 1.5])
            cols[0].write(u["username"])
            cols[1].write(u["email"])
            cols[2].write(u["role"])
            status = u["account_status"]
            if status == "locked" or u["failed_attempts"] >= 3:
                cols[3].markdown(":red[locked]")
            else:
                cols[3].markdown(":green[active]")

            if status == "locked" or u["failed_attempts"] >= 3:
                if cols[4].button("🔓 Unlock", key=f"unlock_{u['id']}"):
                    db.unlock_user(u["id"])
                    st.success("✅ User account unlocked successfully.")
                    st.rerun()
            else:
                cols[4].write("—")

            if cols[5].button("🗑️ Delete", key=f"delete_{u['id']}"):
                db.delete_user(u["id"])
                st.warning(f"User '{u['username']}' deleted.")
                st.rerun()

    # ---------------- ML Model Card ----------------
    with tab_models:
        st.subheader("Model Training Transparency")
        metrics = db.get_model_metrics()
        if not metrics:
            st.info("No models trained yet. Run train_ml_freight.py in the notebook first.")
        else:
            agents = sorted(set(m["agent_name"] for m in metrics))
            for agent in agents:
                st.markdown(f"**{agent}**")
                rows = [m for m in metrics if m["agent_name"] == agent]
                st.table(
                    [{
                        "Algorithm": r["algorithm"],
                        "Metric": r["metric_name"],
                        "Value": round(r["metric_value"], 4),
                        "Champion": "🏆" if r["is_champion"] else "",
                    } for r in rows]
                )

    card_end()
