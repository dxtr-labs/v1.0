// Simple test to verify signup works in browser
console.log('📝 Starting browser signup test...');

window.testSignup = function() {
  const testData = {
    email: `browser-test-${Date.now()}@example.com`,
    password: 'testpassword123',
    firstName: 'Browser',
    lastName: 'Test',
    isOrganization: false
  };

  console.log('🚀 Testing signup with data:', testData);

  fetch('/api/auth/signup', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(testData),
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
      console.log('🔄 Redirecting to dashboard...');
      window.location.href = '/dashboard';
    } else {
      console.error('❌ Signup returned unsuccessful:', result.message);
    }
  })
  .catch(error => {
    console.error('💥 Network/parsing error:', error.message);
  });
};

// Run test automatically
window.testSignup();
console.log('💡 You can also run window.testSignup() manually in the console');
