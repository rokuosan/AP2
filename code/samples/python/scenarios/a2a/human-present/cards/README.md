# Agent Payments Protocol Sample: Human Present Purchases with a Card

This sample demonstrates the A2A ap2-extension for a human present transaction
using a card as the payment method.

## Scenario

Human-Present flows refer to all commerce flows where the user is present to
confirm the details of what is being purchased, and what payment method is to be
used. The user attesting to the details of the purchase allows all parties to
have high confidence of the transaction.

The IntentMandate is still leveraged to share the appropriate information with
Merchant Agents. This is to maintain consistency across Human-Present and
Human-Not-Present flows.

All Human-Present purchases will have a user-signed PaymentMandate authorizing
the purchase.

## Key Actors

This sample consists of:

*   **Shopping Agent:** The main orchestrator that handles user's requests to
    shop and delegates tasks to specialized agents.
*   **Merchant Agent:** An agent that handles product queries from the shopping
    agent.
*   **Merchant Payment Processor Agent:** An agent that takes payments on behalf
    of the merchant.
*   **Credentials Provider Agent:** The credentials provider is the holder of a
    user's payment credentials. As such, it serves two primary roles:
    *   It provides the shopping agent the list of payment methods available in
        a user's wallet.
    *   It facilitates payment between the shopping agent and a merchant's
        payment processor.

## Key Features

**1. Card purchase with DPAN**

*   The merchant agent will advertise support for card purchases through its
    agent card and through the CartMandate once shopping is complete.
*   The preferred payment method in the user's wallet will be a tokenized (DPAN)
    card.

**2. OTP Challenge**

*   The merchant payment processor agent will request an OTP challenge of the
    user in order to complete payment.

## Executing the Example

### Setup

Ensure you have obtained a Google API key from
[Google AI Studio](https://aistudio.google.com/apikey). Then declare the
GOOGLE_API_KEY variable in one of two ways.

*   Option 1: Declare it as an environment variable: `export
    GOOGLE_API_KEY=your_key`
*   Option 2: Put it into an .env file at the root of your repository. `echo
    "GOOGLE_API_KEY=your_key" > .env`

### Execution

You can execute the following command to run all of the steps in one terminal:

```sh
bash code/samples/python/scenarios/a2a/human-present/cards/run.sh
```

Or you can run each server in its own terminal:

1.  Start the Merchant Agent:

    ```sh
    uv run --package ap2-samples python -m roles.merchant_agent
    ```

2.  Start the Credentials Provider:

    ```sh
    uv run --package ap2-samples python -m roles.credentials_provider_agent
    ```

3.  Start the Merchant Payment Processor Agent:

    ```sh
    uv run --package ap2-samples python -m roles.merchant_payment_processor_agent
    ```

4.  Start the Shopping Agent:

    ```sh
    uv run --package ap2-samples adk web code/samples/python/src/roles
    ```

Open a browser and navigate to the shopping agent UI at http://0.0.0.0:8000. You
may now begin interacting with the Shopping Agent.

### Interacting with the Shopping Agent

This section walks you through a typical interaction with the sample.

1.  **Launching Agent Development Kit UI**: Open a browser on your computer and
    navigate to 0.0.0.0:8000/dev-ui. Select `shopping_agent` from the `Select an
    agent` drop down in the upper left hand corner.
1.  **Initial Request**: In the Shopping Agent's terminal, you'll be prompted to
    start a conversation. You can type something like: "I want to buy a coffee
    maker."
1.  **Product Search**: The Shopping Agent will delegate to the Merchant Agent,
    which will find products matching your intent and present you with options
    contained in CartMandates.
1.  **Cart Creation**: The Merchant Agent will create one or more `CartMandate`s
    and share it with the Shopping Agent. Each CartMandate is signed by the
    Merchant, ensuring the offer to the user is accurate.
1.  **Product Selection** The Shopping Agent will present the user with the set
    of products to choose from.
1.  **Link Credential Provider**: The Shopping Agent will prompt you to link
    your preferred Credential Provider in order to access you available payment
    methods.
1.  **Payment Method Selection**: After you select a cart, the Shopping Agent
    will show you a list of available payment methods from the Credentials
    Provider Agent. You will select a payment method.
1.  **PaymentMandate creation**: The Shopping Agent will package the cart and
    transaction information in a PaymentMandate and ask you to sign the
    mandate. It will initiate payment using the PaymentMandate.
1.  **OTP Challenge**: The Merchant Payment Processor will then request an OTP,
    and you'll be asked to provide a mock OTP to the agent. Use `123`
1.  **Purchase Complete**: Once the OTP is provided, the payment will be
    processed, and you'll receive a confirmation message and a digital receipt.

## Advanced Engagements with the samples

### Enabling Verbose Engagement with the Shopping Agent

If you want to understand what the agents are doing internally or inspect the
mandate objects they create and share, you can ask the Shopping Agent to run in
**verbose mode**.

Enabling verbose mode will instruct the Shopping Agent, and any agents it
delegates to, to provide detailed explanations of their process, including:

*   A description of their current and next steps.
*   The JSON representation of all data payloads (such as `IntentMandates`,
    `CartMandates`, or `PaymentMandates`) being created, sent, or received.

#### How to Activate Verbose Mode

To activate this mode, simply include the keyword verbose in your initial prompt
to the Shopping Agent. Example prompt:

*"I'm looking to buy a new pair of shoes. Could you be verbose as we do this,
explaining what you're doing, and display all data payloads?"*

> **💡 TIP: Give elaborate instructions**
>
> While the word **verbose** is usually sufficient, providing more elaborate
> instruction in your prompt tends to result in more detailed and helpful
> explanations from the agent.

> **💡 TIP: If the JSON is missing...**
>
> If the agent is in verbose mode but fails to display the JSON mandate, a quick
> follow-up prompt is often needed. Just say: **"Remember we're in verbose mode,
> please display the JSON."** After this reminder, the agent usually becomes
> more reliable at displaying all data payloads.

### Viewing Agent Communication

To help engineers visualize the exact communication occurring between the agent
servers, a detailed log file is created automatically when the servers start up.

By default, this log file is named `watch.log` and is located in the `.logs`
directory.

#### Log Contents

The watch log is a comprehensive trace that includes three main categories of
data:

| Category              | Details Included                                     |
| :-------------------- | :--------------------------------------------------- |
| **Raw HTTP Data**     | The **HTTP method** (e.g., `POST`) and **URL** for   |
:                       : each request, the **JSON request body**, and the :
:                       : **JSON response body**.                              :
| **A2A Message Data**  | Any **request instructions** extracted from the      |
:                       : Agent-to-Agent (A2A) Message's `TextPart`, and any   :
:                       : data found within the Message's `DataParts`.         :
| **AP2 Protocol Data** | Any **Mandate objects** (`IntentMandate`,            |
:                       : `CartMandate`, `PaymentMandate`) that are identified :
:                       : within a Message's `DataParts`.                      :

## Running with vLLM on Kubernetes

Build the demo image from the repository root for the architecture of your
Kubernetes nodes. Publish it to a registry your nodes can pull from and set
the four image references in `kubernetes/deployment.yaml`, or import
`ap2-cards:vllm` into the container runtime on each eligible node.

```bash
demo=code/samples/python/scenarios/a2a/human-present/cards
docker build --platform linux/arm64 -f "$demo/kubernetes/Dockerfile" -t ap2-cards:vllm .
```

Create the namespace and model configuration before applying the manifest.
Set `VLLM_BASE_URL` to the base for the OpenAI-compatible Chat Completions
API, typically `http://<spark-host>:8000/v1` for a direct connection.
Use the exact served model name. Enable automatic tool choice and configure
the matching tool-call parser on vLLM.

```bash
kubectl create namespace ap2-demo
kubectl -n ap2-demo create configmap ap2-cards-model \
  --from-literal="VLLM_BASE_URL=$VLLM_BASE_URL" \
  --from-literal="AGENT_MODEL=$AGENT_MODEL" \
  --from-literal=PAYMENT_METHOD=CARD
```

For an endpoint that accepts a bearer token, set `VLLM_API_KEY` from your
secret store and create the optional Secret.

```bash
printf '%s' "$VLLM_API_KEY" | kubectl -n ap2-demo create secret generic ap2-cards-model \
  --from-file=VLLM_API_KEY=/dev/stdin
```

```bash
kubectl -n ap2-demo apply -f "$demo/kubernetes/deployment.yaml"
kubectl -n ap2-demo rollout status deployment/ap2-cards
kubectl -n ap2-demo port-forward svc/ap2-cards 8000:8000
```

Open <http://localhost:8000> and select `shopping_agent`. The four demo
processes share a Pod so the A2A endpoints can use loopback and AP2 signing
keys can use a shared volume. Demo state is cleared when the Pod is replaced.
After changing the ConfigMap or Secret, restart the deployment to reload it.
To run the demo locally, set the same model variables and use `run.sh`.
