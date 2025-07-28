from playwright.async_api import async_playwright
import asyncio


async def check_course_status(crn):
    url = 'https://bxeregprod.oit.nd.edu/StudentRegistration/ssb/term/termSelection?mode=search'

    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
            })

            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # Select the term
            await page.click('#s2id_txt_term')
            await page.wait_for_selector('#s2id_autogen1_search', state='visible')
            await page.fill('#s2id_autogen1_search', 'Fall Semester 2025')
            await asyncio.sleep(2)
            await page.keyboard.press("Enter")

            await page.click('button:has-text("Continue")')
            await page.wait_for_selector('#txt_keywordlike')

            # Fill course number
            await page.fill('#txt_keywordlike', crn)

            # Click Search
            await page.click('button:has-text("Search")')

            # Wait for results to load
            await page.wait_for_selector('.odd')  # Use the actual class for result

            # Get content
            status = await page.inner_text('[data-content="Status"]')
            title = await page.inner_text('[data-content="Title"]')
            print(status)
            print(title)
            await browser.close()

            if status[0] != 'F':
                return title, 1  # Course is open
            else:
                return title, 0  # Course is full

    except Exception as e:
        print(f"Error during course check: {str(e)}")
        return None, -1  # Error status



