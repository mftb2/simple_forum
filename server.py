from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import html


# Run this in Powershell to run the server: cd simple_forum, python server.py

# Run this in browser to operate site: http://127.0.0.1:8000/

# Store users and posts in memory
users = {}
posts = []

# HTML templates
TEMPLATES = {
    "base": """
<!DOCTYPE html>
<html>
<head>
    <title>Simple Forum</title>
</head>
<body>
    <nav>
        {nav}
    </nav>
    <div>
        {content}
    </div>
</body>
</html>
""",
    "home": """
<h1>Welcome to Simple Forum</h1>
<ul>
    {posts}
</ul>
""",
    "signup": """
<h1>Sign Up</h1>
<form method="POST" action="/signup">
    Username: <input type="text" name="username"><br>
    Password: <input type="password" name="password"><br>
    <input type="submit" value="Sign Up">
</form>
""",
    "login": """
<h1>Login</h1>
<form method="POST" action="/login">
    Username: <input type="text" name="username"><br>
    Password: <input type="password" name="password"><br>
    <input type="submit" value="Login">
</form>
""",
    "new_post": """
<h1>New Post</h1>
<form method="POST" action="/new_post">
    Content: <textarea name="content"></textarea><br>
    <input type="submit" value="Post">
</form>
"""
}

class SimpleForumHandler(BaseHTTPRequestHandler):
    def render_template(self, template_name, **kwargs):
        nav = ""
        if "username" in self.headers.get("Cookie", ""):
            nav = '''
            <a href="/">Home</a>
            <a href="/new_post">New Post</a>
            <a href="/logout">Logout</a>
            '''
        else:
            nav = '''
            <a href="/login">Login</a>
            <a href="/signup">Sign Up</a>
            '''
        content = TEMPLATES[template_name].format(**kwargs)
        return TEMPLATES["base"].format(nav=nav, content=content)

    def do_GET(self):
        if self.path == "/":
            posts_html = "".join(f"<li><strong>{post['username']}</strong>: {html.escape(post['content'])}</li>" for post in posts)
            content = self.render_template("home", posts=posts_html)
        elif self.path == "/signup":
            content = self.render_template("signup")
        elif self.path == "/login":
            content = self.render_template("login")
        elif self.path == "/new_post":
            content = self.render_template("new_post")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = urllib.parse.parse_qs(self.rfile.read(content_length).decode())

        if self.path == "/signup":
            username = post_data["username"][0]
            password = post_data["password"][0]
            if username in users:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Username already exists")
                return
            users[username] = password
            self.send_response(302)
            self.send_header("Location", "/login")
            self.end_headers()
        elif self.path == "/login":
            username = post_data["username"][0]
            password = post_data["password"][0]
            if users.get(username) != password:
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b"Invalid credentials")
                return
            self.send_response(302)
            self.send_header("Location", "/")
            self.send_header("Set-Cookie", f"username={username}")
            self.end_headers()
        elif self.path == "/new_post":
            if "username" not in self.headers.get("Cookie", ""):
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b"Unauthorized")
                return
            username = self.headers.get("Cookie").split("=")[1]
            content = post_data["content"][0]
            posts.append({"username": username, "content": content})
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()

    def do_LOGOUT(self):
        self.send_response(302)
        self.send_header("Location", "/")
        self.send_header("Set-Cookie", "username=; expires=Thu, 01 Jan 1970 00:00:00 GMT")
        self.end_headers()

def run(server_class=HTTPServer, handler_class=SimpleForumHandler, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
