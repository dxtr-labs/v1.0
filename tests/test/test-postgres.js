// PostgreSQL connection diagnostic test
const { Pool } = require('pg');

// Test both connection configurations
const configs = [
  {
    name: "Current Config (35.202.114.213)",
    config: {
      user: 'postgres',
      host: '35.202.114.213',
      database: 'automation-engine',
      password: 'devhouse',
      port: 5432,
      ssl: false,
      connectionTimeoutMillis: 10000,
      idleTimeoutMillis: 30000,
      max: 1
    }
  },
  {
    name: "Old Config (34.44.98.81)",
    config: {
      user: 'postgres',
      host: '34.44.98.81',
      database: 'automation',
      password: 'devhouse',
      port: 5432,
      ssl: false,
      connectionTimeoutMillis: 10000,
      idleTimeoutMillis: 30000,
      max: 1
    }
  }
];

async function testConnection(configName, config) {
  console.log(`\n🔍 Testing: ${configName}`);
  console.log(`   Host: ${config.host}:${config.port}`);
  console.log(`   Database: ${config.database}`);
  console.log(`   User: ${config.user}`);
  
  const pool = new Pool(config);
  
  try {
    console.log('   ⏳ Connecting...');
    const startTime = Date.now();
    
    const client = await pool.connect();
    const endTime = Date.now();
    
    console.log(`   ✅ Connection successful! (${endTime - startTime}ms)`);
    
    // Test basic query
    const result = await client.query('SELECT version(), current_database(), current_user');
    console.log(`   📊 PostgreSQL Version: ${result.rows[0].version.split(' ')[0]} ${result.rows[0].version.split(' ')[1]}`);
    console.log(`   📊 Connected to database: ${result.rows[0].current_database}`);
    console.log(`   📊 Connected as user: ${result.rows[0].current_user}`);
    
    // Test table existence
    const tablesResult = await client.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      ORDER BY table_name
    `);
    console.log(`   📋 Available tables: ${tablesResult.rows.map(r => r.table_name).join(', ') || 'None'}`);
    
    client.release();
    await pool.end();
    
    return true;
    
  } catch (error) {
    console.log(`   ❌ Connection failed: ${error.message}`);
    console.log(`   🔍 Error code: ${error.code || 'Unknown'}`);
    console.log(`   🔍 Error type: ${error.constructor.name}`);
    
    if (error.code === 'ETIMEDOUT') {
      console.log('   💡 This usually means:');
      console.log('      - Firewall blocking the connection');
      console.log('      - Server is down or unreachable');
      console.log('      - Wrong IP address or port');
    } else if (error.code === 'ECONNREFUSED') {
      console.log('   💡 This usually means:');
      console.log('      - PostgreSQL service is not running');
      console.log('      - Wrong port number');
    } else if (error.code === '28P01') {
      console.log('   💡 This means authentication failed:');
      console.log('      - Wrong username or password');
    } else if (error.code === '3D000') {
      console.log('   💡 This means the database does not exist');
    }
    
    try {
      await pool.end();
    } catch (e) {
      // Ignore cleanup errors
    }
    
    return false;
  }
}

async function runDiagnostics() {
  console.log('🔧 PostgreSQL Connection Diagnostics');
  console.log('=====================================');
  
  for (const { name, config } of configs) {
    await testConnection(name, config);
  }
  
  console.log('\n🌐 Network Connectivity Tests');
  console.log('==============================');
  
  // Test basic network connectivity
  for (const { name, config } of configs) {
    console.log(`\n🔍 Testing network reach to ${config.host}:${config.port}`);
    try {
      const { spawn } = require('child_process');
      const ping = spawn('ping', ['-n', '1', config.host]);
      
      ping.on('close', (code) => {
        if (code === 0) {
          console.log(`   ✅ Host ${config.host} is reachable via ping`);
        } else {
          console.log(`   ❌ Host ${config.host} is not reachable via ping`);
        }
      });
      
      // Wait a bit for ping to complete
      await new Promise(resolve => setTimeout(resolve, 2000));
      
    } catch (error) {
      console.log(`   ❌ Ping test failed: ${error.message}`);
    }
  }
  
  console.log('\n📋 Summary & Recommendations');
  console.log('=============================');
  console.log('Based on the results above:');
  console.log('1. If ETIMEDOUT: Check firewall rules and server status');
  console.log('2. If ECONNREFUSED: PostgreSQL service might be down');
  console.log('3. If authentication fails: Verify credentials');
  console.log('4. Consider using SQLite for local development');
}

runDiagnostics().catch(console.error);
