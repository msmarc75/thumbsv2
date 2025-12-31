from flask import Flask, render_template, request, redirect, url_for
import os
from youtube_optimizer import YoutubeOptimizer
from youtube_fetcher import fetch_channel_videos

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/thumbnails'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/fetch_videos', methods=['POST'])
def fetch_videos():
    channel_url = request.form.get('channel_url')
    if not channel_url:
        return redirect(url_for('index'))
        
    videos = fetch_channel_videos(channel_url)
    return render_template('videos.html', videos=videos)

@app.route('/generate_selection', methods=['POST'])
def generate_selection():
    selected_titles = request.form.getlist('selected_titles')
    
    if not selected_titles:
        return redirect(url_for('index'))

    try:
        optimizer = YoutubeOptimizer()
        # Use sanitized titles for filenames as requested ("nommé en fonction du titre")
        # We pass use_uuids=False
        results = optimizer.process_videos(selected_titles, output_dir=app.config['UPLOAD_FOLDER'], use_uuids=False)
        return render_template('results.html', results=results)
    except Exception as e:
        return f"Une erreur est survenue: {e}", 500

@app.route('/generate', methods=['POST'])
def generate():
    titles_input = request.form.get('titles')
    if not titles_input:
        return redirect(url_for('index'))

    # Split by newlines and filter empty lines
    titles = [t.strip() for t in titles_input.split('\n') if t.strip()]
    
    # Limit to 10 for safety/cost
    titles = titles[:10]

    try:
        optimizer = YoutubeOptimizer()
        # For manual input, we can default to UUIDs or titles. Let's use UUIDs to be safe like before,
        # or titles if we want consistency. But the requirement for specific filenames was mentioned
        # in the context of the channel flow ("le fichier exporté [...] devra etre nommé en fonction du titre").
        # Let's keep UUIDs for the manual flow to avoid breaking existing expectation of previous step (web app safety),
        # but for the new flow we use titles.
        results = optimizer.process_videos(titles, output_dir=app.config['UPLOAD_FOLDER'], use_uuids=True)
        return render_template('results.html', results=results)
    except Exception as e:
        return f"Une erreur est survenue: {e}", 500

import os

if __name__ == "__main__":
    # Render définit une variable d'environnement PORT, on l'utilise par défaut
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
