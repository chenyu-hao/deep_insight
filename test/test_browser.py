import asyncio
from playwright.async_api import async_playwright


async def test_browser():
    async with async_playwright() as p:
        print("正在启动浏览器...")
        browser = await p.chromium.launch(
            headless=False,
            args=['--start-maximized'],
            # 👇 加上这一行，强制使用你手动安装的Chrome，不会再下载！
            executable_path=r"C:\Users\cyh84\AppData\Local\ms-playwright\chromium-1217\chrome-win64\chrome.exe"
        )
        print("浏览器已启动，创建页面...")
        context = await browser.new_context()
        page = await context.new_page()

        print("正在访问百度...")
        await page.goto("https://www.baidu.com")
        print("页面已加载，等待5秒...")
        await asyncio.sleep(5)

        print("关闭浏览器...")
        await browser.close()
        print("测试完成！")


if __name__ == "__main__":
    asyncio.run(test_browser())