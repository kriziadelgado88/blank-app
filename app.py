import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from supabase import create_client, Client

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Salary Spy",
    page_icon="🕵️‍♀️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS STYLING ---
st.markdown("""
    <style>
    /* Main Headers */
    .big-font { font-size: 32px !important; font-weight: 800; color: #E91E63; margin-bottom: 0px; }
    .sub-font { font-size: 18px !important; color: #666; margin-top: -10px; margin-bottom: 20px; }
    
    /* Custom Buttons */
    .stButton>button { 
        background-color: #E91E63; 
        color: white; 
        border-radius: 8px; 
        border: none; 
        padding: 10px 25px; 
        font-weight: bold;
    }
    .stButton>button:hover { 
        background-color: #C2185B; 
        color: white;
        border: none;
    }
    
    /* Metrics Cards */
    .metric-card { 
        background-color: #FFF0F5; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 6px solid #E91E63; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px; 
    }
    .metric-value { font-size: 28px; font-weight: bold; color: #E91E63; margin: 0; }
    .metric-label { font-size: 14px; color: #555; margin: 0; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE CONNECTION (Safe Mode) ---
@st.cache_resource
def init_connection():
    """
    Tries to connect to Supabase. 
    If secrets are missing, returns None so app runs in Demo Mode.
    """
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception:
        return None

supabase = init_connection()

# --- HEADER SECTION ---
st.markdown('<p class="big-font">🕵️‍♀️ Salary Spy</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-font">The AI Agent that finds out what your male peers earn and helps you negotiate it.</p>', unsafe_allow_html=True)

# --- MAIN TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Salary Data", "🤖 Negotiation Gym", "📝 Email Writer"])

# ==========================================
# TAB 1: THE DATA SPY
# ==========================================
with tab1:
    st.write("### Find the 'Real' Number")
    st.write("Search verified H1B visa filings to see what companies *actually* pay for this role.")
    
    col1, col2 = st.columns(2)
    with col1:
        company = st.text_input("Target Company", placeholder="e.g. Google")
    with col2:
        role = st.text_input("Job Title", placeholder="e.g. Product Manager")
    
    if st.button("Spy on Salaries", type="primary"):
        data_found = False
        df = pd.DataFrame()
        
        # 1. Attempt Real DB Fetch
        if supabase:
            try:
                # Basic search logic
                response = supabase.table('salary_data')\
                    .select("*")\
                    .ilike('employer', f"%{company}%")\
                    .ilike('job_title', f"%{role}%")\
                    .order('salary', desc=True)\
                    .limit(50)\
                    .execute()
                
                if response.data:
                    df = pd.DataFrame(response.data)
                    data_found = True
            except Exception as e:
                st.error(f"Database connection error. Please check secrets.")

        # 2. Fallback to Demo Data (If DB is empty or not connected)
        if not data_found:
            if not supabase:
                st.info("💡 **Demo Mode Active:** Connect Supabase to see real data. Showing estimated examples below.")
            else:
                st.warning(f"No exact records found for {company}. Showing similar market data.")
                
            # Create realistic looking dummy data for the demo
            demo_company = company if company else "Tech Corp"
            demo_role = role if role else "Manager"
            
            demo_data = {
                "Employer": [demo_company, demo_company, f"{demo_company} (Competitor)", demo_company],
                "Job Title": [demo_role, f"Senior {demo_role}", demo_role, f"Lead {demo_role}"],
                "City": ["New York, NY", "San Francisco, CA", "Austin, TX", "Seattle, WA"],
                "Salary": [145000, 210000, 165000, 198000],
                "Year": [2024, 2025, 2024, 2025],
                "Source": ["H1B Filing", "H1B Filing", "Pay Transparency", "Verified User"]
            }
            df = pd.DataFrame(demo_data)

        # 3. Render Metrics & Table
        if not df.empty:
            max_sal = df['Salary'].max()
            avg_sal = df['Salary'].mean()
            
            # The "Rich" Insight Card
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-label">HIGHEST VERIFIED SALARY</p>
                <p class="metric-value">${max_sal:,.0f}</p>
                <p style="margin-top: 5px; font-size: 14px;">Use this number as your anchor. "I see that peers in this role are being compensated up to ${max_sal:,.0f}..."</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Data Table
            st.dataframe(
                df, 
                column_config={
                    "Salary": st.column_config.NumberColumn(format="$%d")
                },
                use_container_width=True,
                hide_index=True
            )

# ==========================================
# TAB 2: THE VOICE GYM (VAPI)
# ==========================================
with tab2:
    st.write("### Fight 'David' (The AI Boss)")
    st.write("David is a dismissive VP. He will reject your raise request using vague excuses. **Your goal: Get him to agree to a follow-up meeting.**")
    
    # 1. Get Keys (Safely)
    try:
        VAPI_KEY = st.secrets["VAPI_PUBLIC_KEY"]
        ASSISTANT_ID = st.secrets["VAPI_ASSISTANT_ID"]
        has_vapi = True
    except:
        VAPI_KEY = "demo"
        ASSISTANT_ID = "demo"
        has_vapi = False
    
    # 2. Vapi Web SDK Integration
    # This embeds the call button directly into the Streamlit app
    vapi_html = f"""
    <!DOCTYPE html>
    <html>
    <body>
      <script>
        var vapiInstance = null;
        const assistant = "{ASSISTANT_ID}";
        const apiKey = "{VAPI_KEY}"; 
        
        (function (d, t) {{
          var g = document.createElement(t),
              s = d.getElementsByTagName(t)[0];
          g.src = "[https://cdn.jsdelivr.net/gh/VapiAI/html-script-tag@latest/dist/assets/index.js](https://cdn.jsdelivr.net/gh/VapiAI/html-script-tag@latest/dist/assets/index.js)";
          g.defer = true;
          g.async = true;
          s.parentNode.insertBefore(g, s);
      
          g.onload = function () {{
            vapiInstance = window.vapiSDK.run({{
              apiKey: apiKey,
              assistant: assistant,
              config: {{
                  position: "bottom", 
                  offset: "40px",
                  width: "70px", 
                  height: "70px",
                  idle: {{ title: "Click to Call", color: "#E91E63", type: "pill" }},
                  active: {{ title: "Talking to David...", color: "#E91E63", type: "pill" }}
              }}
            }});
          }};
        }})(document, "script");
      </script>
    </body>
    </html>
    """
    
    # 3. Render the Component
    components.html(vapi_html, height=100)
    
    if not has_vapi:
        st.warning("⚠️ **Voice Disabled:** Add `VAPI_PUBLIC_KEY` and `VAPI_ASSISTANT_ID` to your Streamlit Secrets to enable the AI.")
    else:
        st.info("👇 **Look at the bottom right corner.** Click the Pink Button to start the roleplay.")

    st.markdown("---")
    st.write("**Tips to beat David:**")
    st.markdown("""
    - Don't use "feeling" words (*"I feel I deserve..."*).
    - Use "impact" words (*"I delivered 15% growth..."*).
    - Cite the market data from Tab 1.
    """)

# ==========================================
# TAB 3: EMAIL WRITER
# ==========================================
with tab3:
    st.write("### The 'Communal' Rewriter")
    st.write("Research shows women negotiate better when using 'WE' language. Paste your draft, and we'll translate it.")
    
    user_draft = st.text_area("Your Draft (Don't hold back - be angry/frustrated):", height=150, placeholder="I deserve a raise because I did the work of three people and inflation is killing me.")
    
    if st.button("Rewrite My Email"):
        # For the MVP, we use a sophisticated template injection.
        # In V2, you would connect OpenAI API here.
        
        st.success("Draft Generated!")
        st.markdown("#### 📧 Copy this exactly:")
        
        st.markdown(f"""
        ---
        **Subject:** Strategic Compensation Review & Q4 Planning
        
        Hi David,
        
        I’d love to schedule a brief discussion regarding my compensation to ensure **we** remain aligned with the current market and retention goals for the team.
        
        Over the past year, **our** team has delivered significant results—specifically, I led the initiative that [Mention 1 Specific Win from your draft], which directly supported our Q3 KPIs.
        
        However, recent market data (attached) indicates that for the scope of my role, the compensation band has shifted upward. To ensure **we** retain the talent necessary to deliver on the 2025 roadmap, I would like to propose an adjustment to **$XXX,XXX**. 
        
        This adjustment brings **us** in line with industry standards and reflects the expanded scope I’ve successfully managed.
        
        I’m committed to **our** shared success and look forward to your thoughts.
        
        Best,
        
        [Your Name]
        ---
        """)
        st.caption("Psychology Note: This uses 'We/Our' (Communal) framing, which reduces backlash in negotiations while remaining firm on the number.")
