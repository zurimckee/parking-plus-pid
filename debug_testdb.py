import streamlit as st
import os

st.title("🔌 Database Connection Test")

def check_secrets():
    # Debug: Check if secrets file exists
    st.write("### Debug Info")
    st.write("Current working directory:", os.getcwd())

    secrets_path = os.path.join(os.getcwd(), ".streamlit", "secrets.toml")
    st.write("Looking for secrets at:", secrets_path)
    st.write("File exists?", os.path.exists(secrets_path))

def access_secrets():
    # Try to access secrets
    try:
        st.write("### Secrets Content:")
        st.write(st.secrets)
    except Exception as e:
        st.error(f"Can't read secrets: {e}")


if __name__ == "__main__":
    check_secrets()
    access_secrets()

    # Try database connection
    try:
        st.write("### Attempting Database Connection...")
        conn = st.connection("sql")
        df = conn.query("SELECT VERSION();", ttl=0)
        
        st.success("✅ SUCCESS!")
        st.dataframe(df)

    except Exception as e:
        st.error("❌ Connection Failed")
        st.code(str(e))