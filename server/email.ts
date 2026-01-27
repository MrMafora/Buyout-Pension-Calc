import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY_FED_BUY_OUT);

const FROM_EMAIL = 'FedBuyout <noreply@fedbuyout.com>';
const SUPPORT_EMAILS = ['support@fedbuyout.com', 'mmafora@gmail.com'];

export async function sendContactFormEmail(data: {
  name: string;
  email: string;
  subject: string;
  message: string;
}) {
  try {
    const result = await resend.emails.send({
      from: FROM_EMAIL,
      to: SUPPORT_EMAILS,
      replyTo: data.email,
      subject: `[Contact Form] ${data.subject}`,
      html: `
        <h2>New Contact Form Submission</h2>
        <p><strong>From:</strong> ${data.name} &lt;${data.email}&gt;</p>
        <p><strong>Subject:</strong> ${data.subject}</p>
        <hr>
        <p><strong>Message:</strong></p>
        <p>${data.message.replace(/\n/g, '<br>')}</p>
      `,
    });
    
    console.log('Contact form email sent:', result);
    return { success: true, id: result.data?.id };
  } catch (error) {
    console.error('Failed to send contact form email:', error);
    return { success: false, error };
  }
}

export async function sendWelcomeEmail(email: string) {
  try {
    const result = await resend.emails.send({
      from: FROM_EMAIL,
      to: email,
      subject: 'Welcome to FedBuyout Updates!',
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h1 style="color: #1e3a5f;">Welcome to FedBuyout!</h1>
          <p>Thanks for subscribing to our newsletter. You'll receive updates on:</p>
          <ul>
            <li>Federal buyout news and announcements</li>
            <li>Changes to FERS/CSRS retirement benefits</li>
            <li>Calculator updates and new features</li>
            <li>Tips for evaluating your retirement options</li>
          </ul>
          <p>Have questions? Reply to this email or visit our <a href="https://fedbuyout.com/contact">contact page</a>.</p>
          <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
          <p style="color: #666; font-size: 12px;">
            You're receiving this because you subscribed at fedbuyout.com.
            <br>To unsubscribe, reply with "unsubscribe" in the subject.
          </p>
        </div>
      `,
    });
    
    console.log('Welcome email sent to:', email, result);
    return { success: true, id: result.data?.id };
  } catch (error) {
    console.error('Failed to send welcome email:', error);
    return { success: false, error };
  }
}

export async function sendDailyAnalyticsEmail(data: {
  totalSubscribers: number;
  newSubscribersToday: number;
  totalLeads: number;
  newLeadsToday: number;
  recentSubscribers: Array<{ email: string; source: string; createdAt: Date | null }>;
  recentLeads: Array<{ name: string; email: string; retirementSystem: string | null; createdAt: Date | null }>;
}) {
  const today = new Date().toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });

  try {
    const result = await resend.emails.send({
      from: FROM_EMAIL,
      to: SUPPORT_EMAILS,
      subject: `[Daily Report] FedBuyout Analytics - ${today}`,
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h1 style="color: #1e3a5f;">Daily Analytics Report</h1>
          <p style="color: #666;">${today}</p>
          
          <h2 style="margin-top: 24px; border-bottom: 2px solid #1e3a5f; padding-bottom: 8px;">Summary</h2>
          <table style="width: 100%; border-collapse: collapse; margin-top: 16px;">
            <tr>
              <td style="padding: 12px; background: #f8f9fa; border-radius: 8px; text-align: center; width: 25%;">
                <div style="font-size: 28px; font-weight: bold; color: #1e3a5f;">${data.totalSubscribers}</div>
                <div style="font-size: 12px; color: #666;">Total Subscribers</div>
              </td>
              <td style="padding: 12px; background: #f8f9fa; border-radius: 8px; text-align: center; width: 25%;">
                <div style="font-size: 28px; font-weight: bold; color: #22c55e;">+${data.newSubscribersToday}</div>
                <div style="font-size: 12px; color: #666;">New Today</div>
              </td>
              <td style="padding: 12px; background: #f8f9fa; border-radius: 8px; text-align: center; width: 25%;">
                <div style="font-size: 28px; font-weight: bold; color: #1e3a5f;">${data.totalLeads}</div>
                <div style="font-size: 12px; color: #666;">Total Leads</div>
              </td>
              <td style="padding: 12px; background: #f8f9fa; border-radius: 8px; text-align: center; width: 25%;">
                <div style="font-size: 28px; font-weight: bold; color: #22c55e;">+${data.newLeadsToday}</div>
                <div style="font-size: 12px; color: #666;">New Today</div>
              </td>
            </tr>
          </table>

          ${data.recentSubscribers.length > 0 ? `
            <h2 style="margin-top: 24px; border-bottom: 2px solid #1e3a5f; padding-bottom: 8px;">New Subscribers Today</h2>
            <table style="width: 100%; border-collapse: collapse; margin-top: 16px;">
              <tr style="background: #f8f9fa;">
                <th style="padding: 8px; text-align: left;">Email</th>
                <th style="padding: 8px; text-align: left;">Source</th>
              </tr>
              ${data.recentSubscribers.map(sub => `
                <tr style="border-bottom: 1px solid #eee;">
                  <td style="padding: 8px;">${sub.email}</td>
                  <td style="padding: 8px;">${sub.source}</td>
                </tr>
              `).join('')}
            </table>
          ` : '<p style="color: #666; margin-top: 24px;">No new subscribers today.</p>'}

          ${data.recentLeads.length > 0 ? `
            <h2 style="margin-top: 24px; border-bottom: 2px solid #1e3a5f; padding-bottom: 8px;">New Leads Today</h2>
            <table style="width: 100%; border-collapse: collapse; margin-top: 16px;">
              <tr style="background: #f8f9fa;">
                <th style="padding: 8px; text-align: left;">Name</th>
                <th style="padding: 8px; text-align: left;">Email</th>
                <th style="padding: 8px; text-align: left;">System</th>
              </tr>
              ${data.recentLeads.map(lead => `
                <tr style="border-bottom: 1px solid #eee;">
                  <td style="padding: 8px;">${lead.name}</td>
                  <td style="padding: 8px;">${lead.email}</td>
                  <td style="padding: 8px;">${lead.retirementSystem?.toUpperCase() || '—'}</td>
                </tr>
              `).join('')}
            </table>
          ` : '<p style="color: #666; margin-top: 24px;">No new leads today.</p>'}

          <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
          <p style="color: #666; font-size: 12px; text-align: center;">
            FedBuyout Daily Analytics Report<br>
            <a href="https://fedbuyout.com/admin" style="color: #1e3a5f;">View Full Dashboard</a>
          </p>
        </div>
      `,
    });
    
    console.log('Daily analytics email sent:', result);
    return { success: true, id: result.data?.id };
  } catch (error) {
    console.error('Failed to send daily analytics email:', error);
    return { success: false, error };
  }
}

export async function sendLeadNotificationEmail(data: {
  name: string;
  email: string;
  phone?: string;
  salary: number;
  yearsOfService: number;
  age: number;
  retirementSystem: string;
  monthlyPension: number;
  netBuyout: number;
  breakEvenYears: number;
}) {
  try {
    const result = await resend.emails.send({
      from: FROM_EMAIL,
      to: SUPPORT_EMAILS,
      subject: `[New Lead] ${data.name} - ${data.retirementSystem.toUpperCase()}`,
      html: `
        <h2>New Lead Captured</h2>
        <p><strong>Name:</strong> ${data.name}</p>
        <p><strong>Email:</strong> ${data.email}</p>
        <p><strong>Phone:</strong> ${data.phone || 'Not provided'}</p>
        <hr>
        <h3>Calculator Results</h3>
        <table style="border-collapse: collapse;">
          <tr><td style="padding: 4px 8px;"><strong>Salary:</strong></td><td>$${data.salary.toLocaleString()}</td></tr>
          <tr><td style="padding: 4px 8px;"><strong>Years of Service:</strong></td><td>${data.yearsOfService}</td></tr>
          <tr><td style="padding: 4px 8px;"><strong>Age:</strong></td><td>${data.age}</td></tr>
          <tr><td style="padding: 4px 8px;"><strong>System:</strong></td><td>${data.retirementSystem}</td></tr>
          <tr><td style="padding: 4px 8px;"><strong>Monthly Pension:</strong></td><td>$${data.monthlyPension.toLocaleString()}</td></tr>
          <tr><td style="padding: 4px 8px;"><strong>Net Buyout:</strong></td><td>$${data.netBuyout.toLocaleString()}</td></tr>
          <tr><td style="padding: 4px 8px;"><strong>Break-even:</strong></td><td>${data.breakEvenYears} years</td></tr>
        </table>
      `,
    });
    
    console.log('Lead notification email sent:', result);
    return { success: true, id: result.data?.id };
  } catch (error) {
    console.error('Failed to send lead notification email:', error);
    return { success: false, error };
  }
}
