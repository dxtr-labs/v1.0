// test-signup.js
// Test the signup functionality

async function testSignup() {
  console.log('🧪 Testing signup functionality...');
  
  const testData = {
    email: `test-${Date.now()}@example.com`,
    password: 'TestPassword123!',
    firstName: 'Test',
    lastName: 'User',
    username: `testuser${Date.now()}`,
    isOrganization: false
  };
  
  try {
    const response = await fetch('http://localhost:3001/api/auth/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testData),
    });
    
    const data = await response.json();
    
    console.log('📝 Response status:', response.status);
    console.log('📝 Response data:', JSON.stringify(data, null, 2));
    
    if (data.success) {
      console.log('✅ Signup test successful!');
      console.log('🎉 User created:', data.user);
    } else {
      console.log('❌ Signup test failed:', data.error);
    }
    
  } catch (error) {
    console.error('❌ Test failed with error:', error);
  }
}

// Test waitlist functionality
async function testWaitlist() {
  console.log('\n🧪 Testing waitlist functionality...');
  
  const waitlistData = {
    email: `waitlist-${Date.now()}@example.com`,
    joinWaitlist: true
  };
  
  try {
    const response = await fetch('http://localhost:3001/api/auth/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(waitlistData),
    });
    
    const data = await response.json();
    
    console.log('📝 Response status:', response.status);
    console.log('📝 Response data:', JSON.stringify(data, null, 2));
    
    if (data.success) {
      console.log('✅ Waitlist test successful!');
    } else {
      console.log('❌ Waitlist test failed:', data.error);
    }
    
  } catch (error) {
    console.error('❌ Test failed with error:', error);
  }
}

async function main() {
  await testSignup();
  await testWaitlist();
}

main();
