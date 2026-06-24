import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

import streamlit as st
from detector import analisar_mensagem

st.set_page_config(page_title="Detector de Golpes", page_icon=None)
st.title("Detector de mensagens suspeitas")
st.caption("Analise de phishing e golpes com IA (Groq + Llama) + verificacoes de seguranca")

texto = st.text_area(
    "Cole aqui a mensagem suspeita (SMS, e-mail, WhatsApp...)",
    height=160,
    placeholder="Ex: URGENTE! Sua conta sera bloqueada hoje. Confirme seu CPF: http://bit.ly/...",
)

if st.button("Analisar mensagem", type="primary"):
    if not texto.strip():
        st.warning("Cole uma mensagem para analisar.")
        st.stop()

    with st.spinner("Analisando..."):
        try:
            r = analisar_mensagem(texto)
        except Exception as e:
            st.error(f"Erro ao analisar: {e}")
            st.stop()

    nivel = r.get("nivel_risco", "").lower()
    if nivel == "alto":
        st.error(f"Risco: ALTO")
    elif nivel == "medio":
        st.warning(f"Risco: MEDIO")
    else:
        st.success(f"Risco: BAIXO")

    st.subheader("Por que")
    st.write(r.get("explicacao", ""))

    st.subheader("Sinais detectados")
    for s in r.get("sinais", []):
        st.write(f"- {s}")

    st.subheader("O que fazer")
    st.info(r.get("recomendacao", ""))

    links = r.get("links", [])
    if links:
        st.subheader("Links encontrados")
        for link in links:
            st.code(link, language=None)
        st.caption("Nao clique em links de mensagens suspeitas.")

    with st.expander("Detalhes tecnicos (verificacoes automaticas)"):
        for s in r.get("sinais_tecnicos", []):
            st.write(f"- {s}")
