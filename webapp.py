from flask import Flask, render_template, request, flash
from websummary import create_brochure
import markdown
import os

app = Flask(__name__)
app.secret_key = 'development-key'  # Just for testing

print("OPENAI_API_KEY present:", bool(os.getenv('OPENAI_API_KEY')))
print("OPENAI_API_KEY length:", len(os.getenv('OPENAI_API_KEY', '')))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        url = request.form.get('url')
        
        if not url:
            flash('Please enter a URL', 'error')
            return render_template('index.html')
        
        try:
            markdown_content = create_brochure(name, url)
            if markdown_content:
                # Convert markdown to HTML for display
                html_content = markdown.markdown(markdown_content)
                return render_template('result.html', 
                                    name=name, 
                                    url=url, 
                                    content=html_content,
                                    markdown_content=markdown_content)
            else:
                flash('Could not generate summary', 'error')
                return render_template('index.html')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return render_template('index.html')
            
    return render_template('index.html')

if __name__ == '__main__':
    # Enable debug mode for development
    app.run(host='0.0.0.0', port=5000) 