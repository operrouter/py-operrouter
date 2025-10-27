"""Example: LLM operations using HTTP client."""

import asyncio
import os
from py_operrouter import HTTPClient, LLMConfig, ChatMessage


async def main():
    print("🤖 OperRouter HTTP Client - LLM Example\n")

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("   Set it with: export OPENAI_API_KEY='sk-...'")
        return

    # Create HTTP client
    client = HTTPClient("http://localhost:8080")

    try:
        # 1. Test server connection
        print("1️⃣  Testing server connection...")
        ping_resp = await client.ping()
        if not ping_resp.success:
            print(f"❌ Server ping failed: {ping_resp.message}")
            return
        print("✅ Server is alive\n")

        # 2. Create an OpenAI LLM instance
        print("2️⃣  Creating OpenAI LLM instance...")
        config = LLMConfig(
            provider="openai",
            model="gpt-3.5-turbo",
            api_key=api_key,
        )
        create_resp = await client.create_llm("my_openai", config)
        if not create_resp.success:
            print(f"❌ Failed to create LLM: {create_resp.message}")
            return
        print("✅ OpenAI LLM instance created\n")

        # 3. Generate text
        print("3️⃣  Generating text completion...")
        generate_resp = await client.generate_llm(
            "my_openai",
            "Explain quantum computing in one sentence."
        )
        if generate_resp.success:
            print("✅ Generated text:")
            print(f"   {generate_resp.text}")
        else:
            print(f"❌ Generation failed: {generate_resp.message}")
        print()

        # 4. Chat with the model
        print("4️⃣  Testing chat interface...")
        messages = [
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content="What is the capital of France?"),
        ]
        chat_resp = await client.chat_llm("my_openai", messages)
        if chat_resp.success:
            print("✅ Chat response:")
            print(f"   {chat_resp.text}")
        else:
            print(f"❌ Chat failed: {chat_resp.message}")
        print()

        # 5. Get text embeddings
        print("5️⃣  Getting text embeddings...")
        embedding_resp = await client.embedding_llm(
            "my_openai",
            "Hello world"
        )
        if embedding_resp.success:
            print(f"✅ Embedding generated:")
            print(f"   Dimensions: {len(embedding_resp.embedding)}")
            print(f"   First 5 values: {embedding_resp.embedding[:5]}")
        else:
            print(f"❌ Embedding failed: {embedding_resp.message}")
        print()

        # 6. Ping LLM instance
        print("6️⃣  Pinging LLM instance...")
        ping_llm_resp = await client.ping_llm("my_openai")
        if ping_llm_resp.success:
            print("✅ LLM instance is healthy")
        else:
            print(f"❌ LLM unhealthy: {ping_llm_resp.message}")
        print()

        # 7. Close LLM instance
        print("7️⃣  Closing LLM instance...")
        close_resp = await client.close_llm("my_openai")
        if close_resp.success:
            print("✅ LLM instance closed")
        else:
            print(f"❌ Failed to close: {close_resp.message}")

        print("\n✅ All LLM operations completed successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
