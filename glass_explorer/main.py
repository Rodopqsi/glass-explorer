import os
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Tree, Static, Button, TextLog, Label
from textual.widgets._tree import TreeNode
from . import utils

class GlassExplorer(App):
    TITLE = "Glass Explorer - Terminal File Manager"
    CSS_PATH = os.path.join(os.path.dirname(__file__), "glass.tcss")
    BINDINGS = [
        ("q", "quit", "Salir"),
        ("ctrl+b", "brightness", "Brillo"),
        ("ctrl+w", "wifi", "WiFi"),
        ("c", "compress", "Comprimir"),
        ("e", "extract", "Extraer"),
        ("i", "image_ascii", "Ver Imagen ASCII"),
        ("r", "refresh", "Refrescar"),
        ("enter", "open_file", "Abrir/Navegar"),
        ("backspace", "go_up", "Atrás"),
    ]

    current_path = str(Path.home())
    selected_file = ""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(classes="glass"):
            with Vertical():
                yield Label("Explorador de Archivos", classes="glass-title")
                yield Tree("~", data=str(Path.home()), id="file_tree")
            with Vertical():
                yield Label("Vista Previa", classes="glass-title")
                yield Static("", id="preview", classes="glass-preview")
                yield Label("Acciones", classes="glass-title")
                yield Button("Comprimir (c)", id="btn_compress")
                yield Button("Extraer (e)", id="btn_extract")
                yield Button("WiFi (ctrl+w)", id="btn_wifi")
                yield Button("Brillo (ctrl+b)", id="btn_bri")
                yield Button("Ver Imagen ASCII (i)", id="btn_img")
                yield TextLog(highlight=True, id="status_log", classes="glass-log")
        yield Footer()

    def on_mount(self):
        self.refresh_tree(str(Path.home()))
        self.log("Bienvenido a Glass Explorer. Usa las teclas indicadas abajo.")

    def log(self, text):
        self.query_one("#status_log", TextLog).write(text)

    def refresh_tree(self, path):
        tree = self.query_one("#file_tree", Tree)
        tree.clear()
        self.current_path = path
        self.populate_tree(tree.root, path)
        tree.root.expand()

    def populate_tree(self, node: TreeNode, path: str):
        try:
            for entry in sorted(os.listdir(path)):
                full_path = os.path.join(path, entry)
                label = entry + ("/" if os.path.isdir(full_path) else "")
                child = node.add(label, data=full_path)
                if os.path.isdir(full_path):
                    child.allow_expand = True
        except Exception as e:
            self.log(f"Error: {e}")

    async def on_tree_node_expanded(self, event):
        node = event.node
        path = node.data
        if os.path.isdir(path):
            node.clear()
            self.populate_tree(node, path)

    async def on_tree_node_selected(self, event):
        node = event.node
        path = node.data
        self.selected_file = path
        self.show_preview(path)

    def show_preview(self, path):
        preview = self.query_one("#preview", Static)
        if os.path.isdir(path):
            preview.update(f"[directorio]\n{path}")
        else:
            try:
                with open(path, encoding="utf-8", errors="ignore") as f:
                    content = f.read(300)
                    preview.update(content)
            except Exception:
                preview.update("<No se puede previsualizar este archivo>")

    def action_open_file(self):
        path = self.selected_file
        if os.path.isdir(path):
            self.refresh_tree(path)
        else:
            self.show_preview(path)

    def action_go_up(self):
        path = os.path.dirname(self.current_path)
        if os.path.exists(path):
            self.refresh_tree(path)

    def action_refresh(self):
        self.refresh_tree(self.current_path)

    def action_compress(self):
        import zipfile
        path = self.selected_file or self.current_path
        dest = path + ".zip"
        try:
            with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zipf:
                if os.path.isdir(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            zipf.write(os.path.join(root, file),
                                       os.path.relpath(os.path.join(root, file),
                                                       os.path.join(path, '..')))
                else:
                    zipf.write(path, os.path.basename(path))
            self.log(f"¡Comprimido a {dest}!")
        except Exception as e:
            self.log(f"Error al comprimir: {e}")

    def action_extract(self):
        import zipfile, tarfile
        path = self.selected_file
        if path and path.endswith('.zip'):
            dest = os.path.splitext(path)[0] + "_extraido"
            try:
                with zipfile.ZipFile(path, 'r') as zipf:
                    zipf.extractall(dest)
                self.log(f"¡Extraído en {dest}!")
            except Exception as e:
                self.log(f"Error al extraer: {e}")
        elif path and (path.endswith('.tar.gz') or path.endswith('.tar')):
            dest = os.path.splitext(path)[0] + "_extraido"
            try:
                with tarfile.open(path, "r:gz") as tar:
                    tar.extractall(dest)
                self.log(f"¡Extraído en {dest}!")
            except Exception as e:
                self.log(f"Error al extraer: {e}")
        else:
            self.log("Selecciona un archivo .zip o .tar.gz para extraer.")

    def action_brightness(self):
        try:
            prev = utils.get_brightness()[0]
            new_brightness = (prev + 10) % 110
            utils.set_brightness(new_brightness)
            self.log(f"Brillo ajustado a {new_brightness}%.")
        except Exception as e:
            self.log(f"Brillo no soportado: {e}")

    def action_wifi(self):
        try:
            results = utils.scan_wifi()
            redes = [r.ssid for r in results]
            self.log(f"Redes encontradas: {redes}")
        except Exception as e:
            self.log(f"WiFi no soportado: {e}")

    def action_image_ascii(self):
        if self.selected_file.lower().endswith(('.jpg', '.png', '.gif', '.bmp')):
            try:
                ascii_img = utils.image_to_ascii(self.selected_file)
                self.query_one("#preview", Static).update(ascii_img)
            except Exception as e:
                self.log(f"No se pudo mostrar la imagen ASCII: {e}")
        else:
            self.log("Selecciona una imagen para ver como ASCII.")

    def on_button_pressed(self, event):
        if event.button.id == "btn_compress":
            self.action_compress()
        elif event.button.id == "btn_extract":
            self.action_extract()
        elif event.button.id == "btn_wifi":
            self.action_wifi()
        elif event.button.id == "btn_bri":
            self.action_brightness()
        elif event.button.id == "btn_img":
            self.action_image_ascii()

def main():
    GlassExplorer().run()

if __name__ == "__main__":
    main()