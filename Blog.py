import re
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parse = urlparse(self.path)
        paths = [
            (r'^/$', self.index),
            (r'^/(\d+)$', self.blog)
        ]
        
        for path, view in paths:
            if re.match(path, parse.path):
                return view()
            
        return super().do_GET()
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("utf-8")
        with open("media/blogs.json", "r", encoding="utf-8") as file:
            json_data = json.load(file)
            
        form = parse_qs(post_data)
        print(form)
        json_data[str(len(json_data) + 1)] = {"title": form["title"][0], "content": form["content"][0], "author": form["author"][0]}
        print(json_data)
        
        with open("media/blogs.json", "w", encoding="utf-8") as file:
            json.dump(json_data, file, indent=4, ensure_ascii=False)

        self.index()
            
    def index(self):
      self.send_response(200)
      self.send_header('Content-type', 'text/html')
      self.end_headers()

      with open('media/blogs.json', 'r', encoding='utf-8') as file:
        json_data = json.load(file)

      blogs_html = ''
      for blog_id, blog_info in json_data.items():
        blogs_html += f'<li><a href="/{blog_id}">{blog_info["title"]}</a> (Автор: {blog_info["author"]})</li>'

      with open('media/main.html', 'r', encoding='utf-8') as f:
          html = f.read()

      html = html.replace('{blogs}', blogs_html)
      
      self.wfile.write(html.encode('utf-8'))

    def blog(self):
        self.send_response(200)
        self.send_header("Content-type", 'text/html')
        self.end_headers()

        parse = urlparse(self.path)

        pattern = r"(\d+)"
        id_blog = re.findall(pattern, parse.path)[0]

        with open("media/blogs.json", "r", encoding="utf-8") as file:
            json_data = json.load(file)

        blog = json_data[id_blog]
        print(blog)


        with open('media/blog.html', 'r', encoding='utf-8') as f:
            html = f.read().format(title = blog["title"], content = blog["content"], author = blog["author"])

        self.wfile.write(html.encode('utf-8'))



def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    httpd = server_class(('', 8000), handler_class)
    httpd.serve_forever()

if __name__ == "__main__":
    run(HTTPServer, MyHandler)

    