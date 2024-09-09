import cv2
from pytubefix import YouTube
from io import BytesIO
import os
import tempfile
import logging


class Keyframe:
    
    def __init__(self):
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_dir, "screenshot.log"),
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )


    def generate_keyframes(self, _id: str) -> None:
        """
        Generate keyframes for a YouTube video at 5% intervals.

        Args:
            _id (str): YouTube video ID
        """
        try:
            output_dir = f'screenshot/{_id}'
            if os.path.exists(output_dir) and os.listdir(output_dir):
                logging.info(f'{_id}: Screenshots already exist, skipping processing')
            else:
                os.makedirs(output_dir, exist_ok=True)

                vid_url = f'https://www.youtube.com/watch?v={_id}'
                yt = YouTube(vid_url)
                stream = yt.streams.filter(progressive=True, file_extension='mp4').first()

                if not stream:
                    logging.error(f'{_id}: No suitable stream found')
                    raise Exception("No suitable stream found")
                else:
                    video_bytes = BytesIO()
                    stream.stream_to_buffer(video_bytes)
                    video_bytes.seek(0)

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
                        temp_video_file.write(video_bytes.read())
                        temp_video_path = temp_video_file.name

                    cap = cv2.VideoCapture(temp_video_path)

                    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                    fps = cap.get(cv2.CAP_PROP_FPS)

                    if fps == 0:
                        logging.error(f'{_id}: FPS value is zero, cannot calculate total duration')
                        raise Exception("FPS value is zero, cannot calculate total duration")


                    total_duration = frame_count / fps * 1000
                    interval = total_duration / 20
                    timestamps = [interval * i for i in range(1, 21)]
                    for time in timestamps:
                        cap.set(cv2.CAP_PROP_POS_MSEC, time)
                        ret, frame = cap.read()
                        if not ret:
                            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count - 1)
                            ret, frame = cap.read()

                        if ret:
                            cv2.imwrite(os.path.join(output_dir, f'frame_{int(time/1000)}.jpg'), frame)
                        else:
                            print(f'{_id}: Failed. Could not read frame at {int(time/1000)} seconds')
                            logging.error(f'{_id}: Failed. Could not read frame at {int(time/1000)} seconds')

                    cap.release()

                    os.remove(temp_video_path)
                    print(f'{_id}: Keyframes generated successfully')
                    logging.info(f'{_id}: Keyframes generated successfully')
        except Exception as e:
            print(f"An error occurred: {e}")
            logging.error(f"An error occurred: {e}")

                