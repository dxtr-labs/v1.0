// test-login.js
// Test the login functionality

async function testLogin() {
  console.log('🧪 Testing login functionality...');
  
  // Test with the user we created earlier
  const loginData = {
    email: 'test-1752231095857@example.com', // Use email from previous test
    password: 'TestPassword123!'
  };
  
  try {
    const response = await fetch('http://localhost:3001/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(loginData),
    });
    
    const data = await response.json();
    
    console.log('📝 Response status:', response.status);
    console.log('📝 Response data:', JSON.stringify(data, null, 2));
    
    if (data.success) {
      console.log('✅ Login test successful!');
      console.log('🎉 User logged in:', data.userId);
      console.log('🔑 Session token received:', data.sessionToken ? 'Yes' : 'No');
    } else {
      console.log('❌ Login test failed:', data.error);
    }
    
  } catch (error) {
    console.error('❌ Test failed with error:', error);
  }
}

// Test with wrong password
async function testBadLogin() {
  console.log('\n🧪 Testing login with wrong password...');
  
  const badLoginData = {
    email: 'test-1752231095857@example.com',
    password: 'WrongPassword123!'
  };
  
  try {
    const response = await fetch('http://localhost:3001/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(badLoginData),
    });
    
    const data = await response.json();
    
    console.log('📝 Response status:', response.status);
    console.log('📝 Response data:', JSON.stringify(data, null, 2));
    
    if (!data.success && response.status === 401) {
      console.log('✅ Bad login test successful (correctly rejected)!');
    } else {
      console.log('❌ Bad login test failed - should have been rejected');
    }
    
  } catch (error) {
    console.error('❌ Test failed with error:', error);
  }
}

async function main() {
  await testLogin();
  await testBadLogin();
}

main();
