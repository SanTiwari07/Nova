import asyncio
import os
import time
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:3000"
AUDIO_PATH = r"D:\Projects\Nova\presentation_audio.m4a"
OUTPUT_DIR = Path(r"C:\Users\sansk\Downloads")
RAW_REC_DIR = Path(r"D:\Projects\Nova\temp_raw_rec")
RAW_REC_DIR.mkdir(parents=True, exist_ok=True)
FINAL_VIDEO_PATH = OUTPUT_DIR / "NOVA_Household_Autopilot_Hackathon_Demo.mp4"

CURSOR_SCRIPT = """
(() => {
  if (document.getElementById('__nova_cursor__')) return;
  const cursor = document.createElement('div');
  cursor.id = '__nova_cursor__';
  cursor.style.position = 'fixed';
  cursor.style.width = '24px';
  cursor.style.height = '24px';
  cursor.style.borderRadius = '50%';
  cursor.style.backgroundColor = 'rgba(245, 158, 11, 0.75)';
  cursor.style.border = '2.5px solid rgba(255, 255, 255, 0.95)';
  cursor.style.boxShadow = '0 0 14px rgba(245, 158, 11, 0.6), 0 2px 4px rgba(0,0,0,0.3)';
  cursor.style.pointerEvents = 'none';
  cursor.style.zIndex = '9999999';
  cursor.style.transition = 'transform 0.08s ease, width 0.12s ease, height 0.12s ease, background-color 0.12s ease';
  cursor.style.transform = 'translate(-50%, -50%)';
  cursor.style.top = '100px';
  cursor.style.left = '100px';
  document.documentElement.appendChild(cursor);

  window.addEventListener('mousemove', (e) => {
    cursor.style.top = e.clientY + 'px';
    cursor.style.left = e.clientX + 'px';
  }, true);

  window.addEventListener('mousedown', () => {
    cursor.style.transform = 'translate(-50%, -50%) scale(0.7)';
    cursor.style.backgroundColor = 'rgba(239, 68, 68, 0.9)';
  }, true);

  window.addEventListener('mouseup', () => {
    cursor.style.transform = 'translate(-50%, -50%) scale(1)';
    cursor.style.backgroundColor = 'rgba(245, 158, 11, 0.75)';
  }, true);
})();
"""

async def smooth_move(page, start_x, start_y, end_x, end_y, duration_sec=1.0, steps=25):
    try:
        for i in range(1, steps + 1):
            t = i / steps
            ease = t * t * (3 - 2 * t)
            curr_x = start_x + (end_x - start_x) * ease
            curr_y = start_y + (end_y - start_y) * ease
            await page.mouse.move(curr_x, curr_y)
            await asyncio.sleep(duration_sec / steps)
    except Exception as e:
        print(f"smooth_move error: {e}")

async def smooth_scroll(page, delta_y, duration_sec=1.5, steps=20):
    try:
        step_delta = delta_y / steps
        for _ in range(steps):
            await page.evaluate(f"window.scrollBy({{ top: {step_delta}, behavior: 'smooth' }});")
            await asyncio.sleep(duration_sec / steps)
    except Exception as e:
        print(f"smooth_scroll error: {e}")

async def sleep_until(start_time, target_elapsed):
    current = time.time() - start_time
    rem = target_elapsed - current
    if rem > 0:
        await asyncio.sleep(rem)
async def record_demo():
    print("[1/5] Launching browser and starting video recording...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge", headless=True)
        context = await browser.new_context(
            record_video_dir=str(RAW_REC_DIR),
            record_video_size={"width": 1920, "height": 1080},
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1.0
        )
        page = await context.new_page()
        await page.add_init_script(CURSOR_SCRIPT)

        start_time = time.time()
        print(f"[2/5] Recording started at t=0.00s")

        # Part 1: 0:00 - 0:32 (Storefront - The Problem)
        print("--> 0:00 - 0:32: Traditional Reactive Store (/store)")
        await page.goto(f"{BASE_URL}/store", wait_until="networkidle")
        await page.evaluate(CURSOR_SCRIPT)
        await page.mouse.move(400, 250)
        await asyncio.sleep(4.0)

        await smooth_move(page, 400, 250, 750, 250, duration_sec=2.0)
        await smooth_scroll(page, delta_y=450, duration_sec=3.0)
        await smooth_move(page, 750, 250, 600, 500, duration_sec=2.0)
        await smooth_scroll(page, delta_y=450, duration_sec=3.0)
        await smooth_move(page, 600, 500, 1050, 450, duration_sec=2.5)
        await smooth_scroll(page, delta_y=-900, duration_sec=3.0)
        await smooth_move(page, 1050, 450, 960, 120, duration_sec=2.0)
        await sleep_until(start_time, 32.0)

        # Part 1b: 0:32 - 0:53 (NOVA Introduction - Home Dashboard)
        print("--> 0:32 - 0:53: NOVA Household Autopilot Intro (/)")
        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await page.evaluate(CURSOR_SCRIPT)
        await page.mouse.move(960, 220)
        await asyncio.sleep(2.0)

        await smooth_move(page, 960, 220, 800, 320, duration_sec=2.0)
        await smooth_move(page, 800, 320, 820, 370, duration_sec=3.0)
        await smooth_move(page, 820, 370, 820, 410, duration_sec=3.0)
        await sleep_until(start_time, 53.0)
        # Part 2: 0:53 - 1:28 (Universal Search & Household Overview)
        print("--> 0:53 - 1:28: Context & Universal Search (/)")
        await smooth_move(page, 820, 410, 960, 32, duration_sec=1.5)
        try:
            search_box = page.locator('input[placeholder*="Search pantry"]').first
            if await search_box.count() > 0:
                await search_box.click()
                await asyncio.sleep(0.5)
                await search_box.type("Milk", delay=180)
                await asyncio.sleep(2.5)
                await smooth_move(page, 960, 32, 960, 150, duration_sec=2.0)
                await asyncio.sleep(2.0)
                await smooth_move(page, 960, 150, 960, 240, duration_sec=2.0)
                await asyncio.sleep(2.0)
                await search_box.fill("")
                await page.keyboard.press("Escape")
                await asyncio.sleep(1.0)
        except Exception as e:
            print(f"Search demo error: {e}")

        await smooth_scroll(page, delta_y=420, duration_sec=2.5)
        await smooth_move(page, 960, 240, 720, 520, duration_sec=2.0)
        await asyncio.sleep(1.5)
        await smooth_move(page, 720, 520, 960, 520, duration_sec=2.0)
        await asyncio.sleep(1.5)
        await smooth_move(page, 960, 520, 1180, 520, duration_sec=2.0)
        await sleep_until(start_time, 88.0)

        # Part 2b: 1:28 - 1:50 (Intelligent Layer over Amazon)
        print("--> 1:28 - 1:50: Amazon Integration & Household Intelligence")
        await smooth_scroll(page, delta_y=-300, duration_sec=2.0)
        await smooth_move(page, 1180, 520, 1420, 32, duration_sec=2.0)
        await asyncio.sleep(3.0)
        await smooth_move(page, 1420, 32, 1320, 32, duration_sec=2.0)
        await asyncio.sleep(3.0)
        await sleep_until(start_time, 110.0)

        # Part 3: 1:50 - 2:13 (Idea 1: Predictive Action & Why Modal)
        print("--> 1:50 - 2:13: Predictive Replenishment & Explainability (/)")
        await smooth_scroll(page, delta_y=150, duration_sec=1.5)
        try:
            why_btn = page.locator('button:has-text("Why?")').first
            if await why_btn.count() > 0:
                box = await why_btn.bounding_box()
                if box:
                    await smooth_move(page, 1320, 32, box["x"] + box["width"]/2, box["y"] + box["height"]/2, duration_sec=2.0)
                    await asyncio.sleep(1.0)
                    await why_btn.click()
                    print("Clicked 'Why?' modal")
                    await asyncio.sleep(2.0)
                    await smooth_move(page, box["x"], box["y"], 960, 500, duration_sec=2.0)
                    await asyncio.sleep(4.0)
                    close_btn = page.locator('button:has(svg.lucide-x)').first
                    if await close_btn.count() > 0:
                        cbox = await close_btn.bounding_box()
                        if cbox:
                            await smooth_move(page, 960, 500, cbox["x"] + cbox["width"]/2, cbox["y"] + cbox["height"]/2, duration_sec=1.5)
                            await close_btn.click()
                            await asyncio.sleep(1.0)
        except Exception as e:
            print(f"Why modal error: {e}")
        await sleep_until(start_time, 133.0)
        # Part 3b: 2:13 - 2:40 (Idea 2: Intelligent Restraint - /pantry)
        print("--> 2:13 - 2:40: Intelligent Restraint DO_NOTHING (/pantry)")
        await page.goto(f"{BASE_URL}/pantry", wait_until="networkidle")
        await page.evaluate(CURSOR_SCRIPT)
        await page.mouse.move(960, 200)
        await asyncio.sleep(2.0)
        await smooth_scroll(page, delta_y=350, duration_sec=2.5)
        await smooth_move(page, 960, 200, 850, 480, duration_sec=2.0)
        await asyncio.sleep(3.0)
        await smooth_scroll(page, delta_y=350, duration_sec=2.5)
        await smooth_move(page, 850, 480, 1050, 550, duration_sec=2.0)
        await asyncio.sleep(4.0)
        await sleep_until(start_time, 160.0)

        # Part 3c: 2:40 - 3:06 (Idea 3: Meal Intent & Reconciliation - /plans)
        print("--> 2:40 - 3:06: Natural Intent & Recipe Reconciliation (/plans)")
        await page.goto(f"{BASE_URL}/plans", wait_until="networkidle")
        await page.evaluate(CURSOR_SCRIPT)
        await page.mouse.move(960, 250)
        await asyncio.sleep(2.0)
        await smooth_move(page, 960, 250, 750, 420, duration_sec=2.0)
        await asyncio.sleep(2.0)
        await smooth_move(page, 750, 420, 1150, 420, duration_sec=2.0)
        await asyncio.sleep(2.0)
        await smooth_scroll(page, delta_y=350, duration_sec=2.0)
        try:
            custom_input = page.locator('input[placeholder*="biryani"], input[placeholder*="plan"], input[type="text"]').last
            if await custom_input.count() > 0:
                ibox = await custom_input.bounding_box()
                if ibox:
                    await smooth_move(page, 1150, 420, ibox["x"] + 150, ibox["y"] + ibox["height"]/2, duration_sec=1.5)
                    await custom_input.click()
                    await custom_input.type("Dinner tonight: Biryani for 6 people", delay=120)
                    await asyncio.sleep(2.0)
        except Exception as e:
            print(f"Plans custom input error: {e}")
        await sleep_until(start_time, 186.0)
        # Part 4: 3:06 - 3:42 (Product Experience & Review Options Modal)
        print("--> 3:06 - 3:42: Product Experience & Needs Input (/)")
        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await page.evaluate(CURSOR_SCRIPT)
        await page.mouse.move(960, 300)
        await asyncio.sleep(1.5)
        await smooth_scroll(page, delta_y=550, duration_sec=2.5)
        try:
            review_btn = page.locator('button:has-text("Review options")').first
            if await review_btn.count() > 0:
                rbox = await review_btn.bounding_box()
                if rbox:
                    await smooth_move(page, 960, 300, rbox["x"] + rbox["width"]/2, rbox["y"] + rbox["height"]/2, duration_sec=2.0)
                    await review_btn.click()
                    print("Clicked 'Review options' modal")
                    await asyncio.sleep(2.0)
                    await smooth_move(page, rbox["x"], rbox["y"], 960, 480, duration_sec=2.0)
                    await asyncio.sleep(3.0)
                    await smooth_move(page, 960, 480, 960, 580, duration_sec=2.0)
                    await asyncio.sleep(3.0)
                    close_btn = page.locator('button:has(svg.lucide-x)').first
                    if await close_btn.count() > 0:
                        cbox = await close_btn.bounding_box()
                        if cbox:
                            await smooth_move(page, 960, 580, cbox["x"] + cbox["width"]/2, cbox["y"] + cbox["height"]/2, duration_sec=1.5)
                            await close_btn.click()
                            await asyncio.sleep(1.0)
        except Exception as e:
            print(f"Review options modal error: {e}")
        await sleep_until(start_time, 222.0)

        # Part 4b: 3:42 - 4:11 (Autonomy Rules & Audit Trail)
        print("--> 3:42 - 4:11: Autonomy Rules (/rules) & Audit Trail (/activity)")
        await page.goto(f"{BASE_URL}/rules", wait_until="networkidle")
        await page.evaluate(CURSOR_SCRIPT)
        await page.mouse.move(960, 200)
        await asyncio.sleep(2.0)
        await smooth_move(page, 960, 200, 650, 320, duration_sec=2.0)
        await asyncio.sleep(1.5)
        await smooth_move(page, 650, 320, 1150, 320, duration_sec=2.0)
        await asyncio.sleep(1.5)
        await smooth_scroll(page, delta_y=300, duration_sec=2.0)
        await smooth_move(page, 1150, 320, 850, 500, duration_sec=1.5)
        await asyncio.sleep(3.0)

        print("--> 4:00 - 4:11: Immutable Audit Trail (/activity)")
        await page.goto(f"{BASE_URL}/activity", wait_until="networkidle")
        await page.evaluate(CURSOR_SCRIPT)
        await page.mouse.move(960, 250)
        await asyncio.sleep(1.5)
        await smooth_scroll(page, delta_y=350, duration_sec=2.5)
        await smooth_move(page, 960, 250, 750, 400, duration_sec=2.0)
        await asyncio.sleep(2.0)
        await smooth_scroll(page, delta_y=300, duration_sec=2.0)
        await sleep_until(start_time, 251.0)
        # Part 5: 4:11 - 5:02 (Architecture: Strands SDK & Safety Gates)
        print("--> 4:11 - 5:02: AWS Strands Agents SDK Architecture (/how-it-works)")
        await page.goto(f"{BASE_URL}/how-it-works", wait_until="networkidle")
        await page.evaluate(CURSOR_SCRIPT)
        await page.mouse.move(960, 150)
        await asyncio.sleep(2.0)
        await smooth_move(page, 960, 150, 1380, 140, duration_sec=2.0)
        await asyncio.sleep(2.5)
        await smooth_move(page, 1380, 140, 600, 320, duration_sec=2.0)
        await asyncio.sleep(2.0)
        await smooth_move(page, 600, 320, 960, 320, duration_sec=2.0)
        await asyncio.sleep(2.0)
        await smooth_move(page, 960, 320, 1320, 320, duration_sec=2.0)
        await asyncio.sleep(2.0)
        await smooth_move(page, 1320, 320, 600, 480, duration_sec=2.0)
        await asyncio.sleep(2.5)
        await smooth_move(page, 600, 480, 960, 480, duration_sec=2.0)
        await asyncio.sleep(2.5)
        await smooth_scroll(page, delta_y=450, duration_sec=2.5)
        await smooth_move(page, 960, 480, 720, 650, duration_sec=2.0)
        await asyncio.sleep(2.5)
        await smooth_move(page, 720, 650, 960, 650, duration_sec=2.0)
        await asyncio.sleep(2.5)
        await smooth_move(page, 960, 650, 1200, 650, duration_sec=2.0)
        await sleep_until(start_time, 302.0)

        # Part 5b: 5:02 - 5:33 (Grand Finale & Outro - /)
        print("--> 5:02 - 5:33: Grand Finale & Outro (/)")
        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await page.evaluate(CURSOR_SCRIPT)
        await page.mouse.move(960, 300)
        await asyncio.sleep(2.0)
        await smooth_scroll(page, delta_y=-200, duration_sec=2.0)
        await smooth_move(page, 960, 300, 750, 160, duration_sec=2.5)
        await asyncio.sleep(3.0)
        await smooth_move(page, 750, 160, 450, 32, duration_sec=2.5)
        await asyncio.sleep(3.0)
        await smooth_move(page, 450, 32, 960, 320, duration_sec=2.5)

        await sleep_until(start_time, 333.0)
        print("[3/5] Playwright recording sequence completed successfully.")

        await context.close()
        await browser.close()

    webm_files = list(RAW_REC_DIR.glob("*.webm"))
    if not webm_files:
        raise RuntimeError("No recorded webm video found in " + str(RAW_REC_DIR))
    latest_webm = max(webm_files, key=lambda f: f.stat().st_mtime)
    print(f"[4/5] Raw recording saved to: {latest_webm}")

    print(f"[5/5] Merging video with audio using ffmpeg...")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(latest_webm),
        "-i", AUDIO_PATH,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(FINAL_VIDEO_PATH)
    ]
    subprocess.run(cmd, check=True)
    print(f"--> Saved final video to: {FINAL_VIDEO_PATH}")
    print("ALL DONE! Video generated successfully.")

if __name__ == "__main__":
    asyncio.run(record_demo())