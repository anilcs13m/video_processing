import os
import cv2
import time
from concurrent.futures import ThreadPoolExecutor


class SharpestFrameExtractor:
    """
    Extracts the sharpest frame per second from a video using the Laplacian variance method.
    """

    def __init__(self, output_dir):
        """
        Initialize the extractor with a directory to save sharpest frames.
        
        Args:
            output_dir (str): Directory to save the output sharpest frames.
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _process_second(self, second, frames, laps, video_name):
        """
        Save the sharpest frame for a given second.

        Args:
            second (int): The second index.
            frames (list): List of frames in that second.
            laps (list): Laplacian variances for each frame.
            video_name (str): Base name of the video.
        """
        if frames:
            sharpest_frame = frames[laps.index(max(laps))]
            save_path = os.path.join(self.output_dir, f"{video_name}_sec{second:04d}.png")
            cv2.imwrite(save_path, sharpest_frame)
            return save_path
        return None

    def extract_sharpest_per_second(self, video_path, max_workers=4):
        """
        Extract the sharpest frame for every second of the video.

        Args:
            video_path (str): Path to the input video.
            max_workers (int): Number of threads to use for saving frames.
        """
        cap = cv2.VideoCapture(video_path)

        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        total_seconds = int(frame_count / fps)

        video_name = os.path.splitext(os.path.basename(video_path))[0]
        print(f"Video: {video_name}, FPS: {fps}, Duration: {total_seconds}s")

        saved_paths = []
        executor = ThreadPoolExecutor(max_workers=max_workers)
        futures = []

        for second in range(total_seconds):
            arr_frame = []
            arr_lap = []

            for _ in range(fps):
                success, frame = cap.read()
                if not success:
                    break
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                arr_lap.append(laplacian_var)
                arr_frame.append(frame)

            # Submit saving to thread pool
            futures.append(executor.submit(self._process_second, second, arr_frame, arr_lap, video_name))

        cap.release()

        for f in futures:
            path = f.result()
            if path:
                saved_paths.append(path)

        print(f"Saved {len(saved_paths)} sharpest frames (1 per second) to '{self.output_dir}'")


# -------------------------
# Usage Example
# -------------------------

if __name__ == "__main__":
    output_dir = "video_frames"
    video_path = "video_name.mp4"

    start_time = time.time()
    extractor = SharpestFrameExtractor(output_dir)
    extractor.extract_sharpest_per_second(video_path, max_workers=4)
    print("--- %.2f seconds ---" % (time.time() - start_time))

