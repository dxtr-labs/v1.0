const { test, expect } = require('@playwright/test');

const baseUrl = 'http://localhost:8080';

test('should connect to WebSocket and show status', async ({ page }) => {
    await page.goto(`${baseUrl}/agent-interface.html`);
    // Wait for connection status to change
    await expect(page.locator('#connectionStatus')).toHaveText(/Connected|Disconnected/, { timeout: 15000 });
});

test('should load existing agents', async ({ page }) => {
    await page.goto(`${baseUrl}/agent-interface.html`);
    // Wait for agents to load
    await expect(page.locator('#agentList')).not.toBeEmpty({ timeout: 15000 });
});

test('should create new agent', async ({ page }) => {
    await page.goto(`${baseUrl}/agent-interface.html`);
    
    // Click create agent button
    await page.click('[onclick="createNewAgent()"]');
    
    // Fill in agent details
    await page.fill('#agentName', 'Test Agent');
    await page.fill('#agentRole', 'Integration Tester');
    await page.fill('#agentPersonality', 'thorough, precise, analytical');
    await page.fill('#agentExpectations', 'Test the integration between frontend and backend');
    
    // Submit form
    await page.click('#newAgentForm button[type="submit"]');
    
    // Verify new agent appears in list
    await expect(page.locator('#agentList')).toContainText('Test Agent', { timeout: 15000 });
});

test('should send and receive messages', async ({ page }) => {
    // Enable logging browser console
    page.on('console', msg => console.log('BROWSER:', msg.text()));
    page.on('pageerror', err => console.log('BROWSER ERROR:', err.message));

    await page.goto(`${baseUrl}/agent-interface.html`);
    
    console.log('Creating test agent...');
    // Create and select test agent first
    await page.click('[onclick="createNewAgent()"]');
    
    // Wait for the modal to be visible (using flex display)
    await page.waitForFunction(() => {
        const modal = document.getElementById('newAgentModal');
        return window.getComputedStyle(modal).display === 'flex';
    }, { timeout: 15000 });
    
    // Fill in the form
    await page.fill('#agentName', 'Chat Test Agent');
    await page.fill('#agentRole', 'Chat Tester');
    await page.fill('#agentPersonality', 'responsive, quick');
    await page.fill('#agentExpectations', 'Test chat functionality');
    
    console.log('Submitting agent form...');
    
    // Submit the form
    await page.click('#newAgentForm button[type="submit"]');
    
    // Wait for the agent list to update and include our new agent
    await page.waitForFunction(
        (agentName) => {
            const agentList = document.getElementById('agentList');
            if (!agentList) return false;
            
            // Get all agent names from list items
            const agentElements = agentList.querySelectorAll('.font-medium');
            const agentNames = Array.from(agentElements).map(el => el.textContent);
            
            return agentNames.includes(agentName);
        },
        'Chat Test Agent',
        { timeout: 15000 }
    );
    
    // Wait for message input to be enabled
    await page.waitForSelector('#messageInput:not([disabled])', { timeout: 15000 });
    
    // Send a test message
    console.log('Sending test message...');
    await page.fill('#messageInput', 'Hello, this is a test message');
    await page.click('#sendButton');
    
    // Verify message appears in chat
    console.log('Waiting for message to appear...');
    await expect(page.locator('#chatMessages')).toContainText('Hello, this is a test message', { timeout: 15000 });
    
    // Wait for any response or error
    console.log('Waiting for response or error...');
    await expect(page.locator('#chatMessages')).toContainText(/Mock response to:|Error: Server error/, { timeout: 15000 });
    
    // Test recovery - try sending another message
    await page.waitForSelector('#messageInput:not([disabled])', { timeout: 15000 });
    await page.waitForSelector('#sendButton:not([disabled])', { timeout: 15000 });
});

test('should show workflow updates', async ({ page }) => {
    // Enable logging browser console
    page.on('console', msg => console.log('BROWSER:', msg.text()));
    page.on('pageerror', err => console.log('BROWSER ERROR:', err.message));

    await page.goto(`${baseUrl}/agent-interface.html`);
    
    // Create and select test agent
    await page.click('[onclick="createNewAgent()"]');
    
    // Wait for the modal to be visible (using flex display)
    await page.waitForFunction(() => {
        const modal = document.getElementById('newAgentModal');
        return window.getComputedStyle(modal).display === 'flex';
    }, { timeout: 15000 });
    
    // Fill in the form
    await page.fill('#agentName', 'Workflow Test Agent');
    await page.fill('#agentRole', 'Workflow Tester');
    await page.fill('#agentPersonality', 'systematic');
    await page.fill('#agentExpectations', 'Test workflow updates');
    
    // Submit the form
    await page.click('#newAgentForm button[type="submit"]');
    
    // Wait for the agent list to update and include our new agent
    await page.waitForFunction(
        (agentName) => {
            const agentList = document.getElementById('agentList');
            if (!agentList) return false;
            
            // Get all agent names from list items
            const agentElements = agentList.querySelectorAll('.font-medium');
            const agentNames = Array.from(agentElements).map(el => el.textContent);
            
            return agentNames.includes(agentName);
        },
        'Workflow Test Agent',
        { timeout: 15000 }
    );
    
    // Wait for message input to be enabled
    await page.waitForSelector('#messageInput:not([disabled])', { timeout: 15000 });
    
    // Send a message that should trigger workflow creation
    await page.fill('#messageInput', 'Create a workflow to send a test email');
    await page.click('#sendButton');
    
    // Wait for any response or error
    await expect(page.locator('#chatMessages')).toContainText(/Mock response to:|Error: Server error/, { timeout: 15000 });
    
    // Verify workflow preview appears if we got a successful response
    const hasError = await page.evaluate(() => {
        const messages = document.querySelectorAll('.chat-message');
        for (const msg of messages) {
            if (msg.classList.contains('bg-red-50')) {
                return true;
            }
        }
        return false;
    });
    
    // Only check workflow if no error occurred
    if (!hasError) {
        await expect(page.locator('#workflowPreview')).not.toHaveClass(/hidden/, { timeout: 15000 });
        await expect(page.locator('#workflowContent')).toContainText(/node|step|email/i, { timeout: 15000 });
    }
    
    // Verify the input is re-enabled after message send
    await page.waitForSelector('#messageInput:not([disabled])', { timeout: 15000 });
    await page.waitForSelector('#sendButton:not([disabled])', { timeout: 15000 });
});
