#!/usr/bin/env python3
"""
Test Email Preview Dialog Direct Trigger
"""
import time

def create_dialog_test():
    print("🧪 CREATING EMAIL PREVIEW DIALOG TEST")
    print("=" * 60)
    
    # Create a test HTML page that directly tests the dialog functionality
    test_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Email Preview Dialog Test</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .dialog { 
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: white; border: 2px solid #ccc; padding: 20px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.3); z-index: 1000;
            max-width: 600px; width: 90%;
        }
        .overlay { 
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.5); z-index: 999;
        }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; }
        .confirm { background: #4CAF50; color: white; border: none; }
        .cancel { background: #f44336; color: white; border: none; }
        pre { background: #f5f5f5; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>📧 Email Preview Dialog Test</h1>
    <p>This tests the email preview dialog functionality directly.</p>
    
    <button onclick="showEmailPreview()">🧪 Test Email Preview Dialog</button>
    <button onclick="testFrontendAPI()">🔗 Test Frontend API</button>
    
    <div id="results"></div>
    
    <!-- Email Preview Dialog -->
    <div id="overlay" class="overlay" style="display: none;" onclick="hideDialog()"></div>
    <div id="dialog" class="dialog" style="display: none;">
        <h2>📧 Email Preview</h2>
        <p><strong>To:</strong> <span id="email-to">test@example.com</span></p>
        <p><strong>Subject:</strong> <span id="email-subject">Test Email Subject</span></p>
        <p><strong>Content:</strong></p>
        <pre id="email-content">This is a test email content that should appear in the preview dialog.</pre>
        
        <div style="margin-top: 20px;">
            <button class="confirm" onclick="approveEmail()">✅ Approve & Send</button>
            <button class="cancel" onclick="hideDialog()">❌ Cancel</button>
        </div>
    </div>

    <script>
        function showEmailPreview() {
            console.log('📧 Testing email preview dialog...');
            document.getElementById('overlay').style.display = 'block';
            document.getElementById('dialog').style.display = 'block';
            
            // Simulate email data
            document.getElementById('email-to').textContent = 'premium@test.com';
            document.getElementById('email-subject').textContent = 'Welcome to Our Premium Service';
            document.getElementById('email-content').textContent = 
                'Dear Valued Customer,\\n\\nWelcome to our premium service! We are excited to have you on board.\\n\\nBest regards,\\nThe Team';
        }
        
        function hideDialog() {
            console.log('📧 Hiding email preview dialog...');
            document.getElementById('overlay').style.display = 'none';
            document.getElementById('dialog').style.display = 'none';
        }
        
        function approveEmail() {
            console.log('✅ Email approved for sending!');
            alert('Email approved and would be sent to: ' + document.getElementById('email-to').textContent);
            hideDialog();
        }
        
        async function testFrontendAPI() {
            console.log('🔗 Testing frontend API...');
            const results = document.getElementById('results');
            results.innerHTML = '<p>🔄 Testing frontend API...</p>';
            
            try {
                const response = await fetch('/api/chat/mcpai', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: 'create welcome email for test@example.com',
                        agentId: 'test-agent',
                        agentConfig: { name: 'Test', role: 'Assistant', personality: 'helpful' }
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    results.innerHTML = '<h3>✅ API Response:</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                    
                    // If it's an email preview response, show the dialog
                    if (data.status === 'preview_ready' || (data.message && data.message.includes('Email Preview'))) {
                        console.log('📧 Email preview detected in API response!');
                        if (data.email_content && data.recipient) {
                            document.getElementById('email-to').textContent = data.recipient;
                            document.getElementById('email-subject').textContent = data.email_subject || 'Generated Email';
                            document.getElementById('email-content').textContent = data.email_content;
                            showEmailPreview();
                        }
                    }
                } else {
                    results.innerHTML = '<h3>❌ API Error:</h3><p>Status: ' + response.status + '</p>';
                }
            } catch (error) {
                results.innerHTML = '<h3>❌ Network Error:</h3><p>' + error.message + '</p>';
            }
        }
        
        console.log('📧 Email Preview Dialog Test Page Loaded');
    </script>
</body>
</html>
    """
    
    # Save the test file
    with open('email_preview_dialog_test.html', 'w', encoding='utf-8') as f:
        f.write(test_html)
    
    print("✅ Test page created: email_preview_dialog_test.html")
    print(f"\n🌐 TESTING INSTRUCTIONS:")
    print(f"1. Open: email_preview_dialog_test.html in browser")
    print(f"2. Click: '🧪 Test Email Preview Dialog'")
    print(f"3. Verify: Dialog opens and displays email content")
    print(f"4. Test: Approve/Cancel buttons work")
    print(f"5. Click: '🔗 Test Frontend API' (if servers running)")
    
    print(f"\n🎯 DIALOG FUNCTIONALITY TEST:")
    print(f"✅ Test dialog opening/closing")
    print(f"✅ Test email content display")
    print(f"✅ Test approve/cancel actions")
    print(f"✅ Test API integration")

if __name__ == "__main__":
    create_dialog_test()
    
    print(f"\n🔧 NEXT: Fix React dialog state management in the actual app")
    print(f"The test page will help verify the dialog functionality works")
    print(f"Then we can apply the same logic to the React component")
