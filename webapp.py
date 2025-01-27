from flask import Flask, render_template, request, flash, send_file, session
from websummary import create_brochure
import markdown
import os
import io

app = Flask(__name__)
app.secret_key = 'development-key'  # Just for testing

print("OPENAI_API_KEY present:", bool(os.getenv('OPENAI_API_KEY')))
print("OPENAI_API_KEY length:", len(os.getenv('OPENAI_API_KEY', '')))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        url = request.form.get('url')
        language = request.form.get('language')
        
        if not url:
            flash('Please enter a URL', 'error')
            return render_template('index.html')
        
        try:
            markdown_content = create_brochure(name, url, language)
            if markdown_content:
                # Store content in session for download
                session['markdown_content'] = markdown_content
                
                # Convert markdown to HTML for display
                html_content = markdown.markdown(markdown_content)
                return render_template('result.html', 
                                    name=name, 
                                    url=url, 
                                    content=html_content)
            else:
                flash('Could not generate summary', 'error')
                return render_template('index.html')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return render_template('index.html')
            
    return render_template('index.html')

@app.route('/download')
def download():
    markdown_content = session.get('markdown_content', '')
    if markdown_content:
        # Create a BytesIO object and write the markdown content to it
        buffer = io.BytesIO()
        buffer.write(markdown_content.encode('utf-8'))
        buffer.seek(0)
        
        # Send the file as a downloadable attachment
        return send_file(buffer, as_attachment=True, download_name='summary.md', mimetype='text/markdown')
    else:
        flash('No markdown content available for download', 'error')
        return render_template('index.html')

# Function to translate summary using OpenAI API
def translate_summary(summary, language):
    # Placeholder for OpenAI API call to translate the summary
    # This function should call OpenAI API with the summary and target language
    # and return the translated summary
    return summary  # Replace with actual translation logic

if __name__ == '__main__':
    # Enable debug mode for development
    app.run(host='0.0.0.0', port=5000) 