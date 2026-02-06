import streamlit as st

def test():
    st.write("the app is running")

if __name__ == "__main__":
    test()
    try:
        # This automatically uses the [connections.sql] section from secrets.toml
        conn = st.connection("sql")
        
        # Simple query to test the connection
        df = conn.query("SELECT VERSION();")
        
        st.success("✅ Successfully connected to MySQL!")
        st.write("Database Version:", df.iloc[0,0])

    except Exception as e:
        st.error("❌ Connection failed.")
        st.exception(e)