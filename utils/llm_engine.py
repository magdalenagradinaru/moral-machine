from groq import Groq
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Ești un motor de decizie morală pentru vehicule autonome.
Analizezi scenarii etice și iei decizii ca și cum ai fi sistemul de control al unui vehicul autonom.

Pentru fiecare scenariu primit, răspunzi EXCLUSIV în format JSON valid, fără niciun alt text, fără markdown, fără backtick-uri:
{
  "decision": "A" sau "B",
  "reasoning": "explicația detaliată a deciziei în 2-4 propoziții",
  "moral_principle": "numele principiului moral principal folosit"
}

Principii morale pe care le poți folosi:
- Utilitarism: maximizarea binelui pentru numărul maxim de persoane
- Deontologie: respectarea regulilor și datoriilor morale absolute
- Etica Virtuții: ce ar face o persoană cu caracter moral exemplar
- Contractualism: principii acceptabile pentru toți membrii societății
- Etica Îngrijirii: prioritatea relațiilor și protejării celor vulnerabili
- Egalitarism: toți oamenii au valoare egală indiferent de statut
- Prioritarism: prioritate acordată celor mai defavorizați
- Etica Responsabilității: cine poartă vina determină consecința

Răspunde DOAR cu JSON-ul. Nicio altă propoziție în afara JSON-ului."""


def get_llm_decision(scenario: dict) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY nu este setat în fișierul .env")

    client = Groq(api_key=api_key)

    user_message = f"""Scenariu moral #{scenario['id']}: {scenario['titlu']}

Descriere: {scenario['descriere']}

Opțiunea A: {scenario['optiunea_A']}
Opțiunea B: {scenario['optiunea_B']}

Care este decizia ta morală și de ce? Răspunde DOAR cu JSON."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message}
            ],
            max_tokens=800,
            temperature=0.3
        )

        response_text = response.choices[0].message.content.strip()

        # Curăță eventuale markdown code blocks
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text).strip()

        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                return {
                    "llm_decision": "N/A",
                    "llm_reasoning": response_text,
                    "llm_moral_principle": "Eroare parsare"
                }

        return {
            "llm_decision":        result.get("decision", "N/A").strip().upper(),
            "llm_reasoning":       result.get("reasoning", "").strip(),
            "llm_moral_principle": result.get("moral_principle", "Necunoscut").strip()
        }

    except Exception as e:
        return {
            "llm_decision":        "EROARE",
            "llm_reasoning":       f"Eroare API: {str(e)}",
            "llm_moral_principle": "N/A"
        }


def validate_api_key() -> bool:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "gsk_CHEIA_TA_AICI":
        return False
    return True
