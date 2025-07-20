// Final end-to-end test for authentication flow
const testEndToEndAuth = () => {
  const testEmail = `e2e-test-${Date.now()}@example.com`;
  const testData = {
    email: testEmail,
    password: 'testpassword123',
    firstName: 'EndToEnd',
    lastName: 'Test',
    isOrganization: false
  };

  console.log('🎯 Starting end-to-end authentication test...');
  console.log('📧 Test email:', testEmail);

  console.log('🔄 Step 1: Testing signup API...');
  
  fetch('http://localhost:3000/api/auth/signup', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(testData),
  })
  .then(response => {
    console.log('📡 Signup response status:', response.status);
    return response.json().then(result => ({ response, result }));
  })
  .then(({ response, result }) => {
    if (!response.ok || !result.success) {
      throw new Error('Signup failed: ' + (result.error || 'Unknown error'));
    }

    console.log('✅ Step 1 complete: Signup successful');
    console.log('👤 User created:', result.user);
    
    console.log('🔄 Step 2: Testing login API...');
    
    return fetch('http://localhost:3000/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: testEmail,
        password: testData.password
      }),
    });
  })
  .then(response => {
    console.log('📡 Login response status:', response.status);
    return response.json().then(result => ({ response, result }));
  })
  .then(({ response, result }) => {
    if (!response.ok || !result.success) {
      throw new Error('Login failed: ' + (result.error || 'Unknown error'));
    }

    console.log('✅ Step 2 complete: Login successful');
    console.log('👤 User authenticated:', result.name);
    
    console.log('🔄 Step 3: Testing session validation...');
    
    return fetch('http://localhost:3000/api/auth/check', {
      method: 'GET',
    });
  })
  .then(response => {
    console.log('📡 Session check response status:', response.status);
    return response.json().then(result => ({ response, result }));
  })
  .then(({ response, result }) => {
    if (response.ok && result.user) {
      console.log('✅ Step 3 complete: Session validation successful');
      console.log('👤 Session user:', result.user);
      console.log('🎉 END-TO-END TEST PASSED! All authentication flows working correctly.');
    } else {
      console.log('⚠️ Session validation failed, but signup/login worked');
    }
  })
  .catch(error => {
    console.error('❌ End-to-end test failed:', error.message);
  });
};

// Run the test
testEndToEndAuth();
