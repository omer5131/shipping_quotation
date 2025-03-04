import streamlit as st
import uuid
import json
import requests
import os

# For production, set your API key in environment variables
# PRIORITY1_API_KEY = os.environ.get("PRIORITY1_API_KEY", "YOUR_PRIORITY1_API_KEY")

# Initialize session state variables if not already present
if "request_data" not in st.session_state:
    st.session_state["request_data"] = None
if "request_id" not in st.session_state:
    st.session_state["request_id"] = None
if "quote_options" not in st.session_state:
    st.session_state["quote_options"] = None
if "selected_option" not in st.session_state:
    st.session_state["selected_option"] = None

st.title("Priority1 Quote Request Demo (POC)")

# ----------------------------
# Phase 1: Submit Quote Request
# ----------------------------
st.header("Phase 1: Submit Quote Request")
with st.form("submit_request_form"):
    boxes_number = st.number_input("Boxes Number", min_value=1, step=1)
    weight = st.number_input("Weight", min_value=0.0, format="%.2f")
    height = st.number_input("Height", min_value=0.0, format="%.2f")
    width = st.number_input("Width", min_value=0.0, format="%.2f")
    length = st.number_input("Length", min_value=0.0, format="%.2f")
    cargo_type = st.text_input("Cargo Type")
    weight_unit = st.selectbox("Weight Unit", options=["lbs", "kg"])
    dimension_unit = st.selectbox("Dimension Unit", options=["in", "cm"])
    airport_zipcode_loading = st.text_input("Airport Zipcode - Port of Loading")
    airport_zipcode_discharge = st.text_input("Airport Zipcode - Port of Discharge")
    
    submit_request = st.form_submit_button("Submit Request")
    
    if submit_request:
        # Create a unique request id and store the request data as a dictionary.
        request_id = str(uuid.uuid4())
        request_data = {
            "boxes_number": boxes_number,
            "weight": weight,
            "height": height,
            "width": width,
            "length": length,
            "cargo_type": cargo_type,
            "weightUnit": weight_unit,
            "dimensionunit": dimension_unit,
            "airport_zipcode_loading": airport_zipcode_loading,
            "airport_zipcode_discharge": airport_zipcode_discharge,
        }
        st.session_state["request_data"] = request_data
        st.session_state["request_id"] = request_id
        st.success(f"Request submitted successfully with ID: {request_id}")

# ----------------------------
# Phase 2: Generate Quote via Priority1 API (Simulated)
# ----------------------------
st.header("Phase 2: Generate Quote")
if st.session_state["request_data"]:
    st.subheader("Review Submitted Request")
    st.write("**Request ID:**", st.session_state["request_id"])
    st.json(st.session_state["request_data"])
    
    if st.button("Generate Quote"):
        def call_priority1_api(request_data):
            """
            Call the Priority1 API to get quote rates.
            Endpoint: https://api.priority1.com/v2/parcel/quotes/rates
            For this demo, we simulate the response.
            """
            api_url = "https://api.priority1.com/v2/parcel/quotes/rates"
            headers = {
                "Content-Type": "application/json",
                # "Authorization": f"Bearer {PRIORITY1_API_KEY}",
            }
            try:
                # Uncomment the following lines to call the real API.
                # response = requests.post(api_url, json=request_data, headers=headers)
                # response.raise_for_status()
                # return response.json()
                
                # For demo purposes, we simulate a response:
                simulated_response = {
                    "quote_options": {
                        "Standard": "$300",
                        "Express": "$450",
                        "Overnight": "$600"
                    }
                }
                return simulated_response
            except Exception as e:
                st.error("Error calling Priority1 API, using dummy quote response.")
                return {
                    "quote_options": {
                        "Standard": "$300",
                        "Express": "$450",
                        "Overnight": "$600"
                    }
                }
        
        api_response = call_priority1_api(st.session_state["request_data"])
        st.session_state["quote_options"] = api_response.get("quote_options", {})
        st.success("Quote generated and saved (simulated).")

# ----------------------------
# Phase 3: Summarize and Select Quote Option
# ----------------------------
st.header("Phase 3: Summarize and Select Quote Option")
if st.session_state["quote_options"]:
    st.subheader("Quote Options:")
    for option, value in st.session_state["quote_options"].items():
        st.write(f"**{option}:** {value}")
    
    selected = st.radio("Select your preferred quote option:", list(st.session_state["quote_options"].keys()))
    if st.button("Submit Selection"):
        st.session_state["selected_option"] = selected
        st.success(f"You selected: {selected} with value {st.session_state['quote_options'][selected]}")

# ----------------------------
# Phase 4: Email Summary Draft
# ----------------------------
st.header("Phase 4: Email Summary Draft")
if st.session_state.get("selected_option"):
    def generate_email_summary(request_data, selected_option, quote_value):
        email_body = (
            f"Subject: Your Shipping Quote Proposal\n\n"
            f"Dear Valued Customer,\n\n"
            f"Thank you for your interest in our shipping services. We have received your request with the following details:\n\n"
        )
        # List the request details
        for key, value in request_data.items():
            email_body += f"- {key.replace('_', ' ').capitalize()}: {value}\n"
        
        email_body += (
            f"\nBased on the details provided, we are pleased to offer you the following shipping option:\n"
            f"**{selected_option}** at a rate of {quote_value}.\n\n"
            f"If you have any questions or need further assistance, please do not hesitate to contact us.\n\n"
            f"Best regards,\n"
            f"Your Shipping Team"
        )
        return email_body

    request_data = st.session_state["request_data"]
    selected_option = st.session_state["selected_option"]
    quote_value = st.session_state["quote_options"][selected_option]
    email_summary = generate_email_summary(request_data, selected_option, quote_value)
    
    st.subheader("Draft Email Summary:")
    st.text_area("Email Draft", value=email_summary, height=300)
