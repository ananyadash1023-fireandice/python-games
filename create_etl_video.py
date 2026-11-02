import base64
import json
import os
import shutil
import subprocess
import tempfile
import textwrap
import wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont


WIDTH = 1280
HEIGHT = 720
FPS = 24
PAUSE_SECONDS = 0.35
BACKGROUND = "#101426"
PANEL = "#1b2238"
TEXT = "#f3f5ff"
MUTED = "#aab5d0"
MINT = "#75dfbd"
PINK = "#ff7894"
BLUE = "#83caff"
GOLD = "#ffd166"
OUTPUT = Path(__file__).with_name("etl_memory_match_intro.mp4")

SCENES = (
    {
        "speaker": "Alex",
        "voice": "Microsoft Zira Desktop",
        "title": "MEET ETL MEMORY MATCH",
        "narration": (
            "Meet ETL Memory Match, a fun little game that teaches the basics "
            "of a data pipeline. I'm Alex."
        ),
        "visual": "intro",
    },
    {
        "speaker": "Sam",
        "voice": "Microsoft David Desktop",
        "title": "EVERY RECORD HAS A MATCH",
        "narration": (
            "And I'm Sam. Each customer record appears twice: once messy, "
            "and once cleaned. Match the same ID."
        ),
        "visual": "pair",
    },
    {
        "speaker": "Alex",
        "voice": "Microsoft Zira Desktop",
        "title": "HOW TO PLAY",
        "narration": (
            "Click a tile to reveal its data, then click another. "
            "Remember the customer IDs and find all eight pairs."
        ),
        "visual": "play",
    },
    {
        "speaker": "Sam",
        "voice": "Microsoft David Desktop",
        "title": "1. EXTRACT",
        "narration": (
            "Match one raw tile with the clean tile that has the same ID. "
            "Each correct pair extracts a record from the source."
        ),
        "visual": "extract",
    },
    {
        "speaker": "Alex",
        "voice": "Microsoft Zira Desktop",
        "title": "2. TRANSFORM",
        "narration": (
            "After all eight pairs are found, transform the records. "
            "Names are tidied, emails are lowercased, and amounts become numbers."
        ),
        "visual": "transform",
    },
    {
        "speaker": "Sam",
        "voice": "Microsoft David Desktop",
        "title": "3. LOAD",
        "narration": (
            "Now load the cleaned records. The game saves them into "
            "a CSV warehouse file you can open and inspect."
        ),
        "visual": "load",
    },
    {
        "speaker": "Alex",
        "voice": "Microsoft Zira Desktop",
        "title": "NEED A HINT?",
        "narration": (
            "If you get stuck, choose Give Me a Hint. It can point out a pair "
            "or remind you what to do next."
        ),
        "visual": "hint",
    },
    {
        "speaker": "Sam",
        "voice": "Microsoft David Desktop",
        "title": "READY TO PLAY?",
        "narration": (
            "Run Python etl underscore memory underscore match dot py, "
            "flip the cards, and build your first ETL pipeline. Have fun!"
        ),
        "visual": "finish",
    },
)

POWERSHELL_TTS = r"""
param(
    [Parameter(Mandatory=$true)][string]$ScenesJsonBase64,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$json = [Text.Encoding]::UTF8.GetString(
    [Convert]::FromBase64String($ScenesJsonBase64)
)
$scenes = ConvertFrom-Json -InputObject $json
$available = New-Object System.Speech.Synthesis.SpeechSynthesizer
$voiceNames = @($available.GetInstalledVoices() | ForEach-Object {
    $_.VoiceInfo.Name
})
$available.Dispose()
for ($i = 0; $i -lt $scenes.Count; $i++) {
    $scene = $scenes[$i]
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    if ($voiceNames -contains $scene.voice) {
        $synth.SelectVoice($scene.voice)
    }
    $path = Join-Path $OutputDirectory ('scene_{0:D2}.wav' -f $i)
    $synth.SetOutputToWaveFile($path)
    $synth.Speak($scene.narration)
    $synth.Dispose()
}
"""

STARS = tuple(
    (
        (index * 197 + 41) % WIDTH,
        (index * 113 + 19) % HEIGHT,
        1 + index % 3,
        0.8 + (index % 4) * 0.35,
    )
    for index in range(52)
)


def font(size, bold=False):
    windows_fonts = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    filename = "segoeuib.ttf" if bold else "segoeui.ttf"
    font_path = windows_fonts / filename
    if font_path.exists():
        return ImageFont.truetype(str(font_path), size)
    return ImageFont.load_default(size=size)


def centered_text(draw, xy, text, selected_font, fill, anchor="mm"):
    draw.text(xy, text, font=selected_font, fill=fill, anchor=anchor)


def rounded_box(draw, bounds, fill, outline=None, radius=18, width=2):
    draw.rounded_rectangle(
        bounds, radius=radius, fill=fill, outline=outline, width=width
    )


def draw_card(draw, x, y, width, height, label, title, lines, color, progress=1.0):
    lift = int(10 * (1 - progress))
    bounds = (x, y - lift, x + width, y + height - lift)
    rounded_box(draw, (x + 5, y + 7 - lift, x + width + 5, y + height + 7 - lift),
                "#090d18", radius=16)
    rounded_box(draw, bounds, "#f5f6fb", color, radius=16, width=3)
    rounded_box(draw, (x + 12, y + 12 - lift, x + width - 12, y + 48 - lift),
                color, radius=9, width=1)
    centered_text(draw, (x + width / 2, y + 30 - lift), label,
                  font(18, True), "#101426")
    centered_text(draw, (x + width / 2, y + 75 - lift), title,
                  font(15, True), "#1c2941")
    for line_index, line in enumerate(lines):
        centered_text(
            draw,
            (x + width / 2, y + 112 + line_index * 29 - lift),
            line,
            font(13),
            "#31405b",
        )


def draw_back_card(draw, x, y, width=120, height=145, progress=1.0):
    lift = int(8 * (1 - progress))
    rounded_box(draw, (x + 5, y + 7 - lift, x + width + 5, y + height + 7 - lift),
                "#090d18", radius=16)
    rounded_box(draw, (x, y - lift, x + width, y + height - lift),
                "#303c5a", "#8191b2", radius=16, width=3)
    rounded_box(draw, (x + 11, y + 11 - lift, x + width - 11, y + height - 11 - lift),
                "#252f4b", "#586788", radius=11)
    centered_text(draw, (x + width / 2, y + height / 2 - lift),
                  "✦", font(38, True), GOLD)
    centered_text(draw, (x + width / 2, y + height / 2 + 38 - lift),
                  "DATA", font(13, True), "#d8e2ff")


def draw_person(draw, x, y, name, shirt, hair, talking):
    bob = int(3 * np.sin(talking * 2.8))
    draw.ellipse((x - 76, y + 147, x + 76, y + 174), fill="#090d18")
    draw.rounded_rectangle(
        (x - 83, y + 38 + bob, x + 83, y + 180 + bob),
        radius=48, fill=shirt,
    )
    draw.rounded_rectangle(
        (x - 20, y + 20 + bob, x + 20, y + 63 + bob),
        radius=13, fill="#d99873",
    )
    draw.ellipse((x - 58, y - 83 + bob, x + 58, y + 46 + bob),
                 fill="#efb68e", outline="#ffddc6", width=3)
    draw.pieslice((x - 61, y - 91 + bob, x + 61, y + 21 + bob),
                  start=180, end=360, fill=hair)
    draw.ellipse((x - 43, y - 87 + bob, x - 5, y - 48 + bob), fill=hair)
    draw.ellipse((x + 8, y - 86 + bob, x + 48, y - 46 + bob), fill=hair)
    eye_y = y - 14 + bob
    draw.ellipse((x - 28, eye_y, x - 19, eye_y + 7), fill="#182136")
    draw.ellipse((x + 18, eye_y, x + 27, eye_y + 7), fill="#182136")
    draw.arc((x - 17, y - 5 + bob, x + 18, y + 22 + bob),
             start=10, end=170, fill="#9a4f54", width=3)
    if talking:
        draw.ellipse((x - 8, y + 6 + bob, x + 9, y + 23 + bob), fill="#8f414c")
    centered_text(draw, (x, y + 200), name, font(17, True), TEXT)


def draw_speech_bubble(draw, speaker, narration):
    bounds = (218, 112, 1062, 282)
    rounded_box(draw, bounds, "#202944", "#526486", radius=25, width=2)
    if speaker == "Alex":
        tail = [(330, 277), (365, 277), (313, 315)]
    else:
        tail = [(915, 277), (950, 277), (969, 315)]
    draw.polygon(tail, fill="#202944")
    draw.line((tail[0], tail[2], tail[1]), fill="#526486", width=2)
    wrapped = textwrap.fill(narration, width=58)
    centered_text(draw, (640, 196), wrapped, font(24, True), TEXT)


def draw_pipeline(draw, active):
    stages = (
        ("EXTRACT", "Match data", BLUE),
        ("TRANSFORM", "Clean it", "#b99aff"),
        ("LOAD", "Save CSV", MINT),
    )
    left = 255
    for index, (name, subtitle, color) in enumerate(stages):
        x = left + index * 270
        is_active = index == active
        fill = "#263451" if is_active else "#1a2238"
        outline = color if is_active else "#34415d"
        rounded_box(draw, (x, 569, x + 228, 641), fill, outline, radius=15, width=3)
        centered_text(draw, (x + 114, 593), name, font(16, True), color)
        centered_text(draw, (x + 114, 620), subtitle, font(13), MUTED)
        if index < 2:
            centered_text(draw, (x + 247, 605), "›", font(34, True), MUTED)


def draw_grid(draw, timestamp):
    start_x, start_y = 350, 360
    for index in range(8):
        row, column = divmod(index, 4)
        x = start_x + column * 145
        y = start_y + row * 93
        if index in (1, 6) and timestamp > 1.4:
            is_raw = index == 1
            draw_card(
                draw, x, y, 116, 78,
                "C01", "RAW" if is_raw else "CLEAN",
                ["ADA ..." if is_raw else "Ada ..."],
                PINK if is_raw else BLUE,
            )
        else:
            rounded_box(draw, (x, y, x + 116, y + 78), "#303c5a",
                        "#66789c", radius=12, width=2)
            centered_text(draw, (x + 58, y + 37), "✦", font(24, True), GOLD)


def draw_scene_art(draw, scene, progress, timestamp):
    visual = scene["visual"]
    if visual == "intro":
        draw_card(draw, 306, 350, 172, 190, "C01", "RAW DATA",
                  ["ADA ...", "EMAIL@EXAMPLE"], PINK, progress)
        centered_text(draw, (620, 442), "↔", font(58, True), GOLD)
        draw_card(draw, 765, 350, 172, 190, "C01", "CLEAN DATA",
                  ["Ada Lovelace", "email@example"], BLUE, progress)
        draw_pipeline(draw, -1)
    elif visual == "pair":
        draw_card(draw, 360, 369, 190, 186, "C03", "RAW",
                  ["KATHERINE ...", "Email@EXAMPLE"], PINK, progress)
        centered_text(draw, (640, 456), "?", font(55, True), GOLD)
        draw_card(draw, 730, 369, 190, 186, "C03", "CLEAN",
                  ["Katherine ...", "email@example"], BLUE, progress)
        draw_pipeline(draw, -1)
    elif visual == "play":
        draw_grid(draw, timestamp)
        rounded_box(draw, (414, 551, 867, 609), "#263451", "#526486", radius=14)
        centered_text(draw, (640, 580), "Click  •  Remember  •  Match", font(19, True), GOLD)
        draw_pipeline(draw, -1)
    elif visual == "extract":
        draw_back_card(draw, 360, 377, 132, 160, progress)
        centered_text(draw, (554, 452), "→", font(55, True), BLUE)
        draw_card(draw, 638, 370, 175, 188, "C02", "MATCHED",
                  ["RAW + CLEAN", "Same customer ID"], MINT, progress)
        rounded_box(draw, (846, 398, 986, 528), "#263451", BLUE, radius=17, width=3)
        centered_text(draw, (916, 441), "EXTRACT", font(16, True), BLUE)
        centered_text(draw, (916, 480), "✓", font(32, True), MINT)
        draw_pipeline(draw, 0)
    elif visual == "transform":
        draw_card(draw, 310, 369, 215, 187, "C01", "BEFORE",
                  ["  ADA LOVELACE  ", " EMAIL@EXAMPLE.COM ", "$1,245.50"], PINK, progress)
        centered_text(draw, (640, 458), "→", font(55, True), GOLD)
        draw_card(draw, 754, 369, 215, 187, "C01", "AFTER",
                  ["Ada Lovelace", "email@example.com", "1245.50"], BLUE, progress)
        draw_pipeline(draw, 1)
    elif visual == "load":
        draw_card(draw, 296, 378, 190, 167, "C01", "CLEAN ROW",
                  ["Ada Lovelace", "email@example.com"], MINT, progress)
        centered_text(draw, (548, 460), "→", font(55, True), GOLD)
        rounded_box(draw, (650, 365, 981, 540), "#1b263b", MINT, radius=18, width=3)
        centered_text(draw, (816, 394), "etl_warehouse.csv", font(20, True), MINT)
        for line_index, row in enumerate(
            ("id,name,email,amount", "C01,Ada,...,1245.50", "C02,Grace,...,980.00")
        ):
            draw.text((677, 433 + line_index * 31), row, font=font(13), fill=TEXT)
        draw_pipeline(draw, 2)
    elif visual == "hint":
        draw_grid(draw, timestamp)
        rounded_box(draw, (420, 547, 858, 606), "#3a3151", "#a98df5", radius=15, width=2)
        centered_text(draw, (639, 576), "💡  Hint: find the same ID!", font(18, True), GOLD)
        draw_pipeline(draw, -1)
    else:
        for index, (label, color) in enumerate(
            (("EXTRACT", BLUE), ("TRANSFORM", "#b99aff"), ("LOAD", MINT))
        ):
            x = 340 + index * 210
            draw_back_card(draw, x, 386, 122, 147, progress)
            rounded_box(draw, (x - 5, 534, x + 128, 565), "#202944", color, radius=10)
            centered_text(draw, (x + 61, 550), label, font(13, True), color)
        draw_pipeline(draw, -1)


def draw_frame(scene, scene_index, local_time, duration, frame_number):
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)

    for index, (x, start_y, size, speed) in enumerate(STARS):
        y = (start_y - local_time * 23 * speed) % HEIGHT
        brightness = 120 + int(55 * (0.5 + 0.5 * np.sin(local_time * 2 + index)))
        color = (brightness, brightness - 12, min(255, brightness + 40))
        draw.ellipse((x, y, x + size, y + size), fill=color)

    draw.text((52, 43), "ETL MEMORY MATCH", font=font(16, True), fill=MINT)
    draw.text((1228, 44), f"{scene_index + 1:02d} / {len(SCENES):02d}",
              font=font(15, True), fill=MUTED, anchor="ra")
    centered_text(draw, (640, 85), scene["title"], font(31, True), TEXT)

    draw_speech_bubble(draw, scene["speaker"], scene["narration"])
    talking = local_time if local_time < duration - 0.2 else 0
    draw_person(draw, 137, 420, "ALEX", "#735ec2", "#342c4d",
                talking if scene["speaker"] == "Alex" else 0)
    draw_person(draw, 1143, 420, "SAM", "#3b91a6", "#382640",
                talking if scene["speaker"] == "Sam" else 0)

    progress = min(1.0, local_time / 0.7)
    draw_scene_art(draw, scene, progress, local_time)
    return np.asarray(image, dtype=np.uint8)


def synthesize_narration(temp_dir):
    powershell = shutil.which("powershell.exe") or shutil.which("powershell")
    if powershell is None:
        raise RuntimeError("PowerShell is required for Windows' built-in narration voices.")

    scene_payload = json.dumps(
        [
            {"voice": scene["voice"], "narration": scene["narration"]}
            for scene in SCENES
        ]
    )
    payload_b64 = base64.b64encode(scene_payload.encode("utf-8")).decode("ascii")
    script_path = temp_dir / "synthesize_narration.ps1"
    script_path.write_text(POWERSHELL_TTS, encoding="utf-8-sig")

    subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script_path),
            "-ScenesJsonBase64",
            payload_b64,
            "-OutputDirectory",
            str(temp_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    wav_chunks = []
    scene_durations = []
    wave_params = None
    for index in range(len(SCENES)):
        segment_path = temp_dir / f"scene_{index:02d}.wav"
        with wave.open(str(segment_path), "rb") as audio:
            params = audio.getparams()
            frames = audio.readframes(audio.getnframes())
        signature = (params.nchannels, params.sampwidth, params.framerate, params.comptype)
        if wave_params is None:
            wave_params = params
            audio_signature = signature
        elif signature != audio_signature:
            raise RuntimeError("Windows speech produced narration segments with different audio formats.")

        duration = len(frames) / (params.nchannels * params.sampwidth * params.framerate)
        scene_durations.append(duration + PAUSE_SECONDS)
        wav_chunks.append(frames)
        silence_frames = round(params.framerate * PAUSE_SECONDS)
        wav_chunks.append(b"\x00" * silence_frames * params.nchannels * params.sampwidth)

    narration_path = temp_dir / "narration.wav"
    with wave.open(str(narration_path), "wb") as narration:
        narration.setparams(wave_params)
        narration.writeframes(b"".join(wav_chunks))
    return narration_path, scene_durations


def render_video(temp_dir, narration_path, scene_durations):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    silent_video = temp_dir / "silent_video.mp4"
    output_temp = temp_dir / "etl_memory_match_intro.mp4"
    encode_command = [
        ffmpeg, "-y", "-loglevel", "error",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS),
        "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium",
        "-crf", "22", "-pix_fmt", "yuv420p", str(silent_video),
    ]

    total_frames = sum(round(duration * FPS) for duration in scene_durations)
    print(f"Rendering {total_frames} frames at {WIDTH}x{HEIGHT}...")
    encoder = subprocess.Popen(encode_command, stdin=subprocess.PIPE)
    try:
        frame_number = 0
        for scene_index, (scene, duration) in enumerate(zip(SCENES, scene_durations)):
            scene_frames = round(duration * FPS)
            voice_duration = duration - PAUSE_SECONDS
            for scene_frame in range(scene_frames):
                local_time = min(scene_frame / FPS, voice_duration)
                frame = draw_frame(
                    scene, scene_index, local_time, voice_duration, frame_number
                )
                encoder.stdin.write(frame.tobytes())
                frame_number += 1
                if frame_number % (FPS * 5) == 0:
                    print(f"Rendered {frame_number} / {total_frames} frames")
        encoder.stdin.close()
        return_code = encoder.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, encode_command)
    except Exception:
        if encoder.stdin and not encoder.stdin.closed:
            encoder.stdin.close()
        encoder.kill()
        encoder.wait()
        raise

    mux_command = [
        ffmpeg, "-y", "-loglevel", "error",
        "-i", str(silent_video), "-i", str(narration_path),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        "-shortest", "-movflags", "+faststart", str(output_temp),
    ]
    subprocess.run(mux_command, check=True)
    shutil.copy2(output_temp, OUTPUT)
    return total_frames


def main():
    if os.name != "nt":
        raise SystemExit("This narrator uses Windows' built-in System.Speech voices.")
    if not shutil.which("powershell.exe") and not shutil.which("powershell"):
        raise SystemExit("PowerShell was not found; it is needed to create local narration.")

    with tempfile.TemporaryDirectory(prefix="etl-video-") as temp_name:
        temp_dir = Path(temp_name)
        narration_path, durations = synthesize_narration(temp_dir)
        total_frames = render_video(temp_dir, narration_path, durations)

    print(f"Created {OUTPUT} ({total_frames} frames, {sum(durations):.1f} seconds)")


if __name__ == "__main__":
    main()
