#!/usr/bin/env python3
"""
Google Analytics 4 Setup Automation
Uses Playwright to create GA4 account for FedBuyOut
"""

import asyncio
from playwright.async_api import async_playwright

async def setup_ga4():
    async with async_playwright() as p:
        # Launch browser in headless mode
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Step 1: Navigate to Google Analytics
            print("Navigating to Google Analytics...")
            await page.goto("https://analytics.google.com/")
            
            # Step 2: Sign in
            print("Signing in...")
            await page.fill('input[type="email"]', "fedbuyout@gmail.com")
            await page.click('button:has-text("Next")')
            
            await asyncio.sleep(2)
            
            await page.fill('input[type="password"]', "G0its30n3m")
            await page.click('button:has-text("Next")')
            
            await asyncio.sleep(5)
            
            # Check if we need to handle 2FA or other screens
            if await page.is_visible('text=Welcome to Google Analytics'):
                print("Clicking 'Start measuring'...")
                await page.click('text=Start measuring')
            
            await asyncio.sleep(3)
            
            # Step 3: Create Account
            print("Creating account...")
            if await page.is_visible('input[placeholder="Account name"]'):
                await page.fill('input[placeholder="Account name"]', "FedBuyOut")
                await page.click('button:has-text("Next")')
            
            await asyncio.sleep(2)
            
            # Step 4: Create Property
            print("Creating property...")
            if await page.is_visible('input[placeholder="Property name"]'):
                await page.fill('input[placeholder="Property name"]', "FedBuyOut.com")
                
                # Set timezone
                await page.click('text=Time zone')
                await page.click('text=(GMT-05:00) Eastern Time')
                
                # Set currency
                await page.click('text=Currency')
                await page.click('text=US Dollar ($)')
                
                await page.click('button:has-text("Next")')
            
            await asyncio.sleep(2)
            
            # Step 5: Business information
            print("Setting business info...")
            # Select industry
            await page.click('text=Industry category')
            await page.click('text=Finance')  # or Jobs & Education
            
            # Business size
            await page.click('text=Business size')
            await page.click('text=Small')  # 1-10 employees
            
            await page.click('button:has-text("Next")')
            
            await asyncio.sleep(2)
            
            # Step 6: Accept terms
            print("Accepting terms...")
            if await page.is_visible('text=I accept'):
                await page.click('input[type="checkbox"]')
                await page.click('text=I accept')
            
            await asyncio.sleep(5)
            
            # Step 7: Create Web Stream
            print("Creating web data stream...")
            if await page.is_visible('text=Web'):
                await page.click('text=Web')
                
                await page.fill('input[placeholder="https://example.com"]', "https://fedbuyout.com")
                await page.fill('input[placeholder="My Website"]', "FedBuyOut Website")
                
                await page.click('text=Create stream')
            
            await asyncio.sleep(3)
            
            # Step 8: Get Measurement ID
            print("Getting Measurement ID...")
            measurement_id = await page.text_content('text=G-')
            print(f"Measurement ID found: {measurement_id}")
            
            # Get tracking code
            print("Getting tracking code...")
            await page.click('text=View tag instructions')
            await page.click('text=Install manually')
            
            tracking_code = await page.text_content('code')
            
            # Save to file
            with open('/root/.openclaw/workspace/fedbuyout/GA4_TRACKING_INFO.txt', 'w') as f:
                f.write(f"Measurement ID: {measurement_id}\n\n")
                f.write(f"Tracking Code:\n{tracking_code}\n")
            
            print("✅ GA4 Setup Complete!")
            print(f"Measurement ID: {measurement_id}")
            print("Tracking info saved to GA4_TRACKING_INFO.txt")
            
        except Exception as e:
            print(f"Error: {e}")
            # Take screenshot for debugging
            await page.screenshot(path='/root/.openclaw/workspace/fedbuyout/ga_error.png')
            print("Screenshot saved to ga_error.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(setup_ga4())
