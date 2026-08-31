import streamlit as st
import database
from ultralytics import YOLO
from PIL import Image
import numpy as np
import pandas as pd
import os
import time

st.set_page_config(page_title="AI Car Damage Estimator", layout="wide")
database.init_db()

# Directory configuration for storing uploaded images
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Session state initialization
if 'user' not in st.session_state:
    st.session_state['user'] = None

# Updated Base pricing matrix (LKR) and Brand Multipliers
BASE_DEFECT_COSTS = {
    'scratch': 4000.0,
    'dent': 8000.0,
    'crack': 12000.0,
    'glass': 18000.0,
    'lamp': 15000.0,
    'deformation': 35000.0
}
DEFAULT_BASE_COST = 6000.0

BRAND_TIER_MULTIPLIERS = {
    'Budget': 1.0,
    'Mid': 1.25,
    'Luxury': 1.75
}

def calculate_repair_cost(boxes, class_names, brand_tier, img_shape):
    """Calculates reduced repair cost breakdown based on defect class, bounding box area, and brand tier."""
    multiplier = BRAND_TIER_MULTIPLIERS.get(brand_tier, 1.0)
    img_h, img_w = img_shape[:2]
    img_area = img_w * img_h
    
    total_cost = 0.0
    breakdown = []

    for box in boxes:
        cls_id = int(box.cls[0].item())
        cls_name = class_names[cls_id] if (class_names and cls_id in class_names) else f"Defect_{cls_id}"
        
        xyxy = box.xyxy[0].tolist()
        box_w = xyxy[2] - xyxy[0]
        box_h = xyxy[3] - xyxy[1]
        box_area = box_w * box_h
        area_pct = (box_area / img_area) * 100.0

        if area_pct < 1.5:
            size_label = "Minor (<1.5%)"
            size_multiplier = 0.5
        elif area_pct <= 5.0:
            size_label = "Moderate (1.5%-5.0%)"
            size_multiplier = 0.85
        else:
            size_label = "Major (>5.0%)"
            size_multiplier = 1.25

        base_cost = DEFAULT_BASE_COST
        for key, value in BASE_DEFECT_COSTS.items():
            if key in cls_name.lower():
                base_cost = value
                break
        
        adjusted_cost = base_cost * size_multiplier * multiplier
        total_cost += adjusted_cost
        
        breakdown.append({
            "Defect Type": cls_name,
            "Damage Scale": size_label,
            "Image Area Coverage": f"{area_pct:.2f}%",
            "Confidence": f"{float(box.conf[0]):.2f}",
            "Base Cost (LKR)": f"{base_cost:,.2f}",
            "Final Cost (LKR)": f"{adjusted_cost:,.2f}"
        })

    return total_cost, breakdown

def login_screen(role):
    st.subheader(f"{role.capitalize()} Portal Access")
    
    if role == 'policyholder':
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            username = st.text_input("Username", key=f"login_user_{role}")
            password = st.text_input("Password", type="password", key=f"login_pass_{role}")
            if st.button("Log In", key=f"login_btn_{role}"):
                user = database.verify_user(username, password, role)
                if user:
                    st.session_state['user'] = {'id': user[0], 'username': user[1], 'role': role}
                    st.success(f"Welcome back, {user[1]}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        with tab2:
            reg_user = st.text_input("Choose Username", key=f"reg_user_{role}")
            reg_pass = st.text_input("Choose Password", type="password", key=f"reg_pass_{role}")
            if st.button("Create Account", key=f"reg_btn_{role}"):
                if reg_user and reg_pass:
                    if database.register_user(reg_user, reg_pass, role):
                        st.success("Account created successfully! You can now log in.")
                    else:
                        st.error("Username already exists.")
                else:
                    st.warning("Please fill in all fields.")
    else:
        username = st.text_input("Assessor Username", key=f"login_user_{role}")
        password = st.text_input("Assessor Password", type="password", key=f"login_pass_{role}")
        if st.button("Log In as Assessor", key=f"login_btn_{role}"):
            user = database.verify_user(username, password, role)
            if user:
                st.session_state['user'] = {'id': user[0], 'username': user[1], 'role': role}
                st.success(f"Welcome Admin, {user[1]}!")
                st.rerun()
            else:
                st.error("Invalid admin credentials.")

def main():
    st.sidebar.title("Navigation")
    
    if st.session_state['user']:
        st.sidebar.write(f"Logged in as: **{st.session_state['user']['username']}** ({st.session_state['user']['role'].capitalize()})")
        if st.sidebar.button("Log Out"):
            st.session_state['user'] = None
            st.session_state.pop('analysis_results', None)
            st.session_state.pop('current_file_name', None)
            st.rerun()

    @st.cache_resource
    def load_model():
        return YOLO('models/best.pt')

    model = load_model()
    app_mode = st.sidebar.selectbox("Choose Portal", ["Policyholder Dashboard (B2C)", "Assessor Admin (B2B)"])

    if app_mode == "Policyholder Dashboard (B2C)":
        if st.session_state['user'] and st.session_state['user']['role'] == 'policyholder':
            st.title("Policyholder Portal")
            
            p_tab1, p_tab2 = st.tabs(["New Claim & Assessment", "My Claims History"])
            
            with p_tab1:
                col1, col2, col3 = st.columns(3)
                with col1:
                    vehicle_make = st.text_input("Vehicle Make", placeholder="e.g. Toyota")
                with col2:
                    vehicle_model = st.text_input("Vehicle Model", placeholder="e.g. Corolla")
                with col3:
                    vehicle_year = st.number_input("Vehicle Year", min_value=1990, max_value=2026, value=2020)
                
                brand_tier = st.selectbox("Vehicle Brand Tier", ["Budget", "Mid", "Luxury"])
                
                # Guidance Callout Box for Users
                st.info("💡 **Tip for Best Accuracy:** Upload a clear, well-lit image focused directly on the damaged area. Focused close-up shots yield higher AI detection precision than distant wide-angle vehicle photos.")
                
                uploaded_file = st.file_uploader("Upload Damage Image (JPEG/PNG)", type=['jpg', 'jpeg', 'png'])

                # State Reset Logic: Detect if image changed or was removed
                if uploaded_file is not None:
                    if st.session_state.get('current_file_name') != uploaded_file.name:
                        st.session_state['current_file_name'] = uploaded_file.name
                        st.session_state.pop('analysis_results', None)
                        st.session_state.pop('pending_claim', None)
                else:
                    st.session_state.pop('current_file_name', None)
                    st.session_state.pop('analysis_results', None)
                    st.session_state.pop('pending_claim', None)

                if uploaded_file is not None:
                    image = Image.open(uploaded_file)
                    img_array = np.array(image.convert("RGB"))

                    col_orig, col_pred = st.columns(2)

                    with col_orig:
                        st.write("##### Source Upload Image")
                        st.image(image, use_container_width=True)

                    if st.button("Analyze & Estimate Cost"):
                        with st.spinner("AI analyzing damage size and class..."):
                            results = model.predict(source=img_array, conf=0.25)
                            annotated_img = Image.fromarray(results[0].plot())
                            
                            st.session_state['analysis_results'] = {
                                'annotated_img': annotated_img,
                                'boxes': results[0].boxes,
                                'img_shape': img_array.shape,
                                'filename': f"claim_{st.session_state['user']['id']}_{int(time.time())}.jpg"
                            }

                    if 'analysis_results' in st.session_state:
                        res = st.session_state['analysis_results']
                        
                        with col_pred:
                            st.write("##### AI Detection Output")
                            st.image(res['annotated_img'], use_container_width=True)

                        boxes = res['boxes']
                        total_cost, breakdown = calculate_repair_cost(boxes, model.names, brand_tier, res['img_shape'])
                        
                        st.divider()
                        st.metric("Estimated Total Repair Cost", f"LKR {total_cost:,.2f}")
                        
                        if breakdown:
                            st.write("### Defect Itemization & Size Breakdown")
                            st.dataframe(pd.DataFrame(breakdown), use_container_width=True)
                        else:
                            st.info("No visible defects detected at the current confidence threshold.")

                        saved_path = os.path.join(UPLOAD_DIR, res['filename'])
                        res['annotated_img'].save(saved_path)

                        st.session_state['pending_claim'] = {
                            'make': vehicle_make,
                            'model': vehicle_model,
                            'year': vehicle_year,
                            'tier': brand_tier,
                            'image_path': saved_path,
                            'cost': total_cost
                        }

                        if st.button("Submit Claim to Insurance Assessor"):
                            c = st.session_state['pending_claim']
                            database.add_claim(
                                st.session_state['user']['id'],
                                c['make'], c['model'], c['year'], c['tier'],
                                c['image_path'], c['cost']
                            )
                            st.success("Claim submitted successfully! Track progress under 'My Claims History'.")
                            del st.session_state['pending_claim']
                            del st.session_state['analysis_results']

            with p_tab2:
                st.subheader("Submitted Claims History")
                user_claims = database.get_user_claims(st.session_state['user']['id'])
                if user_claims:
                    df = pd.DataFrame(user_claims, columns=[
                        "Claim ID", "Make", "Model", "Year", "Tier", "Estimated Cost (LKR)", "Status", "Image Path"
                    ])
                    st.dataframe(df.drop(columns=["Image Path"]), use_container_width=True)
                else:
                    st.info("No prior claims found.")

        else:
            login_screen('policyholder')

    elif app_mode == "Assessor Admin (B2B)":
        if st.session_state['user'] and st.session_state['user']['role'] == 'assessor':
            st.title("Assessor Admin Portal")
            
            all_claims = database.get_all_claims()
            if not all_claims:
                st.info("No claims currently submitted.")
                return

            cols = ["Claim ID", "Policyholder", "Make", "Model", "Year", "Tier", "Estimated Cost (LKR)", "Status", "Image Path"]
            df_all = pd.DataFrame(all_claims, columns=cols)
            
            st.write("### Active Claims Overview")
            st.dataframe(df_all.drop(columns=["Image Path"]), use_container_width=True)
            
            st.divider()
            st.write("### Review & Audit Individual Claim")
            
            claim_ids = df_all["Claim ID"].tolist()
            selected_id = st.selectbox("Select Claim ID to Review", claim_ids)
            
            claim_data = df_all[df_all["Claim ID"] == selected_id].iloc[0]
            
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.write(f"**Policyholder:** {claim_data['Policyholder']}")
                st.write(f"**Vehicle:** {claim_data['Make']} {claim_data['Model']} ({claim_data['Year']})")
                st.write(f"**Brand Tier:** {claim_data['Tier']}")
                st.write(f"**Current Status:** `{claim_data['Status']}`")
                st.write(f"**AI System Cost:** LKR {claim_data['Estimated Cost (LKR)']:,.2f}")
                
                if os.path.exists(claim_data["Image Path"]):
                    st.image(claim_data["Image Path"], caption=f"Claim #{selected_id} Image", use_container_width=True)

            with col_b:
                st.subheader("Assessor Action Panel")
                new_status = st.selectbox("Update Status", ["Pending Review", "Approved", "Rejected"])
                override_cost = st.number_input(
                    "Override/Finalize Cost (LKR)", 
                    value=float(claim_data["Estimated Cost (LKR)"]),
                    step=1000.0
                )

                if st.button("Save Assessment Decision"):
                    database.update_claim_status(selected_id, new_status, override_cost)
                    st.success(f"Claim #{selected_id} updated successfully!")
                    st.rerun()

        else:
            login_screen('assessor')

if __name__ == '__main__':
    main()