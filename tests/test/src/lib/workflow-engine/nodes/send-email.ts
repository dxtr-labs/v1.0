
import { NodeType } from '../types';

export const sendEmailNode: NodeType = {
  name: 'send-email',
  label: 'Send Email',
  description: 'Sends an email using a pre-configured service.',
  parameters: [
    { name: 'to', label: 'Recipient', type: 'string', required: true },
    { name: 'subject', label: 'Subject', type: 'string', required: true },
    { name: 'body', label: 'Body', type: 'string', required: true },
  ],
  async execute(params) {
    console.log('Executing send-email node with params:', params);
    // In a real implementation, this would use an email service like SendGrid or Nodemailer
    // For now, we'll just simulate success.
    return { success: true, message: `Email sent to ${params.to}` };
  },
};
