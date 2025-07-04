import json
from pathlib import Path

# API-Details
API_KEY = "<your API-Key>"
BASE_URL_AC = "https://chat-ai.academiccloud.de/v1"
BASE_URL_SC = "https://llm.scads.ai/v1"

# Liste von Modellen
model_configs = [
    {
        "id": "meta-llama/Llama-3.3-70B-Instruct",
        "filename": "test_1.jsonl"
    },
    # Füge weitere Modelle nach Bedarf hinzu
]

input_path = Path("LLM_response_generation") / "uml_prompts.jsonl"
with open(input_path, encoding="utf-8") as f:
    lines = f.readlines()

prompts =["DESCRIPTION: "+json.loads(line)["description"]+";; QUESTION: "+json.loads(line)["question"]+";; EXAMPLE: "+json.loads(line)["example"] for line in lines]
sys_prompts = [json.loads(line)["system_prompt"] for line in lines]
solutions = [json.loads(line)["solution"] for line in lines]


from models.scads_model import ScadsModel
for config in model_configs:
    model = ScadsModel(
        model_name=config["id"],
        api_key=API_KEY,
        base_url=BASE_URL_SC
    )
    # Dateipfad für Ausgaben
    output_path = Path("LLM_response_generation") / config['filename']

    # Erzeuge Antworten und schreibe sie in die Datei
    with open(output_path, "w", encoding="utf-8") as out_file:
        for i, prompt in enumerate(prompts):
            print(f"[{i + 1}/{len(prompts)}] Prompt: {prompt[:60]}...")
            try:
                response = model.inference(prompt, sys_prompts[i])
                result = {
                    #"prompt": prompt,
                    "response": response,
                    "solution": solutions[i]
                }
                out_file.write(json.dumps(result, ensure_ascii=False) + "\n")
            except Exception as e:
                print(f"⚠️ Fehler bei Prompt {i}: {e}")
                continue #um API-Limits zu vermeiden (bei Bedarf weglassen)

    print(f"✅ Modell abgeschlossen: {config['id']} → {output_path}")
