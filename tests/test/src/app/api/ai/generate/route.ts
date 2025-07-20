// src/app/api/ai/generate/route.ts
// AI content generation endpoint with DeepSeek local support

import { NextRequest, NextResponse } from 'next/server';
import { generateWithDeepSeek } from '@/lib/local-ai/deepseek-local';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { prompt, type = 'general', parameters = {} } = body as {
      prompt?: string;
      type?: string;
      parameters?: Record<string, any>;
    };

    if (!prompt) {
      return NextResponse.json(
        { success: false, error: 'Prompt is required' },
        { status: 400 }
      );
    }

    console.log('🤖 [AI Generate] Processing request:', { type, prompt: prompt.substring(0, 100) + '...', parameters });

    // Intelligently analyze the prompt to determine content type and location
    const promptLower = prompt.toLowerCase();
    let enhancedPrompt = prompt;
    let maxTokens = 200;
    let detectedLocation = 'general';
    let detectedType = type;

    // Detect location from prompt
    if (promptLower.includes('arizona')) {
      detectedLocation = 'arizona';
    } else if (promptLower.includes('california') || promptLower.includes('ca ')) {
      detectedLocation = 'california';
    } else if (promptLower.includes('texas') || promptLower.includes('tx ')) {
      detectedLocation = 'texas';
    } else if (promptLower.includes('new york') || promptLower.includes('ny ')) {
      detectedLocation = 'new york';
    } else if (promptLower.includes('florida') || promptLower.includes('fl ')) {
      detectedLocation = 'florida';
    } else if (parameters?.location) {
      detectedLocation = parameters.location.toLowerCase();
    }

    // Detect content type from prompt
    if (promptLower.includes('newsletter') || promptLower.includes('weekly') || promptLower.includes('news update')) {
      detectedType = 'newsletter';
    } else if (promptLower.includes('email') || promptLower.includes('message')) {
      detectedType = 'email';
    } else if (promptLower.includes('news') || promptLower.includes('article')) {
      detectedType = 'news';
    } else if (promptLower.includes('story') || promptLower.includes('blog')) {
      detectedType = 'blog';
    }

    console.log('🔍 [AI Generate] Detected:', { type: detectedType, location: detectedLocation });

    // Create intelligent enhanced prompt based on detection - but stay true to user's request
    if (detectedType === 'newsletter') {
      if (detectedLocation === 'arizona') {
        enhancedPrompt = `Write a professional newsletter about Arizona based on this specific request: "${prompt}"

Include relevant Arizona content such as:
- Current news and events in Arizona
- Weather highlights
- Local business updates  
- Community events
- Tourism recommendations

Make sure to address the specific request: ${prompt}

Newsletter Content:`;
      } else if (detectedLocation !== 'general') {
        enhancedPrompt = `Write a professional newsletter about ${detectedLocation} based on this specific request: "${prompt}"

Include relevant ${detectedLocation} content and make sure to address the user's specific request.

Newsletter Content:`;
      } else {
        enhancedPrompt = `Write a professional newsletter based on this specific request: "${prompt}"

Create content that directly addresses what the user is asking for. Include relevant information, updates, and recommendations related to their request.

Newsletter Content:`;
      }
      maxTokens = 500;
    } else if (detectedType === 'email') {
      enhancedPrompt = `Write a professional email based on this specific request: "${prompt}"

Create personalized content that directly addresses what the user is asking for.

Email:`;
      maxTokens = 300;
    } else if (detectedType === 'news') {
      if (detectedLocation !== 'general') {
        enhancedPrompt = `Write a news article about ${detectedLocation} based on this specific request: "${prompt}"

Focus on what the user is actually asking for while including relevant local information.

Article:`;
      } else {
        enhancedPrompt = `Write a news article based on this specific request: "${prompt}"

Create content that directly addresses the user's request with relevant current information.

Article:`;
      }
      maxTokens = 400;
    } else if (detectedType === 'blog') {
      enhancedPrompt = `Write a blog post based on this specific request: "${prompt}"

Create engaging content that directly addresses what the user is asking for, with useful information and insights.

Blog Post:`;
      maxTokens = 450;
    } else {
      enhancedPrompt = `Create content based on this specific request: "${prompt}"

Provide helpful, relevant, and well-structured information that directly addresses what the user is asking for.

Content:`;
      maxTokens = 350;
    }

    // Try to generate with local DeepSeek first
    const aiResult = await generateWithDeepSeek(enhancedPrompt, {
      maxTokens,
      temperature: 0.8,
      modelName: 'deepseek-chat'
    });

    let generatedContent = '';
    let usedFallback = false;

    if (aiResult.success && aiResult.text) {
      generatedContent = aiResult.text;
    } else {
      // Intelligent fallback content based on detected type and location
      usedFallback = true;
      console.log('🔄 [AI Generate] Using intelligent fallback content');
      
      if (detectedType === 'newsletter') {
        if (detectedLocation === 'arizona') {
          generatedContent = generateArizonaNewsletterContent(parameters);
        } else {
          generatedContent = generateGeneralNewsletterContent(prompt, detectedLocation, parameters);
        }
      } else if (detectedType === 'news') {
        generatedContent = generateNewsContent(prompt, detectedLocation, parameters);
      } else if (detectedType === 'email') {
        generatedContent = generateEmailContent(prompt, parameters);
      } else if (detectedType === 'blog') {
        generatedContent = generateBlogContent(prompt, parameters);
      } else {
        generatedContent = generateGeneralContent(prompt, parameters);
      }
    }

    // Add images based on detected location and type
    let images: string[] = [];
    if (detectedType === 'newsletter' || detectedType === 'news') {
      if (detectedLocation === 'arizona') {
        images = getArizonaNewsletterImages();
      } else {
        images = getGeneralImages(detectedLocation);
      }
    }

    return NextResponse.json({
      success: true,
      content: generatedContent,
      images,
      metadata: {
        type,
        usedFallback,
        timestamp: new Date().toISOString(),
        wordCount: generatedContent.split(' ').length
      }
    });

  } catch (error) {
    console.error('❌ [AI Generate] Error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'AI generation failed' 
      },
      { status: 500 }
    );
  }
}

function generateArizonaNewsletterContent(parameters: any): string {
  const currentDate = new Date().toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });

  return `🌵 ARIZONA WEEKLY NEWSLETTER
${currentDate}

📰 TOP ARIZONA NEWS
• Phoenix Metro continues to see growth in tech sector with new startups establishing headquarters
• Arizona State University announces breakthrough research in sustainable desert agriculture
• Grand Canyon National Park reports record visitor numbers this season
• New solar energy projects approved across Maricopa County

🌡️ WEATHER HIGHLIGHTS
• Temperatures ranging from 75-85°F this week
• Clear skies perfect for outdoor activities
• Low humidity ideal for hiking and exploration

🏢 BUSINESS UPDATES
• Local restaurants in Scottsdale introducing new seasonal menus
• Arizona-based companies expanding operations
• Small business grant programs now available through the state

🎉 COMMUNITY EVENTS
• Farmers markets open across Phoenix Metro area
• Art festivals scheduled in Tucson and Flagstaff
• Desert botanical garden hosting special exhibitions
• Local hiking groups organizing weekend adventures

🏜️ TOURISM RECOMMENDATIONS
• Antelope Canyon tours now accepting spring reservations
• Sedona red rock formations offering spectacular sunrise views
• Historic Route 66 attractions hosting vintage car shows
• Desert museums featuring new Native American art collections

Stay connected with Arizona's vibrant community and natural beauty!

---
For more updates, visit local Arizona news sources and community boards.`;
}

function generateArizonaNewsContent(parameters: any): string {
  return `🌵 ARIZONA NEWS UPDATE

PHOENIX - Arizona continues to experience significant growth and development across multiple sectors. The state's unique blend of natural beauty, growing economy, and strong communities makes it a focal point for both residents and visitors.

Recent developments include:

🏢 ECONOMIC GROWTH
The Phoenix metropolitan area has seen an influx of technology companies choosing Arizona as their base of operations. This growth is driving job creation and attracting young professionals to the region.

🌱 ENVIRONMENTAL INITIATIVES
Arizona State University researchers are making strides in desert sustainability, developing new methods for water conservation and renewable energy utilization that could serve as models for other arid regions.

🏜️ TOURISM BOOM
Arizona's natural attractions continue to draw visitors from around the world. The Grand Canyon, Sedona's red rocks, and the Sonoran Desert provide unique experiences that showcase the state's geological diversity.

🎭 CULTURAL DEVELOPMENTS
Local communities are celebrating Arizona's rich cultural heritage through various festivals and events, highlighting both Native American traditions and modern artistic expressions.

The state's commitment to balancing growth with environmental stewardship positions Arizona as a leader in sustainable development practices.

For ongoing updates about Arizona news, community events, and opportunities, stay connected with local news sources and community organizations.`;
}

function getArizonaNewsletterImages(): string[] {
  return [
    'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&h=400&fit=crop&q=80', // Grand Canyon
    'https://images.unsplash.com/photo-1539650116574-75c0c6d73f6e?w=600&h=400&fit=crop&q=80', // Sedona red rocks
    'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=600&h=400&fit=crop&q=80', // Desert landscape
    'https://images.unsplash.com/photo-1544966503-7cc5ac882d5d?w=600&h=400&fit=crop&q=80', // Arizona sunset
  ];
}

function generateGeneralNewsletterContent(prompt: string, location: string, parameters: any): string {
  const currentDate = new Date().toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });

  const locationTitle = location !== 'general' ? location.toUpperCase() : 'WEEKLY';
  
  return `📰 ${locationTitle} NEWSLETTER
${currentDate}

📋 CONTENT HIGHLIGHTS
Based on your request: "${prompt}"

📈 KEY UPDATES
• Current developments and trending topics
• Local community news and events
• Business updates and opportunities
• Upcoming activities and recommendations

🌟 FEATURED CONTENT
This newsletter addresses your specific request about ${prompt.toLowerCase()}. We've compiled relevant information, insights, and updates to keep you informed about the topics that matter most to you.

📅 UPCOMING EVENTS
• Community gatherings and networking opportunities
• Educational workshops and seminars
• Cultural events and entertainment
• Outdoor activities and seasonal highlights

🔗 STAY CONNECTED
Thank you for reading! We're committed to bringing you relevant content based on your interests and needs.

Generated based on: ${prompt}`;
}

function generateNewsContent(prompt: string, location: string, parameters: any): string {
  const locationPrefix = location !== 'general' ? `${location.toUpperCase()} - ` : '';
  
  return `📰 ${locationPrefix}NEWS UPDATE

🔥 BREAKING: ${prompt}

📋 STORY DETAILS
This developing story covers important aspects of ${prompt.toLowerCase()}. Our coverage includes the latest updates, expert insights, and community impact analysis.

📊 KEY POINTS
• Current situation and background information
• Community response and stakeholder reactions
• Expert analysis and future implications
• Resources and next steps for those affected

🎯 IMPACT ANALYSIS
The developments related to ${prompt.toLowerCase()} have significant implications for the local community and broader region. We continue to monitor the situation and provide updates as they become available.

📞 FOR MORE INFORMATION
Stay tuned for continued coverage of this developing story.

Story focus: ${prompt}`;
}

function generateEmailContent(prompt: string, parameters: any): string {
  return `Subject: Re: ${prompt}

Dear Recipient,

I hope this email finds you well. I'm writing to address your request regarding: ${prompt}

📋 DETAILS
Based on your inquiry, I've prepared the following information to help address your needs and provide the assistance you're looking for.

🎯 KEY INFORMATION
• Relevant details about your request
• Helpful resources and recommendations
• Next steps and action items
• Contact information for follow-up

📞 NEXT STEPS
Please don't hesitate to reach out if you need any additional information or clarification regarding ${prompt.toLowerCase()}.

Best regards,
[Your Name]

Generated in response to: ${prompt}`;
}

function generateBlogContent(prompt: string, parameters: any): string {
  return `📝 BLOG POST: ${prompt}

✨ INTRODUCTION
Welcome to our latest blog post exploring ${prompt.toLowerCase()}. In this article, we'll dive deep into this fascinating topic and provide you with valuable insights and practical information.

🔍 MAIN CONTENT
${prompt} is an important topic that deserves careful consideration and analysis. Here's what you need to know:

• Background and context
• Current trends and developments
• Expert perspectives and insights
• Practical applications and benefits
• Tips and recommendations for implementation

💡 KEY TAKEAWAYS
Understanding ${prompt.toLowerCase()} can help you make more informed decisions and achieve better outcomes in your personal or professional endeavors.

🎯 CONCLUSION
We hope this blog post has provided valuable insights into ${prompt.toLowerCase()}. Stay tuned for more content on related topics!

Blog topic: ${prompt}`;
}

function generateGeneralContent(prompt: string, parameters: any): string {
  return `📄 CONTENT: ${prompt}

🎯 OVERVIEW
This content has been generated based on your request: "${prompt}"

📋 MAIN INFORMATION
Here's comprehensive information addressing your request:

• Relevant background and context
• Key points and important details
• Practical insights and recommendations
• Useful resources and next steps

✅ SUMMARY
This content aims to provide helpful information related to ${prompt.toLowerCase()}. The information has been tailored to address your specific needs and interests.

🔗 ADDITIONAL RESOURCES
For more detailed information, please consider exploring additional resources or reaching out with specific questions.

Generated for: ${prompt}`;
}

function getGeneralImages(location: string): string[] {
  // Return generic placeholder images for different locations
  const images = [
    'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=500&h=300&fit=crop',
    'https://images.unsplash.com/photo-1477414348463-c0eb7f1359b6?w=500&h=300&fit=crop',
    'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=500&h=300&fit=crop',
    'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=500&h=300&fit=crop'
  ];
  
  return images;
}

export async function GET() {
  return NextResponse.json({
    message: 'AI Generate endpoint is running',
    status: 'active',
    capabilities: ['newsletter', 'email', 'news', 'general'],
    timestamp: new Date().toISOString()
  });
}
