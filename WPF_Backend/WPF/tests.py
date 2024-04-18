import os
import openai

openai.api_key = "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"
openai.Model.retrieve("text-davinci-003")

completion = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ]
)

print(completion.choices[0].message)
