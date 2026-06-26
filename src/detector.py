import os
import re
import json
from urllib.parse import urlparse
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def _get_api_key():
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        try:
            import streamlit as st
            key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass
    if not key:
        raise RuntimeError("GROQ_API_KEY nao encontrada (.env ou Secrets do Streamlit)")
    return key


client = Groq(api_key=_get_api_key())
MODELO = "llama-3.1-8b-instant"

ENCURTADORES = ["bit.ly", "tinyurl", "goo.gl", "is.gd", "t.co", "ow.ly",
                "cutt.ly", "encurtador", "shorturl", "rebrand.ly"]

URGENCIA = ["urgente", "agora", "imediatamente", "ultima chance", "expira",
            "hoje", "bloquead", "suspens", "limite", "voce ganhou", "premio",
            "parabens", "resgatar", "clique aqui", "confirme seus dados"]

DADOS_SENSIVEIS = ["cpf", "senha", "codigo", "cartao", "cvv", "pix",
                   "conta bancaria", "agencia", "token", "validade"]

MARCAS = ["bradesco", "itau", "nubank", "caixa", "santander", "bb", "banco",
          "mercadolivre", "magalu", "amazon", "shopee", "correios", "receita",
          "gov", "pix", "whatsapp", "netflix", "serasa"]

TLDS_SUSPEITOS = [".xyz", ".top", ".click", ".live", ".online", ".site",
                  ".shop", ".fun", ".icu", ".cyou", ".rest", ".buzz"]

URL_RE = re.compile(
    r"\b(?:https?://)?(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[^\s]*)?",
    re.IGNORECASE
)
IP_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def _extrair_host(url):
    if not url.lower().startswith(("http://", "https://")):
        url = "http://" + url
    try:
        return (urlparse(url).hostname or "").lower()
    except Exception:
        return ""


def analisar_dominio(url):
    host = _extrair_host(url)
    if not host:
        return ["URL malformada"]

    achados = []
    if IP_RE.match(host):
        achados.append(f"Usa endereco IP em vez de nome ({host}) — tipico de golpe")
    if host.count("-") >= 3:
        achados.append(f"Dominio com muitos hifens ({host})")
    if any(host.endswith(tld) for tld in TLDS_SUSPEITOS):
        achados.append(f"Terminacao de dominio suspeita ({host})")
    partes = host.split(".")
    dominio_principal = ".".join(partes[-2:]) if len(partes) >= 2 else host
    for marca in MARCAS:
        if marca in host and marca not in dominio_principal:
            achados.append(f"Marca '{marca}' usada em subdominio falso ({host})")
            break
    return achados


def analisar_sinais(texto):
    t = texto.lower()
    urls = [u for u in URL_RE.findall(texto) if "." in u and " " not in u]

    sinais = []
    if any(enc in t for enc in ENCURTADORES):
        sinais.append("Usa link encurtado (esconde o destino real)")
    urgencia_achada = [p for p in URGENCIA if p in t]
    if urgencia_achada:
        sinais.append(f"Linguagem de urgencia/pressao: {', '.join(urgencia_achada[:3])}")
    dados_achados = [p for p in DADOS_SENSIVEIS if p in t]
    if dados_achados:
        sinais.append(f"Pede dados sensiveis: {', '.join(dados_achados[:3])}")
    if urls:
        sinais.append(f"Contem {len(urls)} link(s)")
    for u in urls:
        sinais.extend(analisar_dominio(u))

    return {"urls": urls, "sinais_detectados": sinais}


SYSTEM_PROMPT = """Voce e um especialista em seguranca digital que avalia mensagens
suspeitas de golpe (phishing, smishing, fraudes) no Brasil. Responda SEMPRE em portugues
do Brasil e SOMENTE com um objeto JSON valido, sem texto extra, com exatamente estas chaves:
- "nivel_risco": um de ["baixo", "medio", "alto"]
- "sinais": lista de strings curtas explicando o que torna a mensagem suspeita (ou segura)
- "explicacao": 2 a 3 frases em linguagem simples, para leigos
- "recomendacao": uma frase com o que a pessoa deve fazer

Exemplos de calibracao:

Mensagem: "Oi mae, troquei de numero, salva ai. Me manda um pix que to sem acesso ao banco"
Risco: alto (golpe do falso parente/numero novo pedindo dinheiro)

Mensagem: "Seu pacote dos Correios esta retido. Pague a taxa de R$3,28 aqui: http://correios-br.top/x"
Risco: alto (cobranca falsa + dominio suspeito imitando os Correios)

Mensagem: "Promocao Magalu: 20% off em eletronicos neste fim de semana. Veja em magazineluiza.com.br"
Risco: baixo (oferta plausivel, dominio oficial, sem urgencia nem pedido de dados)

Mensagem: "Bom dia! Confirmando nossa reuniao de amanha as 14h."
Risco: baixo (mensagem comum, sem nenhum sinal de golpe)

Baseie-se nos sinais tecnicos fornecidos, mas use seu julgamento. Nao invente dados."""


def analisar_mensagem(texto):
    base = analisar_sinais(texto)

    contexto = (
        f"Mensagem suspeita:\n\"\"\"\n{texto}\n\"\"\"\n\n"
        f"Sinais tecnicos detectados automaticamente: "
        f"{base['sinais_detectados'] or 'nenhum sinal obvio'}\n"
        f"Links encontrados: {base['urls'] or 'nenhum'}"
    )

    resposta = client.chat.completions.create(
        model=MODELO,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": contexto},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    resultado = json.loads(resposta.choices[0].message.content)
    resultado["sinais_tecnicos"] = base["sinais_detectados"]
    resultado["links"] = base["urls"]
    return resultado
