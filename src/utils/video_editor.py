import math
import logging
import os

import ffmpeg

import vcodec
import log_wrapper

logger = logging.getLogger(__name__)


# leave one core for other tasks
MAX_THREAD = str(max(os.cpu_count() - 1, 1))

# ffmpeg_log_level = "info"
ffmpeg_log_level = "warning"


class VideoEditor:
    def __init__(self) -> None:
        pass

    @staticmethod
    def ratio_calculator(width, height):
        gcd = math.gcd(width, height)
        return width // gcd, height // gcd

    @staticmethod
    def get_metadata(input_video_path):
        probe = ffmpeg.probe(input_video_path)
        return next(stream for stream in probe["streams"] if stream["codec_type"] == "video")

    @staticmethod
    def get_width_height(video_path):
        # Probe video file to get stream information
        video_stream = VideoEditor.get_metadata(video_path)

        # Extract width and height
        width = int(video_stream["width"])
        height = int(video_stream["height"])

        # Calculate aspect ratio
        return width, height

    @staticmethod
    def get_width_height(video_path):
        # Probe video file to get stream information
        video_stream = VideoEditor.get_metadata(video_path)

        # Extract width and height
        width = int(video_stream["width"])
        height = int(video_stream["height"])

        # Calculate aspect ratio
        return width, height

    @staticmethod
    def get_duration(video_path) -> float:
        metadata = VideoEditor.get_metadata(video_path)
        if "duration" in metadata:
            return float(metadata["duration"])
        probe = ffmpeg.probe(video_path)
        # Extracting duration
        return float(probe["format"]["duration"])

    @staticmethod
    @log_wrapper.log_inputs
    def calculate_scale_dimensions(width, height, target_width, target_height):
        """Calculate the scale dimensions while maintaining aspect ratio."""

        scale_width = target_width
        scale_height = round(height * (target_width / width))

        if scale_height > target_height:
            scale_height = target_height
            scale_width = round(width * (target_height / height))

        return scale_width, scale_height

    @staticmethod
    @log_wrapper.log_inputs
    def pad_video(
        video_path: str, out_video_path: str, new_width: int, new_height: int, frame_rate=30, vcodec=vcodec.VCodec.H264
    ):
        width, height = VideoEditor.get_width_height(video_path)

        scale_width, scale_height = VideoEditor.calculate_scale_dimensions(width, height, new_width, new_height)

        input_video = ffmpeg.input(video_path)
        (
            ffmpeg.input(video_path)
            .filter("scale", new_width, new_height)
            .output(input_video.audio, out_video_path, vcodec=vcodec.value, acodec="aac", r=frame_rate)
            .global_args("-loglevel", ffmpeg_log_level)
            .run(overwrite_output=True)
        )

        # Calculate padding
        pad_x = (new_width - scale_width) // 2
        pad_y = (new_height - scale_height) // 2

        # Run ffmpeg command to scale and pad the video
        (
            ffmpeg.input(video_path)
            .filter("scale", scale_width, scale_height)
            .filter("pad", new_width, new_height, pad_x, pad_y, color="black")
            .output(input_video.audio, out_video_path, vcodec=vcodec.value, acodec="aac", r=frame_rate)
            .global_args("-loglevel", ffmpeg_log_level)
            .run(overwrite_output=True)
        )

    @staticmethod
    @log_wrapper.log_inputs
    def cut_video(input_file, output_file, start_time=-1, duration=-1):
        (
            ffmpeg.input(input_file, ss=start_time, t=duration)
            .output(output_file, codec="copy")  # Using 'copy' to avoid re-encoding and preserve original codecs
            .global_args("-loglevel", ffmpeg_log_level)
            .run(overwrite_output=True)
        )

    @staticmethod
    @log_wrapper.log_inputs
    def pad_video_blured(
        video_path: str, out_video_path: str, new_width: int, new_height: int, frame_rate=30, vcodec=vcodec.VCodec.H264
    ):
        width, height = VideoEditor.get_width_height(video_path)

        scale_width, scale_height = VideoEditor.calculate_scale_dimensions(width, height, new_width, new_height)

        blure_width, blure_height = -1, -1
        if new_width == scale_width:
            blure_height = new_height
        if new_height == scale_height:
            blure_width = new_width

        input_video = ffmpeg.input(video_path)

        # Set up the FFmpeg command chain
        (
            ffmpeg.input(video_path)
            # First, create a blurred background
            .filter("scale", blure_width, blure_height)  # Scale video to fit the new width, keeping aspect ratio
            .filter("boxblur", 10)  # Apply blur
            .filter("crop", new_width, new_height)  # Crop to the target height
            # Then, overlay the scaled video on top of the blurred background
            .overlay(
                ffmpeg.input(video_path).filter("scale", scale_width, scale_height),
                x=(new_width - scale_width) // 2,
                y=(new_height - scale_height) // 2,
            )
            # Output configuration
            .output(input_video.audio, out_video_path, vcodec=vcodec.value, acodec="aac", r=frame_rate)
            .global_args("-loglevel", ffmpeg_log_level)
            .run(overwrite_output=True)
        )

    @staticmethod
    @log_wrapper.log_inputs
    def scale_video(
        video_path: str, out_video_path: str, new_width: int, new_height: int, frame_rate=30, vcodec=vcodec.VCodec.H264
    ):
        input_video = ffmpeg.input(video_path)
        (
            ffmpeg.input(video_path)
            .filter("scale", new_width, new_height)
            .output(input_video.audio, out_video_path, vcodec=vcodec.value, acodec="aac", r=frame_rate)
            .global_args("-loglevel", ffmpeg_log_level)
            .run(overwrite_output=True)
        )

    @staticmethod
    @log_wrapper.log_inputs
    def strech_video(
        video_path: str, out_video_path: str, new_width: int, new_height: int, frame_rate=30, vcodec=vcodec.VCodec.H264
    ):
        input_video = ffmpeg.input(video_path)
        filter_complex = f"scale={new_width}:{new_height}"
        w, h = VideoEditor.ratio_calculator(new_width, new_height)
        (
            ffmpeg.input(video_path)
            .output(
                input_video.audio,
                out_video_path,
                vf=filter_complex,
                vcodec=vcodec.value,
                acodec="aac",
                aspect=f"{w}:{h}",
                r=frame_rate,
            )
            .global_args("-loglevel", ffmpeg_log_level)
            .run(overwrite_output=True)
        )

    @staticmethod
    @log_wrapper.log_inputs
    def merge_video_audio(video_path, audio_path, output_path):
        # Define the video and audio inputs
        input_video = ffmpeg.input(video_path)
        input_audio = ffmpeg.input(audio_path)

        # Merge video and audio
        (
            ffmpeg.output(input_video, input_audio, output_path, vcodec="copy", acodec="aac", strict="experimental")
            .global_args("-loglevel", ffmpeg_log_level)
            .run(overwrite_output=True)
        )

    @staticmethod
    @log_wrapper.log_inputs
    def vertical_combine_videos(video1_path, video2_path, output_path, frame_rate=30, vcodec=vcodec.VCodec.H264):
        # Input streams for both videos
        duration1 = VideoEditor.get_duration(video1_path)
        duration2 = VideoEditor.get_duration(video2_path)
        shortest_duration = min(duration1, duration2)

        input1 = ffmpeg.input(video1_path, t=shortest_duration)
        input2 = ffmpeg.input(video2_path, t=shortest_duration)

        # Vertically stack the videos
        stacked_video = ffmpeg.filter_([input1, input2], "vstack")
        # Output file configuration
        (
            ffmpeg.output(stacked_video, input1.audio, output_path, vcodec=vcodec.value, r=frame_rate, acodec="aac", format="mp4")
            .global_args("-loglevel", ffmpeg_log_level)
            .run(overwrite_output=True)
        )

    @staticmethod
    @log_wrapper.log_inputs
    def concatenate_videos(videos: list[str], output_path: str, sar="1/1", width=-1, height=-1, vcodec=vcodec.VCodec.H264):
        # Common resolution and SAR for all videos
        max_width, max_height = 0, 0
        for video in videos:
            width, height = VideoEditor.get_width_height(video)
            max_width = max(width, max_width)
            max_height = max(height, max_height)
        if width == -1:
            width = max_width
        if height == -1:
            height = max_height

        # Prepare a list of scaled and SAR adjusted video and audio streams
        scaled_streams = []
        for video in videos:
            input_stream = ffmpeg.input(video)
            video_stream = input_stream.video
            width, height = VideoEditor.get_width_height(video)
            video_stream = input_stream.video.filter("scale", width, height).filter("setsar", sar)
            scaled_streams.extend([video_stream, input_stream.audio])

        # Concatenate all videos and audio streams
        joined = ffmpeg.concat(*scaled_streams, v=1, a=1).node

        # Output the concatenated streams
        (
            ffmpeg.output(joined[0], joined[1], output_path, vcodec=vcodec.value, acodec="aac")
            .global_args("-loglevel", ffmpeg_log_level)
            .run(overwrite_output=True)
        )


# None Audio verison
#  @staticmethod
# def strech_video(video_path : str, out_video_path : str,
#                  new_width : int,new_height : int,
#                  frame_rate = 30, vcodec = vcodec.VCodec.H264):
#     input_video = ffmpeg.input(video_path)
#     filter_complex=f"scale={new_width}:{new_height}"
#     filter_complex = f"scale={new_width}:{new_height}"
#     w, h = VideoEditor.ratio_calculator(new_width, new_height)

#     # Build FFmpeg command
#     input_video = ffmpeg.input(video_path)
#     output_args = {
#         'vf': filter_complex,
#         'vcodec': vcodec.value,
#         'aspect': f'{w}:{h}',
#         'r': frame_rate
#     }
#     probe = ffmpeg.probe(video_path)
#     has_audio = any(stream['codec_type'] == 'audio' for stream in probe['streams'])

#     if has_audio:
#         # If audio stream exists, include it in the output
#         output_args['acodec'] = 'aac'

#     (
#         ffmpeg
#         .output(input_video, out_video_path, **output_args)
#         .run(overwrite_output=True)
#     )


if __name__ == "__main__":
    video_path1 = "/home/debian/ai-studio/tmp/youtube/I CANT BELIEVING SHE SAID THIS shorts youtubeshorts 🥰🤣🤣.mp4"
    VideoEditor.pad_video_blured(video_path1, "./test.mp4", 1080, 1080)
