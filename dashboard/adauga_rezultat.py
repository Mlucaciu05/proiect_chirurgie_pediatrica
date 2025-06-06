import streamlit as st
from datetime import datetime
import pandas as pd

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.database import SessionLocal, Patient, LabResult
from blockchain.MedicalLog import log_event

def pagina_adauga_rezultate():
    if st.session_state.role not in ["doctor", "nurse", "admin"]:
        st.warning("Nu aveți permisiuni pentru această secțiune")
        return

    st.title("Adăugare Rezultate Laborator")
    st.write("---")

    st.subheader("Selecteaza pacientul")

    db = SessionLocal()
    patients = db.query(Patient).all()
    if not patients:
        st.warning("Nu există pacienți în baza de date.")
        return
    optiuni = {f"{p.pseudonym} ({p.patient_id})": p.patient_id for p in patients}
    selectie = st.selectbox("Selectează pacientul:", list(optiuni.keys()))
    
    with st.form("form_lab_results", clear_on_submit=True):
        patient_id = optiuni[selectie]
        st.write(f"ID pacient: {patient_id}")
        cols = st.columns(2)
        with cols[0]:
            test_name = st.selectbox("Test*", ["CRP", "Leucocite", "Hemoglobina", "ALT", "AST", "Glicemie", "Altele"])
            value = st.number_input("Valoare*", step=0.1)
            
        with cols[1]:
            units = st.text_input("Unitate*")
            reference_range = st.text_input("Interval de referință*")
        
        data_rezultat = st.date_input("Data rezultatului*", value=datetime.now())
        
        submitted = st.form_submit_button("Salvează Rezultat")
        
        if submitted:
            log_event(
                user_name=st.session_state.username,
                user_role=st.session_state.role,
                patient_id=patient_id,
                event_type="adauga_rezultat_laborator"
            )
            if not all([patient_id, test_name, value, units, reference_range, data_rezultat]):
                st.error("Completați câmpurile obligatorii (*)")
            else:
                st.success("Rezultat laborator înregistrat cu succes!")
                st.balloons()
    
                # Save to database
                db = SessionLocal()
                new_result = LabResult(
                    patient_id=patient_id,
                    test_name=test_name,
                    value=value,
                    units=units,
                    reference_range=reference_range,
                    timestamp=data_rezultat
                )
                db.add(new_result)
                db.commit()
                db.refresh(new_result)
                db.close()
