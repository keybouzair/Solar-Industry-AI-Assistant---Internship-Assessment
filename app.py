import streamlit as st
import numpy as np
from datetime import datetime
from PIL import Image
import os
import openai

# Mock: Define constants
SOLAR_EFFICIENCY = 0.18  # 18%
SYSTEM_COST_PER_KW = 1200  # USD
AVG_SUN_HOURS = 4.5  # per day

# Load API Key from environment or fallback
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
openai.api_key = OPENROUTER_API_KEY
openai.api_base = "https://openrouter.ai/api/v1"

st.set_page_config(page_title="Solar Rooftop Analyzer", layout="centered")
st.title("🔆 Solar Rooftop Analyzer")

# Sidebar Inputs
st.sidebar.header("📍 Rooftop & Location Details")
uploaded_image = st.sidebar.file_uploader("Upload Satellite Image of Rooftop", type=["jpg", "jpeg", "png"])

if uploaded_image:
    st.image(uploaded_image, caption="Uploaded Rooftop Image", use_column_width=True)
    st.sidebar.success("Image uploaded successfully.")
else:
    st.sidebar.warning("Please upload a rooftop image.")

roof_area = st.sidebar.number_input("Rooftop Usable Area (m²) — estimated manually", min_value=10.0, max_value=500.0, value=50.0)
zip_code = st.sidebar.text_input("ZIP Code", "94016")
local_cost_per_kWh = st.sidebar.number_input("Your Electricity Cost ($/kWh)", min_value=0.05, max_value=0.50, value=0.15)

# Solar System Calculations
@st.cache_data
def calculate_system(roof_area, cost_per_kWh):
    panel_area = 1.7  # m² per panel
    panel_output_kw = 0.3  # kW per panel
    num_panels = int(roof_area // panel_area)
    total_kw = round(num_panels * panel_output_kw, 2)

    daily_output_kWh = total_kw * AVG_SUN_HOURS
    yearly_output_kWh = daily_output_kWh * 365
    install_cost = total_kw * SYSTEM_COST_PER_KW
    annual_savings = yearly_output_kWh * cost_per_kWh
    payback_years = round(install_cost / annual_savings, 1)
    savings_25yr = round(annual_savings * 25 - install_cost, 2)

    return {
        "num_panels": num_panels,
        "total_kw": total_kw,
        "yearly_output_kWh": round(yearly_output_kWh, 2),
        "install_cost": round(install_cost, 2),
        "annual_savings": round(annual_savings, 2),
        "payback_years": payback_years,
        "savings_25yr": savings_25yr,
    }

# LLM Summary Generation
def generate_summary(data):
    prompt = (
        f"Based on a rooftop area of {roof_area} m², we estimate the installation of {data['num_panels']} panels "
        f"with a total system size of {data['total_kw']} kW. This system can generate approximately {data['yearly_output_kWh']} kWh annually, "
        f"costing ${data['install_cost']} to install. Expected yearly savings are ${data['annual_savings']}, with a payback period of {data['payback_years']} years. "
        f"Over 25 years, you could save ${data['savings_25yr']}. Provide this in a friendly summary."
    )

    try:
        response = openai.ChatCompletion.create(
            model="openrouter/openchat",
            messages=[{"role": "user", "content": prompt}],
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error generating summary: {e}"

# Run calculation
if st.button("Analyze My Rooftop"):
    if not uploaded_image:
        st.error("Please upload a rooftop image first.")
    else:
        result = calculate_system(roof_area, local_cost_per_kWh)

        st.subheader("📊 Analysis Results")
        st.write(f"**Estimated Panels:** {result['num_panels']}")
        st.write(f"**System Size:** {result['total_kw']} kW")
        st.write(f"**Annual Energy Output:** {result['yearly_output_kWh']} kWh")
        st.write(f"**Installation Cost:** ${result['install_cost']}")
        st.write(f"**Annual Savings:** ${result['annual_savings']}")
        st.write(f"**Payback Period:** {result['payback_years']} years")
        st.write(f"**Estimated 25-Year Net Savings:** ${result['savings_25yr']}")

        st.success("This system looks viable for solar installation. Consider speaking to a professional installer!")

        st.subheader("🧠 AI-Generated Summary")
        summary = generate_summary(result)
        st.info(summary)

# Footer
st.markdown("---")
st.markdown("Made for Solar Industry AI Internship Assessment ✨")