from flask import Flask, request, send_file, Response
import asyncio
import edge_tts
import os

app = Flask(name)

@app.route("/api", methods=["GET"])
def text_to_speech():
    """Convert text to speech and return the MP3 file"""
    prompt = request.args.get("prompt")
    if not prompt:
        return {"error": "Missing 'prompt' query parameter."}, 400

    VOICE = "en-GB-SoniaNeural"
    OUTPUT_FILE = "output.mp3"

    async def convert_text_to_speech():
        communicate = edge_tts.Communicate(prompt, VOICE)
        await communicate.save(OUTPUT_FILE)

    # Run the TTS conversion asynchronously
    asyncio.run(convert_text_to_speech())

    # Return the MP3 file as an inline response
    def generate():
        with open(OUTPUT_FILE, "rb") as f:
            yield from f

    return Response(generate(), mimetype="audio/mpeg")

if name == "main":
    app.run(host="0.0.0.0", port=8000)
