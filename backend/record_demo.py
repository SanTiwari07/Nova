import asyncio
import os
import time
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:3000"
AUDIO_PATH = r"D:\Projects\Nova\Video_Content\Nova_audio.m4a"
OUTPUT_DIR = Path(r"C:\Users\sansk\Downloads")
RAW_REC_DIR = Path(r"D:\Projects\Nova\temp_raw_rec")
RAW_REC_DIR.mkdir(parents=True, exist_ok=True)
FINAL_VIDEO_PATH = OUTPUT_DIR / "NOVA_Household_Autopilot_Hackathon_Demo.mp4"
WORKSPACE_COPY_PATH = Path(r"D:\Projects\Nova") / "NOVA_Household_Autopilot_Hackathon_Demo.mp4"

TOTAL_DURATION = 331.25

STUDIO_FX = """
(() => {
  if (document.getElementById('__studio_cursor__')) return;
  
  const style = document.createElement('style');
  style.innerHTML = `
    #__studio_cursor__ {
      position: fixed;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(245, 158, 11, 0.95) 0%, rgba(217, 119, 6, 0.85) 100%);
      border: 2px solid rgba(255, 255, 255, 0.95);
      box-shadow: 0 0 16px rgba(245, 158, 11, 0.6), 0 2px 6px rgba(0,0,0,0.35);
      pointer-events: none;
      z-index: 99999999;
      transform: translate(-50%, -50%);
      transition: width 0.12s ease, height 0.12s ease, transform 0.08s ease;
    }
    .__click_pulse__ {
      position: fixed;
      border-radius: 50%;
      border: 2.5px solid rgba(245, 158, 11, 0.85);
      background: rgba(245, 158, 11, 0.25);
      pointer-events: none;
      z-index: 99999998;
      transform: translate(-50%, -50%);
      animation: __pulse_anim__ 0.45s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
    }
    @keyframes __pulse_anim__ {
      0% { width: 8px; height: 8px; opacity: 1; }
      100% { width: 68px; height: 68px; opacity: 0; }
    }
    #__fps_keeper__ {
      position: fixed;
      bottom: 0;
      right: 0;
      width: 1px;
      height: 1px;
      opacity: 0.01;
      pointer-events: none;
      z-index: 1;
    }
  `;
  document.head.appendChild(style);

  const cursor = document.createElement('div');
  cursor.id = '__studio_cursor__';
  cursor.style.top = '150px';
  cursor.style.left = '300px';
  document.documentElement.appendChild(cursor);

  const fpsEl = document.createElement('div');
  fpsEl.id = '__fps_keeper__';
  document.documentElement.appendChild(fpsEl);
  let frame = 0;
  function tick() {
    frame = (frame + 1) % 2;
    fpsEl.style.opacity = frame === 0 ? '0.01' : '0.015';
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);

  window.addEventListener('mousemove', (e) => {
    cursor.style.top = e.clientY + 'px';
    cursor.style.left = e.clientX + 'px';
  }, true);

  window.addEventListener('mousedown', (e) => {
    cursor.style.transform = 'translate(-50%, -50%) scale(0.75)';
    const pulse = document.createElement('div');
    pulse.className = '__click_pulse__';
    pulse.style.top = e.clientY + 'px';
    pulse.style.left = e.clientX + 'px';
    document.documentElement.appendChild(pulse);
    setTimeout(() => pulse.remove(), 480);
  }, true);

  window.addEventListener('mouseup', () => {
    cursor.style.transform = 'translate(-50%, -50%) scale(1)';
  }, true);
})();
"""

async def smooth_move(page, start_x, start_y, end_x, end_y, duration_sec=0.8, steps=25):
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

async def smooth_scroll(page, delta_y, duration_sec=1.0, steps=20):
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

async def safe_goto(page, url):
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    except Exception as e:
        print(f"safe_goto notice {url}: {e}")
    await asyncio.sleep(0.8)

async def record_demo():
    print("[1/5] Launching browser in 1080p 60fps mode...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="msedge",
            headless=True,
            args=[
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--enable-gpu-rasterization",
                "--disable-features=CalculateNativeWinOcclusion",
                "--no-sandbox"
            ]
        )
        context = await browser.new_context(
            record_video_dir=str(RAW_REC_DIR),
            record_video_size={"width": 1920, "height": 1080},
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1.0
        )
        page = await context.new_page()
        await page.add_init_script(STUDIO_FX)

        start_time = time.time()
        print(f"[2/5] Recording started at t=0.00s (Target: {TOTAL_DURATION}s)")

        # -------------------------------------------------------------
        # SECTION 1A: 0:00 - 0:15 (The Problem - Home Dashboard Opening)
        # -------------------------------------------------------------
        print("--> 0:00 - 0:15: Section 1A - Household decisions & mental load (/)")
        await safe_goto(page, f"{BASE_URL}/")
        await page.mouse.move(960, 240)
        await asyncio.sleep(2.0)
        
        # 0:03 ("What is running low?"): hover over Pantry summary tile
        await smooth_move(page, 960, 240, 720, 520, duration_sec=1.0)
        await asyncio.sleep(2.0)

        # 0:07 ("What should we buy? What should we not buy?"): glide to restraint card
        await smooth_scroll(page, delta_y=350, duration_sec=1.2)
        await smooth_move(page, 720, 520, 850, 480, duration_sec=1.0)
        await asyncio.sleep(2.0)

        # 0:12 ("mental load"): scroll back up calmly
        await smooth_scroll(page, delta_y=-350, duration_sec=1.0)
        await smooth_move(page, 850, 480, 960, 32, duration_sec=0.8)
        await sleep_until(start_time, 15.0)

        # -------------------------------------------------------------
        # SECTION 1B: 0:15 - 0:32 (Traditional Reactive Shopping - /store)
        # -------------------------------------------------------------
        print("--> 0:15 - 0:32: Section 1B - The Contrast: Reactive Shopping (/store)")
        await safe_goto(page, f"{BASE_URL}/store")
        await page.mouse.move(500, 250)
        await asyncio.sleep(1.5)

        # 0:17 - 0:21 ("open app, search, compare options, add to cart, order")
        await smooth_move(page, 500, 250, 800, 250, duration_sec=1.0)
        await smooth_scroll(page, delta_y=450, duration_sec=2.0)
        await smooth_move(page, 800, 250, 950, 450, duration_sec=1.0)
        await smooth_scroll(page, delta_y=400, duration_sec=2.0)

        # 0:27 - 0:32 ("smartest shopping decision is simply do nothing"): scroll up
        await smooth_scroll(page, delta_y=-850, duration_sec=2.0)
        await smooth_move(page, 950, 450, 960, 32, duration_sec=1.0)
        await sleep_until(start_time, 32.0)

        # -------------------------------------------------------------
        # SECTION 2A: 0:32 - 0:53 (Introduce NOVA - Autonomy != Automation)
        # -------------------------------------------------------------
        print("--> 0:32 - 0:53: Section 2A - Introduce NOVA: Autonomy != Automation (/)")
        await safe_goto(page, f"{BASE_URL}/")
        await page.mouse.move(960, 220)
        await asyncio.sleep(1.5)

        # 0:36 ("understands state of house"): hover on Briefing summary
        await smooth_move(page, 960, 220, 820, 320, duration_sec=1.0)
        await asyncio.sleep(2.0)

        # 0:41 ("Autonomy is not just automation"): move across decision state badges
        await smooth_move(page, 820, 320, 820, 370, duration_sec=1.2)
        await asyncio.sleep(2.0)
        await smooth_move(page, 820, 370, 820, 410, duration_sec=1.2)
        await asyncio.sleep(2.0)
        await sleep_until(start_time, 53.0)

        # -------------------------------------------------------------
        # SECTION 2B: 0:53 - 1:28 (Store vs Assistant: Context & Plans)
        # -------------------------------------------------------------
        print("--> 0:53 - 1:28: Section 2B - Store vs Assistant: Context & Plans (/)")
        # 0:53: Click search bar and type Milk
        await smooth_move(page, 820, 410, 960, 32, duration_sec=1.0)
        try:
            search_box = page.locator('input[placeholder*="Search pantry"]').first
            if await search_box.count() > 0:
                await search_box.click()
                await asyncio.sleep(0.4)
                await search_box.type("Milk", delay=120)
                await asyncio.sleep(3.0)
                # Hover over pantry result in preview
                await smooth_move(page, 960, 32, 960, 160, duration_sec=1.0)
                await asyncio.sleep(2.5)
                await search_box.fill("")
                await page.keyboard.press("Escape")
                await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Search demo error: {e}")

        # 1:12 ("brings together inventory, consumption patterns, upcoming plans..."): visit /plans
        print("--> 1:12 - 1:28: Meal Plans reconciliation (/plans)")
        await safe_goto(page, f"{BASE_URL}/plans")
        await page.mouse.move(960, 250)
        await asyncio.sleep(1.5)
        await smooth_move(page, 960, 250, 750, 420, duration_sec=1.0)
        await asyncio.sleep(2.0)
        await smooth_move(page, 750, 420, 1150, 420, duration_sec=1.0)
        await asyncio.sleep(2.0)
        await smooth_scroll(page, delta_y=300, duration_sec=1.5)
        await sleep_until(start_time, 88.0)

        # -------------------------------------------------------------
        # SECTION 2C: 1:28 - 1:50 (Intelligent Layer over Commerce)
        # -------------------------------------------------------------
        print("--> 1:28 - 1:50: Section 2C - Intelligent Layer over Commerce (/)")
        await safe_goto(page, f"{BASE_URL}/")
        await page.mouse.move(960, 200)
        await asyncio.sleep(1.0)

        # Spotlight commerce indicator in header
        await smooth_move(page, 960, 200, 1420, 32, duration_sec=1.0)
        await asyncio.sleep(2.5)
        
        # Scroll to household status tiles
        await smooth_scroll(page, delta_y=400, duration_sec=1.5)
        await smooth_move(page, 1420, 32, 960, 520, duration_sec=1.0)
        await asyncio.sleep(3.0)
        await smooth_scroll(page, delta_y=-400, duration_sec=1.2)
        await sleep_until(start_time, 110.0)

        # -------------------------------------------------------------
        # SECTION 3A: 1:50 - 2:13 (Idea 1: Predictive Action - Milk)
        # -------------------------------------------------------------
        print("--> 1:50 - 2:13: Section 3A - Predictive Action: Milk (/pantry -> /)")
        # 1:50: Go to /pantry and inspect Milk inventory & velocity
        await safe_goto(page, f"{BASE_URL}/pantry")
        await page.mouse.move(960, 200)
        await asyncio.sleep(1.0)
        # Hover over Amul Milk card (0.3L, 92% confidence)
        await smooth_move(page, 960, 200, 750, 380, duration_sec=1.0)
        await asyncio.sleep(3.5)

        # 2:02: Return to Home and show AUTO replenishment decision
        await safe_goto(page, f"{BASE_URL}/")
        await page.mouse.move(960, 300)
        await asyncio.sleep(1.0)
        await smooth_scroll(page, delta_y=250, duration_sec=1.0)

        # 2:06: Click "Why?" modal on Milk card
        try:
            why_btn = page.locator('button:has-text("Why?")').first
            if await why_btn.count() > 0:
                box = await why_btn.bounding_box()
                if box:
                    await smooth_move(page, 960, 300, box["x"] + box["width"]/2, box["y"] + box["height"]/2, duration_sec=1.0)
                    await why_btn.click()
                    print("Clicked 'Why?' modal")
                    await asyncio.sleep(1.5)
                    # Float across reasons
                    await smooth_move(page, box["x"], box["y"], 960, 480, duration_sec=1.0)
                    await asyncio.sleep(3.0)
                    # Close modal cleanly
                    close_btn = page.locator('button:has-text("Got it"), button:has(svg.lucide-x)').first
                    if await close_btn.count() > 0:
                        cbox = await close_btn.bounding_box()
                        if cbox:
                            await smooth_move(page, 960, 480, cbox["x"] + cbox["width"]/2, cbox["y"] + cbox["height"]/2, duration_sec=0.8)
                            await close_btn.click()
                            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Why modal error: {e}")
        await sleep_until(start_time, 133.0)

        # -------------------------------------------------------------
        # SECTION 3B: 2:13 - 2:40 (Idea 2: Intelligent Restraint - Oil)
        # -------------------------------------------------------------
        print("--> 2:13 - 2:40: Section 3B - Intelligent Restraint: Fortune Cooking Oil")
        # Scroll to All Sorted / Restraint section on Home
        await smooth_scroll(page, delta_y=450, duration_sec=1.5)
        await smooth_move(page, 960, 400, 850, 520, duration_sec=1.0)
        # Hold focus calmly on the DO_NOTHING card (Enough for 19 days, restraint applied)
        await asyncio.sleep(5.0)
        await smooth_move(page, 850, 520, 1050, 520, duration_sec=1.5)
        await asyncio.sleep(5.0)
        await sleep_until(start_time, 160.0)

        # -------------------------------------------------------------
        # SECTION 3C: 2:40 - 3:06 (Idea 3: Natural Intent - Maggi)
        # -------------------------------------------------------------
        print("--> 2:40 - 3:06: Section 3C - Natural Intent Reconciliation (Maggi)")
        # Scroll to CommandBox
        await smooth_scroll(page, delta_y=350, duration_sec=1.2)
        try:
            textarea = page.locator('textarea[placeholder*="Tell NOVA"]').first
            if await textarea.count() > 0:
                tbox = await textarea.bounding_box()
                if tbox:
                    await smooth_move(page, 1050, 520, tbox["x"] + 150, tbox["y"] + 30, duration_sec=1.0)
                    await textarea.click()
                    await asyncio.sleep(0.3)
                    await textarea.type("I want to make Maggi tonight.", delay=80)
                    await asyncio.sleep(1.0)
                    # Click Send button
                    send_btn = page.locator('button[type="submit"]:has-text("Send")').first
                    if await send_btn.count() > 0:
                        sbox = await send_btn.bounding_box()
                        if sbox:
                            await smooth_move(page, tbox["x"] + 150, tbox["y"] + 30, sbox["x"] + sbox["width"]/2, sbox["y"] + sbox["height"]/2, duration_sec=0.8)
                            await send_btn.click()
                            print("Submitted Maggi intent prompt")
                            await asyncio.sleep(3.5)
                            # Scroll down slightly to show parsed recipe & pantry result
                            await smooth_scroll(page, delta_y=200, duration_sec=1.0)
                            await asyncio.sleep(3.0)
        except Exception as e:
            print(f"CommandBox Maggi error: {e}")
        await sleep_until(start_time, 186.0)

        # -------------------------------------------------------------
        # SECTION 4: 3:06 - 3:40 (User Experience & Trust - Review Options)
        # -------------------------------------------------------------
        print("--> 3:06 - 3:40: Section 4 - Briefing & Review Options modal (/)")
        # Scroll to top of Home
        await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' });")
        await asyncio.sleep(1.5)
        await smooth_move(page, 960, 500, 960, 300, duration_sec=1.0)
        await asyncio.sleep(2.0)
        
        # Scroll to "Needs your input" section
        await smooth_scroll(page, delta_y=400, duration_sec=1.2)
        try:
            review_btn = page.locator('button:has-text("Review options")').first
            if await review_btn.count() > 0:
                rbox = await review_btn.bounding_box()
                if rbox:
                    await smooth_move(page, 960, 300, rbox["x"] + rbox["width"]/2, rbox["y"] + rbox["height"]/2, duration_sec=1.0)
                    await review_btn.click()
                    print("Clicked 'Review options' modal")
                    await asyncio.sleep(1.5)
                    # Move across the 3 options
                    await smooth_move(page, rbox["x"], rbox["y"], 960, 480, duration_sec=1.0)
                    await asyncio.sleep(2.5)
                    await smooth_move(page, 960, 480, 960, 560, duration_sec=1.0)
                    await asyncio.sleep(2.5)
                    close_btn = page.locator('button:has(svg.lucide-x)').first
                    if await close_btn.count() > 0:
                        cbox = await close_btn.bounding_box()
                        if cbox:
                            await smooth_move(page, 960, 560, cbox["x"] + cbox["width"]/2, cbox["y"] + cbox["height"]/2, duration_sec=0.8)
                            await close_btn.click()
                            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Review options modal error: {e}")

        # Quick glance at Pantry product cards
        await safe_goto(page, f"{BASE_URL}/pantry")
        await page.mouse.move(960, 250)
        await asyncio.sleep(2.0)
        await smooth_scroll(page, delta_y=300, duration_sec=1.5)
        await sleep_until(start_time, 220.0)

        # -------------------------------------------------------------
        # SECTION 5: 3:40 - 4:11 (Autonomy Rules & Audit Trail)
        # -------------------------------------------------------------
        print("--> 3:40 - 4:11: Section 5 - Rules (/rules) & Audit Trail (/activity)")
        await safe_goto(page, f"{BASE_URL}/rules")
        await page.mouse.move(960, 200)
        await asyncio.sleep(1.5)
        # Hover over Autopilot profiles
        await smooth_move(page, 960, 200, 650, 320, duration_sec=1.0)
        await asyncio.sleep(2.0)
        await smooth_move(page, 650, 320, 1150, 320, duration_sec=1.0)
        await asyncio.sleep(2.0)
        await smooth_scroll(page, delta_y=300, duration_sec=1.2)
        await smooth_move(page, 1150, 320, 850, 480, duration_sec=1.0)
        await asyncio.sleep(2.0)

        # 4:02: Visit Activity (Audit Trail)
        print("--> 4:02 - 4:11: Activity Audit Trail (/activity)")
        await safe_goto(page, f"{BASE_URL}/activity")
        await page.mouse.move(960, 250)
        await asyncio.sleep(1.5)
        await smooth_scroll(page, delta_y=350, duration_sec=1.5)
        await smooth_move(page, 960, 250, 750, 400, duration_sec=1.0)
        await asyncio.sleep(2.0)
        await smooth_scroll(page, delta_y=250, duration_sec=1.2)
        await sleep_until(start_time, 251.0)

        # -------------------------------------------------------------
        # SECTION 6: 4:11 - 5:02 (Architecture: Strands SDK & Safety Gates)
        # -------------------------------------------------------------
        print("--> 4:11 - 5:02: Section 6 - Architecture: Strands SDK (/how-it-works)")
        await safe_goto(page, f"{BASE_URL}/how-it-works")
        await page.mouse.move(960, 150)
        await asyncio.sleep(1.5)
        # Spotlight Strands SDK badge in header
        await smooth_move(page, 960, 150, 1380, 140, duration_sec=1.0)
        await asyncio.sleep(2.0)
        # Walk across the 6 pipeline stages
        await smooth_move(page, 1380, 140, 600, 320, duration_sec=1.0)
        await asyncio.sleep(2.0)
        await smooth_move(page, 600, 320, 960, 320, duration_sec=1.0)
        await asyncio.sleep(2.0)
        await smooth_move(page, 960, 320, 1320, 320, duration_sec=1.0)
        await asyncio.sleep(2.0)
        # Stages 4, 5, 6: Deterministic safety gates
        await smooth_move(page, 1320, 320, 600, 480, duration_sec=1.0)
        await asyncio.sleep(2.0)
        await smooth_move(page, 600, 480, 960, 480, duration_sec=1.0)
        await asyncio.sleep(2.0)
        await smooth_scroll(page, delta_y=450, duration_sec=1.5)
        # Highlight LLM vs Deterministic boundary
        await smooth_move(page, 960, 480, 720, 650, duration_sec=1.0)
        await asyncio.sleep(2.5)
        await smooth_move(page, 720, 650, 1200, 650, duration_sec=1.0)
        await asyncio.sleep(2.5)
        await sleep_until(start_time, 302.0)

        # -------------------------------------------------------------
        # SECTION 7: 5:02 - 5:31.2 (Closing & Grand Finale)
        # -------------------------------------------------------------
        print("--> 5:02 - 5:31.2: Section 7 - Closing & Grand Finale (/)")
        await safe_goto(page, f"{BASE_URL}/")
        await page.mouse.move(960, 300)
        await asyncio.sleep(1.5)
        # Smooth scroll to top hero
        await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' });")
        await asyncio.sleep(1.5)
        # Center cursor serenely on NOVA header & greeting
        await smooth_move(page, 960, 300, 750, 160, duration_sec=1.5)
        await asyncio.sleep(2.5)
        await smooth_move(page, 750, 160, 960, 280, duration_sec=1.5)
        
        # Hold rock-solid until exact end of narration
        await sleep_until(start_time, TOTAL_DURATION)
        print(f"[3/5] Playwright recording sequence completed at {time.time() - start_time:.2f}s")

        await context.close()
        await browser.close()

    webm_files = list(RAW_REC_DIR.glob("*.webm"))
    if not webm_files:
        raise RuntimeError("No recorded webm video found in " + str(RAW_REC_DIR))
    latest_webm = max(webm_files, key=lambda f: f.stat().st_mtime)
    print(f"[4/5] Raw recording saved to: {latest_webm}")

    print(f"[5/5] Merging video with audio using ffmpeg in 60fps...")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(latest_webm),
        "-i", AUDIO_PATH,
        "-vf", "fps=60",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(FINAL_VIDEO_PATH)
    ]
    subprocess.run(cmd, check=True)
    print(f"--> Saved final video to: {FINAL_VIDEO_PATH}")

    # Copy to project root
    import shutil
    shutil.copy2(str(FINAL_VIDEO_PATH), str(WORKSPACE_COPY_PATH))
    print(f"--> Copied backup to: {WORKSPACE_COPY_PATH}")
    print("ALL DONE! Professional video generated successfully.")

if __name__ == "__main__":
    asyncio.run(record_demo())