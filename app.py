import os
import re

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from groq import Groq
from hindsight_client import Hindsight


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing in .env")

if not HINDSIGHT_API_KEY:
    raise ValueError("HINDSIGHT_API_KEY is missing in .env")


# =========================================================
# APP
# =========================================================

app = Flask(__name__)

BANK_ID = "customer-support-agent"

groq_client = Groq(
    api_key=GROQ_API_KEY
)


# =========================================================
# CUSTOMER ID
# =========================================================

def clean_user_id(user_id):

    user_id = str(user_id).strip()

    if not user_id:
        user_id = "demo-customer"

    return re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        user_id
    )


# =========================================================
# HINDSIGHT CLIENT
# =========================================================

def create_hindsight_client():

    return Hindsight(
        base_url="https://api.hindsight.vectorize.io",
        api_key=HINDSIGHT_API_KEY,
        timeout=30.0
    )


# =========================================================
# CREATE MEMORY BANK
# =========================================================

async def ensure_bank(hindsight_client):

    try:

        await hindsight_client.acreate_bank(
            bank_id=BANK_ID,
            name="Customer Support Memory Agent"
        )

        print("Hindsight bank is ready.")

    except Exception as error:

        print(
            "Hindsight bank message:",
            error
        )


# =========================================================
# RECALL MEMORIES
# =========================================================

async def recall_memories(
    hindsight_client,
    user_id,
    message
):

    query = f"""
Customer ID: {user_id}

Current customer message:
{message}

Find information from previous conversations
with this customer that is relevant to the
current issue.

Look for:

- customer name
- previous problems
- previous solutions
- customer preferences
- device information
- unresolved issues
- previous interactions

Return only information actually stored
in memory.

Do not invent information.
"""

    try:

        print("Hindsight: starting recall...")

        result = await hindsight_client.arecall(
            bank_id=BANK_ID,
            query=query,
            max_tokens=3000,
            budget="mid"
        )

        memories = []

        for memory in result.results:

            if memory.text:

                memories.append(
                    memory.text.strip()
                )


        # -------------------------------------------------
        # REMOVE EXACT DUPLICATES
        # -------------------------------------------------

        unique_memories = []

        seen = set()

        for memory in memories:

            normalized = (
                memory
                .lower()
                .strip()
            )

            if normalized not in seen:

                seen.add(normalized)

                unique_memories.append(
                    memory
                )


        # -------------------------------------------------
        # LIMIT DISPLAYED MEMORIES
        # -------------------------------------------------

        unique_memories = unique_memories[:5]


        print(
            "Hindsight: recall completed.",
            len(unique_memories),
            "unique memories found."
        )


        return unique_memories


    except Exception as error:

        print(
            "Hindsight recall error:",
            error
        )

        return []


# =========================================================
# SAVE CONVERSATION
# =========================================================

async def retain_conversation(
    hindsight_client,
    user_id,
    user_message,
    assistant_message
):

    conversation = f"""
Customer ID: {user_id}

Customer:
{user_message}

Support Agent:
{assistant_message}
"""


    try:

        print(
            "Hindsight: submitting memory..."
        )


        result = await hindsight_client.aretain(
            bank_id=BANK_ID,
            content=conversation,
            context="Customer support conversation",
            retain_async=True
        )


        print(
            "Hindsight: memory submitted successfully."
        )


        operation_id = getattr(
            result,
            "operation_id",
            None
        )


        if operation_id:

            print(
                "Hindsight operation ID:",
                operation_id
            )


        return True


    except Exception as error:

        print(
            "Hindsight retain error:",
            error
        )

        return False


# =========================================================
# GROQ RESPONSE
# =========================================================

def generate_response(
    user_id,
    user_message,
    memories
):


    if memories:

        memory_text = "\n".join(
            f"- {memory}"
            for memory in memories
        )

    else:

        memory_text = (
            "No previous relevant memories were found."
        )


    system_prompt = f"""
You are a professional customer support AI agent.

Your job is to help customers clearly,
naturally, politely, and efficiently.

You have persistent memory powered by Hindsight.

Customer ID:
{user_id}


RELEVANT PREVIOUS MEMORIES:

{memory_text}


IMPORTANT RULES:

1. Use relevant memories when they help answer
   the customer.

2. NEVER invent customer information.

3. NEVER invent dates.

4. NEVER invent transaction IDs.

5. NEVER invent previous events.

6. Only say that you remember something when
   it is present in the retrieved memories.

7. If previous information is relevant,
   naturally refer to it.

8. Do not repeatedly ask for information that
   is already known.

9. If an issue was previously discussed,
   continue from that context.

10. Be concise, friendly, and helpful.

11. If you don't know something, say so.

12. Do not claim that a memory exists unless
    it appears in the retrieved memories.

13. Never mention an exact calendar date from
    a memory unless that exact date was explicitly
    provided by the customer in the conversation.

14. If a memory contains a date generated by the
    memory system, do not repeat that date as a
    fact to the customer.

15. Never convert words such as "yesterday",
    "today", or "last week" into an exact date.

16. When memories are duplicated or very similar,
    treat them as one fact.

17. Only use memories that are relevant to the
    customer's current question.

18. Do not expose internal memory metadata such as
    "When:", "Involving:", or "To resolve".

19. Do not list all retrieved memories in your
    response.

20. If the customer previously mentioned their name
    or device, naturally use that information when
    relevant.
"""


    try:

        print(
            "Groq: generating response..."
        )


        completion = (
            groq_client
            .chat
            .completions
            .create(

                model="openai/gpt-oss-120b",

                messages=[

                    {
                        "role": "system",
                        "content": system_prompt
                    },

                    {
                        "role": "user",
                        "content": user_message
                    }

                ],

                temperature=0.3,

                max_tokens=600
            )
        )


        response = (
            completion
            .choices[0]
            .message
            .content
        )


        print(
            "Groq: response generated."
        )


        return response


    except Exception as error:

        print(
            "Groq error:",
            error
        )


        return (
            "Sorry, I couldn't generate a "
            "response right now."
        )


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# CHAT
# =========================================================

@app.route(
    "/chat",
    methods=["POST"]
)
async def chat():

    print(
        "\n================================"
    )

    print(
        "New customer message received"
    )

    print(
        "================================"
    )


    try:

        data = request.get_json()


        if not data:

            return jsonify({
                "error": "Invalid request."
            }), 400


        user_id = clean_user_id(
            data.get(
                "user_id",
                "demo-customer"
            )
        )


        message = str(
            data.get(
                "message",
                ""
            )
        ).strip()


        if not message:

            return jsonify({
                "error": "Please enter a message."
            }), 400


        print(
            "Customer ID:",
            user_id
        )


        print(
            "Message:",
            message
        )


        # -------------------------------------------------
        # HINDSIGHT CLIENT
        # -------------------------------------------------

        hindsight_client = (
            create_hindsight_client()
        )


        try:

            # ---------------------------------------------
            # MEMORY BANK
            # ---------------------------------------------

            await ensure_bank(
                hindsight_client
            )


            # ---------------------------------------------
            # RECALL
            # ---------------------------------------------

            memories = await recall_memories(
                hindsight_client,
                user_id,
                message
            )


            # ---------------------------------------------
            # GROQ
            # ---------------------------------------------

            response = generate_response(
                user_id,
                message,
                memories
            )


            # ---------------------------------------------
            # RETAIN
            # ---------------------------------------------

            memory_saved = (
                await retain_conversation(
                    hindsight_client,
                    user_id,
                    message,
                    response
                )
            )


            # ---------------------------------------------
            # RETURN TO WEBSITE
            # ---------------------------------------------

            print(
                "Request completed."
            )

            print(
                "================================\n"
            )


            return jsonify({

                "response": response,

                "memories": memories,

                "memory_saved": memory_saved

            })


        finally:

            try:

                await hindsight_client.aclose()

            except Exception as error:

                print(
                    "Hindsight close error:",
                    error
                )


    except Exception as error:

        print(
            "CHAT ROUTE ERROR:",
            error
        )


        return jsonify({

            "error":
                "Something went wrong while "
                "processing your message."

        }), 500


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )