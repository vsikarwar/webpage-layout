import asyncio
from pyppeteer import launch

async def screenshot(url, filePath):
    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.setViewport({ 'width': 1920, 'height': 1080 });
    await page.goto(url)
    await page.screenshot({'path': filePath, 'fullPage':True})
    element = await page.querySelectorAll('a')
    hrefs = []
    for ele in element:
        href = await page.evaluate('(ele) => ele.href', ele)
        hrefs.append(href)
    return hrefs
    await browser.close()

hrefs = asyncio.get_event_loop().run_until_complete(screenshot('https://pythonprogramming.net', './example2.png'))

print(hrefs)
