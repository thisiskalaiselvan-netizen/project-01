from flask import Flask, render_template, request, redirect, session, url_for, send_file
from google.cloud import storage
from flask import redirect
import os
import io

app:app
app.secret_key = "secret123"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"

BUCKET_NAME = "kalai_project-02"   # 🔁 change only if bucket name different

def get_bucket():
    client = storage.Client()
    return client.bucket(BUCKET_NAME)

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            session["user"] = "admin"
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid login")

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- DASHBOARD ----------------
@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    bucket = get_bucket()
    files = [blob.name for blob in bucket.list_blobs()]
    return render_template("index.html", files=files)

# ---------------- UPLOAD ----------------
@app.route("/upload", methods=["POST"])
def upload():
    if "user" not in session:
        return redirect(url_for("login"))

    file = request.files["file"]
    if file.filename != "":
        bucket = get_bucket()
        blob = bucket.blob(file.filename)
        blob.upload_from_file(file)

    return redirect(url_for("index"))
#----------- VIEW -------------
@app.route("/view/<filename>")
def view_file(filename):
    bucket = get_bucket()
    blob = bucket.blob(filename)

    url = blob.generate_signed_url(
        version="v4",
        expiration=300,   # 5 minutes
        method="GET"
    )
    return redirect(url)

# ---------------- DOWNLOAD ----------------
@app.route("/download/<filename>")
def download(filename):
    if "user" not in session:
        return redirect(url_for("login"))

    bucket = get_bucket()
    blob = bucket.blob(filename)

    file_data = io.BytesIO()
    blob.download_to_file(file_data)
    file_data.seek(0)

    return send_file(file_data, download_name=filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
