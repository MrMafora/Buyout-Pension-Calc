const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: "new",
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  
  try {
    console.log('Navigating to login...');
    await page.goto('https://twitter.com/i/flow/login', { waitUntil: 'networkidle2' });
    
    console.log('Waiting for username input...');
    await page.waitForSelector('input[autocomplete="username"]');
    await page.type('input[autocomplete="username"]', 'fedbuyout@gmail.com');
    await page.keyboard.press('Enter');
    
    // Handle potential "Verify your identity" step (enter username/phone)
    try {
        // Wait briefly to see if password field appears or intermediate step
        await new Promise(r => setTimeout(r, 2000));
        
        const passwordInput = await page.$('input[name="password"]');
        if (!passwordInput) {
            console.log('Password field not immediately visible. Checking for verification...');
            const verificationInput = await page.$('input[data-testid="ocfEnterTextTextInput"]');
            if (verificationInput) {
                console.log('Verification step detected. Entering handle @FedBuyOut...');
                await verificationInput.type('@FedBuyOut');
                await page.keyboard.press('Enter');
                // Wait for password field again
                await page.waitForSelector('input[name="password"]');
            }
        }
    } catch (e) {
        console.log('Navigation flow check failed:', e);
    }
    
    console.log('Entering password...');
    await page.waitForSelector('input[name="password"]');
    await page.type('input[name="password"]', '@G0its30n3m');
    await page.keyboard.press('Enter');
    
    console.log('Waiting for login to complete...');
    try {
        await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 });
    } catch (e) {
        console.log('Navigation timeout (might be okay if SPA loaded)');
    }
    
    const cookies = await page.cookies();
    const authToken = cookies.find(c => c.name === 'auth_token');
    const ct0 = cookies.find(c => c.name === 'ct0');
    
    if (authToken && ct0) {
        console.log('SUCCESS: Login successful!');
        console.log(`auth_token=${authToken.value}`);
        console.log(`ct0=${ct0.value}`);
    } else {
        console.log('FAILED: Could not find auth cookies.');
        await page.screenshot({ path: 'login_fail.png' });
        console.log('Screenshot saved to login_fail.png');
        
        // Check for 2FA input
        const twoFa = await page.$('input[data-testid="ocfEnterTextTextInput"]');
        if (twoFa) {
            console.log('2FA DETECTED! Please check email for code.');
        }
    }
    
  } catch (error) {
    console.error('Error:', error);
    await page.screenshot({ path: 'error.png' });
  } finally {
    await browser.close();
  }
})();
