from flask import Flask, request, render_template_string, jsonify
import platform
import json
import datetime

app = Flask(__name__)

# Database to store visitor info
DB_FILE = "visitor_info.json"

@app.route('/')
def capture_info():
    # Get client info
    user_agent = request.headers.get('User-Agent')
    ip_address = request.remote_addr
    timestamp = datetime.datetime.now().isoformat()
    
    # Collect OS info
    os_info = {
        'platform': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'architecture': platform.architecture()[0],
        'node': platform.node(),
        'uname': ' '.join(platform.uname())
    }
    
    # Store in JSON database
    entry = {
        'timestamp': timestamp,
        'ip': ip_address,
        'user_agent': user_agent,
        'os_info': os_info
    }
    
    # Append to DB file
    try:
        with open(DB_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []
    
    data.append(entry)
    
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    
    return "Info captured successfully"

@app.route('/admin')
def admin_page():
    # Load visitor data
    try:
        with open(DB_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []
    
    # Reverse the list to show newest entries first
    data.reverse()
    
    # HTML template for admin page
    html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard - Visitor Information</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .visitor-entry { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 4px; background-color: #fafafa; position: relative; }
        .timestamp { font-weight: bold; color: #007bff; }
        .section { margin: 10px 0; }
        .section-title { font-weight: bold; color: #555; background-color: #e9ecef; padding: 5px; border-radius: 3px; }
        .entry-count { text-align: center; margin-bottom: 20px; color: #666; font-style: italic; }
        .delete-btn { position: absolute; top: 10px; right: 10px; background-color: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; }
        .delete-btn:hover { background-color: #c82333; }
        .confirm-delete { background-color: #ffc107; color: #212529; }
        .confirm-delete:hover { background-color: #e0a800; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Admin Dashboard - Visitor Information</h1>
        <div class="entry-count">Total Entries: {{ data|length }}</div>
        {% for entry in data %}
        <div class="visitor-entry">
            <button class="delete-btn" onclick="deleteEntry({{ loop.index0 }})">Delete</button>
            <div class="section">
                <span class="timestamp">{{ entry.timestamp }}</span> | 
                <strong>IP:</strong> {{ entry.ip }}
            </div>
            <div class="section">
                <div class="section-title">User Agent</div>
                <div>{{ entry.user_agent }}</div>
            </div>
            <div class="section">
                <div class="section-title">OS Information</div>
                <div><strong>Platform:</strong> {{ entry.os_info.platform }}</div>
                <div><strong>Release:</strong> {{ entry.os_info.release }}</div>
                <div><strong>Version:</strong> {{ entry.os_info.version }}</div>
                <div><strong>Machine:</strong> {{ entry.os_info.machine }}</div>
                <div><strong>Processor:</strong> {{ entry.os_info.processor }}</div>
                <div><strong>Architecture:</strong> {{ entry.os_info.architecture }}</div>
                <div><strong>Node:</strong> {{ entry.os_info.node }}</div>
            </div>
        </div>
        {% endfor %}
    </div>
    <script>
        function deleteEntry(index) {
            if (confirm('Are you sure you want to delete this entry?')) {
                fetch('/delete_entry', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: 'index=' + index
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Entry deleted successfully');
                        location.reload();
                    } else {
                        alert('Error deleting entry: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error deleting entry');
                });
            }
        }
    </script>
</body>
</html>
    '''
    
    return render_template_string(html_template, data=data)

@app.route('/delete_entry', methods=['POST'])
def delete_entry():
    index = int(request.form.get('index'))
    
    # Load existing data
    try:
        with open(DB_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return jsonify({'success': False, 'message': 'Database file not found'})
    
    # Check if index is valid
    if 0 <= index < len(data):
        # Remove the entry at the specified index
        data.pop(index)
        
        # Save updated data
        with open(DB_FILE, 'w') as f:
            json.dump(data, f, indent=4)
            
        return jsonify({'success': True, 'message': 'Entry deleted successfully'})
    else:
        return jsonify({'success': False, 'message': 'Invalid index'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)