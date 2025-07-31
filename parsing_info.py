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
            await page.wait_for_selector('.odd', timeout = 10000)  # Use the actual class for result

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


async def send_notification(bot, chat_id, crn, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            course_title, status = await check_course_status(crn)
            if status == 1:
                message = f"🚨 COURSE AVAILABLE! 🚨\n\n{course_title}\n\nGo register now!"
                await bot.send_message(chat_id, message)
                break
            elif status == -1:
                error_msg = "⚠️ Error checking course status."
                await bot.send_message(chat_id, error_msg)
        except Exception as e:
            if attempt == max_attempts - 1:
                print(f"Failed after {max_attempts} attempts: {e}")
            await asyncio.sleep(2)

