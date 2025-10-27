"""Example: LLM operations using FFI client (direct Rust calls)."""

import asyncio
import os
from py_operrouter import FFIClient, LLMConfig, ChatMessage


async def main():
    print("🚀 OperRouter FFI Client - LLM Example\n")

    # Check for API key
    api_key = os.getenv("OLLAMA_API_KEY", "")
    
    try:
        # Create FFI client (direct Rust library calls)
        client = FFIClient()
        print("✅ FFI library loaded successfully\n")

    except RuntimeError as e:
        print(f"❌ Failed to load FFI library: {e}")
        print("\n💡 Make sure to build the FFI library first:")
        print("   cd bridges/operrouter-core-ffi")
        print("   cargo build --release")
        return

    try:
        # 1. Test FFI connection
        print("1️⃣  Testing FFI connection...")
        ping_resp = await client.ping()
        if not ping_resp.success:
            print(f"❌ FFI ping failed: {ping_resp.message}")
            return
        print("✅ FFI core is alive\n")

        # 2. Create an Ollama LLM instance (local, no API key needed)
        print("2️⃣  Creating Ollama LLM instance...")
        config = LLMConfig(
            provider="ollama",
            model="llama2",
            api_key=api_key,  # Ollama usually doesn't need API key
        )
        create_resp = await client.create_llm("my_ollama", config)
        if not create_resp.success:
            print(f"❌ Failed to create LLM: {create_resp.message}")
            print("   Make sure Ollama is running: ollama serve")
            return
        print("✅ Ollama LLM instance created\n")

        # 3. Generate text
        print("3️⃣  Generating text completion...")
        generate_resp = await client.generate_llm(
            "my_ollama",
            "Explain the concept of async/await in one paragraph."
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
            ChatMessage(role="system", content="You are a concise technical assistant."),
            ChatMessage(role="user", content="What are the benefits of using Rust?"),
        ]
        chat_resp = await client.chat_llm("my_ollama", messages)
        if chat_resp.success:
            print("✅ Chat response:")
            print(f"   {chat_resp.text[:300]}..." if len(chat_resp.text) > 300 else f"   {chat_resp.text}")
        else:
            print(f"❌ Chat failed: {chat_resp.message}")
        print()

        # 5. Get text embeddings
        print("5️⃣  Getting text embeddings...")
        embedding_resp = await client.embedding_llm(
            "my_ollama",
            "Rust programming language for systems development"
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
        ping_llm_resp = await client.ping_llm("my_ollama")
        if ping_llm_resp.success:
            print("✅ LLM instance is healthy")
        else:
            print(f"❌ LLM unhealthy: {ping_llm_resp.message}")
        print()

        # 7. Close LLM instance
        print("7️⃣  Closing LLM instance...")
        close_resp = await client.close_llm("my_ollama")
        if close_resp.success:
            print("✅ LLM instance closed")
        else:
            print(f"❌ Failed to close: {close_resp.message}")

        print("\n✅ All LLM operations completed successfully!")
        print("\n💡 FFI client provides maximum performance by bypassing network overhead!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
