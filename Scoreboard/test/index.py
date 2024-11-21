import tkinter as tk
from tkhtmlview import HTMLLabel

root = tk.Tk()
html_code = """
<html>
    <body>
        <h1>Hello, wooorld!</h1>
        <img width="100px" height="100px" src="https://"></img>
        <p>This is a simple embedded HTML page.</p>
    </body>
</html>
"""

label = HTMLLabel(root, html=html_code)
label.pack(padx=10, pady=10)

root.mainloop()