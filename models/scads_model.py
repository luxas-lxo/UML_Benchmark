from openai import OpenAI

class ScadsModel:
    def __init__(self, model_name: str, api_key: str, base_url: str):
        self.model_name = model_name
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    #@cache.cached(data_ex=timedelta(days=30), no_data_ex=timedelta(hours=1), prepended_key_attr='model_name')
    def inference(self, prompt: str, system_prompt: str = None) -> str:
        
        messages = []
        if system_prompt and self.model_name != "openGPT-X/Teuken-7B-instruct-research-v0.4":
            messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
        elif system_prompt and self.model_name == "openGPT-X/Teuken-7B-instruct-research-v0.4":
            prompt_teu = f"System: {system_prompt}\nUser: {prompt}\nAssistant:"
            messages.append({"role": "user", "content": prompt_teu})
        else:
            messages.append({"role": "user", "content": prompt})
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"[WARNUNG] API-Fehler: {e} – Warte 10 Sekunden und fahre fort...")



