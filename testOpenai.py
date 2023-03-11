# -*- coding: utf-8 -*-

import openai

# Replace YOUR_API_KEY with your OpenAI API key
openai.api_key = "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"

model_engine = "text-davinci-003"
prompt = "расскажи чего ожидать от конференции google 2023"

# задаем макс кол-во слов
max_tokens = 1024

# генерируем ответ
completion = openai.Completion.create(
    engine=model_engine,
    prompt=prompt,
    max_tokens=1024,
    temperature=0.5,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
)

# выводим ответ
print(completion.choices[0].text)
"""

response = openai.Image.create(
  prompt="very realistic man fixing computer very high resolution",
  n=1,
  size="1024x1024"
)
image_url = response['data'][0]['url']
print(image_url)
"""