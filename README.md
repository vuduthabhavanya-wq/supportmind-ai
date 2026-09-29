# 🧠 SupportMind AI

### Customer Support That Remembers

SupportMind AI is an AI-powered customer support agent that uses persistent memory to remember previous customer interactions.

Instead of treating every support conversation as a new conversation, SupportMind uses Hindsight to recall relevant customer history and provide more personalized responses.

## 🚨 The Problem

Traditional AI support agents often forget previous conversations.

A customer may report a payment failure today and contact support again tomorrow, only to be asked the same questions again.

This creates a frustrating experience for customers and makes support less efficient.

## 💡 Our Solution

SupportMind AI gives the support agent persistent memory.

It remembers information such as:

- Previous customer issues
- Payment failures
- Device information
- Previous support interactions
- Information requested by the support agent

When the same customer contacts support again, relevant memories are retrieved and provided to the AI.

## 🧠 How Hindsight Is Used

Hindsight is the persistent memory layer of SupportMind AI.

The application:

1. Receives a customer message.
2. Retrieves relevant memories from Hindsight.
3. Provides those memories to the AI agent.
4. Generates a personalized response.
5. Stores the new conversation in Hindsight.
6. Uses that information in future conversations.

This allows the agent to build up a history for each customer.

## 🔄 Example

### First interaction

Customer:

> My payment failed on my Android phone.

SupportMind responds and stores the interaction in Hindsight.

### Later interaction

Customer:

> My payment failed again.

Instead of starting from zero, SupportMind can recall that the customer previously experienced payment failures on an Android device.

The agent can then respond using that context.

## 🏗️ Architecture

```text
                 Customer
                    │
                    ▼
             SupportMind AI
                    │
                    ▼
              Flask Backend
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     Hindsight             Groq LLM
      Memory                 │
          │                  │
          └─────────┬────────┘
                    ▼
             Personalized
               Response
                    │
                    ▼
                Customer



🛠️ Technology
Python
Flask
Groq
Hindsight
HTML/CSS/JavaScript
Gunicorn
Render
🌐 Live Demo


SupportMind AI Live Demo: https://supportmind-ai-jvny.onrender.com

📸 Demo

The application demonstrates:

Persistent customer memory
Memory recall across conversations
Personalized support responses
Conversation storage
Hindsight memories displayed to the user

🎯 Why Memory Matters

The main value of SupportMind AI is not simply generating another support response.

The important part is that the agent can remember.

As customers interact with the system repeatedly, the memory layer provides historical context that can be used in future conversations.

🔗 Resources
Hindsight GitHub: https://github.com/vectorize-io/hindsight
Hindsight Documentation: https://hindsight.vectorize.io/
Vectorize Agent Memory: https://vectorize.io/what-is-agent-memory
👥 Team

Add your team members
1. Sindhu sree
2. Bhavanya
3. Shyamala
4. Sreeja
5. Deepa
6. Rishitha
