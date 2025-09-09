#!/usr/bin/env python3
import subprocess
import argparse
import sys
import time
import signal
import os
from pathlib import Path


class TikTokStreamer:
    def __init__(self):
        self.ffmpeg_process = None
        self.running = False

    def signal_handler(self, signum, frame):
        """Handle Ctrl+C and other signals to gracefully stop streaming"""
        print(f"\nReceived signal {signum}, stopping stream...")
        self.stop_stream()
        sys.exit(0)

    def start_stream(self, input_source, rtmp_url, 
                    video_codec='libx264', preset='veryfast', 
                    maxrate='3000k', bufsize='6000k',
                    audio_codec='aac', audio_bitrate='128k',
                    loop=True, custom_ffmpeg_path=None):
        """
        Start streaming to TikTok using FFmpeg
        
        Args:
            input_source: Path to video file or stream source
            rtmp_url: RTMP URL from TikTok stream key generator
            video_codec: Video codec (default: libx264)
            preset: FFmpeg preset (default: veryfast)
            maxrate: Maximum video bitrate (default: 3000k)
            bufsize: Buffer size (default: 6000k)
            audio_codec: Audio codec (default: aac)
            audio_bitrate: Audio bitrate (default: 128k)
            loop: Loop video input (default: True)
            custom_ffmpeg_path: Custom path to ffmpeg executable
        """
        
        # Check if input source exists
        if not Path(input_source).exists():
            print(f"Error: Input source '{input_source}' not found")
            return False
        
        # Determine ffmpeg executable
        ffmpeg_cmd = custom_ffmpeg_path if custom_ffmpeg_path else 'ffmpeg'
        
        # Build ffmpeg command
        command = [ffmpeg_cmd]
        
        # Add input options
        command.extend(['-re'])  # Read input at native frame rate
        
        if loop:
            command.extend(['-stream_loop', '-1'])  # Loop input video
        
        command.extend(['-i', input_source])  # Input file
        
        # Add video options
        command.extend(['-c:v', video_codec])
        command.extend(['-preset', preset])
        command.extend(['-maxrate', maxrate])
        command.extend(['-bufsize', bufsize])
        command.extend(['-vf', 'format=yuv420p'])
        command.extend(['-pix_fmt', 'yuv420p'])
        
        # Add audio options
        command.extend(['-c:a', audio_codec])
        command.extend(['-b:a', audio_bitrate])
        
        # Add output format and URL
        command.extend(['-f', 'flv'])
        command.append(rtmp_url)
        
        print(f"Starting stream with command:")
        print(" ".join(command))
        print(f"Input: {input_source}")
        print(f"Output: {rtmp_url}")
        print("Press Ctrl+C to stop streaming...")
        
        try:
            # Start ffmpeg process
            self.ffmpeg_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            self.running = True
            
            # Monitor the process
            while self.running and self.ffmpeg_process.poll() is None:
                # Read and display ffmpeg output in real-time
                if self.ffmpeg_process.stderr:
                    line = self.ffmpeg_process.stderr.readline()
                    if line:
                        print(line.strip())
                
                time.sleep(0.1)
            
            # Check if process completed normally
            if self.ffmpeg_process.poll() is not None:
                return_code = self.ffmpeg_process.returncode
                if return_code == 0:
                    print("Stream completed successfully")
                else:
                    print(f"Stream ended with return code: {return_code}")
                
                # Show any remaining output
                if self.ffmpeg_process.stderr:
                    remaining_output = self.ffmpeg_process.stderr.read()
                    if remaining_output:
                        print("Remaining output:")
                        print(remaining_output.strip())
                
                return return_code == 0
            
        except FileNotFoundError:
            print(f"Error: '{ffmpeg_cmd}' not found. Please install FFmpeg or provide custom path with --ffmpeg-path")
            return False
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            self.stop_stream()
            return False
        except Exception as e:
            print(f"Error starting stream: {e}")
            return False

    def stop_stream(self):
        """Stop the current stream"""
        if self.ffmpeg_process and self.running:
            print("Stopping stream...")
            self.ffmpeg_process.terminate()
            
            # Wait for graceful shutdown
            try:
                self.ffmpeg_process.wait(timeout=5)
                print("Stream stopped gracefully")
            except subprocess.TimeoutExpired:
                print("Force killing stream...")
                self.ffmpeg_process.kill()
                self.ffmpeg_process.wait()
                print("Stream force stopped")
            
            self.running = False
            self.ffmpeg_process = None
        else:
            print("No active stream to stop")

    def get_stream_info(self, rtmp_url):
        """Extract stream information from RTMP URL"""
        try:
            # Parse RTMP URL to get server and stream key
            if 'rtmp://' in rtmp_url:
                # Extract server URL
                stream_key_start = rtmp_url.rfind('/') + 1
                server_url = rtmp_url[:stream_key_start]
                stream_key = rtmp_url[stream_key_start:]
                
                return {
                    'server_url': server_url,
                    'stream_key': stream_key,
                    'full_url': rtmp_url
                }
            else:
                return {'full_url': rtmp_url}
        except Exception as e:
            print(f"Error parsing RTMP URL: {e}")
            return {'full_url': rtmp_url}


def load_rtmp_url_from_file(file_path='rtmp_url.txt'):
    """Load RTMP URL from a text file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
            if content:
                return content
    except FileNotFoundError:
        print(f"File '{file_path}' not found")
    except Exception as e:
        print(f"Error reading RTMP URL from file: {e}")
    return None


def save_rtmp_url_to_file(rtmp_url, file_path='rtmp_url.txt'):
    """Save RTMP URL to a text file"""
    try:
        with open(file_path, 'w') as f:
            f.write(rtmp_url.strip())
        print(f"RTMP URL saved to {file_path}")
    except Exception as e:
        print(f"Error saving RTMP URL to file: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="TikTok FFmpeg Streamer - Stream video to TikTok Live",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python3 ffmpeg.py video.mp4 "rtmp://server/stream_key"
  
  # Load RTMP URL from file
  python3 ffmpeg.py video.mp4 --load-url
  
  # Save RTMP URL to file
  python3 ffmpeg.py video.mp4 "rtmp://server/stream_key" --save-url
  
  # Custom settings
  python3 ffmpeg.py video.mp4 "rtmp://server/stream_key" --preset ultrafast --maxrate 2500k
  
  # No loop
  python3 ffmpeg.py video.mp4 "rtmp://server/stream_key" --no-loop
  
  # Custom ffmpeg path
  python3 ffmpeg.py video.mp4 "rtmp://server/stream_key" --ffmpeg-path /usr/local/bin/ffmpeg
        """
    )
    
    parser.add_argument('input_source', help='Path to video file or stream source')
    parser.add_argument('rtmp_url', nargs='?', help='RTMP URL from TikTok stream key generator')
    
    # Video options
    parser.add_argument('--video-codec', default='libx264', help='Video codec (default: libx264)')
    parser.add_argument('--preset', default='veryfast', 
                       choices=['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
                       help='FFmpeg preset (default: veryfast)')
    parser.add_argument('--maxrate', default='3000k', help='Maximum video bitrate (default: 3000k)')
    parser.add_argument('--bufsize', default='6000k', help='Buffer size (default: 6000k)')
    
    # Audio options
    parser.add_argument('--audio-codec', default='aac', help='Audio codec (default: aac)')
    parser.add_argument('--audio-bitrate', default='128k', help='Audio bitrate (default: 128k)')
    
    # Streaming options
    parser.add_argument('--no-loop', action='store_true', help='Disable video looping')
    parser.add_argument('--ffmpeg-path', help='Custom path to ffmpeg executable')
    
    # File operations
    parser.add_argument('--load-url', action='store_true', help='Load RTMP URL from rtmp_url.txt')
    parser.add_argument('--save-url', action='store_true', help='Save RTMP URL to rtmp_url.txt')
    parser.add_argument('--url-file', default='rtmp_url.txt', help='File to load/save RTMP URL (default: rtmp_url.txt)')
    
    # Info options
    parser.add_argument('--info', action='store_true', help='Show stream information and exit')
    parser.add_argument('--stop', action='store_true', help='Stop any running stream and exit')
    
    args = parser.parse_args()
    
    # Create streamer instance
    streamer = TikTokStreamer()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, streamer.signal_handler)
    signal.signal(signal.SIGTERM, streamer.signal_handler)
    
    # Handle stop command
    if args.stop:
        streamer.stop_stream()
        print("Stream stopped")
        return
    
    # Load RTMP URL from file if requested
    rtmp_url = args.rtmp_url
    if args.load_url:
        rtmp_url = load_rtmp_url_from_file(args.url_file)
        if not rtmp_url:
            print("No RTMP URL found in file")
            return
    
    # Validate RTMP URL
    if not rtmp_url:
        print("Error: RTMP URL is required")
        print("Provide it as argument or use --load-url")
        return
    
    # Show stream info if requested
    if args.info:
        info = streamer.get_stream_info(rtmp_url)
        print("Stream Information:")
        print(f"  Full URL: {info.get('full_url', 'N/A')}")
        if 'server_url' in info:
            print(f"  Server: {info['server_url']}")
            print(f"  Stream Key: {info['stream_key']}")
        return
    
    # Save RTMP URL to file if requested
    if args.save_url:
        save_rtmp_url_to_file(rtmp_url, args.url_file)
    
    # Check if input source exists
    if not Path(args.input_source).exists():
        print(f"Error: Input source '{args.input_source}' not found")
        return
    
    # Start streaming
    success = streamer.start_stream(
        input_source=args.input_source,
        rtmp_url=rtmp_url,
        video_codec=args.video_codec,
        preset=args.preset,
        maxrate=args.maxrate,
        bufsize=args.bufsize,
        audio_codec=args.audio_codec,
        audio_bitrate=args.audio_bitrate,
        loop=not args.no_loop,
        custom_ffmpeg_path=args.ffmpeg_path
    )
    
    if success:
        print("Streaming completed successfully")
    else:
        print("Streaming failed")
        sys.exit(1)


if __name__ == "__main__":
    main()