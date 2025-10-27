"""Example: LLM operations using gRPC client."""

import asyncio
import os
from py_operrouter import GRPCClient, LLMConfig, ChatMessage


async def main():
    print("⚡ OperRouter gRPC Client - LLM Example\n")

    # Check for API key
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        print("❌ CLAUDE_API_KEY environment variable not set")
        print("   Set it with: export CLAUDE_API_KEY='sk-...'")
        return

    # Create gRPC client
    client = GRPCClient("localhost:50051")

    try:
        # 1. Test server connection
        print("1️⃣  Testing server connection...")
        ping_resp = await client.ping()
        if not ping_resp.success:
            print(f"❌ Server ping failed: {ping_resp.message}")
            return
        print("✅ Server is alive\n")

        # 2. Create a Claude LLM instance
        print("2️⃣  Creating Claude LLM instance...")
        config = LLMConfig(
            provider="claude",
            model="claude-3-opus-20240229",
            api_key=api_key,
        )
        create_resp = await client.create_llm("my_claude", config)
        if not create_resp.success:
            print(f"❌ Failed to create LLM: {create_resp.message}")
            return
        print("✅ Claude LLM instance created\n")

        # 3. Generate text
        print("3️⃣  Generating text completion...")
        generate_resp = await client.generate_llm(
            "my_claude",
            "Write a haiku about programming."
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
            ChatMessage(role="system", content="You are a helpful coding assistant."),
            ChatMessage(role="user", content="What is the difference between Python and Rust?"),
        ]
        chat_resp = await client.chat_llm("my_claude", messages)
        if chat_resp.success:
            print("✅ Chat response:")
            print(f"   {chat_resp.text[:200]}..." if len(chat_resp.text) > 200 else f"   {chat_resp.text}")
        else:
            print(f"❌ Chat failed: {chat_resp.message}")
        print()

        # 5. Get text embeddings
        print("5️⃣  Getting text embeddings...")
        embedding_resp = await client.embedding_llm(
            "my_claude",
            "Machine learning and artificial intelligence"
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
        ping_llm_resp = await client.ping_llm("my_claude")
        if ping_llm_resp.success:
            print("✅ LLM instance is healthy")
        else:
            print(f"❌ LLM unhealthy: {ping_llm_resp.message}")
        print()

        # 7. Close LLM instance
        print("7️⃣  Closing LLM instance...")
        close_resp = await client.close_llm("my_claude")
        if close_resp.success:
            print("✅ LLM instance closed")
        else:
            print(f"❌ Failed to close: {close_resp.message}")

        print("\n✅ All LLM operations completed successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Always close the gRPC channel
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
