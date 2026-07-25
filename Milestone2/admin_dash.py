"""
admin_dash.py — Admin Dashboard (Phase 4, Section 9).
Restricted to users authenticated with role == 'Admin'.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

import db
import auth
import ui_theme


def render_admin_dashboard(current_username: str):
    ui_theme.render_header("FreightQuote AI", "Admin Control Panel", right_label=current_username)

    tab1, tab2, tab3 = st.tabs(["👥 User Management", "🧠 LLM Activity Monitor", "📊 ML Model Card"])

    with tab1:
        _render_user_management()

    with tab2:
        _render_llm_activity_monitor()

    with tab3:
        _render_ml_model_card()


# ------------------------------------------------------------------
# Tab 1: User Management (Add / Delete / Unlock)
# ------------------------------------------------------------------
def _render_user_management():
    st.subheader("👥 User Management")

    with st.expander("➕ Add New User"):
        with st.form("add_user_form", clear_on_submit=True):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Initial Password", type="password")
            new_role = st.selectbox("Role", ["Admin", "Logistics Manager", "Carrier Auditor"])
            submitted = st.form_submit_button("Create Account")

            if submitted:
                if not (new_username and new_email and new_password):
                    st.warning("All fields are required.")
                else:
                    ok, msg = auth.register_user(new_username, new_email, new_password, role=new_role)
                    if ok:
                        st.success(f"✅ User '{new_username}' created with role [{new_role}].")
                        st.rerun()
                    else:
                        st.error(msg)

    st.divider()

    conn = db.get_conn()
    users = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    conn.close()

    for u in users:
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
        col1.markdown(f"**{u['username']}**")
        col2.markdown(f"[{u['role']}]")
        col3.markdown(f"{u['created_at']}")

        needs_unlock = (u["account_status"] == "locked") or (u["failed_attempts"] and u["failed_attempts"] >= 3)
        if needs_unlock:
            if col4.button("Unlock", key=f"unlock_{u['id']}"):
                conn = db.get_conn()
                conn.execute(
                    "UPDATE users SET failed_attempts = 0, lock_until = NULL, "
                    "account_status = 'active' WHERE id = ?",
                    (u["id"],),
                )
                conn.commit()
                conn.close()
                st.success("✅ User account unlocked successfully.")
                st.rerun()

        if col5.button("Delete", key=f"delete_{u['id']}"):
            current = st.session_state.get("username")
            if u["username"] == current:
                st.error("You cannot delete the account you're logged in as.")
            else:
                conn = db.get_conn()
                conn.execute("DELETE FROM users WHERE id = ?", (u["id"],))
                conn.commit()
                conn.close()
                st.success(f"Deleted user '{u['username']}'.")
                st.rerun()


# ------------------------------------------------------------------
# Tab 2: LLM Activity Monitor
# ------------------------------------------------------------------
def _render_llm_activity_monitor():
    st.subheader("🧠 LLM Activity Monitor")

    conn = db.get_conn()
    logs = conn.execute("SELECT username, COUNT(*) as queries FROM copilot_logs GROUP BY username").fetchall()
    total = conn.execute("SELECT COUNT(*) as c FROM copilot_logs").fetchone()["c"]
    conn.close()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Copilot Queries", total)
        if logs:
            df = pd.DataFrame([dict(r) for r in logs])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No Copilot queries logged yet.")

    with col2:
        st.markdown("**Queries per User**")
        if logs:
            df = pd.DataFrame([dict(r) for r in logs])
            st.bar_chart(df.set_index("username"))
        else:
            st.info("No data to chart yet.")


# ------------------------------------------------------------------
# Tab 3: ML Model Card (training transparency)
# ------------------------------------------------------------------
def _render_ml_model_card():
    st.subheader("📊 ML Model Card — Training Transparency")

    conn = db.get_conn()
    rows = conn.execute(
        "SELECT * FROM ml_models WHERE is_champion = 1 ORDER BY agent_name"
    ).fetchall()
    conn.close()

    if not rows:
        st.info("No models trained yet. Run train_ml_freight.train_all_agents() in the notebook first.")
        return

    for r in rows:
        c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
        c1.markdown(f"**{r['agent_name']}**")
        c2.markdown(f"Champion: `{r['algorithm']}`")
        c3.markdown(f"{r['metric_name']}: **{r['metric_value']:.4f}**")
        c4.markdown(f"🏆 Champion")

    st.divider()
    st.markdown("**All algorithms compared (per agent):**")
    conn = db.get_conn()
    all_rows = conn.execute("SELECT agent_name, algorithm, metric_name, metric_value, is_champion "
                             "FROM ml_models ORDER BY agent_name, metric_value DESC").fetchall()
    conn.close()
    df_all = pd.DataFrame([dict(r) for r in all_rows])
    if not df_all.empty:
        df_all["is_champion"] = df_all["is_champion"].map({1: "🏆", 0: ""})
        st.dataframe(df_all, use_container_width=True)
