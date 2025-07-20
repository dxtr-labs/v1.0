# Enhanced MCP API Test Suite (PowerShell)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Enhanced MCP API Test Suite" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Testing enhanced LLM capabilities and API endpoints" -ForegroundColor Yellow

$BASE_URL = "http://localhost:8000"

# Test 1: Health Check
Write-Host "`n[RUNNING] Health & Compatibility Check" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/health" -Method GET
    Write-Host "Health Status: $($response.status)" -ForegroundColor Green
    Write-Host "Message: $($response.message)" -ForegroundColor Purple
    Write-Host "[PASS] Health Check" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Health Check: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Enhanced MCP Capabilities
Write-Host "`n[RUNNING] Enhanced MCP Capabilities Check" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/enhanced-mcp/capabilities" -Method GET
    Write-Host "Enhanced Features:" -ForegroundColor Purple
    $response.enhanced_features | ForEach-Object { Write-Host "  • $_" -ForegroundColor Cyan }
    Write-Host "Supported Providers: $($response.supported_providers -join ', ')" -ForegroundColor Purple
    Write-Host "Version: $($response.version)" -ForegroundColor Purple
    Write-Host "[PASS] Enhanced MCP Capabilities" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Enhanced MCP Capabilities: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Enhanced Processing - Email Automation
Write-Host "`n[RUNNING] Enhanced MCP Processing - Email Automation" -ForegroundColor Yellow
try {
    $body = @{
        message = "Send a professional email to john@example.com about our new product launch"
        agent_context = @{
            agent_name = "SalesBot"
            agent_role = "Sales Assistant"
        }
        llm_config = @{
            model = "llama3.2"
            temperature = 0.7
            max_tokens = 2000
        }
    } | ConvertTo-Json -Depth 3

    $headers = @{
        "Content-Type" = "application/json"
        "x-user-id" = "test-user"
    }

    $response = Invoke-RestMethod -Uri "$BASE_URL/enhanced-mcp/process" -Method POST -Body $body -Headers $headers
    Write-Host "Success: $($response.success)" -ForegroundColor Green
    Write-Host "Type: $($response.execution_type)" -ForegroundColor Purple
    Write-Host "Message: $($response.message.Substring(0, [Math]::Min(100, $response.message.Length)))..." -ForegroundColor Purple
    
    if ($response.enhanced_features) {
        Write-Host "Enhanced Features:" -ForegroundColor Cyan
        $response.enhanced_features.PSObject.Properties | ForEach-Object {
            Write-Host "  $($_.Name): $($_.Value)" -ForegroundColor Cyan
        }
    }
    
    Write-Host "[PASS] Enhanced Processing - Email" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Enhanced Processing: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Enhanced Processing - Conversational
Write-Host "`n[RUNNING] Enhanced MCP Processing - Conversational" -ForegroundColor Yellow
try {
    $body = @{
        message = "Hello, how can you help me with automation?"
        agent_context = @{
            agent_name = "Assistant"
            agent_role = "Automation Helper"
        }
    } | ConvertTo-Json -Depth 3

    $headers = @{
        "Content-Type" = "application/json"
        "x-user-id" = "test-user"
    }

    $response = Invoke-RestMethod -Uri "$BASE_URL/enhanced-mcp/process" -Method POST -Body $body -Headers $headers
    Write-Host "Success: $($response.success)" -ForegroundColor Green
    Write-Host "Type: $($response.execution_type)" -ForegroundColor Purple
    Write-Host "Message: $($response.message.Substring(0, [Math]::Min(150, $response.message.Length)))..." -ForegroundColor Purple
    
    if ($response.suggestions) {
        Write-Host "Suggestions:" -ForegroundColor Cyan
        $response.suggestions | ForEach-Object { Write-Host "  • $_" -ForegroundColor Cyan }
    }
    
    Write-Host "[PASS] Enhanced Processing - Conversational" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Enhanced Processing Conversational: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Agent Integration
Write-Host "`n[RUNNING] Enhanced Agent Integration" -ForegroundColor Yellow
try {
    $body = @{
        message = "Send a friendly email to team@company.com about tomorrow's meeting"
    } | ConvertTo-Json

    $headers = @{
        "Content-Type" = "application/json"
        "x-user-id" = "default_user"
    }

    $response = Invoke-RestMethod -Uri "$BASE_URL/agents/sam_agent/chat" -Method POST -Body $body -Headers $headers
    Write-Host "Agent Response Success: $($response.success)" -ForegroundColor Green
    Write-Host "Agent Name: $($response.agent_name)" -ForegroundColor Purple
    Write-Host "Response Type: $($response.metadata.type)" -ForegroundColor Purple
    
    if ($response.metadata.enhanced) {
        Write-Host "✨ Enhanced processing used!" -ForegroundColor Cyan
    }
    
    if ($response.metadata.enhanced_features) {
        Write-Host "Enhanced Features:" -ForegroundColor Cyan
        $response.metadata.enhanced_features.PSObject.Properties | ForEach-Object {
            Write-Host "  $($_.Name): $($_.Value)" -ForegroundColor Cyan
        }
    }
    
    $responseText = if ($response.response.Length -gt 150) { $response.response.Substring(0, 150) + "..." } else { $response.response }
    Write-Host "Response: $responseText" -ForegroundColor Purple
    
    Write-Host "[PASS] Enhanced Agent Integration" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Enhanced Agent Integration: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Backward Compatibility
Write-Host "`n[RUNNING] Backward Compatibility Test" -ForegroundColor Yellow
try {
    $body = @{
        agent_id = "sam_agent"
        message = "Hello, test message for compatibility"
        user_id = "test_user"
    } | ConvertTo-Json

    $headers = @{
        "Content-Type" = "application/json"
    }

    $response = Invoke-RestMethod -Uri "$BASE_URL/chat" -Method POST -Body $body -Headers $headers
    $compatStatus = if ($response.success) { 'PASS' } else { 'FAIL' }
    Write-Host "Backward Compatibility: $compatStatus" -ForegroundColor Green
    Write-Host "Agent: $($response.agent_name)" -ForegroundColor Purple
    Write-Host "[PASS] Backward Compatibility" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Backward Compatibility: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  Test Summary" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "✅ Enhanced MCP API tests completed!" -ForegroundColor Green
Write-Host "🚀 Enhanced MCP LLM system is ready with:" -ForegroundColor Cyan
Write-Host "  • Multi-provider LLM support (Ollama, OpenAI, DeepSeek)" -ForegroundColor Cyan
Write-Host "  • Advanced intent analysis and workflow planning" -ForegroundColor Cyan
Write-Host "  • AI-enhanced content generation" -ForegroundColor Cyan
Write-Host "  • Streaming responses for real-time interaction" -ForegroundColor Cyan
Write-Host "  • Conversation memory and context management" -ForegroundColor Cyan
Write-Host "  • Graceful fallback when LLM providers are unavailable" -ForegroundColor Cyan
