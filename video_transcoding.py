import os
import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime

class VideoTranscoder:
    def __init__(self):
        self.state_file = "transcoding_state.json"
        self.output_dir = "transcoded_output"
        self.temp_dir = "temp_transcode"
        self.log_file = "transcoding_log.json"
        
        # Create necessary directories
        Path(self.output_dir).mkdir(exist_ok=True)
        Path(self.temp_dir).mkdir(exist_ok=True)
        
        # Load previous state if exists
        self.state = self._load_state()
    
    def transcode_video(self, input_path, output_name,
                       resolutions=[(1920, 1080), (1280, 720), (854, 480)],
                       bitrates=['5000k', '2500k', '1200k'],
                       audio_bitrate='192k'):
        """
        Robust video transcoder with resume capability
        
        Parameters:
        - resolutions: List of target resolutions (width, height)
        - bitrates: Corresponding bitrates for each resolution
        - audio_bitrate: Audio bitrate for all outputs
        """

