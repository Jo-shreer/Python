# LangChain OpenAI (`ChatOpenAI`) — Complete Practical Guide

## What you will learn

This guide focuses exclusively on LangChain's OpenAI integration.

It explains what each feature does, why you need it, how to implement it, and the important parameters, methods, attributes, and return values.

### Table of Contents

1. What is ChatOpenAI?
2. Installation and API-key configuration
3. Model initialization
4. ChatOpenAI constructor parameters
5. Messages and roles
6. Model invocation methods
7. Understanding the response object
8. Token usage and metadata
9. Prompt templates
10. Structured output and JSON
11. Tool calling and function execution
12. OpenAI Responses API and built-in tools
13. Advanced features
    - Retries
    - Fallbacks
    - Callbacks
    - Tracing
    - Log probabilities
    - Multimodal inputs
    - Caching
    - Token management
14. Complete practical application
15. Quick reference and official documentation

---

# 1. What is ChatOpenAI?

`ChatOpenAI` is LangChain's integration class for communicating with OpenAI chat models.

It acts as a bridge between your Python application and OpenAI's API.

Without LangChain, you could use the OpenAI Python SDK directly. With LangChain, you get a standardized interface that integrates with:

- Prompt templates
- Output parsers
- Pydantic schemas
- Tool and function calling
- Agents
- Chains and runnable pipelines
- Streaming
- Callbacks and tracing
- Multimodal inputs

### Why use ChatOpenAI?

Imagine you are building a customer-support chatbot.

You might want to:

1. Send a system instruction to the model.
2. Send the user's question.
3. Get the model's response.
4. Validate the response against a schema.
5. Call a Python function if necessary.
6. Track token usage.
7. Stream the response to the frontend.
8. Save the conversation history.

`ChatOpenAI` provides the model interface for these workflows.

---

# 2. Installation and API-key configuration

## 2.1 Install packages

```bash
pip install -U langchain langchain-openai pydantic
```

Package purposes:

| Package | Purpose |
|---|---|
| `langchain` | Main LangChain framework |
| `langchain-openai` | OpenAI model integration |
| `pydantic` | Data validation and structured schemas |

Some advanced examples in this guide require additional packages. They will be mentioned in their respective sections.

## 2.2 Configure your API key

Create an API key:

https://platform.openai.com/api-keys

Set it as an environment variable.

Linux/macOS:

```bash
export OPENAI_API_KEY="your-api-key"
```

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="your-api-key"
```

Alternatively, configure it in Python:

```python
import os
import getpass

os.environ["OPENAI_API_KEY"] = getpass.getpass(
    "Enter your OpenAI API key: "
)
```

### Why use environment variables?

- Avoid hardcoding credentials.
- Reduce the risk of committing API keys to Git.
- Make it easier to switch between development and production environments.

---

# 3. Model initialization

## 3.1 Basic initialization

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1-mini"
)
```

Explanation:

- `ChatOpenAI`: LangChain's OpenAI integration class.
- `llm`: An instance of the model class.
- `model`: Specifies which OpenAI model to use.

Send a request:

```python
response = llm.invoke(
    "Explain what an LLM is."
)

print(response.content)
```

Example output:

```text
An LLM (Large Language Model) is an AI model
trained on large amounts of text data to understand
and generate human language.
```

Important distinction:

- `ChatOpenAI` is the integration class.
- `llm` is the model instance.
- `invoke()` is a method.
- `response` is the returned message object.
- `response.content` contains the generated content.

## 3.2 Reusable initialization

```python
import os
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
    api_key=os.getenv("OPENAI_API_KEY")
)
```

Now you can change the model using an environment variable without modifying your Python code.

---

# 4. ChatOpenAI constructor parameters

Constructor parameters are passed when creating the model instance.

They control the model, generation behavior, API connection, and request handling.

## 4.1 Model and connection parameters

| Parameter | Meaning | Why use it |
|---|---|---|
| `model` | OpenAI model identifier | Selects the model |
| `api_key` | OpenAI API key | Authenticates requests |
| `base_url` | API endpoint URL | Custom endpoint or proxy |
| `organization` | OpenAI organization ID | Specifies an organization |
| `project` | OpenAI project ID | Specifies a project |
| `timeout` | Request timeout | Limits waiting time |
| `max_retries` | Number of retries | Handles temporary failures |
| `default_headers` | Additional HTTP headers | Sends custom headers |
| `http_client` | Custom synchronous HTTP client | Controls HTTP transport |
| `http_async_client` | Custom asynchronous HTTP client | Controls async transport |

Example:

```python
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    timeout=30,
    max_retries=2
)
```

- `timeout=30`: Sets a 30-second request timeout.
- `max_retries=2`: Allows retries for eligible failures.

These settings are useful in production applications.

## 4.2 Generation parameters

| Parameter | Meaning | Typical use |
|---|---|---|
| `temperature` | Controls randomness | Creative vs predictable output |
| `max_tokens` | Legacy output-token limit | Compatibility |
| `max_completion_tokens` | Maximum completion-token budget | Limits generated output |
| `top_p` | Nucleus sampling threshold | Controls sampling |
| `frequency_penalty` | Penalizes repeated tokens | Reduces repetition |
| `presence_penalty` | Penalizes tokens based on whether they appeared | Encourages new topics |
| `logit_bias` | Adjusts token selection likelihood | Influences specific tokens |
| `stop` | Stop sequences | Stops generation at specified text |
| `n` | Number of completions | Multiple candidates |
| `seed` | Best-effort deterministic seed | Reproducibility experiments |
| `logprobs` | Requests token log probabilities | Analyzing token likelihood |
| `top_logprobs` | Number of top token alternatives | Inspecting alternatives |

### A. temperature

```python
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.2
)
```

Controls randomness.

- Lower temperature: generally more predictable output.
- Higher temperature: generally more varied output.

Illustrative settings:

| Application | Possible temperature |
|---|---:|
| Data extraction | 0 |
| Classification | 0 |
| Technical explanations | 0.2 |
| General conversation | 0.7 |
| Creative writing | 0.9 |

These are examples, not guaranteed behavior. Supported values depend on the selected model.

### B. max_completion_tokens

```python
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    max_completion_tokens=300
)
```

Limits the maximum number of completion tokens.

Useful when you want to control response length and generation cost.

Prefer `max_completion_tokens` over the older `max_tokens` option where the selected model supports it.

### C. top_p

```python
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    top_p=0.9
)
```

Controls nucleus sampling. The model samples from a group of tokens whose cumulative probability reaches the configured threshold.

Usually adjust `temperature` or `top_p`, rather than tuning both simultaneously.

### D. frequency_penalty

```python
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    frequency_penalty=0.5
)
```

Discourages repeating tokens in the generated output.

### E. presence_penalty

```python
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    presence_penalty=0.5
)
```

Encourages introducing tokens that have not appeared previously.

It can encourage topic diversity but does not guarantee better answers.

## 4.3 Reasoning and model-specific parameters

Some models support additional settings.

| Parameter | Meaning |
|---|---|
| `reasoning_effort` | Controls reasoning effort where supported |
| `verbosity` | Controls response verbosity where supported |
| `truncation` | Controls oversized input handling where supported |

Example:

```python
llm = ChatOpenAI(
    model="gpt-5.4-mini",
    reasoning_effort="low"
)
```

These options depend on the model and API being used.

Do not assume every model supports every parameter.

## 4.4 Streaming and response configuration

| Parameter | Meaning |
|---|---|
| `streaming` | Enables streaming behavior for supported use |
| `stream_usage` | Includes token usage in streamed responses |
| `use_responses_api` | Uses OpenAI's Responses API |
| `include` | Requests additional response information where supported |
| `output_version` | Controls the output representation where supported |

Example:

```python
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    stream_usage=True
)
```

`stream_usage=True` is useful when you want token usage information along with streamed output.

## 4.5 Complete initialization example

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.2,
    max_completion_tokens=500,
    timeout=30,
    max_retries=2,
    stream_usage=True
)

response = llm.invoke(
    "Explain the difference between AI and ML."
)

print(response.content)
```

---

# 5. Messages and roles

A chat model can receive a list of messages rather than just one string.

Each message has a role and content.

| Role | Meaning | Purpose |
|---|---|---|
| `system` | System instruction | Defines model behavior |
| `human` | User message | Contains user input |
| `ai` | Assistant message | Represents previous assistant output |

## 5.1 Simple string input

```python
response = llm.invoke(
    "What is LangChain?"
)

print(response.content)
```

Use this when you only need to send one question.

## 5.2 Multiple messages

```python
messages = [
    ("system", "You are an experienced Python developer."),
    ("human", "Explain Python decorators.")
]

response = llm.invoke(messages)

print(response.content)
```

- `system`: Defines the assistant's behavior.
- `human`: Contains the user's question.
- `invoke()`: Sends the messages to OpenAI.

## 5.3 Conversation history

```python
messages = [
    ("system", "You are a helpful Python tutor."),
    ("human", "What is Python?"),
    ("ai", "Python is a high-level programming language."),
    ("human", "What are its advantages?")
]

response = llm.invoke(messages)

print(response.content)
```

The model does not automatically remember previous independent calls to `invoke()`.

If you want it to consider earlier conversation turns, supply the history or use a conversation-management mechanism.

## 5.4 Using message classes

```python
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

messages = [
    SystemMessage(
        content="You are a Python tutor."
    ),
    HumanMessage(
        content="What is a list?"
    ),
    AIMessage(
        content="A list is an ordered collection."
    ),
    HumanMessage(
        content="Can you show an example?"
    )
]

response = llm.invoke(messages)

print(response.content)
```

Tuple-based messages and message classes are both valid approaches.

---

# 6. Model invocation methods

| Method | Purpose |
|---|---|
| `invoke()` | One request, completed response |
| `ainvoke()` | Asynchronous request |
| `stream()` | Progressive response chunks |
| `astream()` | Asynchronous streaming |
| `batch()` | Multiple inputs |
| `abatch()` | Asynchronous multiple inputs |

## 6.1 invoke()

```python
response = llm.invoke(
    "Explain machine learning."
)

print(response.content)
```

Returns an `AIMessage`, not simply a string.

## 6.2 ainvoke()

```python
import asyncio

async def main():

    response = await llm.ainvoke(
        "Explain deep learning."
    )

    print(response.content)


asyncio.run(main())
```

Useful in asynchronous applications such as FastAPI.

## 6.3 stream()

```python
for chunk in llm.stream(
    "Explain LangChain in detail."
):
    print(chunk.text, end="", flush=True)
```

The model produces chunks progressively rather than waiting for the entire response.

## 6.4 batch()

```python
questions = [
    "What is Python?",
    "What is Java?",
    "What is JavaScript?"
]

responses = llm.batch(questions)

for response in responses:
    print(response.content)
```

Useful for processing multiple records or documents.

## 6.5 abatch()

```python
import asyncio

async def main():

    questions = [
        "What is Python?",
        "What is Java?",
        "What is JavaScript?"
    ]

    responses = await llm.abatch(questions)

    for response in responses:
        print(response.content)


asyncio.run(main())
```

This is the asynchronous version of batch processing.

---

# 7. Understanding the response object

`invoke()` normally returns a LangChain `AIMessage`.

Example:

```python
response = llm.invoke(
    "What is artificial intelligence?"
)

print(type(response))
print(response)
```

Important attributes:

| Attribute | Meaning |
|---|---|
| `content` | Main response content |
| `text` | Text representation |
| `content_blocks` | Standardized content blocks |
| `additional_kwargs` | Additional provider-specific data |
| `response_metadata` | Provider response metadata |
| `usage_metadata` | Standardized token usage |
| `id` | Message identifier |
| `name` | Optional message name |
| `tool_calls` | Tool calls requested by the model |
| `invalid_tool_calls` | Invalid tool-call information |

Example:

```python
response = llm.invoke(
    "Explain artificial intelligence."
)

print("Content:", response.content)
print("Metadata:", response.response_metadata)
print("Usage:", response.usage_metadata)
print("ID:", response.id)
```

Example output structure (values vary):

```text
Content: Artificial intelligence is...

Metadata: {
    'model_name': 'gpt-4.1-mini',
    'finish_reason': 'stop'
}

Usage: {
    'input_tokens': 12,
    'output_tokens': 45,
    'total_tokens': 57
}

ID: run-...
```

---

# 8. Token usage and metadata

Token usage helps you monitor how much input and output the model consumes.

Example:

```python
response = llm.invoke(
    "Explain artificial intelligence."
)

usage = response.usage_metadata

print("Input tokens:", usage["input_tokens"])
print("Output tokens:", usage["output_tokens"])
print("Total tokens:", usage["total_tokens"])
```

Example output:

```text
Input tokens: 12
Output tokens: 45
Total tokens: 57
```

The values are illustrative.

### Important usage fields

| Field | Meaning |
|---|---|
| `input_tokens` | Tokens sent to the model |
| `output_tokens` | Tokens generated by the model |
| `total_tokens` | Combined token usage |
| `input_token_details` | Additional input token details, where available |
| `output_token_details` | Additional output token details, where available |

Token counts can be useful for:

- Monitoring usage.
- Estimating cost.
- Preventing context-window overflow.
- Comparing prompt sizes.
- Optimizing application performance.

---

# 9. Prompt templates

Prompt templates allow you to create reusable prompts with dynamic variables.

Instead of writing a different prompt every time, define a template once and supply different values.

There are two important concepts:

1. `PromptTemplate`: Used for string prompts.
2. `ChatPromptTemplate`: Used for chat messages with roles.

## 9.1 PromptTemplate

### What is it?

`PromptTemplate` creates a reusable string prompt.

### Why use it?

Imagine you want to explain multiple programming languages using the same prompt structure.

Without templates, you repeatedly write the same instructions.

With `PromptTemplate`, you define the structure once.

### Complete example

```python
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4.1-mini")

prompt = PromptTemplate(
    input_variables=["language", "level"],
    template=(
        "Explain {language} for a {level} programmer. "
        "Include one practical example."
    )
)

formatted_prompt = prompt.format(
    language="Python",
    level="beginner"
)

print(formatted_prompt)

response = llm.invoke(formatted_prompt)

print(response.content)
```

Formatted prompt output:

```text
Explain Python for a beginner programmer.
Include one practical example.
```

Example model output:

```text
Python is a beginner-friendly programming language.

Example:

name = "John"
print(name)

This prints John.
```

### Important PromptTemplate parameters

| Parameter | Meaning |
|---|---|
| `template` | Actual prompt text |
| `input_variables` | Variables required by the template |
| `partial_variables` | Variables supplied in advance |
| `template_format` | Template format, commonly `f-string` |
| `validate_template` | Whether to validate the template |

### Important methods and attributes

| Method / Attribute | Purpose |
|---|---|
| `format()` | Returns a formatted string |
| `format_prompt()` | Returns a prompt value |
| `partial()` | Creates a template with some variables already supplied |
| `input_variables` | Lists required variables |
| `partial_variables` | Lists pre-supplied variables |

### Example: partial variables

```python
from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate(
    template=(
        "You are a {role}. "
        "Explain {topic} in simple language."
    ),
    input_variables=["topic"],
    partial_variables={
        "role": "Python instructor"
    }
)

result = prompt.format(
    topic="decorators"
)

print(result)
```

Output:

```text
You are a Python instructor.
Explain decorators in simple language.
```

`role` is supplied once and does not need to be passed each time.

## 9.2 ChatPromptTemplate

### What is it?

`ChatPromptTemplate` creates a reusable list of chat messages.

Unlike `PromptTemplate`, it lets you define different roles.

### Why use it?

You may want to keep system instructions separate from user input.

This is particularly useful when building:

- Chatbots
- AI assistants
- Classification applications
- Customer-support systems
- Multi-turn conversations

### Complete example

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4.1-mini")

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert {subject} teacher. "
        "Explain concepts simply."
    ),
    (
        "human",
        "Explain {topic}."
    )
])

chain = prompt | llm

response = chain.invoke({
    "subject": "Python",
    "topic": "decorators"
})

print(response.content)
```

Example output:

```text
A Python decorator is a function that modifies
the behavior of another function without changing
its original code.
```

### What is `|`?

The pipe operator connects LangChain components.

```python
chain = prompt | llm
```

This means:

1. Pass input variables to the prompt.
2. Generate formatted chat messages.
3. Pass those messages to the model.
4. Return the model response.

This is called a runnable pipeline.

### Important ChatPromptTemplate methods

| Method | Purpose |
|---|---|
| `from_messages()` | Creates a chat prompt from messages |
| `invoke()` | Formats the prompt using input values |
| `format_messages()` | Returns formatted message objects |
| `format_prompt()` | Returns a prompt value |
| `partial()` | Supplies some variables in advance |
| `from_template()` | Creates a prompt from a template |

### Important attributes

| Attribute | Meaning |
|---|---|
| `input_variables` | Required variables |
| `partial_variables` | Variables already supplied |
| `messages` | Prompt message templates |
| `input_types` | Expected input types, where specified |

## 9.3 MessagesPlaceholder

### What is it?

`MessagesPlaceholder` is used to insert a list of messages into a chat prompt.

It is especially useful for conversation history.

### Why use it?

Suppose your chatbot has already exchanged five messages with the user.

Instead of manually adding each message to the prompt template, you can insert the entire history using `MessagesPlaceholder`.

### Complete example

```python
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4.1-mini")

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful Python tutor."
    ),
    MessagesPlaceholder(variable_name="history"),
    (
        "human",
        "{question}"
    )
])

history = [
    HumanMessage(content="What is Python?"),
    AIMessage(content="Python is a programming language.")
]

chain = prompt | llm

response = chain.invoke({
    "history": history,
    "question": "What are its advantages?"
})

print(response.content)
```

Example output:

```text
Python has several advantages:

1. Easy-to-read syntax.
2. Large ecosystem of libraries.
3. Cross-platform support.
4. Strong community support.
```

### Important MessagesPlaceholder parameters

| Parameter | Meaning |
|---|---|
| `variable_name` | Name of the variable containing messages |
| `optional` | Whether the history can be omitted |
| `n_messages` | Maximum number of messages to include |

Example:

```python
MessagesPlaceholder(
    variable_name="history",
    optional=True,
    n_messages=10
)
```

This allows an optional history containing up to ten messages.

## 9.4 Combining prompt templates with models

This is a common LangChain pattern.

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4.1-mini")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert technical writer."),
    ("human", "Write a short explanation of {topic}.")
])

chain = prompt | llm

response = chain.invoke({
    "topic": "Retrieval-Augmented Generation"
})

print(response.content)
```

You can extend this pipeline with output parsers and other runnable components.

Example:

```python
chain = prompt | llm | output_parser
```

---

# 10. Structured output and JSON

One of the most useful features of `ChatOpenAI` is structured output.

## 10.1 What is structured output?

Normally, an LLM returns natural language.

For example:

```text
John is 25 years old and lives in Dublin.
```

But your application may need predictable data:

```json
{
  "name": "John",
  "age": 25,
  "city": "Dublin"
}
```

Structured output allows you to request data in a predefined format.

## 10.2 Why use it?

Useful for:

- Data extraction
- Resume parsing
- Invoice processing
- Classification
- API response generation
- Database insertion
- Form filling

## 10.3 Pydantic models

Pydantic lets you define the expected data structure.

Install:

```bash
pip install -U pydantic
```

### Complete example

```python
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

class Person(BaseModel):
    name: str = Field(
        description="Person's full name"
    )

    age: int = Field(
        description="Person's age"
    )

    city: str = Field(
        description="Person's city"
    )


llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

structured_llm = llm.with_structured_output(
    Person
)

response = structured_llm.invoke(
    "John is 25 years old and lives in Dublin."
)

print(response)

print(response.name)
print(response.age)
print(response.city)
```

Example output:

```text
name='John' age=25 city='Dublin'

John
25
Dublin
```

Notice that the response is a Pydantic object, not merely a string.

### Important Pydantic components

| Component | Purpose |
|---|---|
| `BaseModel` | Defines a data model |
| `Field()` | Adds field descriptions and constraints |
| Type annotations | Define expected data types |
| `model_validate()` | Validates data |
| `model_dump()` | Converts model to dictionary |
| `model_dump_json()` | Converts model to JSON string |

### Convert the result into a dictionary

```python
data = response.model_dump()

print(data)
```

Output:

```python
{
    "name": "John",
    "age": 25,
    "city": "Dublin"
}
```

### Convert the result into JSON

```python
json_data = response.model_dump_json(
    indent=2
)

print(json_data)
```

Output:

```json
{
  "name": "John",
  "age": 25,
  "city": "Dublin"
}
```

## 10.4 Understanding with_structured_output()

This method converts a normal chat model into a model that returns structured data.

```python
structured_llm = llm.with_structured_output(
    Person
)
```

Important parameters:

| Parameter | Meaning |
|---|---|
| `schema` | Expected output schema |
| `method` | How structured output is generated |
| `strict` | Requests strict schema adherence where supported |
| `include_raw` | Includes original model response |
| `tools` | Optional tools supported by the method |
| Additional keyword arguments | Passed through to the model |

### The three methods

`with_structured_output()` supports three main approaches.

**1. json_schema**

Uses OpenAI's Structured Outputs API.

```python
structured_llm = llm.with_structured_output(
    Person,
    method="json_schema",
    strict=True
)
```

Use this when the selected model supports OpenAI Structured Outputs.

**2. function_calling**

Uses the tool-calling mechanism to obtain structured data.

```python
structured_llm = llm.with_structured_output(
    Person,
    method="function_calling"
)
```

**3. json_mode**

Requests valid JSON output, but you must also instruct the model to produce the required schema.

```python
structured_llm = llm.with_structured_output(
    Person,
    method="json_mode"
)

response = structured_llm.invoke(
    "Return a JSON object with name, age and city. "
    "John is 25 years old and lives in Dublin."
)

print(response)
```

JSON mode guarantees JSON formatting under supported conditions, not that every requested field or business rule is satisfied.

## 10.5 Understanding strict mode

```python
structured_llm = llm.with_structured_output(
    Person,
    method="json_schema",
    strict=True
)
```

`strict=True` requests exact schema adherence from the supported Structured Outputs or function-calling mechanism.

Important:

- Not every model supports strict mode.
- JSON Schema has restrictions when strict mode is enabled.
- Pydantic schema features must be compatible with OpenAI's supported schema subset.
- Schema adherence does not guarantee that the extracted facts are true.

## 10.6 include_raw

Normally, structured output returns only the parsed result.

If you want both the raw response and parsed result:

```python
structured_llm = llm.with_structured_output(
    Person,
    include_raw=True
)

result = structured_llm.invoke(
    "John is 25 years old and lives in Dublin."
)

print("Raw:", result["raw"])
print("Parsed:", result["parsed"])
print("Parsing error:", result["parsing_error"])
```

The returned dictionary contains:

| Key | Meaning |
|---|---|
| `raw` | Original AIMessage |
| `parsed` | Parsed structured result |
| `parsing_error` | Parsing error, if one occurred |

## 10.7 JSON Schema without Pydantic

You can also pass a JSON Schema dictionary.

```python
schema = {
    "title": "Person",
    "description": "Person information",
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "age": {
            "type": "integer"
        },
        "city": {
            "type": "string"
        }
    },
    "required": [
        "name",
        "age",
        "city"
    ],
    "additionalProperties": False
}

structured_llm = llm.with_structured_output(
    schema,
    method="json_schema",
    strict=True
)

response = structured_llm.invoke(
    "John is 25 years old and lives in Dublin."
)

print(response)
```

The returned value is normally a dictionary when a dictionary schema is used.

Important difference:

- Pydantic schema: returns a validated Pydantic object.
- JSON Schema dictionary: returns a dictionary; it does not automatically provide Pydantic model validation.

---

# 11. Tool calling and function execution

## 11.1 What is tool calling?

Tool calling allows the model to request that your application execute a function.

For example, a user asks:

"What is 25 multiplied by 4?"

The model can decide to call a Python function:

```python
multiply(25, 4)
```

Your application executes the function and sends the result back to the model.

The model can then generate a natural-language response.

## 11.2 Why use tool calling?

An LLM cannot directly execute arbitrary Python functions simply because you mention them in a prompt.

Tool calling provides a structured mechanism for connecting the model to application capabilities.

Typical use cases:

- Calculator
- Weather API
- Database lookup
- CRM integration
- Order tracking
- Search systems
- Internal business functions

## 11.3 The @tool decorator

LangChain provides the `@tool` decorator to define tools.

```python
from langchain_core.tools import tool

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b
```

Explanation:

- `@tool`: Converts a Python function into a LangChain tool.
- `multiply`: Tool name.
- `a`, `b`: Input arguments.
- Type hints: Help define the input schema.
- Docstring: Describes what the tool does.
- `return`: Produces the tool result.

## 11.4 bind_tools()

`bind_tools()` attaches tool definitions to the model.

```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

llm = ChatOpenAI(
    model="gpt-4.1-mini"
)

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

llm_with_tools = llm.bind_tools([
    multiply
])

response = llm_with_tools.invoke(
    "What is 25 multiplied by 4?"
)

print(response.tool_calls)
```

Example output:

```python
[
    {
        "name": "multiply",
        "args": {
            "a": 25,
            "b": 4
        },
        "id": "call_..."
    }
]
```

Important: At this stage, the model has requested the tool. The Python function has not necessarily been executed.

## 11.5 Important bind_tools() parameters

| Parameter | Meaning |
|---|---|
| `tools` | List of available tool definitions |
| `tool_choice` | Controls which tool the model must or may call |
| `strict` | Requests strict schema adherence |
| `parallel_tool_calls` | Controls parallel tool calls |
| `response_format` | Optional structured response schema |
| Additional keyword arguments | Passed to the underlying model binding |

### tool_choice

Common choices:

| Value | Meaning |
|---|---|
| `"auto"` | Model decides whether to call a tool |
| `"none"` | Prevents tool calls |
| `"required"` | Requires a tool call |
| `"any"` | Requires at least one tool call |
| `"multiply"` | Selects a specific tool by name |

Example:

```python
llm_with_tools = llm.bind_tools(
    [multiply],
    tool_choice="multiply"
)
```

Tool-choice support depends on the model and API.

### strict

```python
llm_with_tools = llm.bind_tools(
    [multiply],
    strict=True
)
```

Requests that tool arguments adhere to the supported JSON Schema.

### parallel_tool_calls

```python
llm_with_tools = llm.bind_tools(
    [multiply],
    parallel_tool_calls=False
)
```

Disables parallel tool calls.

This is useful when your application needs tool operations to happen one at a time.

## 11.6 Understanding tool-call arguments

```python
response = llm_with_tools.invoke(
    "Multiply 25 by 4."
)

for tool_call in response.tool_calls:

    print("Tool name:", tool_call["name"])

    print("Arguments:", tool_call["args"])

    print("Tool call ID:", tool_call["id"])
```

The important attributes are:

- `name`: Name of the requested tool.
- `args`: Arguments supplied by the model.
- `id`: Unique identifier for that tool call.

## 11.7 Executing the tool manually

Here is the complete tool-calling cycle.

```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage

llm = ChatOpenAI(
    model="gpt-4.1-mini"
)

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

tools = [multiply]

llm_with_tools = llm.bind_tools(tools)

# Step 1: Ask the model
messages = [
    ("human", "What is 25 multiplied by 4?")
]

ai_message = llm_with_tools.invoke(messages)

# Step 2: Execute requested tools
tool_messages = []

for tool_call in ai_message.tool_calls:

    selected_tool = next(
        tool for tool in tools
        if tool.name == tool_call["name"]
    )

    result = selected_tool.invoke(
        tool_call["args"]
    )

    tool_messages.append(
        ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"]
        )
    )

# Step 3: Send tool result back to model
messages = messages + [ai_message] + tool_messages

final_response = llm_with_tools.invoke(messages)

print(final_response.content)
```

Example output:

```text
100
```

### Understand the complete flow

1. User asks a question.
2. Model decides to call a tool.
3. Model returns a structured tool-call request.
4. Python application executes the function.
5. Application sends the tool result back.
6. Model generates the final response.

**Important:** Tool execution happens in your application. The model requests a tool; your application decides whether to execute it.

For production applications, validate tool arguments, check permissions, handle errors, and apply appropriate authorization before executing tools.

---

# 12. OpenAI Responses API and built-in tools

## 12.1 What is the Responses API?

OpenAI's Responses API provides an interface for model responses and supported built-in capabilities.

With LangChain's OpenAI integration, you can use the Responses API and access supported server-side tools.

Examples include:

- Web search
- File search
- Image generation
- Computer use, where supported

This is different from ordinary Python tools created with `@tool`.

With a normal LangChain tool, your application executes the function.

With a supported built-in OpenAI tool, OpenAI handles the tool execution on its side.

## 12.2 Enable the Responses API

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1",
    use_responses_api=True,
    output_version="responses/v1"
)

response = llm.invoke(
    "Explain what LangChain is."
)

print(response.text)
```

The selected model must support the requested API and features.

`output_version="responses/v1"` opts into the Responses-style message content representation supported by the integration.

## 12.3 Web search

### What is it?

Web search lets a supported OpenAI model search the web as part of responding to a question.

### Why use it?

A normal language model may not know about events or facts that changed after its training data.

Web search can provide more current information.

### Example

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1",
    use_responses_api=True,
    output_version="responses/v1"
)

llm_with_search = llm.bind_tools([
    {
        "type": "web_search"
    }
])

response = llm_with_search.invoke(
    "Find recent developments in artificial intelligence."
)

print(response.content)
```

Example output structure:

```python
[
    {
        "type": "text",
        "text": "Recent developments include ...",
        "annotations": [
            {
                "type": "url_citation",
                "title": "Example source",
                "url": "https://example.com"
            }
        ]
    }
]
```

The actual output and citations depend on the search results.

Important:

- `bind_tools()` makes the built-in tool available.
- The model decides how to use it.
- OpenAI performs the supported server-side search.
- The response may contain source annotations.

## 12.4 File search

### What is it?

File search allows a supported OpenAI model to search files stored in an OpenAI vector store.

### Why use it?

Imagine you have:

- Company policies
- Product documentation
- Employee manuals
- Research reports
- Technical documentation

You can make these files searchable for your AI application.

### Step 1: Create or obtain a vector store

You can create a vector store using the OpenAI Python SDK and upload files.

```bash
pip install -U openai
```

```python
from openai import OpenAI

client = OpenAI()

vector_store = client.vector_stores.create(
    name="Company Knowledge Base"
)

print(vector_store.id)
```

Upload a file:

```python
with open("company_policy.pdf", "rb") as file:

    uploaded_file = client.files.create(
        file=file,
        purpose="assistants"
    )

vector_store_file = client.vector_stores.files.create(
    vector_store_id=vector_store.id,
    file_id=uploaded_file.id
)

print(vector_store_file.id)
```

File ingestion and indexing may take time. Check that the file has completed processing before relying on search.

### Step 2: Use file search with ChatOpenAI

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1",
    use_responses_api=True,
    output_version="responses/v1"
)

llm_with_file_search = llm.bind_tools([
    {
        "type": "file_search",
        "vector_store_ids": [
            "YOUR_VECTOR_STORE_ID"
        ]
    }
])

response = llm_with_file_search.invoke(
    "What is our company's leave policy?"
)

print(response.content)
```

Example output:

```text
According to the company policy, employees
are entitled to the leave described in the
relevant policy document.
```

The actual answer depends on the uploaded files and retrieval results.

Important:

- `vector_store_ids` identifies the vector stores to search.
- Files must be uploaded and indexed.
- The model may use file search when relevant.
- File search is a server-side OpenAI capability, not a local Python file search.

## 12.5 Image generation

### What is it?

Image generation allows a supported OpenAI model to create images using an image-generation tool.

### Example

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1",
    use_responses_api=True,
    output_version="responses/v1"
)

llm_with_image = llm.bind_tools([
    {
        "type": "image_generation"
    }
])

response = llm_with_image.invoke(
    "Create an image of a futuristic city at sunset."
)

print(response.content)
```

The response may contain image-generation output or image-related content blocks.

Important:

- Availability depends on the selected model and API.
- The image-generation tool may return image data rather than ordinary text.
- Your application needs to handle the returned image content appropriately.

## 12.6 Computer use

### What is it?

Computer use allows a supported model to interact with a computer interface through a computer-use tool.

It can be used for tasks such as:

- Reading information on a screen.
- Clicking interface elements.
- Typing text.
- Navigating supported applications.

### Important distinction

Computer use is not simply another Python function.

It involves an interaction loop:

1. The model receives a task.
2. The model requests a computer action.
3. The application or computer-use environment executes that action.
4. A screenshot or observation is returned.
5. The model decides what to do next.

The exact tool schema, model support, and execution environment depend on the OpenAI API version.

For safety, computer actions should be controlled by an application with appropriate permissions and user confirmation for consequential operations.

## 12.7 Conversation state using Responses API

One useful feature of the Responses API is conversation-state management.

You can continue a conversation using a previous response ID.

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1",
    use_responses_api=True,
    output_version="responses/v1"
)

# First request
response1 = llm.invoke(
    "My name is John."
)

print(response1.text)

# Get the response ID
response_id = response1.response_metadata["id"]

# Continue the same conversation
response2 = llm.invoke(
    "What is my name?",
    previous_response_id=response_id
)

print(response2.text)
```

Example output:

```text
My name is John.

Your name is John.
```

The previous response ID allows the API to continue the conversation using its stored state.

The response ID is not the same as a LangChain message ID.

You can also configure:

```python
llm = ChatOpenAI(
    model="gpt-4.1",
    use_responses_api=True,
    use_previous_response_id=True
)
```

This enables the integration to use the previous response ID when appropriate.

Do not assume conversation state is permanent. Check the API's storage, retention, and expiration behavior for your use case.

---

# 13. Advanced features

## 13.1 Retries

### What are retries?

Retries allow your application to attempt a request again when an eligible temporary error occurs.

Examples:

- Temporary network problems
- Rate-limit responses
- Temporary service errors

### Why use retries?

Suppose your application makes an API request and the network temporarily fails.

Instead of immediately failing, your application can try again.

### Example using max_retries

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    max_retries=3,
    timeout=30
)

response = llm.invoke(
    "Explain LangChain."
)

print(response.content)
```

### Example using with_retry()

```python
llm = ChatOpenAI(
    model="gpt-4.1-mini"
)

reliable_llm = llm.with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True
)

response = reliable_llm.invoke(
    "Explain LangChain."
)

print(response.content)
```

Important parameters:

| Parameter | Meaning |
|---|---|
| `stop_after_attempt` | Maximum attempts |
| `wait_exponential_jitter` | Adds randomized exponential backoff |
| `retry_if_exception_type` | Selects exception types to retry |

Retry only errors that are appropriate to retry. Do not blindly repeat operations that might have side effects.

## 13.2 Fallbacks

### What are fallbacks?

Fallbacks allow your application to use another model if the primary model fails.

### Why use them?

Suppose your primary model is unavailable.

You can configure a second model to handle the request.

### Complete example

```python
from langchain_openai import ChatOpenAI

primary_llm = ChatOpenAI(
    model="gpt-4.1"
)

fallback_llm = ChatOpenAI(
    model="gpt-4.1-mini"
)

llm = primary_llm.with_fallbacks([
    fallback_llm
])

response = llm.invoke(
    "Explain artificial intelligence."
)

print(response.content)
```

Explanation:

- `primary_llm`: First model.
- `fallback_llm`: Backup model.
- `with_fallbacks()`: Configures fallback behavior.
- `invoke()`: Attempts the request through the configured runnable.

Fallbacks are useful for improving application resilience.

## 13.3 Callbacks

### What are callbacks?

Callbacks let you observe and respond to events during a LangChain execution.

They can help you:

- Log model activity.
- Track execution.
- Debug errors.
- Monitor token usage.
- Measure latency.

### Example using a callback handler

```python
from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import ChatOpenAI

class MyCallbackHandler(BaseCallbackHandler):

    def on_llm_start(
        self,
        serialized,
        prompts,
        **kwargs
    ):
        print("LLM started")

    def on_llm_end(
        self,
        response,
        **kwargs
    ):
        print("LLM completed")

    def on_llm_error(
        self,
        error,
        **kwargs
    ):
        print("LLM error:", error)


llm = ChatOpenAI(
    model="gpt-4.1-mini"
)

response = llm.invoke(
    "Explain Python.",
    config={
        "callbacks": [
            MyCallbackHandler()
        ]
    }
)

print(response.content)
```

Example output:

```text
LLM started
LLM completed
Python is a programming language...
```

Important callback methods include:

| Callback | Purpose |
|---|---|
| `on_llm_start` | Called when an LLM starts |
| `on_llm_end` | Called when an LLM finishes |
| `on_llm_error` | Called when an LLM errors |
| `on_chat_model_start` | Called when a chat model starts |
| `on_tool_start` | Called when a tool starts |
| `on_tool_end` | Called when a tool finishes |
| `on_tool_error` | Called when a tool errors |

Callbacks are useful for custom application monitoring.

## 13.4 Tracing with LangSmith

### What is tracing?

Tracing lets you inspect how your LangChain application executes.

You can inspect:

- Model inputs
- Model outputs
- Prompt templates
- Tool calls
- Errors
- Execution duration
- Token usage, where available

### Why use it?

Imagine a chatbot gives an incorrect answer.

You want to know:

- What prompt was sent?
- What messages were included?
- Which tool was called?
- What did the tool return?
- What did the model generate?

Tracing helps you investigate the execution.

### Configure LangSmith

Install:

```bash
pip install -U langsmith
```

Set environment variables:

```bash
export LANGSMITH_TRACING="true"
export LANGSMITH_API_KEY="your-langsmith-api-key"
export LANGSMITH_PROJECT="my-langchain-project"
```

Python example:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1-mini"
)

response = llm.invoke(
    "Explain LangChain tracing."
)

print(response.content)
```

When tracing is enabled and configured correctly, LangChain can send execution traces to LangSmith.

Tracing is especially useful when developing and debugging production applications.

## 13.5 Log probabilities

### What are log probabilities?

Log probabilities provide information about how likely the model considered particular generated tokens.

They are useful for:

- Research
- Token-level analysis
- Understanding alternative token choices
- Some classification and confidence-analysis workflows

They are not a general guarantee of factual correctness.

### Example

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    logprobs=True,
    top_logprobs=3
)

response = llm.invoke(
    "The capital of France is"
)

print(response.content)

print(response.response_metadata)
```

Important parameters:

| Parameter | Meaning |
|---|---|
| `logprobs` | Requests token log probabilities |
| `top_logprobs` | Requests alternative high-probability tokens |

Availability depends on the model and API endpoint.

## 13.6 Multimodal inputs

### What is multimodal input?

Multimodal models can process more than ordinary text.

Depending on the model and supported API, inputs may include:

- Text
- Images
- Audio
- Video or sequences of frames

### A. Image input

You can send an image to a supported model.

Example using an image URL:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1-mini"
)

messages = [
    (
        "human",
        [
            {
                "type": "text",
                "text": "Describe this image."
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://example.com/image.jpg"
                }
            }
        ]
    )
]

response = llm.invoke(messages)

print(response.content)
```

The image URL must be accessible to the API.

Example output:

```text
The image shows a landscape with mountains
and a lake.
```

The actual result depends on the image.

### B. Image input using a base64 data URL

```python
import base64

from langchain_openai import ChatOpenAI

with open("image.jpg", "rb") as image_file:
    image_data = base64.b64encode(
        image_file.read()
    ).decode("utf-8")

data_url = (
    f"data:image/jpeg;base64,{image_data}"
)

llm = ChatOpenAI(
    model="gpt-4.1-mini"
)

response = llm.invoke([
    (
        "human",
        [
            {
                "type": "text",
                "text": "Describe this image."
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": data_url
                }
            }
        ]
    )
])

print(response.content)
```

This is useful when your application receives uploaded images.

### C. Audio input

Audio support depends on the selected model and API.

For audio transcription, one common approach is to use OpenAI's audio transcription API directly.

```python
from openai import OpenAI

client = OpenAI()

with open("audio.mp3", "rb") as audio_file:

    transcription = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=audio_file
    )

print(transcription.text)
```

Example output:

```text
Hello, how are you today?
```

You can then pass the transcription into LangChain:

```python
response = llm.invoke(
    f"Summarize this conversation: {transcription.text}"
)

print(response.content)
```

This example uses the OpenAI SDK for the transcription step and LangChain for the subsequent chat-model request.

## 13.7 Caching

### What is caching?

Caching stores the result of an earlier request so that an identical request can potentially reuse the previous result.

### Why use it?

Suppose many users ask:

"What is Python?"

Instead of making a new model request every time, a cache may reuse the stored result when the cache key matches.

This can reduce repeated requests and latency.

### Example using an in-memory cache

```python
from langchain_openai import ChatOpenAI
from langchain_core.caches import InMemoryCache
from langchain_core.globals import set_llm_cache

set_llm_cache(
    InMemoryCache()
)

llm = ChatOpenAI(
    model="gpt-4.1-mini"
)

response1 = llm.invoke(
    "What is Python?"
)

response2 = llm.invoke(
    "What is Python?"
)

print(response1.content)
print(response2.content)
```

The second identical request may be served from the cache.

Important:

- `InMemoryCache` stores data in process memory.
- Cache contents disappear when the process ends.
- Cache behavior depends on model configuration and request inputs.
- Avoid caching requests containing sensitive data unless your storage and privacy requirements permit it.

## 13.8 Token management

### What is token management?

Token management means controlling how much text and other content you send to the model and how much output it generates.

It is important because models have context limits and API usage costs.

### Common techniques

1. Limit output tokens.
2. Shorten unnecessary prompts.
3. Limit conversation history.
4. Summarize old messages.
5. Retrieve relevant documents instead of sending every document.
6. Monitor token usage.
7. Use an appropriate model.

### Example: limit output tokens

```python
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    max_completion_tokens=200
)
```

### Example: limit conversation history

```python
from langchain_core.messages import (
    HumanMessage,
    AIMessage
)

history = [
    HumanMessage(content="Question 1"),
    AIMessage(content="Answer 1"),
    HumanMessage(content="Question 2"),
    AIMessage(content="Answer 2"),
    HumanMessage(content="Question 3"),
    AIMessage(content="Answer 3")
]

recent_history = history[-4:]

print(recent_history)
```

This keeps only the latest four messages.

### Example: count tokens

The OpenAI integration provides token-counting functionality for supported model configurations.

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1-mini"
)

messages = [
    ("system", "You are a helpful assistant."),
    ("human", "Explain LangChain.")
]

token_count = llm.get_num_tokens_from_messages(
    messages
)

print("Token count:", token_count)
```

Token-counting support and accuracy depend on the model and message content. For multimodal requests, token usage may involve image or audio details that simple text counting cannot fully represent.

---

# 14. Complete practical application

Now let's combine several features into one practical application.

We will create a simple AI assistant that:

1. Uses `ChatOpenAI`.
2. Uses `ChatPromptTemplate`.
3. Uses a Pydantic output schema.
4. Uses a Python tool.
5. Reads token usage.

## Complete example

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from pydantic import BaseModel, Field


# ---------------------------------
# 1. Initialize the model
# ---------------------------------

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)


# ---------------------------------
# 2. Define a tool
# ---------------------------------

@tool
def calculate_age_difference(
    age1: int,
    age2: int
) -> int:
    """Calculate the absolute difference between two ages."""

    return abs(age1 - age2)


tools = [calculate_age_difference]

llm_with_tools = llm.bind_tools(tools)


# ---------------------------------
# 3. Create a prompt template
# ---------------------------------

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful personal assistant."
    ),
    (
        "human",
        "{question}"
    )
])


# ---------------------------------
# 4. Ask the model
# ---------------------------------

question = (
    "Calculate the age difference between "
    "a person aged 30 and another aged 24."
)

messages = prompt.format_messages(
    question=question
)

ai_message = llm_with_tools.invoke(messages)


# ---------------------------------
# 5. Execute requested tools
# ---------------------------------

tool_messages = []

for tool_call in ai_message.tool_calls:

    selected_tool = next(
        tool for tool in tools
        if tool.name == tool_call["name"]
    )

    result = selected_tool.invoke(
        tool_call["args"]
    )

    tool_messages.append(
        ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"]
        )
    )


# ---------------------------------
# 6. Get the final answer
# ---------------------------------

if tool_messages:

    final_messages = (
        messages + [ai_message] + tool_messages
    )

    final_response = llm_with_tools.invoke(
        final_messages
    )

else:
    final_response = ai_message


print("Final answer:")
print(final_response.content)


# ---------------------------------
# 7. Read token usage
# ---------------------------------

print("Token usage:")

print(final_response.usage_metadata)
```

Example output:

```text
Final answer:

The age difference is 6 years.

Token usage:

{
    'input_tokens': 50,
    'output_tokens': 12,
    'total_tokens': 62
}
```

Token counts are illustrative and depend on the actual request.

### What did we implement?

| Feature | Where it was used |
|---|---|
| Model initialization | `ChatOpenAI()` |
| Prompt template | `ChatPromptTemplate` |
| Tool definition | `@tool` |
| Tool binding | `bind_tools()` |
| Model invocation | `invoke()` |
| Tool execution | `selected_tool.invoke()` |
| Tool result message | `ToolMessage` |
| Token tracking | `usage_metadata` |

This demonstrates how several LangChain OpenAI features work together in a single application.

---

# 15. Quick reference

## Model initialization

```python
llm = ChatOpenAI(
    model="gpt-4.1-mini"
)
```

## Model invocation

```python
response = llm.invoke("Hello")
```

## Prompt template

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are helpful."),
    ("human", "{question}")
])
```

## Structured output

```python
structured_llm = llm.with_structured_output(
    MyPydanticSchema
)
```

## Tool calling

```python
llm_with_tools = llm.bind_tools([
    my_tool
])
```

## Streaming

```python
for chunk in llm.stream("Hello"):
    print(chunk.text, end="")
```

## Async invocation

```python
response = await llm.ainvoke("Hello")
```

## Batch invocation

```python
responses = llm.batch([
    "Question 1",
    "Question 2"
])
```

## Token usage

```python
print(response.usage_metadata)
```

## Response metadata

```python
print(response.response_metadata)
```

## Retries

```python
reliable_llm = llm.with_retry(
    stop_after_attempt=3
)
```

## Fallbacks

```python
reliable_llm = llm.with_fallbacks([
    backup_llm
])
```

---

# 16. Official documentation

Use these references when checking current APIs, parameters, and model-specific capabilities.

1. LangChain OpenAI integration:
   https://docs.langchain.com/oss/python/integrations/chat/openai

2. ChatOpenAI API reference:
   https://reference.langchain.com/python/integrations/langchain_openai/ChatOpenAI

3. Structured output:
   https://reference.langchain.com/python/langchain-openai/langchain_openai/chat_models/base/ChatOpenAI/with_structured_output

4. Tool binding:
   https://reference.langchain.com/python/langchain-openai/langchain_openai/chat_models/base/ChatOpenAI/bind_tools

5. LangChain prompts:
   https://docs.langchain.com/oss/python/langchain/prompts

6. LangChain messages:
   https://docs.langchain.com/oss/python/langchain/messages

7. OpenAI API documentation:
   https://platform.openai.com/docs/api-reference

8. OpenAI Responses API:
   https://platform.openai.com/docs/api-reference/responses

---

# Final learning roadmap

After completing this guide, you should understand the core LangChain OpenAI integration and how its major features fit together.

Recommended order for practical learning:

1. Master `ChatOpenAI` initialization and invocation.
2. Master `ChatPromptTemplate` and `MessagesPlaceholder`.
3. Learn Pydantic and `with_structured_output()`.
4. Learn `@tool`, `bind_tools()`, and tool execution.
5. Learn the OpenAI Responses API and built-in tools.
6. Learn retries, fallbacks, callbacks, and tracing.
7. Learn multimodal inputs.
8. Learn conversation history, token management, and caching.
9. Combine everything into a complete application.

**Important:** The examples are educational starting points. Exact constructor options, model support, output formats, and built-in tool availability depend on your installed `langchain-openai` version and the selected OpenAI model. Always check the official API reference before deploying a feature in production.
