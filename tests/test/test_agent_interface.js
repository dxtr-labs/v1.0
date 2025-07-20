// Frontend Integration Tests for Agent Interface
const { test, expect } = require('@playwright/test');

test.describe('Agent Interface Integration Tests', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('http://localhost:8000/agent-interface.html');
    });

    test('should connect to WebSocket and show status', async ({ page }) => {
        // Wait for connection status to update
        await expect(page.locator('#connectionStatus')).toHaveText(/Connected|Disconnected/);
    });

    test('should load existing agents', async ({ page }) => {
        // Wait for agent list to populate
        const agentList = page.locator('#agentList');
        await expect(agentList).not.toBeEmpty();
    });

    test('should create new agent', async ({ page }) => {
        // Click create agent button
        await page.click('button:text("Create New Agent")');
        
        // Fill in agent details
        await page.fill('#agentName', 'Test Agent');
        await page.fill('#agentRole', 'Integration Tester');
        await page.fill('#agentPersonality', 'thorough, precise, analytical');
        await page.fill('#agentExpectations', 'Test the integration between frontend and backend');
        
        // Submit form
        await page.click('button:text("Create")');
        
        // Verify new agent appears in list
        await expect(page.locator('#agentList')).toContainText('Test Agent');
    });

    test('should send and receive messages', async ({ page }) => {
        // Create and select test agent first
        await page.click('button:text("Create New Agent")');
        await page.fill('#agentName', 'Chat Test Agent');
        await page.fill('#agentRole', 'Chat Tester');
        await page.fill('#agentPersonality', 'responsive, quick');
        await page.fill('#agentExpectations', 'Test chat functionality');
        await page.click('button:text("Create")');
        
        // Wait for agent to be created and selected
        await page.click('text=Chat Test Agent');
        
        // Send a test message
        await page.fill('#messageInput', 'Hello, this is a test message');
        await page.click('#sendButton');
        
        // Verify message appears in chat and gets response
        await expect(page.locator('#chatMessages')).toContainText('Hello, this is a test message');
        await expect(page.locator('#chatMessages')).toContainText(/./); // Any response
    });

    test('should show workflow updates', async ({ page }) => {
        // Create and select test agent
        await page.click('button:text("Create New Agent")');
        await page.fill('#agentName', 'Workflow Test Agent');
        await page.fill('#agentRole', 'Workflow Tester');
        await page.fill('#agentPersonality', 'systematic');
        await page.fill('#agentExpectations', 'Test workflow updates');
        await page.click('button:text("Create")');
        
        // Select the agent
        await page.click('text=Workflow Test Agent');
        
        // Send a message that should trigger workflow creation
        await page.fill('#messageInput', 'Create a workflow to send a test email');
        await page.click('#sendButton');
        
        // Verify workflow preview appears and updates
        await expect(page.locator('#workflowPreview')).not.toHaveClass(/hidden/);
        await expect(page.locator('#workflowContent')).toContainText(/node|step|email/i);
    });
});
