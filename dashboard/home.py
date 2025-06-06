import streamlit as st
import requests
from jose import jwt
import grafice, adauga_pacient, adauga_rezultat, export, vizualizare, calculare_scor, modificare_date, stergere
from blockchain.MedicalLog import log_event

def login_form():
    st.title("Autentificare")
    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Logare")
        if submit:
            r = requests.post("http://127.0.0.1:8000/token", data={"username": username, "password": password})
            if r.status_code == 200:
                token = r.json()["access_token"]
                decoded = jwt.decode(token, "secrettoken2025", algorithms=["HS256"])
                st.session_state.token = token
                st.session_state.username = decoded["sub"]
                st.session_state.role = decoded["role"]
                log_event(user_name=st.session_state.username, user_role=st.session_state.role, patient_id=0 , event_type="login")
            else:
                st.error("Login eșuat.")
                st.session_state.token = None
                st.session_state.username = None
                st.session_state.role = None

def render_sidebar():
    st.sidebar.title("Navigare")
    if st.sidebar.button("Acasa", key="home"):
        st.session_state.page = "home"
        
    if st.sidebar.button("Dashboard", key="dashboard"):
        st.session_state.page = "dashboard"

    with st.sidebar.expander("Adaugă Date", expanded=False):
        if st.session_state.role in ["doctor", "nurse", "admin"]:
            if st.button("Adaugă Pacient"):
                st.session_state.page = "adauga_pacient"
            if st.button("Adaugă Rezultate"):
                st.session_state.page = "adauga_rezultate"
            if st.button("Calculează Scoruri Clinice"):
                st.session_state.page = "calculeaza_scoruri"
        else:
            st.warning("Permisiuni insuficiente")

    with st.sidebar.expander("Modifică Date", expanded=False):
        if st.session_state.role in ["doctor", "admin"]:
            if st.button("Modifică Date Pacient"):
                st.session_state.page = "modificare_date"
            if st.button("Șterge Date Pacient"):
                st.session_state.page = "stergere"
        else:
            st.warning("Permisiuni insuficiente")

    if st.sidebar.button("Export", key="export"):
        st.session_state.page = "export"

    if st.sidebar.button("Vizualizare", key="vizualizare"):
        st.session_state.page = "vizualizare"

    if st.sidebar.button("Logout", key="logout"):
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.token = None
        st.session_state.page = "login"
        log_event(user_name=st.session_state.username, user_role=st.session_state.role, patient_id=0, event_type="logout")
        st.stop()

def pagina_home():
    st.title("Bine ai venit!")
    st.write(f"Rol: **{st.session_state.role}** | Utilizator: **{st.session_state.username}**")
    st.info("Folosește meniul din stânga pentru a naviga între module.")

if "token" not in st.session_state:
    st.session_state.token = None

if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.token is None:
    login_form()
    st.stop()
else:
    render_sidebar()
    pagina = st.session_state.page

    if pagina == "home":
        pagina_home()
    elif pagina == "dashboard":
        grafice.run_monitorizare()
    elif pagina == "adauga_pacient":
        adauga_pacient.pagina_adauga_pacient()
    elif pagina == "adauga_rezultate":  
        adauga_rezultat.pagina_adauga_rezultate()
    elif pagina == "export":
        export.pagina_export()
    elif pagina == "vizualizare":
        vizualizare.pagina_vizualizare()
    elif pagina == "calculeaza_scoruri":
        calculare_scor.pagina_scor()
    elif pagina == "modificare_date":
        modificare_date.modificare_date()
    elif pagina == "stergere":
        stergere.delete_patient_data()
    else:
        st.error("Pagina nu a fost găsită.")
