from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr

######

load_dotenv(override=True)
openai = OpenAI()

#######
pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

########
def record_user_details(email, celular, name="Nombre no proporcionado", notes="not provided"):
    push(f"Registrando interés de {name} con email {email}, celular {celular} y notas {notes}")
    return {"recorded": "ok"}

#####

def record_unknown_question(question):
    push(f"Registrando pregunta no respondida: {question}")
    return {"recorded": "ok"}
  ##########

record_user_details_json = {
    "name": "record_user_details",
    "description": "Utilice esta herramienta para registrar que un usuario está interesado en estar en contacto y proporcionó una dirección de correo electrónico.",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "La dirección de correo electrónico de este usuario"
            },
            "celular":{
                "type": "string",
                "description": "el numero de contacto de este usuario."

            },
            "name": {
                "type": "string",
                "description": "El nombre del usuario, si lo proporcionó"
            }
            ,
            "notes": {
                "type": "string",
                "description": "Cualquier información adicional sobre la conversación que merezca ser registrada para dar contexto"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

##

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Siempre use esta herramienta para registrar cualquier pregunta que no se pueda responder, ya que no sabía la respuesta",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "La pregunta que no se pudo responder"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}
##########

tools = [{"type": "function", "function": record_user_details_json},
        {"type": "function", "function": record_unknown_question_json}]
#######


def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Herramienta llamada: {tool_name}", flush=True)
        tool = globals().get(tool_name)
        result = tool(**arguments) if tool else {}
        results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
    return results

###########

reader = PdfReader("me/linkedin.pdf")
linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text

with open("me/summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()

name = "Juan Miguel Quijano"

##########

system_prompt = f"""Estás actuando como {name}. Estás respondiendo preguntas en el sitio web de {name}, en particular preguntas relacionadas con la carrera, los antecedentes, las habilidades y la experiencia de {name}.
Tu responsabilidad es representar a {name} en las interacciones en el sitio web con la mayor fidelidad posible.
Se te proporciona un resumen de los antecedentes y el perfil de LinkedIn de {name} que puedes usar para responder preguntas.
Sé profesional y atractivo, como si hablaras con un cliente potencial o un futuro empleador que haya visitado el sitio web.
Si no sabes la respuesta a alguna pregunta, usa la herramienta record_unknown_question para registrar la pregunta que no pudiste responder, incluso si se trata de algo trivial o no relacionado con tu carrera.
Si el usuario participa en una conversación, intenta que se ponga en contacto por correo electrónico; pídele su correo electrónico, numero de celular y regístralo con la herramienta record_user_details."""

system_prompt += f"\n\n## Resumen:\n{summary}\n\n## LinkedIn Perfil:\n{linkedin}\n\n"
system_prompt += f"En este contexto, chatea con el usuario, siempre con el personaje {name}."
#############

def chat(message, history):
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    done = False
    while not done:

        # Esta es la llamada a la LLM - nota que pasamos el json de las herramientas

        response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)

        finish_reason = response.choices[0].finish_reason
        
        # Si la LLM quiere llamar a una herramienta, la llamamos!
         
        if finish_reason=="tool_calls":
            message = response.choices[0].message
            tool_calls = message.tool_calls
            results = handle_tool_calls(tool_calls)
            messages.append(message)
            messages.extend(results)
        else:
            done = True
    return response.choices[0].message.content

############

gr.ChatInterface(chat, type="messages").launch()
