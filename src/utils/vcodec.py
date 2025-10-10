import enum


class VCodec(enum.Enum):
    H264 = "libx264"
    # H.264/MPEG-4 AVC - widely used format, good balance between quality and file size.

    H265 = "libx265"
    # H.265/HEVC - more efficient than H.264, especially for 4K and higher resolutions.

    MPEG4 = "mpeg4"
    # MPEG-4 Part 2 - older format, widely supported, less efficient than H.264.

    VP9 = "vp9"
    # Google's VP9 - open and royalty-free, efficient for web videos.

    RAWVIDEO = "rawvideo"
    # Uncompressed video - extremely large file sizes, used in professional editing.

    COPY = "copy"
    # Direct stream copy - no re-encoding, preserves original quality.

    VP8 = "libvpx"
    # VP8 - open video codec by Google, commonly used for web applications.

    AV1 = "libaom-av1"
    # AV1 - ultra-high-performance codec, efficient for high-resolution streaming.

    MJPEG = "mjpeg"
    # Motion JPEG - useful for videos where frame-by-frame access is important.

    PRORES = "prores"
    # Apple ProRes - high-quality, lossy compression for professional video editing.
