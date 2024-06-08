import requests
from vertexai.preview.generative_models import GenerativeModel, Image

def load_image_from_url(image_url):
    response = requests.get(image_url)
    return Image.from_bytes(response.content)

landmark1 = load_image_from_url("https://storage.googleapis.com/cloud-samples-data/vertex-ai/llm/prompts/landmark1.png")
landmark2 = load_image_from_url("https://storage.googleapis.com/cloud-samples-data/vertex-ai/llm/prompts/landmark2.png")
landmark3 = load_image_from_url("https://www.pngkey.com/png/full/320-3208379_golden-gate-bridge-in-san-francisco-ca-golden.png")

model = GenerativeModel("gemini-pro-vision")

response = model.generate_content(
    [landmark1, "city: Rome, country: Italy, Landmark: the Colosseum",
     landmark2, "city: Beijing, country: China, Landmark: Forbidden City",
     landmark3,  ]
)

print(response)
