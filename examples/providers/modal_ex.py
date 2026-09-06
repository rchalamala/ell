import ell
import openai
import os

ell.init(verbose=True)

# Models are automatically registered, so we can use them without specifying the client.
# Set MODAL_PROXY_TOKEN_ID / MODAL_PROXY_TOKEN_SECRET (from `modal workspace proxy-tokens create`)
# in your environment to run this example (MODAL_ENDPOINT_URL overrides the endpoint
# the model is served from).
@ell.simple(model='moonshotai/Kimi-K3')
def use_default_modal_client(prompt: str) -> str:
    return prompt

print(use_default_modal_client("Tell me a joke, Kimi!"))


# If you want to use a custom client you can: any Modal Endpoint speaks the
# OpenAI Chat Completions API under /v1 and takes the proxy token as the API key.
modal_client = openai.Client(
    base_url="https://<your-endpoint>.us-west.modal.direct/v1",
    api_key=f"{os.environ['MODAL_PROXY_TOKEN_ID']}.{os.environ['MODAL_PROXY_TOKEN_SECRET']}",
)

@ell.simple(model='moonshotai/Kimi-K3', client=modal_client)
def chat_modal(prompt: str) -> str:
    return prompt
