from openai import OpenAI
import re
import time

class AcademicModel:
    def __init__(self, model_name: str, api_key: str, base_url: str):
        self.model_name = model_name
        self.engine = model_name
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def _strip_think_tags(self, text: str) -> str:
        # Entfernt <think>...</think> inklusive Zeilenumbrüche davor/danach
        return re.sub(r"<think>.*?</think>\s*", "", text, flags=re.DOTALL).strip()
    
    #@cache.cached(data_ex=timedelta(days=30), no_data_ex=timedelta(hours=1), prepended_key_attr='model_name')
    def inference(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            content = response.choices[0].message.content.strip()
            # nur wichtig für Modelle die mit enable_thinking=True arbeiten (z.B. qwen3-32b)
            clean_content = self._strip_think_tags(content)
            return clean_content
        except Exception as e:
            print(f"[WARNUNG] API-Fehler: {e} – Warte 10 Sekunden und fahre fort...")
            time.sleep(1)
