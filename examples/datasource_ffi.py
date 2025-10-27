"""Example: DataSource operations using FFI client (direct Rust calls)."""

import asyncio
from py_operrouter import FFIClient, DataSourceConfig


async def main():
    print("🚀 OperRouter FFI Client - DataSource Example\n")

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
        # 1. Test server connection (local FFI doesn't need server)
        print("1️⃣  Testing FFI connection...")
        ping_resp = await client.ping()
        if not ping_resp.success:
            print(f"❌ FFI ping failed: {ping_resp.message}")
            return
        print("✅ FFI core is alive\n")

        # 2. Create a MongoDB datasource
        print("2️⃣  Creating MongoDB datasource...")
        config = DataSourceConfig(
            driver="mongodb",
            host="localhost",
            port=27017,
            database="testdb",
            username="admin",
            password="admin",
        )
        create_resp = await client.create_datasource("my_mongo", config)
        if not create_resp.success:
            print(f"❌ Failed to create datasource: {create_resp.message}")
            return
        print("✅ MongoDB datasource created\n")

        # 3. Query data
        print("3️⃣  Querying database collections...")
        query_resp = await client.query_datasource(
            "my_mongo", '{"listCollections": 1}'
        )
        if query_resp.success:
            print(f"✅ Query successful, found {len(query_resp.rows)} rows")
            for row in query_resp.rows[:5]:
                print(f"   {row}")
        else:
            print(f"❌ Query failed: {query_resp.message}")
        print()

        # 4. Execute command
        print("4️⃣  Creating test collection...")
        execute_resp = await client.execute_datasource(
            "my_mongo",
            '{"createCollection": "test_items"}'
        )
        if execute_resp.success:
            print("✅ Collection created successfully")
        else:
            print(f"❌ Failed to create collection: {execute_resp.message}")
        print()

        # 5. Insert data
        print("5️⃣  Inserting test data...")
        insert_resp = await client.insert_datasource(
            "my_mongo",
            {
                "name": "Test Item",
                "category": "electronics",
                "price": 299.99,
                "in_stock": True,
            }
        )
        if insert_resp.success:
            print("✅ Data inserted successfully")
        else:
            print(f"❌ Failed to insert data: {insert_resp.message}")
        print()

        # 6. Query inserted data
        print("6️⃣  Querying test_items collection...")
        query_resp = await client.query_datasource(
            "my_mongo",
            '{"find": "test_items", "limit": 10}'
        )
        if query_resp.success:
            print(f"✅ Found {len(query_resp.rows)} rows:")
            for row in query_resp.rows[:5]:  # Show first 5
                print(f"   {row}")
        else:
            print(f"❌ Query failed: {query_resp.message}")
        print()

        # 7. Ping datasource
        print("7️⃣  Pinging datasource...")
        ping_ds_resp = await client.ping_datasource("my_mongo")
        if ping_ds_resp.success:
            print("✅ Datasource is healthy")
        else:
            print(f"❌ Datasource unhealthy: {ping_ds_resp.message}")
        print()

        # 8. Close datasource
        print("8️⃣  Closing datasource...")
        close_resp = await client.close_datasource("my_mongo")
        if close_resp.success:
            print("✅ Datasource closed")
        else:
            print(f"❌ Failed to close: {close_resp.message}")

        print("\n✅ All DataSource operations completed successfully!")
        print("\n💡 FFI client provides zero-copy performance by directly calling Rust core!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
