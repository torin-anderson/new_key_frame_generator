import pandas as pd
from video_screenshot import Keyframe

kf = Keyframe()

# change the file here for each set
df = pd.read_csv("./get_keyframes/duration_set_5.csv")

video_ids = df['videoId'].tolist()
video_ids = [id.split(':')[1] for id in video_ids]

for _id in video_ids:
    kf.generate_keyframes(_id)
