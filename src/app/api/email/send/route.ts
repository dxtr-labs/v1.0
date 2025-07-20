// Simple email-only API endpoint for testing
import { NextRequest, NextResponse } from 'next/server';
import { executeEmailWorkflow } from '../../../../../lib/email-executor.js';
import { mockEmailExecutor } from '../../../../../lib/mock-email-executor.js';

interface EmailRequest {
  to: string;
  subject: string;
  content: string;
  type?: string;
  images?: string[];
  useMock?: boolean; // Force mock mode for testing
}

export async function POST(request: NextRequest) {
  console.log('📧 [EMAIL API] Request received');
  
  try {
    console.log('📧 [EMAIL API] Parsing request body...');
    const body = await request.json() as EmailRequest;
    const { to, subject, content, type, images, useMock } = body;
    
    console.log('📧 [EMAIL API] Request parsed successfully');
    console.log(`📧 [EMAIL API] To: ${to}`);
    console.log(`📧 [EMAIL API] Subject: ${subject}`);
    console.log(`📧 [EMAIL API] Content length: ${content?.length || 0}`);
    console.log(`📧 [EMAIL API] Images: ${images?.length || 0}`);
    console.log(`📧 [EMAIL API] UseMock: ${useMock}`);
    
    if (!to || !subject || !content) {
      console.log('📧 [EMAIL API] Missing required fields');
      return NextResponse.json({
        success: false,
        error: 'Missing required fields: to, subject, content'
      }, { status: 400 });
    }

    console.log(`📧 Testing email send to: ${to}`);
    console.log(`📧 Subject: ${subject}`);
    console.log(`📧 Content: ${content.substring(0, 50)}...`);
    console.log(`📧 Type: ${type || 'general'}`);
    console.log(`📧 Images: ${images?.length || 0}`);

    // Create HTML content with images
    let htmlContent = content.replace(/\n/g, '<br>');
    
    if (images && images.length > 0) {
      console.log('🖼️  Adding images to email...');
      const imageHtml = images.map((imageUrl, index) => 
        `<div style="margin: 20px 0;"><img src="${imageUrl}" alt="Arizona Image ${index + 1}" style="max-width: 100%; height: auto; border-radius: 8px;" /></div>`
      ).join('');
      
      htmlContent = `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <div style="white-space: pre-line;">${htmlContent}</div>
          <div style="margin-top: 30px;">
            <h3 style="color: #2C5530;">📸 Images from Arizona:</h3>
            ${imageHtml}
          </div>
        </div>
      `;
    } else {
      htmlContent = `<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; white-space: pre-line;">${htmlContent}</div>`;
    }

    // Use real email unless explicitly set to mock or forced by request
    const useMockEmail = useMock || process.env.USE_MOCK_EMAIL === 'true';
    
    console.log(`📧 [EMAIL API] Using ${useMockEmail ? 'mock' : 'real'} email service`);
    
    // Skip connection test for faster response - send email directly
    console.log('📧 [EMAIL API] Starting email send process...');
    
    try {
      // Add timeout to email sending
      console.log('📧 [EMAIL API] Creating email promise with timeout...');
      
      const emailData = {
        recipient: to,
        subject,
        content: htmlContent,
        from: process.env.FROM_EMAIL || 'noreply@example.com'
      };
      
      const emailPromise = useMockEmail 
        ? mockEmailExecutor.send(emailData)
        : executeEmailWorkflow({
            name: 'Direct Email Send',
            nodes: [{
              type: 'email',
              data: emailData
            }]
          }, { email: process.env.FROM_EMAIL || 'noreply@example.com' });

      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Email send timeout after 20 seconds')), 20000);
      });

      console.log('📧 [EMAIL API] Waiting for email result...');
      const result = await Promise.race([emailPromise, timeoutPromise]) as { success: boolean; messageId?: string; error?: string };
      console.log('📧 [EMAIL API] Email result received:', result.success);

      if (result.success) {
        console.log('✅ [EMAIL API] Email sent successfully!', result.messageId);
        return NextResponse.json({
          success: true,
          message: `Email sent successfully to ${to}`,
          messageId: result.messageId,
          recipientCount: 1,
          imagesIncluded: images?.length || 0
        });
      } else {
        console.error('❌ [EMAIL API] Email sending failed:', result.error);
        return NextResponse.json({
          success: false,
          error: `Email sending failed: ${result.error}`,
          details: 'Check your email configuration and credentials'
        }, { status: 500 });
      }
    } catch (error) {
      console.error('❌ [EMAIL API] Email process error:', error);
      return NextResponse.json({
        success: false,
        error: `Email process error: ${error instanceof Error ? error.message : 'Unknown error'}`
      }, { status: 500 });
    }

  } catch (error) {
    console.error('❌ Email API error:', error);
    return NextResponse.json({
      success: false,
      error: `Email API error: ${error instanceof Error ? error.message : 'Unknown error'}`
    }, { status: 500 });
  }
}
