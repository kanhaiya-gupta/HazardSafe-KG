# Neo4j AuraDB Setup Guide

## Step 1: Create Neo4j AuraDB Instance

1. Go to https://neo4j.com/cloud/platform/aura-graph-database/
2. Sign up for a free account
3. Create a new instance with these details:
   - **Instance name**: HazardSafe-KG
   - **Neo4j version**: 2025.05.0
   - **Database user**: neo4j
   - **Password**: HazardSafe123

## Step 2: Get Connection Details

After creating the instance, you'll receive:
- **Connection URI**: `neo4j+s://your-instance-id.databases.neo4j.io:7687`
- **Username**: neo4j
- **Password**: HazardSafe123

## Step 3: Configure Environment Variables

Set these environment variables before running the application:

### Windows (PowerShell):
```powershell
$env:NEO4J_URI="neo4j+s://your-instance-id.databases.neo4j.io:7687"
$env:NEO4J_USER="neo4j"
$env:NEO4J_PASSWORD="HazardSafe123"
$env:NEO4J_DATABASE="neo4j"
```

### Windows (Command Prompt):
```cmd
set NEO4J_URI=neo4j+s://your-instance-id.databases.neo4j.io:7687
set NEO4J_USER=neo4j
set NEO4J_PASSWORD=HazardSafe123
set NEO4J_DATABASE=neo4j
```

### Create .env file (recommended):
Create a file named `.env` in the project root:
```
NEO4J_URI=neo4j+s://your-instance-id.databases.neo4j.io:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=HazardSafe123
NEO4J_DATABASE=neo4j
VECTOR_DB_TYPE=local
DEBUG=true
LOG_LEVEL=INFO
```

## Step 4: Test Connection

1. Start your application: `python main.py`
2. Check the logs for successful Neo4j connection
3. Visit http://localhost:8000/kg/ to test KG functionality

## Step 5: Access Neo4j Browser

You can also access the Neo4j Browser directly:
- URL: Provided in your AuraDB dashboard
- Username: neo4j
- Password: HazardSafe123

## Troubleshooting

### Connection Issues:
- Verify the URI format: `neo4j+s://` (not `bolt://`)
- Check that your IP is whitelisted in AuraDB
- Ensure the password is correct

### SSL Issues:
- AuraDB requires SSL connections
- The `neo4j+s://` protocol handles SSL automatically

### Performance:
- AuraDB free tier has limitations
- Consider upgrading for production use 