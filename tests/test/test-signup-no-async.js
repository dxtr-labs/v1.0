// Test signup API with promise-based approach (no async/await)
const testSignupNoAsync = () => {
  const testEmail = `test-no-async-${Date.now()}@example.com`;
  const signupData = {
    email: testEmail,
    password: 'testpassword123',
    firstName: 'Test',
    lastName: 'User',
    isOrganization: false
  };

  console.log('🧪 Testing signup with promise-based approach...');
  console.log('📤 Signup data:', signupData);

  fetch('http://localhost:3000/api/auth/signup', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(signupData),
  })
  .then(response => {
    console.log('📡 Response status:', response.status);
    return response.json().then(result => ({ response, result }));
  })
  .then(({ response, result }) => {
    console.log('📋 Response result:', result);
    
    if (!response.ok) {
      console.error('❌ Signup failed:', result.error || 'Unknown error');
      return;
    }

    if (result.success) {
      console.log('✅ Signup successful!');
      console.log('👤 User created:', result.user);
      console.log('🎫 Session token created');
    } else {
      console.error('❌ Signup returned unsuccessful:', result.message);
    }
  })
  .catch(error => {
    console.error('💥 Network/parsing error:', error.message);
  });
};

// Run the test
testSignupNoAsync();
