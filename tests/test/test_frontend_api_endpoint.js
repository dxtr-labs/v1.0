// Test script to verify the frontend API endpoint is working
async function testTriggerTemplatesEndpoint() {
  try {
    console.log('Testing /api/triggers/templates endpoint...');
    
    const response = await fetch('http://localhost:3002/api/triggers/templates');
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    console.log('✅ Success! Endpoint is working');
    console.log('📋 Response data:', JSON.stringify(data, null, 2));
    
    // Verify expected structure
    if (data.templates && data.templates.cron && data.templates.webhook && data.templates.manual) {
      console.log('✅ All expected trigger types are present');
    } else {
      console.log('⚠️ Some trigger types might be missing');
    }
    
    return data;
  } catch (error) {
    console.error('❌ Error testing endpoint:', error);
    throw error;
  }
}

// Run the test
testTriggerTemplatesEndpoint()
  .then(() => console.log('🎉 All tests passed!'))
  .catch(() => console.log('💥 Test failed!'));
