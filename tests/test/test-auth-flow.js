/**
 * Test Authentication Flow with Corrected PostgreSQL Configuration
 * Tests both signup and login endpoints to verify the database connection works
 */

const API_BASE = 'http://localhost:3000';

async function testSignup() {
  console.log('🔄 Testing Signup API...');
  
  const signupData = {
    email: `test-${Date.now()}@example.com`,
    password: 'testpassword123',
    firstName: 'Test',
    lastName: 'User',
    isOrganization: false
  };

  try {
    const response = await fetch(`${API_BASE}/api/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(signupData),
    });

    const result = await response.json();
    
    if (response.ok) {
      console.log('✅ Signup successful!');
      console.log('📊 Response:', result);
      return { success: true, data: result, signupData };
    } else {
      console.log('❌ Signup failed:', result);
      return { success: false, error: result };
    }
  } catch (error) {
    console.log('❌ Signup request failed:', error.message);
    return { success: false, error: error.message };
  }
}

async function testLogin(email, password) {
  console.log('🔄 Testing Login API...');
  
  const loginData = {
    email,
    password
  };

  try {
    const response = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(loginData),
    });

    const result = await response.json();
    
    if (response.ok) {
      console.log('✅ Login successful!');
      console.log('📊 Response:', result);
      return { success: true, data: result };
    } else {
      console.log('❌ Login failed:', result);
      return { success: false, error: result };
    }
  } catch (error) {
    console.log('❌ Login request failed:', error.message);
    return { success: false, error: error.message };
  }
}

async function runAuthTest() {
  console.log('🚀 Starting Authentication Flow Test with PostgreSQL');
  console.log('=' .repeat(60));
  
  // Test signup
  const signupResult = await testSignup();
  
  if (signupResult.success) {
    console.log('\n⏳ Waiting 1 second before testing login...');
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Test login with the same credentials
    const loginResult = await testLogin(
      signupResult.signupData.email, 
      signupResult.signupData.password
    );
    
    if (loginResult.success) {
      console.log('\n🎉 Complete authentication flow successful!');
      console.log('✅ PostgreSQL database connection is working properly');
    } else {
      console.log('\n⚠️  Signup worked but login failed');
    }
  } else {
    console.log('\n❌ Signup failed, cannot test complete flow');
    console.log('🔍 This might indicate PostgreSQL connection issues');
  }
  
  console.log('\n' + '=' .repeat(60));
  console.log('Test completed');
}

// Run the test
runAuthTest().catch(console.error);
