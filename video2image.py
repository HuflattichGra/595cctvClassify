import os
import cv2
import csv
import argparse
from datetime import timedelta


def split_video(input_video, output_folder, segment_duration_seconds):
    """Split a video into segments."""
    cap = cv2.VideoCapture(input_video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = timedelta(seconds=int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps))

    start_time = 0
    segment_count = 0
    while start_time < duration.total_seconds():
        end_time = min(start_time + segment_duration_seconds, duration.total_seconds())
        output_video = os.path.join(output_folder, f"segment_{segment_count + 1}.mp4")

        cmd = f"ffmpeg -i '{input_video}' -ss {start_time} -to {end_time} -c copy '{output_video}'"
        os.system(cmd)  

        start_time = end_time
        segment_count += 1

    cap.release()
def extract_frames_and_create_csv(video_file, output_folder, csv_filename):
    if os.path.isfile(video_file):
        video_folder = os.path.dirname(video_file)
        output_folder = os.path.join(video_folder, output_folder)
    else:
        video_folder = video_file
    if output_folder == "output":
        output_folder = os.getcwd() + "/output"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    csv_path = os.path.join(output_folder, csv_filename)
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['image_name', 'video_name', 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        image_counter = 1
        video_counter = 1

        for video_file in os.listdir(video_folder):
            if os.path.isfile(os.path.join(video_folder, video_file)):
                ext = os.path.splitext(video_file)[1].lower()
                if ext in ['.mp4', '.avi', '.mov', '.mkv']:
                    frame_count = 0
                    timestamp = 0

                    cap = cv2.VideoCapture(os.path.join(video_folder, video_file))
                    if not cap.isOpened():
                        print(f"Error opening video file: {video_file}")
                        continue

                    while True:
                        ret, frame = cap.read()
                        if not ret:
                            print(f"End of video: {video_file}")
                            break

                        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

                        if frame_count % 120 == 0:
                            output_filename = f"image_{image_counter}.jpg"
                            output_path = os.path.join(output_folder, output_filename)
                            print(f"Saving frame to: {output_path}")
                            cv2.imwrite(output_path, frame)

                            writer.writerow({
                                'image_name': output_filename,
                                'video_name': video_file,
                                'timestamp': timestamp,
                            })

                            image_counter += 1

                        frame_count += 1

                    cap.release()
                    video_counter += 1

    print("Frame extraction and CSV generation completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract frames from a video and create a CSV file.')
    parser.add_argument('--video-file', type=str, required=True, help='Path to the video file')
    parser.add_argument('--output-folder', type=str, default="output", help='Output folder for images and CSV (default: "output")')
    parser.add_argument('--csv-filename', type=str, default="frames_info.csv", help='Name of the CSV file (default: "frames_info.csv")')

    args = parser.parse_args()

    extract_frames_and_create_csv(args.video_file, args.output_folder, args.csv_filename)