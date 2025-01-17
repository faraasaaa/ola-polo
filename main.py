from flask import Flask, request, jsonify, send_file
import asyncio
import edge_tts
import os
import threading
import time


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
AUTO_DELETE_TIME = 300  # Time in seconds before deleting the file

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/api", methods=["GET"])
def text_to_speech():
    """Convert text to speech, save as MP3, and return a download link"""
    prompt = request.args.get("prompt")
    if not prompt:
        return {"error": "Missing 'prompt' query parameter."}, 400

    VOICE = "en-GB-SoniaNeural"
    filename = f"{int(time.time())}.mp3"
    output_file = os.path.join(UPLOAD_FOLDER, filename)

    async def convert_text_to_speech():
        communicate = edge_tts.Communicate(prompt, VOICE)
        await communicate.save(output_file)

    # Run the TTS conversion asynchronously
    asyncio.run(convert_text_to_speech())

    # Start a thread to delete the file after a delay
    def auto_delete_file(file_path, delay):
        time.sleep(delay)
        if os.path.exists(file_path):
            os.remove(file_path)

    threading.Thread(target=auto_delete_file, args=(output_file, AUTO_DELETE_TIME), daemon=True).start()

    # Return the download link
    download_link = f"http://{request.host}/{UPLOAD_FOLDER}/{filename}"
    return jsonify({"download_link": download_link})

@app.route(f"/{UPLOAD_FOLDER}/<filename>", methods=["GET"])
def download_file(filename):
    """Serve the MP3 file for download"""
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return {"error": "File not found."}, 404

    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
