/**
 * Test ONLY Signup to isolate the "Create Account" error
 */

const API_BASE = 'http://localhost:3000';

async function testSignupOnly() {
  console.log('🔄 Testing ONLY Signup API (Create Account)...');
  
  const signupData = {
    email: `test-signup-${Date.now()}@example.com`,
    password: 'testpassword123',
    firstName: 'Test',
    lastName: 'User',
    isOrganization: false
  };

  try {
    console.log('📤 Sending signup request with data:', signupData);
    
    const response = await fetch(`${API_BASE}/api/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(signupData),
    });

    console.log('📥 Response status:', response.status);
    console.log('📥 Response headers:', Object.fromEntries(response.headers.entries()));
    
    const result = await response.json();
    
    if (response.ok) {
      console.log('✅ Signup successful!');
      console.log('📊 Response:', result);
      return { success: true, data: result, signupData };
    } else {
      console.log('❌ Signup failed with status:', response.status);
      console.log('📊 Error response:', result);
      return { success: false, error: result, status: response.status };
    }
  } catch (error) {
    console.log('❌ Signup request failed:', error.message);
    return { success: false, error: error.message };
  }
}

// Run the test
console.log('🚀 Testing Create Account functionality');
console.log('=' .repeat(50));
testSignupOnly().then(result => {
  console.log('\n' + '=' .repeat(50));
  if (result.success) {
    console.log('🎉 Create Account is working!');
  } else {
    console.log('⚠️  Create Account has issues');
    console.log('Error details:', result);
  }
}).catch(console.error);
