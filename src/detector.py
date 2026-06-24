import os
import re
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODELO = "llama-3.1-8b-instant"

ENCURTADORES = ["bit.ly", "tinyurl", "goo.gl", "is.gd", "t.co", "ow.ly",
                "cutt.ly", "encurtador", "shorturl", "rebrand.ly"]

URGENCIA = ["urgente", "agora", "imediatamente", "ultima chance", "expira",
            "hoje", "bloquead", "suspens", "limite", "voce ganhou", "premio",
            "parabens", "resgatar", "clique aqui", "confirme seus dados"]

DADOS_SENSIVEIS = ["cpf", "senha", "codigo", "cartao", "cvv", "pix",
                   "conta bancaria", "agencia", "token", "validade"]

URL_RE = re.compile(r"https?://[^\s]+", re.IGNORECASE)


def _normalizar(texto):
    return texto.lower()


def analisar_sinais(texto):
    """Verificacoes deterministicas: extrai sinais objetivos do texto."""
    t = _normalizar(texto)
    urls = URL_RE.findall(texto)

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

    return {"urls": urls, "sinais_detectados": sinais}


SYSTEM_PROMPT = """Voce e um especialista em seguranca digital que avalia mensagens
suspeitas de golpe (phishing, smishing, fraudes). Responda SEMPRE em portugues do Brasil
e SOMENTE com um objeto JSON valido, sem texto extra, com exatamente estas chaves:
- "nivel_risco": um de ["baixo", "medio", "alto"]
- "sinais": lista de strings curtas explicando o que torna a mensagem suspeita (ou segura)
- "explicacao": 2 a 3 frases em linguagem simples, para leigos, sobre por que e ou nao golpe
- "recomendacao": uma frase com o que a pessoa deve fazer
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


if __name__ == "__main__":
    exemplo = (
        "URGENTE! Sua conta sera bloqueada hoje. "
        "Confirme seus dados e CPF agora: http://bit.ly/banco-seguro"
    )
    print(json.dumps(analisar_mensagem(exemplo), indent=2, ensure_ascii=False))
