
import os
import math
import tempfile
import subprocess
from flask import Flask, request, send_file, jsonify

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 250 * 1024 * 1024

@app.get("/")
def home():
    return jsonify({
        "status": "online",
        "service": "Prite Itik FFmpeg",
        "message": "MP4 rendering server is ready"
    })

@app.post("/render")
def render():
    images = request.files.getlist("images")
    audio = request.files.get("audio")
    
    try:
        duration = float(request.form.get("duration", 60))
    except ValueError:
        return jsonify({"error": "Invalid duration"}), 400

    if not images or len(images) > 12:
        return jsonify({"error": "Upload 1 to 12 images"}), 400

    if duration < 10 or duration > 90:
        return jsonify({"error": "Duration must be 10 to 90 seconds"}), 400

    allowed = {".jpg", ".jpeg", ".png", ".webp"}

    with tempfile.TemporaryDirectory() as folder:
        clips = []

        for index, image in enumerate(images):
            ext = os.path.splitext(image.filename)[1].lower()
            if ext not in allowed:
                return jsonify({"error": "Unsupported image format"}), 400

            image_path = os.path.join(folder, f"image_{index}{ext}")
            clip_path = os.path.join(folder, f"clip_{index}.mp4")
            image.save(image_path)

            segment = duration / len(images)
            frames = math.ceil(segment * 30)

            command = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-framerate", "30",
                "-i", image_path,
                "-vf",
                "scale=1080:1920:force_original_aspect_ratio=increase,"
                "crop=1080:1920,"
                "zoompan=z='min(zoom+0.0005,1.12)':"
                "x='iw/2-(iw/zoom/2)':"
                "y='ih/2-(ih/zoom/2)':"
                "d=1:s=1080x1920:fps=30,"
                "format=yuv420p",
                "-frames:v", str(frames),
                "-an",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-pix_fmt", "yuv420p",
                clip_path
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return jsonify({
                    "error": "Video rendering failed",
                    "details": result.stderr[-2000:]
                }), 500

            clips.append(clip_path)

        concat_file = os.path.join(folder, "clips.txt")
        with open(concat_file, "w") as file:
            for clip in clips:
                file.write(f"file '{clip}'\n")

        silent_video = os.path.join(folder, "silent.mp4")
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            silent_video
        ], check=True, capture_output=True)

        output = os.path.join(folder, "prite-itik.mp4")

        if audio and audio.filename:
            audio_path = os.path.join(folder, "audio")
            audio.save(audio_path)

            subprocess.run([
                "ffmpeg", "-y",
                "-i", silent_video,
                "-i", audio_path,
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-af", "apad",
                "-t", str(duration),
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
                output
            ], check=True, capture_output=True)
        else:
            subprocess.run([
                "ffmpeg", "-y",
                "-i", silent_video,
                "-t", str(duration),
                "-c:v", "copy",
                "-movflags", "+faststart",
                output
            ], check=True, capture_output=True)

        return send_file(
            output,
            mimetype="video/mp4",
            as_attachment=True,
            download_name="prite-itik.mp4"
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
      
