"""Example: DataSource operations using HTTP client."""

import asyncio
from py_operrouter import HTTPClient, DataSourceConfig


async def main():
    print("🌐 OperRouter HTTP Client - DataSource Example\n")

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

        # 2. Create a PostgreSQL datasource
        print("2️⃣  Creating PostgreSQL datasource...")
        config = DataSourceConfig(
            driver="postgres",
            host="localhost",
            port=5432,
            database="testdb",
            username="postgres",
            password="postgres",
        )
        create_resp = await client.create_datasource("my_postgres", config)
        if not create_resp.success:
            print(f"❌ Failed to create datasource: {create_resp.message}")
            return
        print("✅ PostgreSQL datasource created\n")

        # 3. Query data
        print("3️⃣  Querying database version...")
        query_resp = await client.query_datasource(
            "my_postgres", "SELECT version()"
        )
        if query_resp.success:
            print(f"✅ Query successful, found {len(query_resp.rows)} rows")
            if query_resp.rows:
                print(f"   Version: {query_resp.rows[0]}")
        else:
            print(f"❌ Query failed: {query_resp.message}")
        print()

        # 4. Execute DDL statement
        print("4️⃣  Creating test table...")
        execute_resp = await client.execute_datasource(
            "my_postgres",
            """
            CREATE TABLE IF NOT EXISTS test_users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        if execute_resp.success:
            print("✅ Table created successfully")
        else:
            print(f"❌ Failed to create table: {execute_resp.message}")
        print()

        # 5. Insert data
        print("5️⃣  Inserting test data...")
        insert_resp = await client.insert_datasource(
            "my_postgres",
            {
                "name": "Test User",
                "email": "test@example.com",
            }
        )
        if insert_resp.success:
            print("✅ Data inserted successfully")
        else:
            print(f"❌ Failed to insert data: {insert_resp.message}")
        print()

        # 6. Query inserted data
        print("6️⃣  Querying test_users table...")
        query_resp = await client.query_datasource(
            "my_postgres",
            "SELECT * FROM test_users LIMIT 10"
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
        ping_ds_resp = await client.ping_datasource("my_postgres")
        if ping_ds_resp.success:
            print("✅ Datasource is healthy")
        else:
            print(f"❌ Datasource unhealthy: {ping_ds_resp.message}")
        print()

        # 8. Close datasource
        print("8️⃣  Closing datasource...")
        close_resp = await client.close_datasource("my_postgres")
        if close_resp.success:
            print("✅ Datasource closed")
        else:
            print(f"❌ Failed to close: {close_resp.message}")

        print("\n✅ All DataSource operations completed successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
