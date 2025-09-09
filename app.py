#!/usr/bin/env python3
import hashlib
import json
import os
import argparse
import requests
import time
import random
from urllib.parse import urlencode
import urllib.parse
import glob
from datetime import datetime

# Import the required libraries (assuming they're in the Libs directory)
try:
    from Libs.device import Device
    from Libs.device_gen import Applog, Xlog
    from Libs.xgorgon import Gorgon
    from Libs.signature import ladon_encrypt, get_x_ss_stub
    LIBS_AVAILABLE = True
except ImportError:
    print("Warning: Libs modules not found. Some features may not work.")
    LIBS_AVAILABLE = False

# Import Flask with error handling
try:
    from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    print("Error: Flask not installed. Please install it with: pip install flask")
    FLASK_AVAILABLE = False

# Initialize Flask app only if Flask is available
if FLASK_AVAILABLE:
    app = Flask(__name__)
    app.secret_key = "tiktok_stream_key_generator_secret_key"
else:
    app = None

class Stream:
    def __init__(self, cookies_file):
        self.s = requests.session()
        if not os.path.exists(cookies_file):
            raise FileNotFoundError(f"Cookies file not found: {cookies_file}")
            
        with open(cookies_file, "r") as file:
            cookies_data = json.load(file)
        cookies = {}
        for cookie in cookies_data:
            cookies[cookie["name"]] = cookie["value"]
        self.s.cookies.update(cookies)
        # self.renewCookies()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.s.close()
    
    def getLiveStudioLatestVersion(self):
        url = "https://tron-sg.bytelemon.com/api/sdk/check_update"
        params = {
            "pid": "7393277106664249610",
            "uid": "7464643088460875280",
            "branch": "studio/release/stable",
            "buildId": "0"
        }
        try:
            with self.s.get(url, params=params) as response:
                return response.json()["data"]["manifest"]["win32"]["version"]
        except Exception as e:
            print(f"Failed to fetch latest version: {e}")
            return "0.99.0"
        

    def createStream(
        self,
        title,
        hashtag_id,
        game_tag_id="0",
        gen_replay=False,
        close_room_when_close_stream=True,
        age_restricted=False,
        priority_region="",
        spoof_plat=0,
        openudid = "",
        device_id = "",
        iid = "",
        thumbnail_path = ""
    ):
        base_url = self.getServerUrl()
        if spoof_plat == 1:
            self.s.headers = {
                "user-agent": "com.zhiliaoapp.musically/2023508030 (Linux; U; Android 14; en_US_#u-mu-celsius; M2102J20SG; Build/AP2A.240905.003; Cronet/TTNetVersion:f58efab5 2024-06-13 QuicVersion:5d23606e 2024-05-23)",
            }
            params = {
                # App ID for Tiktok Mobile App
                "aid": "1233",
                # App name for Tiktok Mobile App
                "app_name": "musical_ly",
                # Channel for Tiktok Mobile App
                "channel": "googleplay",
                "device_platform": "android",
                "iid": iid,
                "device_id": device_id,
                "openudid": openudid,
                "os": "android",
                "ssmix": "a",
                "_rticket": "1730304478660",
                "cdid": "1fb4eb4c-99f5-4534-a637-e3ac7d52fddb",
                "version_code": "370104",
                "version_name": "37.1.4",
                "manifest_version_code": "2024701040",
                "update_version_code": "2024701040",
                "ab_version": "37.1.4",
                "resolution": "1080*2309",
                "dpi": "410",
                "device_type": "M2102J20SG",
                "device_brand": "POCO",
                "language": "en",
                "os_api": "34",
                "os_version": "14",
                "ac": "wifi",
                "is_pad": "0",
                "current_region": "TN",
                "app_type": "normal",
                "sys_region": "US",
                "last_install_time": "1717207722",
                "mcc_mnc": "60501",
                "timezone_name": "Africa/Tunis",
                "carrier_region_v2": "605",
                "residence": "TN",
                "app_language": "en",
                "carrier_region": "TN",
                "ac2": "wifi5g",
                "uoo": "0",
                "op_region": "TN",
                "timezone_offset": "3600",
                "build_number": "37.1.4",
                "host_abi": "arm64-v8a",
                "locale": "en",
                "region": "US",
                "ts": "1730304477",
                "webcast_sdk_version": "3590",
                "webcast_language": "en",
                "webcast_locale": "en_US_#u-mu-celsius",
                "es_version": "2",
                "effect_sdk_version": "17.0.0",
                "current_network_quality_info": '{"tcp_rtt":64,"quic_rtt":64,"http_rtt":198,"downstream_throughput_kbps":31920,"quic_send_loss_rate":-1,"quic_receive_loss_rate":-1,"net_effective_connection_type":4,"video_download_speed":787}'
            }
            data = {
                "hashtag_id": hashtag_id,
                "hold_living_room": "1",
                "chat_sub_only_auth": "2",
                "community_flagged_chat_auth": "2",
                "ecom_bc_toggle": "3",
                "live_sub_only": "0",
                "overwrite_push_base_parameter": "false",
                "chat_l_2": "1",
                "caption": "0",
                "overwrite_push_base_min_bit_rate": "-1",
                "title": title,
                "live_sub_only_use_music": "0",
                "mobile_binded": "0",
                "create_source": "0",
                "spam_comments": "1",
                "commercial_content_promote_third_party": "false",
                "grant_level": "0",
                "screenshot_cover_status": "0",
                "overwrite_push_base_max_bit_rate": "-1",
                "enable_http_dns": "0",
                "mobile_validated": "0",
                "live_agreement": "0",
                "commercial_content_promote_myself": "false",
                "allow_preview_duration_exp": "0",
                "is_user_select": "0",
                "transaction_history": "1",
                "probe_recommend_resolution": "1",
                "chat_auth": "1",
                "disable_preview_sub_only": "0",
                "comment_tray_switch": "1",
                "overwrite_push_base_default_bit_rate": "-1",
                "overwrite_push_base_resolution": "1",
                "grant_group": "1",
                "gift_auth": "1",
                "star_comment_switch": "true",
                "has_commerce_goods": "false",
                "open_commercial_content_toggle": "false",
                "event_id": "-1",
                "star_comment_qualification": "false",
                "game_tag_id": game_tag_id,
                "community_flagged_chat_review_auth": "2",
                "age_restricted": "0",
                "group_chat_id": "0",
                "optout_gift_gallery": "false",
                "gen_replay": str(gen_replay).lower(),
                "shopping_ranking": "0"
            }

        elif spoof_plat == 2:
            self.s.headers = {
                "user-agent": "com.zhiliaoapp.musically/2023508030 (Linux; U; Android 14; en_US_#u-mu-celsius; M2102J20SG; Build/AP2A.240905.003; Cronet/TTNetVersion:f58efab5 2024-06-13 QuicVersion:5d23606e 2024-05-23)",
            }
            params = {
                # App ID for Tiktok Mobile App
                "aid": "1233",
                # App name for Tiktok Mobile App
                "app_name": "musical_ly",
                # Channel for Tiktok Mobile App
                "channel": "googleplay",
                "device_platform": "android",
                "iid": iid,
                "device_id": device_id,
                "openudid": openudid,
                "screen_shot": "1",
                "ac": "wifi",
                "version_code": "370104",
                "version_name": "37.1.4",
                "os": "android",
                "ab_version": "37.1.4",
                "ssmix": "a",
                "device_type": "M2102J20SG",
                "device_brand": "POCO",
                "language": "en",
                "os_api": "34",
                "os_version": "14",
                "manifest_version_code": "2023701040",
                "resolution": "1080*2309",
                "dpi": "410",
                "update_version_code": "2023701040",
                "_rticket": "1730306440278",
                "is_pad": "0",
                "current_region": "TN",
                "app_type": "normal",
                "sys_region": "US",
                "last_install_time": "1730305998",
                "mcc_mnc": "60501",
                "timezone_name": "Africa/Tunis",
                "carrier_region_v2": "605",
                "residence": "TN",
                "app_language": "en",
                "carrier_region": "TN",
                "ac2": "wifi5g",
                "uoo": "0",
                "op_region": "TN",
                "timezone_offset": "3600",
                "build_number": "37.1.4",
                "host_abi": "arm64-v8a",
                "locale": "en",
                "region": "US",
                "ts": "1730306440",
                "cdid": "bfe31618-558b-4e0d-a4e5-c4221be305a1",
                "webcast_sdk_version": "3490",
                "webcast_language": "en",
                "webcast_locale": "en_US_#u-mu-celsius",
                "es_version": "2",
                "effect_sdk_version": "17.0.0",
                "current_network_quality_info": '{"tcp_rtt":99,"quic_rtt":99,"http_rtt":203,"downstream_throughput_kbps":2734,"quic_send_loss_rate":-1,"quic_receive_loss_rate":-1,"net_effective_connection_type":4,"video_download_speed":7}'
            }
            data = {
                "hashtag_id": hashtag_id,
                "hold_living_room": "1",
                "chat_sub_only_auth": "2",
                "screen_shot": "1",
                "mute_duration": "1",
                "community_flagged_chat_auth": "2",
                "ecom_bc_toggle": "3",
                "live_sub_only": "0",
                "chat_l_2": "1",
                "caption": "0",
                "live_sub_only_use_music": "0",
                "mobile_binded": "0",
                "create_source": "0",
                "spam_comments": "1",
                "commercial_content_promote_third_party": "false",
                "grant_level": "0",
                "screenshot_cover_status": "1",
                "enable_http_dns": "0",
                "mobile_validated": "0",
                "live_agreement": "0",
                "orientation": "2",
                "commercial_content_promote_myself": "false",
                "allow_preview_duration_exp": "0",
                "transaction_history": "1",
                "chat_auth": "1",
                "disable_preview_sub_only": "0",
                "comment_tray_switch": "1",
                "grant_group": "1",
                "gift_auth": "1",
                "star_comment_switch": "true",
                "has_commerce_goods": "false",
                "open_commercial_content_toggle": "false",
                "event_id": "-1",
                "star_comment_qualification": "true",
                "game_tag_id": game_tag_id,
                "community_flagged_chat_review_auth": "2",
                "age_restricted": "0",
                "sdk_key": "hd",
                "live_room_mode": "4",
                "gen_replay": str(gen_replay).lower(),
                "shopping_ranking": "0"
            }
        else:
            version = self.getLiveStudioLatestVersion()
            self.s.headers = {
                "user-agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) TikTokLIVEStudio/{version} Chrome/108.0.5359.215 Electron/22.3.18-tt.8.release.main.44 TTElectron/22.3.18-tt.8.release.main.44 Safari/537.36",
            }
            params = {
                # App ID for TikTok Live Studio
                "aid": "8311",
                # App name for TikTok Live Studio
                "app_name": "tiktok_live_studio",
                # Channel for TikTok Live Studio
                "channel": "studio",
                "device_platform": "windows",
                # Priority region for the stream
                "priority_region": priority_region,
                "live_mode": "6",
                "version_code": version,
                "webcast_sdk_version": version.replace(".", "").replace("0", ""),
                "webcast_language": "en",
                "app_language": "en",
                "language": "en",
                "browser_version": "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) TikTokLIVEStudio/0.69.2 Chrome/108.0.5359.215 Electron/22.3.18-tt.8.release.main.44 TTElectron/22.3.18-tt.8.release.main.44 Safari/537.36",
                "browser_name": "Mozilla",
                "browser_platform": "Win32",
                "browser_language": "en-US",
                "screen_height": "1080",
                "screen_width": "1920",
                "timezone_name": "Africa/Lagos",
                "device_id": "7378193331631310352",
                "install_id": "7378196538524927745"
            }
            data = {
                "title": title,
                "live_studio": "1",
                "gen_replay": str(gen_replay).lower(),
                "chat_auth": "1",
                "cover_uri": "",
                "close_room_when_close_stream": str(close_room_when_close_stream).lower(),
                "hashtag_id": str(hashtag_id),
                "game_tag_id": str(game_tag_id),
                "screenshot_cover_status": "1",
                "live_sub_only": "0",
                "chat_sub_only_auth": "2",
                "multi_stream_scene": "0",
                "gift_auth": "1",
                "chat_l2": "1",
                "star_comment_switch": "true",
                "multi_stream_source": "1"
            }
        if age_restricted:
            data["age_restricted"] = "4"
        if thumbnail_path:
            uri = self.uploadThumbnail(thumbnail_path, base_url, params)
            data["cover_uri"] = uri
        # Signing is disabled for now
        # sig = Gorgon(urlencode(params, quote_via=urllib.parse.quote), urlencode(data, quote_via=urllib.parse.quote), urlencode(self.s.cookies, quote_via=urllib.parse.quote)).get_value()
        # self.s.headers.update(sig)
        # x_ss_stub = get_x_ss_stub(data)
        # self.s.headers.update(x_ss_stub)
        # if spoof_plat in [1, 2]:
        #     self.s.headers.update(ladon_encrypt(sig["x-khronos"], 1611921764, 1233))
        # else:
        #     self.s.headers.update(ladon_encrypt(sig["x-khronos"], 1611921764, 8311))
            
        streamInfo = self.s.post(
            base_url + "webcast/room/create/",
            params=params,
            data=data
        ).json()
        try:
            self.streamUrl = streamInfo["data"]["stream_url"][
                "rtmp_push_url"
            ]
            split_index = self.streamUrl.rfind("/")
            self.baseStreamUrl = self.streamUrl[:split_index]
            self.streamKey = self.streamUrl[split_index + 1:]
            self.streamShareUrl = streamInfo["data"]["share_url"]
            return True
        except KeyError:
            print(f"Error: {streamInfo['data']['prompts']}")
            return False

    def endStream(self):
        base_url = self.getServerUrl()
        params = {
            # App ID for TikTok Live Studio
            "aid": "8311",
            # App name for TikTok Live Studio
            "app_name": "tiktok_live_studio",
            # Channel for TikTok Live Studio
            "channel": "studio",
            "device_platform": "windows",
            "live_mode": "6",
        }
        streamInfo = self.s.post(
            base_url + "webcast/room/finish_abnormal/",
            params=params
        ).json()
        if "data" in streamInfo and "prompts" in streamInfo["data"]:
            print(f"Error: {streamInfo['data']['prompts']}")
            return False
        return True

    def getServerUrl(self):
        url = (
            "https://tnc16-platform-useast1a.tiktokv.com/get_domains/v4/?"
            "aid=8311&ttwebview_version=1130022001&device_platform=win"
        )
        response = self.s.get(url).json()
        for data in response["data"]["ttnet_dispatch_actions"]:
            if "param" in data and "strategy_info" in data["param"] and "webcast-normal.tiktokv.com" in data["param"]["strategy_info"]:
                server_url = data['param']['strategy_info']['webcast-normal.tiktokv.com']
                for data2 in response["data"]["ttnet_dispatch_actions"]:
                    if "param" in data2 and "strategy_info" in data2["param"] and server_url in data2["param"]["strategy_info"]:
                        server_url = data2['param']['strategy_info'][server_url]
                        return f"https://{server_url}/"
                return f"https://{server_url}/"
            
    def uploadThumbnail(
        self,
        file_path,
        base_url,
        params
    ):
        files = {
            "file": (f"crop_{round(time.time() * 1000)}.png", open(file_path, "rb"), "multipart/form-data")
        }
        thumbnailInfo = self.s.post(
                    base_url + "webcast/room/upload/image/",
                    params=params,
                    files=files
        ).json()
        return thumbnailInfo.get("data", {}).get("uri", "")
            
    def renewCookies(self):
        response = self.s.get("https://www.tiktok.com/foryou")
        if response.url == "https://www.tiktok.com/login/phone-or-email":
            print("Error: Cookies are invalid. Please login again.")
            return False
        else:
            new_cookies = []
            cookies = dict(self.s.cookies)
            for cookie in cookies:
                new_cookies.append(
                    {
                        "name": cookie,
                        "value": cookies[cookie]
                    }
                )
            with open("cookies.json", "w") as file:
                json.dump(new_cookies, file)
            return True


def fetch_game_tags():
    url = (
        "https://webcast16-normal-c-useast2a.tiktokv.com/webcast/"
        "room/hashtag/list/"
    )
    try:
        response = requests.get(url)
        game_tags = response.json()["data"]["game_tag_list"]
        return {game["id"]: game["show_name"] for game in game_tags}
    except Exception as e:
        print(f"Failed to fetch game tags: {e}")
        return {}


def generate_device():
    if not LIBS_AVAILABLE:
        print("Error: Libs modules not found. Cannot generate device.")
        return None, None, None
        
    device: dict = Device().create_device()
    device_id, install_id = Applog(device).register_device()
    Xlog(device_id).bypass()
    return device["openudid"], device_id, install_id


def find_cookies_files(cookies_dir="cookies"):
    """Find all JSON files in the cookies directory."""
    if not os.path.exists(cookies_dir):
        print(f"Cookies directory '{cookies_dir}' not found.")
        return []
    
    cookies_files = []
    for file in os.listdir(cookies_dir):
        if file.endswith('.json'):
            cookies_files.append(os.path.join(cookies_dir, file))
    
    return sorted(cookies_files)


def select_cookies_file(cookies_dir="cookies"):
    """Interactive cookies file selection."""
    cookies_files = find_cookies_files(cookies_dir)
    
    if not cookies_files:
        print("No cookies files found.")
        return None
    
    print("\nAvailable cookies files:")
    for i, file_path in enumerate(cookies_files, 1):
        file_name = os.path.basename(file_path)
        print(f"{i}. {file_name}")
    
    while True:
        try:
            choice = input(f"\nSelect cookies file (1-{len(cookies_files)}) or 'q' to quit: ")
            if choice.lower() == 'q':
                return None
            
            choice = int(choice)
            if 1 <= choice <= len(cookies_files):
                return cookies_files[choice - 1]
            else:
                print(f"Please enter a number between 1 and {len(cookies_files)}")
        except ValueError:
            print("Please enter a valid number or 'q' to quit")


def validate_cookies_file(file_path):
    """Validate if the cookies file is properly formatted."""
    try:
        with open(file_path, 'r') as f:
            cookies_data = json.load(f)
        
        if not isinstance(cookies_data, list):
            print(f"Error: {file_path} is not a valid cookies file. Expected a list of cookies.")
            return False
        
        required_fields = ['name', 'value']
        for cookie in cookies_data:
            if not isinstance(cookie, dict):
                print(f"Error: Invalid cookie format in {file_path}")
                return False
            if not all(field in cookie for field in required_fields):
                print(f"Error: Missing required fields in cookie from {file_path}")
                return False
        
        return True
    except json.JSONDecodeError:
        print(f"Error: {file_path} is not a valid JSON file.")
        return False
    except Exception as e:
        print(f"Error validating {file_path}: {e}")
        return False


def list_cookies_info(cookies_dir="cookies"):
    """List information about available cookies files."""
    cookies_files = find_cookies_files(cookies_dir)
    
    if not cookies_files:
        print("No cookies files found.")
        return
    
    print(f"\nCookies files in '{cookies_dir}' directory:")
    print("-" * 50)
    
    for file_path in cookies_files:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        try:
            with open(file_path, 'r') as f:
                cookies_data = json.load(f)
            
            if isinstance(cookies_data, list):
                cookie_count = len(cookies_data)
                domains = set()
                for cookie in cookies_data:
                    if 'domain' in cookie:
                        domains.add(cookie['domain'])
                
                domain_str = ', '.join(sorted(domains)) if domains else 'No domain info'
                print(f"📁 {file_name}")
                print(f"   Size: {file_size} bytes")
                print(f"   Cookies: {cookie_count}")
                print(f"   Domains: {domain_str}")
                print()
            else:
                print(f"📁 {file_name} (Invalid format)")
                print(f"   Size: {file_size} bytes")
                print()
        except Exception as e:
            print(f"📁 {file_name} (Error reading: {e})")
            print()


def save_last_used_cookies(cookies_file):
    """Save the last used cookies file path for future reference."""
    with open(".last_cookies", "w") as f:
        f.write(cookies_file)

def load_last_used_cookies():
    """Load the last used cookies file path."""
    try:
        with open(".last_cookies", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def generate_title_from_file(file_path="tittle.txt"):
    """Pick a random title from file and return it."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            titles = [line.strip() for line in f if line.strip()]
        if not titles:
            print(f"Error: {file_path} is empty.")
            return None
        return random.choice(titles)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None
    except Exception as e:
        print(f"Failed to generate title: {e}")
        return None


def save_config(config_data, file_path="config.json"):
    """Save configuration to a JSON file."""
    with open(file_path, "w") as file:
        json.dump(config_data, file)
    print(f"Config saved successfully to {file_path}.")


def load_config(file_path="config.json"):
    """Load configuration from a JSON file."""
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Config file {file_path} not found. Using defaults.")
        return {}
    except Exception as e:
        print(f"Error loading config file: {e}")
        return {}


# Define topics
topics = {
    "5": "Gaming",
    "6": "Music",
    "42": "Chat & Interview",
    "9": "Beauty & Fashion",
    "3": "Dance",
    "13": "Fitness & Sports",
    "4": "Food",
    "43": "News & Event",
    "45": "Education"
}

# Flask routes - only if Flask is available
if FLASK_AVAILABLE and app:
    @app.route('/')
    def index():
        """Main page with stream creation form"""
        cookies_files = find_cookies_files()
        game_tags = fetch_game_tags()
        
        return render_template('index.html', 
                              topics=topics, 
                              game_tags=game_tags,
                              cookies_files=cookies_files,
                              now={'year': time.strftime('%Y')})

    @app.route('/create_stream', methods=['POST'])
    def create_stream():
        """Handle stream creation form submission"""
        # Get form data
        title = request.form.get('title')
        hashtag_id = request.form.get('topic')
        game_tag_id = request.form.get('game_tag', '0')
        priority_region = request.form.get('region', '')
        gen_replay = 'gen_replay' in request.form
        close_room = 'close_room' in request.form
        age_restricted = 'age_restricted' in request.form
        spoof_plat = int(request.form.get('spoof_plat', '0'))
        thumbnail_path = request.form.get('thumbnail', '')
        cookies_file = request.form.get('cookies_file')
        
        # Validate required fields
        if not title:
            flash('Stream title is required', 'error')
            return redirect(url_for('index'))
        
        if not hashtag_id:
            flash('Stream topic is required', 'error')
            return redirect(url_for('index'))
        
        # Check if game tag is required for gaming
        if hashtag_id == "5" and not game_tag_id:
            flash('Game tag is required for Gaming topic', 'error')
            return redirect(url_for('index'))
        
        # Check if spoofing parameters are required
        if spoof_plat in [1, 2]:
            openudid = request.form.get('openudid', '')
            device_id = request.form.get('device_id', '')
            iid = request.form.get('iid', '')
            
            if not all([openudid, device_id, iid]):
                flash('OpenUDID, Device ID, and IID are required for mobile spoofing', 'error')
                return redirect(url_for('index'))
        else:
            openudid = ""
            device_id = ""
            iid = ""
        
        try:
            with Stream(cookies_file) as s:
                created = s.createStream(
                    title,
                    hashtag_id,
                    game_tag_id,
                    gen_replay,
                    close_room,
                    age_restricted,
                    priority_region,
                    spoof_plat,
                    openudid,
                    device_id,
                    iid,
                    thumbnail_path
                )
                
                if created:
                    # Save the cookies file for future use (like ending stream)
                    save_last_used_cookies(cookies_file)
                    
                    # Prepare stream data for saving
                    stream_data = {
                        'title': title,
                        'baseStreamUrl': s.baseStreamUrl,
                        'streamKey': s.streamKey,
                        'streamShareUrl': s.streamShareUrl,
                        'hashtag_id': hashtag_id,
                        'game_tag_id': game_tag_id,
                        'priority_region': priority_region,
                        'created_at': time.time()
                    }
                    
                    # Save stream data
                    stream_id = str(int(time.time()))
                    file_path = f"stream_{stream_id}.json"
                    with open(file_path, 'w') as f:
                        json.dump(stream_data, f)
                    
                    return render_template('stream_created.html',
                                          baseStreamUrl=s.baseStreamUrl,
                                          streamKey=s.streamKey,
                                          streamShareUrl=s.streamShareUrl,
                                          title=title,
                                          stream_id=stream_id,
                                          now={'year': time.strftime('%Y')})
                else:
                    flash('Failed to create stream. Please check your settings and try again.', 'error')
                    return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error creating stream: {str(e)}', 'error')
            return redirect(url_for('index'))

    @app.route('/end_stream', methods=['POST'])
    def end_stream():
        """End the current stream"""
        cookies_file = load_last_used_cookies()
        
        if not cookies_file:
            flash('No active stream found or cookies file missing', 'error')
            return redirect(url_for('index'))
        
        try:
            with Stream(cookies_file) as s:
                if s.endStream():
                    flash('Stream ended successfully', 'success')
                else:
                    flash('Failed to end stream', 'error')
        except Exception as e:
            flash(f'Error ending stream: {str(e)}', 'error')
        
        return redirect(url_for('index'))

    @app.route('/generate_device')
    def generate_device_route():
        """Generate device info for spoofing"""
        openudid, device_id, iid = generate_device()
        
        if openudid:
            return jsonify({
                'openudid': openudid,
                'device_id': device_id,
                'iid': iid
            })
        else:
            return jsonify({'error': 'Failed to generate device info'}), 500

    @app.route('/list_cookies')
    def list_cookies_route():
        """List available cookies files"""
        cookies_files = find_cookies_files()
        cookies_info = []
        
        for file_path in cookies_files:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            try:
                with open(file_path, 'r') as f:
                    cookies_data = json.load(f)
                
                if isinstance(cookies_data, list):
                    cookie_count = len(cookies_data)
                    domains = set()
                    for cookie in cookies_data:
                        if 'domain' in cookie:
                            domains.add(cookie['domain'])
                    
                    domain_str = ', '.join(sorted(domains)) if domains else 'No domain info'
                    cookies_info.append({
                        'file_name': file_name,
                        'file_path': file_path,
                        'file_size': file_size,
                        'cookie_count': cookie_count,
                        'domains': domain_str
                    })
            except Exception as e:
                cookies_info.append({
                    'file_name': file_name,
                    'file_path': file_path,
                    'file_size': file_size,
                    'error': str(e)
                })
        
        return render_template('cookies_list.html', cookies_info=cookies_info, now={'year': time.strftime('%Y')})

    @app.route('/random_title')
    def random_title():
        """Generate a random title from file"""
        file_path = request.args.get('file', 'tittle.txt')
        title = generate_title_from_file(file_path)
        
        if title:
            return jsonify({'title': title})
        else:
            return jsonify({'error': 'Failed to generate title'}), 500

    @app.route('/streams')
    def streams_list():
        """Display list of streams with RTMP and stream key information"""
        streams = []
        
        # Cari file stream yang tersimpan (misalnya dalam format JSON)
        stream_files = glob.glob("stream_*.json")
        
        for file_path in stream_files:
            try:
                with open(file_path, 'r') as f:
                    stream_data = json.load(f)
                    
                # Ekstrak informasi file
                file_name = os.path.basename(file_path)
                created_time = os.path.getctime(file_path)
                created_date = datetime.fromtimestamp(created_time).strftime('%Y-%m-%d %H:%M:%S')
                
                # Tambahkan ke list streams
                streams.append({
                    'id': file_name.replace('stream_', '').replace('.json', ''),
                    'title': stream_data.get('title', 'Unknown'),
                    'baseStreamUrl': stream_data.get('baseStreamUrl', ''),
                    'streamKey': stream_data.get('streamKey', ''),
                    'streamShareUrl': stream_data.get('streamShareUrl', ''),
                    'created_date': created_date,
                    'file_path': file_path
                })
            except Exception as e:
                print(f"Error reading stream file {file_path}: {e}")
        
        return render_template('streams_list.html', streams=streams, now={'year': time.strftime('%Y')})

    @app.route('/delete_stream/<stream_id>', methods=['POST'])
    def delete_stream(stream_id):
        """Delete a stream"""
        file_path = f"stream_{stream_id}.json"
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return jsonify({
                    'success': True,
                    'message': 'Stream deleted successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Stream not found'
                }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

def main():
    # Create command line parser
    parser = argparse.ArgumentParser(description="TikTok Stream Key Generator (CLI Version)")
    
    # Add arguments
    parser.add_argument("--title", type=str, help="Stream title")
    parser.add_argument("--topic", type=str, help=f"Stream topic. Options: {', '.join(topics.values())}")
    parser.add_argument("--game", type=str, help="Game tag (required if topic is Gaming)")
    parser.add_argument("--region", type=str, help="Priority region (e.g., US, ID, etc.)")
    parser.add_argument("--replay", action="store_true", help="Generate replay after stream ends")
    parser.add_argument("--close-room", action="store_true", default=True, help="Close room when stream ends")
    parser.add_argument("--age-restricted", action="store_true", help="Mark stream as age restricted")
    parser.add_argument("--spoof-plat", type=int, choices=[0, 1, 2], default=0, 
                        help="Platform spoofing: 0=None, 1=Mobile Camera, 2=Mobile Screenshare")
    parser.add_argument("--thumbnail", type=str, help="Path to thumbnail image")
    parser.add_argument("--cookies-dir", type=str, default="cookies", help="Directory containing cookies files (default: cookies)")
    parser.add_argument("--config", type=str, default="config.json", help="Path to config JSON file")
    parser.add_argument("--save-config", action="store_true", help="Save current settings to config file")
    parser.add_argument("--end-stream", action="store_true", help="End current stream")
    parser.add_argument("--list-games", action="store_true", help="List available game tags")
    parser.add_argument("--list-cookies", action="store_true", help="List available cookies files")
    parser.add_argument("--select-cookies", action="store_true", help="Interactively select cookies file")
    parser.add_argument("--random-title", type=str, help="Generate random title from specified file")
    parser.add_argument("--generate-device", action="store_true", help="Generate device info for spoofing")
    parser.add_argument("--no-select", action="store_true", help="Skip account selection and use first valid cookies")
    parser.add_argument("--web", action="store_true", help="Run as web application")
    parser.add_argument("--port", type=int, default=5000, help="Port for web application")
    
    # Spoofing arguments
    parser.add_argument("--openudid", type=str, help="OpenUDID for mobile spoofing")
    parser.add_argument("--device-id", type=str, help="Device ID for mobile spoofing")
    parser.add_argument("--iid", type=str, help="Install ID for mobile spoofing")
    
    args = parser.parse_args()
    
    # Handle web mode
    if args.web:
        if not FLASK_AVAILABLE:
            print("Error: Flask is not installed. Please install it with: pip install flask")
            return
            
        # Create templates directory if it doesn't exist
        if not os.path.exists('templates'):
            os.makedirs('templates')
        
        # Check if template files exist
        required_templates = ['index.html', 'stream_created.html', 'cookies_list.html', 'streams_list.html']
        for template in required_templates:
            if not os.path.exists(f'templates/{template}'):
                print(f"Error: templates/{template} not found. Please make sure the template files are in the correct location.")
                return
        
        app.run(host='0.0.0.0', port=args.port, debug=True)
        return
    
    # Handle special commands
    if args.list_games:
        games = fetch_game_tags()
        print("Available game tags:")
        for game_id, game_name in games.items():
            print(f"{game_id}: {game_name}")
        return
    
    if args.list_cookies:
        list_cookies_info(args.cookies_dir)
        return
    
    if args.select_cookies:
        selected_cookies = select_cookies_file(args.cookies_dir)
        if selected_cookies:
            if validate_cookies_file(selected_cookies):
                print(f"Selected cookies file: {selected_cookies}")
                # Copy selected cookies to default location for easier use
                import shutil
                shutil.copy2(selected_cookies, "cookies.json")
                print("Cookies file copied to cookies.json for future use.")
            else:
                print("Selected cookies file is invalid.")
        return
    
    if args.generate_device:
        openudid, device_id, iid = generate_device()
        if openudid:
            print(f"Generated device info:")
            print(f"OpenUDID: {openudid}")
            print(f"Device ID: {device_id}")
            print(f"IID: {iid}")
        return
    
    if args.end_stream:
        # Try to load the last used cookies file first
        cookies_file = load_last_used_cookies()
        
        if not cookies_file:
            # If no last used cookies, find the first valid cookies file
            cookies_files = find_cookies_files(args.cookies_dir)
            
            if cookies_files:
                for file_path in cookies_files:
                    if validate_cookies_file(file_path):
                        cookies_file = file_path
                        break
        
        if not cookies_file:
            print("No valid cookies files found.")
            return
        
        account_name = os.path.basename(cookies_file).replace('.json', '')
        print(f"Using account: {account_name}")
        print(f"Cookies file: {cookies_file}")
        
        try:
            with Stream(cookies_file) as s:
                if s.endStream():
                    print("Stream ended successfully.")
                else:
                    print("Failed to end stream.")
        except Exception as e:
            print(f"Error ending stream: {e}")
        return
    
    # Load config if it exists
    config = load_config(args.config)
    
    # Override config with command line arguments
    if args.title:
        config["title"] = args.title
    elif args.random_title:
        title = generate_title_from_file(args.random_title)
        if title:
            config["title"] = title
            print(f"Generated title: {title}")
    
    if args.topic:
        # Find topic ID from topic name
        topic_id = None
        for tid, tname in topics.items():
            if tname.lower() == args.topic.lower():
                topic_id = tid
                break
        if topic_id:
            config["hashtag_id"] = topic_id
        else:
            print(f"Error: Invalid topic '{args.topic}'. Valid options are: {', '.join(topics.values())}")
            return
    
    if args.game:
        games = fetch_game_tags()
        game_id = None
        for gid, gname in games.items():
            if gname.lower() == args.game.lower():
                game_id = gid
                break
        if game_id:
            config["game_tag_id"] = game_id
        else:
            print(f"Error: Invalid game '{args.game}'. Use --list-games to see available games.")
            return
    
    if args.region:
        config["priority_region"] = args.region
    
    if args.replay:
        config["generate_replay"] = True
    
    if not args.close_room:
        config["close_room_when_close_stream"] = False
    
    if args.age_restricted:
        config["age_restricted"] = True
    
    if args.spoof_plat:
        config["spoof_plat"] = args.spoof_plat
    
    if args.thumbnail:
        config["thumbnail_path"] = args.thumbnail
    
    if args.openudid:
        config["openudid"] = args.openudid
    
    if args.device_id:
        config["device_id"] = args.device_id
    
    if args.iid:
        config["iid"] = args.iid
    
    # Save config if requested
    if args.save_config:
        save_config(config, args.config)
    
    # Check required parameters
    if "title" not in config or not config["title"]:
        print("Error: Stream title is required. Use --title or --random-title.")
        return
    
    if "hashtag_id" not in config or not config["hashtag_id"]:
        print("Error: Stream topic is required. Use --topic.")
        return
    
    # Check if game tag is required for gaming
    if config["hashtag_id"] == "5" and ("game_tag_id" not in config or not config["game_tag_id"]):
        print("Error: Game tag is required for Gaming topic. Use --game.")
        return
    
    # Check if spoofing parameters are required
    if config.get("spoof_plat", 0) in [1, 2]:
        if not all(k in config for k in ["openudid", "device_id", "iid"]):
            print("Error: OpenUDID, Device ID, and IID are required for mobile spoofing.")
            print("Use --generate-device to generate these values or provide them manually.")
            return
    
    # Get cookies file
    cookies_files = find_cookies_files(args.cookies_dir)
    cookies_file = None
    
    if not cookies_files:
        print("No cookies files found.")
        return
    
    # If there are multiple cookies files and no --no-select flag, let user choose
    if len(cookies_files) == 1 or args.no_select:
        # Only one cookies file or --no-select flag, use first valid automatically
        for file_path in cookies_files:
            if validate_cookies_file(file_path):
                cookies_file = file_path
                break
    else:
        # Multiple cookies files, show selection menu
        print("Available accounts:")
        valid_cookies = []
        for i, file_path in enumerate(cookies_files, 1):
            if validate_cookies_file(file_path):
                valid_cookies.append(file_path)
                file_name = os.path.basename(file_path)
                # Try to extract account name from filename
                account_name = file_name.replace('.json', '')
                # Remove "cookies/" prefix if present
                if account_name.startswith('cookies/'):
                    account_name = account_name[8:]
                print(f"{i}. {account_name}")
        
        if not valid_cookies:
            print("No valid cookies files found.")
            return
        
        while True:
            try:
                choice = input(f"\nSelect account (1-{len(valid_cookies)}) or 'q' to quit: ")
                if choice.lower() == 'q':
                    return
                
                choice = int(choice)
                if 1 <= choice <= len(valid_cookies):
                    cookies_file = valid_cookies[choice - 1]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(valid_cookies)}")
            except ValueError:
                print("Please enter a valid number or 'q' to quit")
    
    if not cookies_file:
        print("No valid cookies files found.")
        return
    
    account_name = os.path.basename(cookies_file).replace('.json', '')
    print(f"Using account: {account_name}")
    print(f"Cookies file: {cookies_file}")
    
    # Save the cookies file for future use (like ending stream)
    save_last_used_cookies(cookies_file)
    
    # Create stream
    try:
        with Stream(cookies_file) as s:
            created = s.createStream(
                config.get("title", ""),
                config.get("hashtag_id", ""),
                config.get("game_tag_id", "0"),
                config.get("generate_replay", False),
                config.get("close_room_when_close_stream", True),
                config.get("age_restricted", False),
                config.get("priority_region", ""),
                config.get("spoof_plat", 0),
                config.get("openudid", ""),
                config.get("device_id", ""),
                config.get("iid", ""),
                config.get("thumbnail_path", "")
            )
            
            if created:
                print("Stream created successfully!")
                print(f"Server URL: {s.baseStreamUrl}")
                print(f"Stream Key: {s.streamKey}")
                print(f"Share URL: {s.streamShareUrl}")
                print("\nRTMP URL:")
                print(f"{s.baseStreamUrl}/{s.streamKey}")
            else:
                print("Failed to create stream.")
    except Exception as e:
        print(f"Error creating stream: {e}")


if __name__ == "__main__":
    main()

app.run(host='0.0.0.0', port=5000, debug=True)
