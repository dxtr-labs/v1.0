// lib/mock-email-executor.js
// Mock email executor for testing purposes

export const sendMockEmail = async (emailData) => {
  try {
    console.log('📧 [MOCK-EMAIL] Sending mock email...');
    console.log('To:', emailData.recipient);
    console.log('Subject:', emailData.subject);
    console.log('Content:', emailData.content?.substring(0, 100) + '...');

    // Simulate email processing time
    await new Promise(resolve => setTimeout(resolve, 500));

    return {
      success: true,
      messageId: `mock-${Date.now()}@example.com`,
      timestamp: new Date().toISOString(),
      provider: 'mock'
    };

  } catch (error) {
    console.error('❌ [MOCK-EMAIL] Error sending mock email:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

export const mockEmailExecutor = {
  send: sendMockEmail
};
