import hmac
import hashlib
import time
from datetime import datetime, timedelta, timezone

import bcrypt
import streamlit as st

import db
import estilos

COOKIE_NOMBRE  = "domus_session"
SESION_TTL_SEG = 60 * 60 * 24  # 1 día


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verificar_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def _session_secret() -> str:
    return st.secrets["auth"]["session_secret"]


def generar_token_sesion(casa_id: int) -> str:
    expira  = int(time.time()) + SESION_TTL_SEG
    payload = f"{casa_id}:{expira}"
    firma   = hmac.new(_session_secret().encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{firma}"


def verificar_token_sesion(token: str):
    try:
        casa_id_s, expira_s, firma = token.split(":")
        payload         = f"{casa_id_s}:{expira_s}"
        firma_esperada  = hmac.new(_session_secret().encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(firma, firma_esperada):
            return None
        if int(expira_s) < time.time():
            return None
        return int(casa_id_s)
    except (ValueError, AttributeError):
        return None


def _header():
    E = estilos
    st.markdown(f"""
<div style="max-width:420px;margin:60px auto 0;">
  <div style="background:linear-gradient(140deg,{E.NAVY},{E.NAVY2} 70%,{E.BLUE});
       border-radius:22px;padding:36px 34px 30px;
       box-shadow:0 10px 40px rgba(15,27,53,.28);text-align:center;margin-bottom:28px;">
    <div style="font-size:42px;margin-bottom:8px;">🏠</div>
    <div style="color:#fff;font-family:{E.DISPLAY};font-size:52px;font-weight:600;
         line-height:1;letter-spacing:2px;">DOMUS</div>
    <div style="color:{E.GOLD_L};font-size:13px;font-weight:500;margin-top:6px;
         letter-spacing:.5px;">Gastos de nuestro hogar</div>
  </div>
</div>""", unsafe_allow_html=True)


def _loguear(cookie_manager, casa_id, personas, nombre):
    st.session_state["casa_id"]     = int(casa_id)
    st.session_state["personas"]    = list(personas)
    st.session_state["casa_nombre"] = nombre
    if cookie_manager is not None:
        expira_en = datetime.now(timezone.utc) + timedelta(seconds=SESION_TTL_SEG)
        cookie_manager.set(COOKIE_NOMBRE, generar_token_sesion(casa_id), expires_at=expira_en)
        # Le da tiempo al componente a escribir la cookie en el navegador antes de que el
        # rerun tire abajo el iframe que la está seteando.
        time.sleep(0.5)
    st.rerun()


def _tab_login(cookie_manager):
    with st.form("form_login"):
        usuario = st.text_input("Usuario", placeholder="Tu usuario…")
        clave   = st.text_input("Contraseña", type="password", placeholder="Tu contraseña…")
        ok      = st.form_submit_button("Entrar →", use_container_width=True, type="primary")

    if ok:
        casa = db.obtener_casa_por_usuario(usuario.strip().lower())
        if casa and verificar_password(clave, casa[2]):
            casa_id, _, _, nombre = casa
            personas = db.obtener_personas_casa(casa_id)
            _loguear(cookie_manager, casa_id, personas, nombre)
        else:
            st.error("Usuario o contraseña incorrectos.")


def _tab_reset():
    with st.form("form_reset"):
        usuario     = st.text_input("Usuario", placeholder="Tu usuario…")
        invitacion  = st.text_input("Código de invitación", type="password",
                                     placeholder="El mismo que usaron para crear el hogar")
        clave       = st.text_input("Nueva contraseña", type="password")
        clave2      = st.text_input("Confirmar nueva contraseña", type="password")
        ok          = st.form_submit_button("Cambiar contraseña", use_container_width=True, type="primary")

    if not ok:
        return

    usuario = usuario.strip().lower()
    codigo_valido = st.secrets.get("auth", {}).get("invite_code", "")

    if not codigo_valido or invitacion != codigo_valido:
        st.error("Código de invitación incorrecto.")
    elif not db.usuario_existe(usuario):
        st.error("No existe ese usuario.")
    elif len(clave) < 6:
        st.error("La contraseña debe tener al menos 6 caracteres.")
    elif clave != clave2:
        st.error("Las contraseñas no coinciden.")
    else:
        db.actualizar_password_casa(usuario, hash_password(clave))
        st.success("✅ Contraseña actualizada. Ya podés entrar con la nueva.")


def _tab_signup(cookie_manager):
    st.session_state.setdefault("signup_slot_ids", [0, 1])
    st.session_state.setdefault("signup_next_id", 2)
    slot_ids = st.session_state.signup_slot_ids

    nombre_hogar = st.text_input("Nombre del hogar", placeholder="Ej: Familia Pérez", key="signup_nombre_hogar")
    usuario      = st.text_input("Elegí un usuario", placeholder="Ej: familiaperez", key="signup_usuario")

    st.markdown("**Integrantes del hogar**")
    for i, slot_id in enumerate(slot_ids):
        col_p, col_x = st.columns([5, 1])
        col_p.text_input(f"Persona {i + 1}", placeholder="Nombre", key=f"signup_persona_{slot_id}",
                          label_visibility="collapsed")
        if len(slot_ids) > 1:
            if col_x.button("✕", key=f"signup_quitar_{slot_id}", use_container_width=True):
                st.session_state.signup_slot_ids.remove(slot_id)
                st.session_state.pop(f"signup_persona_{slot_id}", None)
                st.rerun()
    if st.button("+ Agregar persona", key="signup_agregar_persona"):
        st.session_state.signup_slot_ids.append(st.session_state.signup_next_id)
        st.session_state.signup_next_id += 1
        st.rerun()

    clave      = st.text_input("Contraseña", type="password", key="signup_clave")
    clave2     = st.text_input("Confirmar contraseña", type="password", key="signup_clave2")
    invitacion = st.text_input("Código de invitación", type="password",
                                placeholder="Te lo pasó quien te invitó", key="signup_invitacion")
    ok = st.button("Crear hogar →", use_container_width=True, type="primary", key="signup_ok")

    if not ok:
        return

    usuario = usuario.strip().lower()
    personas = [st.session_state.get(f"signup_persona_{slot_id}", "").strip() for slot_id in slot_ids]
    personas = [p for p in personas if p]
    codigo_valido = st.secrets.get("auth", {}).get("invite_code", "")

    if not codigo_valido or invitacion != codigo_valido:
        st.error("Código de invitación incorrecto.")
    elif not nombre_hogar or not usuario or not personas:
        st.error("Completá el nombre del hogar, el usuario y al menos una persona.")
    elif len(clave) < 6:
        st.error("La contraseña debe tener al menos 6 caracteres.")
    elif clave != clave2:
        st.error("Las contraseñas no coinciden.")
    elif db.usuario_existe(usuario):
        st.error("Ese usuario ya existe. Elegí otro.")
    else:
        casa_id = db.crear_casa(usuario, hash_password(clave), nombre_hogar, personas)
        for slot_id in slot_ids:
            st.session_state.pop(f"signup_persona_{slot_id}", None)
        st.session_state.pop("signup_slot_ids", None)
        st.session_state.pop("signup_next_id", None)
        _loguear(cookie_manager, casa_id, personas, nombre_hogar)


def pantalla_login(cookie_manager=None):
    _header()
    tab_login, tab_signup, tab_reset = st.tabs(["Entrar", "Crear hogar", "Olvidé mi contraseña"])
    with tab_login:
        _tab_login(cookie_manager)
    with tab_signup:
        _tab_signup(cookie_manager)
    with tab_reset:
        _tab_reset()
    st.stop()
