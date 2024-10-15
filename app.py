from flask import Flask, jsonify, render_template, send_from_directory
import os

app = Flask(__name__)

NOVEL_DIRS = 'novels\\'

def get_chapter_data(novel_name, chapter_number):
    """Read the chapter file for a specific novel and return the heading and content."""
    try:
        chapter_path = os.path.join(os.getcwd(), NOVEL_DIRS, novel_name, f"{chapter_number}")
        print(chapter_path)

        if not os.path.exists(chapter_path):
            return None, None

        with open(chapter_path, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
            if lines:
                chapter_heading = lines[0].strip()
                chapter_content = "\n".join(lines[1:])
                return {"heading": chapter_heading, "content": chapter_content}
    except FileNotFoundError:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    print("here")
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'), 'reader.png', mimetype='image/png')

@app.route('/<novel_name>/<int:chapter_number>', methods=['GET'])
def chapter(novel_name, chapter_number):
    chapter_data = get_chapter_data(novel_name, chapter_number)
    if chapter_data:
        return render_template('chapter.html', novel_name=novel_name, chapter_number=chapter_number, chapter_data=chapter_data)
    else:
        return "Chapter not found", 404
@app.route('/<novel_name>/<int:chapter_number>/', methods=['GET'])
def chapter_safe(novel_name, chapter_number):
    chapter_data = get_chapter_data(novel_name, chapter_number)
    if chapter_data:
        return render_template('chapter.html', novel_name=novel_name, chapter_number=chapter_number, chapter_data=chapter_data)
    else:
        return "Chapter not found", 404

@app.route('/api/<novel_name>/<int:chapter_number>', methods=['GET'])
def api_chapter(novel_name, chapter_number):
    chapter_data = get_chapter_data(novel_name, chapter_number)
    if chapter_data:
        return jsonify(chapter_data)
    else:
        return jsonify({"error": "Chapter not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)