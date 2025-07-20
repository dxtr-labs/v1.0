// Simplified PostgreSQL connection test
const { Pool } = require('pg');

async function testPostgreSQLConnections() {
  console.log('🔧 PostgreSQL Connection Analysis');
  console.log('==================================\n');
  
  // Test current configuration from .env.local
  const currentConfig = {
    user: 'postgres',
    host: '35.202.114.213',
    database: 'automation-engine',
    password: 'devhouse',
    port: 5432,
    ssl: false,
    connectionTimeoutMillis: 5000
  };
  
  console.log('🔍 Testing Current Configuration:');
  console.log(`   Host: ${currentConfig.host}:${currentConfig.port}`);
  console.log(`   Database: ${currentConfig.database}`);
  console.log(`   User: ${currentConfig.user}`);
  
  const pool = new Pool(currentConfig);
  
  try {
    console.log('   ⏳ Attempting connection...');
    const client = await pool.connect();
    
    console.log('   ✅ Connection successful!');
    
    const result = await client.query('SELECT current_database(), current_user');
    console.log(`   📊 Connected to: ${result.rows[0].current_database}`);
    console.log(`   👤 Connected as: ${result.rows[0].current_user}`);
    
    client.release();
    await pool.end();
    
  } catch (error) {
    console.log(`   ❌ Connection failed: ${error.message}`);
    console.log(`   🔍 Error code: ${error.code}`);
    
    // Analyze the specific error
    if (error.code === '3D000') {
      console.log('\n🎯 DIAGNOSIS: Database does not exist');
      console.log('   Problem: The database "automation-engine" doesn\'t exist on the server');
      console.log('   Solutions:');
      console.log('   1. Create the database on the PostgreSQL server');
      console.log('   2. Use an existing database name');
      console.log('   3. Check if the database name is correct');
      
      // Try with different database names
      const commonDbs = ['postgres', 'automation', 'devlabs', 'template1'];
      console.log('\n🔍 Testing with common database names...');
      
      for (const dbName of commonDbs) {
        try {
          const testConfig = { ...currentConfig, database: dbName };
          const testPool = new Pool(testConfig);
          const testClient = await testPool.connect();
          
          console.log(`   ✅ Found working database: "${dbName}"`);
          
          // List all databases
          const dbResult = await testClient.query('SELECT datname FROM pg_database WHERE datistemplate = false');
          console.log('   📋 Available databases:');
          dbResult.rows.forEach(row => {
            console.log(`      - ${row.datname}`);
          });
          
          testClient.release();
          await testPool.end();
          break;
          
        } catch (testError) {
          if (testError.code === 'ETIMEDOUT') {
            console.log(`   ❌ Timeout testing "${dbName}" - server unreachable`);
            break;
          } else if (testError.code === '3D000') {
            console.log(`   ❌ Database "${dbName}" doesn't exist`);
          } else {
            console.log(`   ❌ Error testing "${dbName}": ${testError.message}`);
          }
        }
      }
      
    } else if (error.message.includes('timeout') || error.code === 'ETIMEDOUT') {
      console.log('\n🎯 DIAGNOSIS: Connection timeout');
      console.log('   Problem: Cannot reach the PostgreSQL server');
      console.log('   Possible causes:');
      console.log('   1. Server is down or offline');
      console.log('   2. Firewall blocking port 5432');
      console.log('   3. Network connectivity issues');
      console.log('   4. Incorrect IP address');
      
    } else if (error.code === 'ECONNREFUSED') {
      console.log('\n🎯 DIAGNOSIS: Connection refused');
      console.log('   Problem: Server actively refused the connection');
      console.log('   Possible causes:');
      console.log('   1. PostgreSQL service not running');
      console.log('   2. Wrong port number');
      console.log('   3. Server not accepting connections');
      
    } else if (error.code === '28P01') {
      console.log('\n🎯 DIAGNOSIS: Authentication failed');
      console.log('   Problem: Invalid username or password');
      console.log('   Solutions:');
      console.log('   1. Verify username and password');
      console.log('   2. Check pg_hba.conf settings');
    }
    
    await pool.end();
  }
  
  console.log('\n💡 RECOMMENDATION:');
  console.log('   For local development, consider using SQLite which is already working');
  console.log('   SQLite database: local-auth.db (✅ Confirmed working)');
  console.log('\n   To use SQLite instead of PostgreSQL:');
  console.log('   1. Update your authentication code to use SQLite first');
  console.log('   2. Use PostgreSQL only for production deployment');
}

testPostgreSQLConnections().catch(console.error);
