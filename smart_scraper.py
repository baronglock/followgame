#!/usr/bin/env python3
"""
Smart Instagram Scraper - Pre-loads followers before collecting
Scrolls first to load everything, then collects data
"""

import json
import time
import random
import os
import requests
import sqlite3
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

class SmartInstagramScraper:
    """Scraper that pre-loads followers before collecting"""
    
    def __init__(self):
        self.driver = None
        self.followers_data = []
        self.setup_browser()
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database to track scraped users"""
        self.conn = sqlite3.connect('scraped_users.db')
        self.cursor = self.conn.cursor()
        
        # Create table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                profile_pic_url TEXT,
                profile_pic_path TEXT,
                scraped_at TIMESTAMP,
                has_picture BOOLEAN
            )
        ''')
        self.conn.commit()
    
    def is_user_scraped(self, username):
        """Check if user is already in database"""
        self.cursor.execute('SELECT has_picture FROM users WHERE username = ?', (username,))
        result = self.cursor.fetchone()
        return result is not None and result[0] == 1  # Return True only if we have the picture
    
    def save_user_to_db(self, username, pic_url=None, pic_path=None):
        """Save or update user in database"""
        self.cursor.execute('''
            INSERT OR REPLACE INTO users (username, profile_pic_url, profile_pic_path, scraped_at, has_picture)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, pic_url, pic_path, datetime.now(), bool(pic_path)))
        self.conn.commit()
    
    def setup_browser(self):
        """Setup Chrome with stealth settings"""
        chrome_options = Options()
        
        # Stealth settings
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Random user agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        ]
        chrome_options.add_argument(f'user-agent={random.choice(user_agents)}')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Anti-detection JavaScript
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            '''
        })
        
        print("✅ Browser ready with stealth mode")
    
    def login(self):
        """Simple manual login"""
        print("\n🔐 Opening Instagram...")
        self.driver.get("https://www.instagram.com/")
        time.sleep(3)
        
        input("\n⏸️ Please login manually, then press Enter...")
        print("✅ Login complete")
        return True
    
    def pre_scroll_followers(self, dialog, target_count=None):
        """
        STEP 1: Scroll until the END of the followers list
        Keep scrolling until we can't load any more
        """
        print(f"\n📜 PHASE 1: Scrolling to load ALL followers...")
        print("(Fast continuous scrolling until we reach the end)")
        
        last_count = 0
        scroll_count = 0
        estimated_loaded = 0
        stuck_count = 0
        max_stuck = 5  # If stuck 5 times, we've reached the end
        
        while stuck_count < max_stuck:  # Keep going until truly stuck
            # Get the scrollable container inside the dialog
            try:
                # Find the actual scrollable list container
                scrollable = dialog.find_element(By.XPATH, ".//div[contains(@style, 'overflow')]")
            except:
                scrollable = dialog
            
            # FAST human-like scrolling - humans scroll fast!
            self.driver.execute_script("""
                var element = arguments[0];
                element.scrollTop = element.scrollHeight;
            """, scrollable)
            
            # Short wait - humans don't wait long between scrolls
            time.sleep(random.uniform(0.3, 0.8))  # Much faster!
            
            # Count loaded followers (check multiple element types)
            elements = []
            
            # Count method 1: Links
            links = dialog.find_elements(By.XPATH, ".//a[contains(@href, '/') and not(contains(@href, '/explore'))]")
            elements.extend(links)
            
            # Count method 2: Buttons with usernames
            buttons = dialog.find_elements(By.XPATH, ".//div[@role='button']")
            elements.extend(buttons)
            
            # Remove duplicates and count unique
            unique_count = len(set([e.text for e in elements if e.text]))
            
            # Use the higher count
            estimated_loaded = max(len(links), unique_count)
            
            print(f"⚡ Scroll #{scroll_count + 1}: {estimated_loaded} followers loaded")
            
            # Check if we loaded more followers
            if estimated_loaded > last_count:
                # Still loading, reset stuck counter
                stuck_count = 0
                last_count = estimated_loaded
            else:
                # No new followers loaded
                stuck_count += 1
                print(f"  ⏳ No new followers (attempt {stuck_count}/{max_stuck})")
            
            # If stuck, try aggressive scrolling
            if stuck_count > 0 and stuck_count < max_stuck:
                # Try different scroll methods to unstick
                self.driver.execute_script("""
                    var dialog = arguments[0];
                    // Find all scrollable elements
                    var scrollables = dialog.querySelectorAll('*');
                    for (var i = 0; i < scrollables.length; i++) {
                        var el = scrollables[i];
                        if (el.scrollHeight > el.clientHeight) {
                            el.scrollTop = el.scrollHeight;
                        }
                    }
                """, dialog)
                time.sleep(0.5)
            
            # Check if we've reached the end
            if stuck_count >= max_stuck:
                print(f"✅ Reached the END of followers list!")
                print(f"📊 Total followers loaded: {estimated_loaded}")
                break
            scroll_count += 1
            
            # Safety limit
            if scroll_count > 30:
                print("⚠️ Reached scroll limit")
                break
        
        return estimated_loaded
    
    def collect_loaded_followers(self, dialog, max_collect=None):
        """
        STEP 2: Collect data from already-loaded followers
        Now we go through slowly with proper delays
        """
        print(f"\n📊 PHASE 2: Collecting data from loaded followers...")
        print("(Now using human-like delays for data collection)")
        
        # Scroll back to top first
        try:
            scrollable = dialog.find_element(By.XPATH, ".//div[contains(@style, 'overflow')]")
            self.driver.execute_script("arguments[0].scrollTop = 0", scrollable)
        except:
            self.driver.execute_script("arguments[0].scrollTop = 0", dialog)
        
        time.sleep(2)
        
        followers_collected = []
        usernames_seen = set()
        
        # Find ALL follower elements using multiple strategies
        all_elements = []
        
        # Strategy 1: Find all links
        links = dialog.find_elements(By.XPATH, ".//a[contains(@href, '/')]")
        all_elements.extend(links)
        
        # Strategy 2: Find divs with role=button (Instagram uses these)
        buttons = dialog.find_elements(By.XPATH, ".//div[@role='button']")
        
        # Strategy 3: Find spans that might contain usernames
        spans = dialog.find_elements(By.XPATH, ".//span[contains(@class, '_ap3a')]")
        
        print(f"📋 Found {len(links)} links, {len(buttons)} buttons, {len(spans)} spans")
        
        # Process each link with its corresponding image
        for element in links:
            try:
                href = element.get_attribute('href')
                
                if not href or '/p/' in href or '/explore' in href or '/reels' in href:
                    continue
                
                # Extract username from URL
                parts = href.rstrip('/').split('/')
                if len(parts) < 4:
                    continue
                    
                username = parts[-1]
                
                # Skip invalid or duplicate
                if not username or username in usernames_seen or len(username) < 2:
                    continue
                
                usernames_seen.add(username)
                
                # Find the image directly associated with this link
                profile_pic = None
                try:
                    # Find the closest parent container that has both link and image
                    parent = element
                    for _ in range(5):  # Try up to 5 parent levels
                        parent = parent.find_element(By.XPATH, '..')
                        imgs = parent.find_elements(By.TAG_NAME, 'img')
                        for img in imgs:
                            src = img.get_attribute('src')
                            if src and 'blank.gif' not in src and ('/v/' in src or 'scontent' in src):
                                profile_pic = src
                                break
                        if profile_pic:
                            break
                except:
                    pass
                
                # Add to collection
                followers_collected.append({
                    'username': username,
                    'profile_pic_url': profile_pic
                })
                
                # Show unique URL indicator
                url_preview = profile_pic[:50] + "..." if profile_pic else "No image"
                print(f"✅ {len(followers_collected):3d}: {username} - {url_preview}")
                
                # Don't break early - continue collecting ALL followers
                # We'll limit later if needed
                    
            except Exception as e:
                continue
        
        # If we don't have enough, try processing buttons/spans
        if len(followers_collected) < (max_collect or 100):
            for element in buttons + spans:
                try:
                    text = element.text.strip()
                    if text and len(text) > 1 and text not in usernames_seen:
                        # Check if it looks like a username
                        if not any(word in text.lower() for word in ['follow', 'following', 'remove', 'message']):
                            usernames_seen.add(text)
                            
                            # Try to find associated image
                            profile_pic = None
                            try:
                                parent = element.find_element(By.XPATH, './ancestor::div[2]')
                                img = parent.find_element(By.XPATH, './/img')
                                profile_pic = img.get_attribute('src')
                            except:
                                pass
                            
                            followers_collected.append({
                                'username': text,
                                'profile_pic_url': profile_pic
                            })
                            
                            print(f"✅ {len(followers_collected):3d}: {text}")
                            
                            if max_collect and len(followers_collected) >= max_collect:
                                break
                                
                except:
                    continue
        
        # Quick pause if we collected a lot
        if len(followers_collected) > 50 and len(followers_collected) % 50 == 0:
            print(f"⏸️ Quick 0.5s pause...")
            time.sleep(0.5)
        
        return followers_collected
    
    def smart_fetch_followers(self, target_username, target_count=None):
        """
        Main method: Pre-scroll then collect
        """
        print(f"\n🎯 Smart fetching for @{target_username}")
        print(f"📌 Target: ALL followers")
        
        # Navigate to profile
        self.driver.get(f"https://www.instagram.com/{target_username}/")
        time.sleep(3)
        
        try:
            # Click followers link
            followers_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[contains(@href, '/{target_username}/followers/')]"))
            )
            
            followers_text = followers_link.text
            print(f"📊 Profile shows: {followers_text}")
            
            followers_link.click()
            time.sleep(3)
            
            # Wait for dialog
            dialog = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
            )
            
            print("✅ Followers dialog opened")
            
            # PHASE 1: Pre-scroll to load followers
            # Scroll to load ALL followers (no target limit)
            loaded_count = self.pre_scroll_followers(dialog)
            
            if loaded_count == 0:
                print("❌ No followers loaded")
                return []
            
            # Small pause before collection
            print("\n⏸️ 3 second pause before data collection...")
            time.sleep(3)
            
            # PHASE 2: Collect data from loaded followers
            # Pass None to collect ALL loaded followers
            followers = self.collect_loaded_followers(dialog, None)
            
            self.followers_data = followers
            return followers
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def download_profile_pictures(self):
        """Download profile pictures with delays"""
        if not self.followers_data:
            print("No followers to download pictures for")
            return
        
        print(f"\n📸 Downloading {len(self.followers_data)} profile pictures...")
        os.makedirs("profiles", exist_ok=True)
        
        downloaded = 0
        batch_size = 10
        
        for i, follower in enumerate(self.followers_data):
            username = follower['username']
            pic_url = follower.get('profile_pic_url')
            
            if pic_url:
                try:
                    # Download image
                    response = requests.get(pic_url, timeout=10)
                    if response.status_code == 200:
                        filepath = f"profiles/{username}.jpg"
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        
                        follower['profile_pic_path'] = filepath
                        downloaded += 1
                        print(f"  ✅ {downloaded}/{len(self.followers_data)}: {username}")
                        
                        # Save to database
                        self.save_user_to_db(username, pic_url, filepath)
                    
                    # Very quick delay
                    time.sleep(random.uniform(0.1, 0.3))  # Much faster!
                    
                except Exception as e:
                    print(f"  ❌ Failed: {username}")
                    follower['profile_pic_path'] = None
            
            # Quick break every batch
            if (i + 1) % batch_size == 0:
                pause = random.uniform(0.5, 1.0)  # Faster!
                print(f"  ⏸️ Quick batch pause...")
                time.sleep(pause)
        
        print(f"✅ Downloaded {downloaded} pictures")
    
    def save_data(self):
        """Save to JSON files"""
        # Save detailed data
        output = {
            'metadata': {
                'total_followers': len(self.followers_data),
                'scraped_at': datetime.now().isoformat()
            },
            'followers': self.followers_data
        }
        
        with open('followers_data.json', 'w') as f:
            json.dump(output, f, indent=2)
        
        # Save game format
        game_data = []
        for follower in self.followers_data:
            # Generate random stats
            random.seed(follower['username'])
            
            game_data.append({
                'instagram_username': follower['username'],
                'profile_pic_path': follower.get('profile_pic_path', f"profiles/{follower['username']}.png"),
                'profile_pic_url': follower.get('profile_pic_url'),
                'is_active_follower': True,
                'stats': {
                    'hp': random.randint(80, 150),
                    'strength': random.randint(2, 10),
                    'armor': random.randint(1, 8),
                    'luck': random.randint(1, 7)
                }
            })
        
        with open('users.json', 'w') as f:
            json.dump(game_data, f, indent=2)
        
        print(f"✅ Saved {len(self.followers_data)} followers to JSON files")
    
    def cleanup(self):
        """Close browser and database"""
        if self.driver:
            self.driver.quit()
        if hasattr(self, 'conn'):
            self.conn.close()
        print("✅ Browser closed")

def main():
    print("\n" + "="*60)
    print("🚀 SMART INSTAGRAM SCRAPER")
    print("Pre-loads followers, then collects data")
    print("="*60)
    
    scraper = SmartInstagramScraper()
    
    try:
        # Login
        scraper.login()
        
        # Get target
        target = input("\n🎯 Target username: ").strip()
        
        # Fetch ALL followers - no limit
        print("🔄 Fetching ALL followers...")
        followers = scraper.smart_fetch_followers(target, None)  # None = get all
        
        if followers:
            print(f"\n✅ Successfully collected {len(followers)} followers!")
            
            # Download pictures
            download = input("\n📸 Download profile pictures? (y/n): ").lower() == 'y'
            if download:
                scraper.download_profile_pictures()
            
            # Save data
            scraper.save_data()
            
            print("\n" + "="*50)
            print("🎉 SUCCESS!")
            print(f"✅ {len(followers)} followers ready")
            print("✅ Run game: python3 main.py")
            print("="*50)
        else:
            print("❌ No followers collected")
            
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()