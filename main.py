from flask import Flask, request, jsonify, send_from_directory
import openai
import base64
import os
import random
import string
from io import BytesIO
from PIL import Image
from typing import Tuple

app = Flask(__name__, static_folder="static")

# Configure your OpenAI API key
OPENAI_KEY =  os.getenv("OPENAI_API_KEY")  # Store API key in environment variable for security




def encode_image(image_path, image_size: Tuple[int, int]) -> str:
    with open(image_path, "rb") as image_file:
        image = Image.open(image_file).resize(image_size)
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        base64_encoded_data = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
    return f"data:image/jpeg;base64,{base64_encoded_data}"


def png_to_jpg(png_file_path, jpg_file_path):
    with Image.open(png_file_path) as img:
        img = img.convert('RGB')
        img.save(jpg_file_path, 'JPEG')

charset = string.ascii_uppercase + string.ascii_lowercase + string.digits
def genUID():
    return "".join([charset[random.randint(0, len(charset)-1)] for _ in range(0, 32)])

def upload_file(fn,fs):
    uid = genUID()
    ext = fn.split(".")[-1]
    if ext.lower() not in ["png", "jpg", "jpeg"]:
        return -1, "N/A"
    os.mkdir(f"./public/{uid}")
    fpath = f"./public/{uid}/shot.{ext}"
    fs.save(fpath)
    return 1, fpath

def upload_img(fs):
    response = openai.Image.create(
      file=fs,
      purpose="answers"  # You can choose other purposes like "fine-tune", "generation", etc.
    )
    # Get the image URL from the response
    image_url = response['data'][0]['url']
    return image_url


@app.route('/api/convert', methods=['POST'])
def convert_image_to_latex():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    image_file = request.files['image']
    r,fpath = upload_file(image_file.filename, image_file)

    if r != 1:
        return "CANT UPLOAD FILE",500
    #img_url = upload_img(image_file)
    # Read the image file into bytes
    #image_bytes = image_file.read()

    # Optionally, you can open the image using Pillow for further processing
    #image = Image.open(BytesIO(image_bytes))

    prompt = ("You are an AI model that converts mathematical images into LaTeX code. "
              "Extract the mathematical content from the given image and return only valid LaTeX code, "
              "without any additional text or explanation.")
    
    try:
        client = openai.OpenAI(api_key=OPENAI_KEY)
        response = client.chat.completions.create(
            model='gpt-4-turbo',
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": encode_image(fpath, (755, 103))
                        }
                    }
                ]}    
            ])
        print(response)
        latex_code = response.choices[0].message.content.strip()
        return jsonify({"latex": latex_code})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/')
def serve_index():
    return send_from_directory("static", "index.html")


if __name__ == '__main__':
    app.run(debug=True)