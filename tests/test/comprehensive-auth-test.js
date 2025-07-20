// comprehensive-auth-test.js
// Test the complete authentication flow

async function testCompleteFlow() {
  console.log('🧪 Testing complete authentication flow...\n');
  
  const timestamp = Date.now();
  const testEmail = `test-${timestamp}@example.com`;
  const testPassword = 'TestPassword123!';
  
  // Step 1: Create a new user
  console.log('📝 Step 1: Creating new user...');
  const signupData = {
    email: testEmail,
    password: testPassword,
    firstName: 'Test',
    lastName: 'User',
    username: `testuser${timestamp}`,
    isOrganization: false
  };
  
  try {
    const signupResponse = await fetch('http://localhost:3001/api/auth/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(signupData),
    });
    
    const signupResult = await signupResponse.json();
    
    if (signupResult.success) {
      console.log('✅ Signup successful!');
      console.log(`   User ID: ${signupResult.user.id}`);
      console.log(`   Credits: ${signupResult.user.credits}`);
    } else {
      console.log('❌ Signup failed:', signupResult.error);
      return;
    }
    
  } catch (error) {
    console.error('❌ Signup failed with error:', error);
    return;
  }
  
  // Step 2: Login with the new user
  console.log('\n📝 Step 2: Logging in...');
  const loginData = {
    email: testEmail,
    password: testPassword
  };
  
  try {
    const loginResponse = await fetch('http://localhost:3001/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(loginData),
    });
    
    const loginResult = await loginResponse.json();
    
    if (loginResult.success) {
      console.log('✅ Login successful!');
      console.log(`   User ID: ${loginResult.userId}`);
      console.log(`   Session Token: ${loginResult.sessionToken ? 'Present' : 'Missing'}`);
    } else {
      console.log('❌ Login failed:', loginResult.error);
      return;
    }
    
  } catch (error) {
    console.error('❌ Login failed with error:', error);
    return;
  }
  
  // Step 3: Test waitlist functionality
  console.log('\n📝 Step 3: Testing waitlist...');
  const waitlistData = {
    email: `waitlist-${timestamp}@example.com`,
    joinWaitlist: true
  };
  
  try {
    const waitlistResponse = await fetch('http://localhost:3001/api/auth/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(waitlistData),
    });
    
    const waitlistResult = await waitlistResponse.json();
    
    if (waitlistResult.success) {
      console.log('✅ Waitlist signup successful!');
      console.log(`   Waitlist ID: ${waitlistResult.waitlistId}`);
    } else {
      console.log('❌ Waitlist signup failed:', waitlistResult.error);
    }
    
  } catch (error) {
    console.error('❌ Waitlist signup failed with error:', error);
  }
  
  console.log('\n🎉 Complete authentication flow test finished!');
}

// Test database connection
async function testDatabaseStats() {
  console.log('\n📊 Checking database statistics...');
  
  // This would require a custom endpoint, but we can check via direct database query
  // For now, let's just confirm our test worked by trying to create another user
  
  const timestamp = Date.now();
  const testData = {
    email: `stats-test-${timestamp}@example.com`,
    password: 'TestPassword123!',
    firstName: 'Stats',
    lastName: 'Test',
    username: `statstest${timestamp}`,
    isOrganization: true // Test organization account
  };
  
  try {
    const response = await fetch('http://localhost:3001/api/auth/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testData),
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('✅ Organization account created successfully!');
      console.log(`   Account type: ${result.user.isOrganization ? 'Organization' : 'Individual'}`);
    } else {
      console.log('❌ Organization account creation failed:', result.error);
    }
    
  } catch (error) {
    console.error('❌ Organization test failed:', error);
  }
}

async function main() {
  await testCompleteFlow();
  await testDatabaseStats();
  
  console.log('\n🏁 All tests completed!');
  console.log('💡 You can now:');
  console.log('   - Visit http://localhost:3001/signup to create an account');
  console.log('   - Visit http://localhost:3001/login to sign in');
  console.log('   - Use the credentials from this test to login');
}

main();
