import os
import wx
import re
import json
from concurrent.futures import ThreadPoolExecutor

class FileSearch:
    def __init__(self, folder_path, subfolders, use_regex):
        self.folder_path = folder_path
        self.subfolders = subfolders
        self.use_regex = use_regex

    def search_in_files(self, search_term):
        results = []
        if not os.path.exists(self.folder_path):
            raise FileNotFoundError("La carpeta de búsqueda no existe.")
        with ThreadPoolExecutor() as executor:
            for root, dirs, files in os.walk(self.folder_path):
                if not self.subfolders and root != self.folder_path:
                    continue
                for file_name in files:
                    if file_name.endswith('.txt'):
                        file_path = os.path.join(root, file_name)
                        with open(file_path, 'r', encoding='utf-8') as file:
                            for line_number, line in enumerate(file, 1):
                                if (self.use_regex and re.search(search_term, line, re.IGNORECASE)) or (not self.use_regex and search_term.lower() in line.lower()):
                                    result = f"Encontrado en '{file_path}' en la línea {line_number}: {line.strip()}"
                                    results.append((file_path, result))
        return results

class SearchFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Buscar Palabra en Archivos", size=(400, 300))
        self.panel = wx.Panel(self)
        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.search_label = wx.StaticText(self.panel, label="Ingresa la palabra a buscar:")
        vbox.Add(self.search_label, 0, wx.EXPAND|wx.ALL, 5)
        self.search_textctrl = wx.TextCtrl(self.panel)
        self.search_textctrl.Bind(wx.EVT_KEY_DOWN, self.on_key_press)
        vbox.Add(self.search_textctrl, 0, wx.EXPAND|wx.ALL, 5)
        self.search_button = wx.Button(self.panel, label="Buscar")
        self.search_button.Bind(wx.EVT_BUTTON, self.on_search)
        vbox.Add(self.search_button, 0, wx.EXPAND|wx.ALL, 5)
        self.choose_folder_button = wx.Button(self.panel, label="Seleccionar Carpeta")
        self.choose_folder_button.Bind(wx.EVT_BUTTON, self.on_choose_folder)
        vbox.Add(self.choose_folder_button, 0, wx.EXPAND|wx.ALL, 5)
        self.subfolders_checkbox = wx.CheckBox(self.panel, label="Buscar en subcarpetas")
        vbox.Add(self.subfolders_checkbox, 0, wx.EXPAND|wx.ALL, 5)
        self.regex_checkbox = wx.CheckBox(self.panel, label="Usar Expresiones Regulares")
        vbox.Add(self.regex_checkbox, 0, wx.EXPAND|wx.ALL, 5)
        self.results_list = wx.ListBox(self.panel, style=wx.LB_SINGLE)
        vbox.Add(self.results_list, 1, wx.EXPAND|wx.ALL, 5)
        self.panel.SetSizer(vbox)

    def on_search(self, event):
        search_term = self.search_textctrl.GetValue()
        if not search_term:
            wx.MessageBox("Por favor ingresa una palabra para buscar.", "Error", wx.OK | wx.ICON_ERROR)
            return
        try:
            file_search = FileSearch(self.folder_path, self.subfolders_checkbox.GetValue(), self.regex_checkbox.GetValue())
            results = file_search.search_in_files(search_term)
            self.display_results(results)
        except Exception as e:
            wx.MessageBox(str(e), "Error", wx.OK | wx.ICON_ERROR)

    def display_results(self, results):
        self.results_list.Clear()
        if results:
            for _, result in results:
                self.results_list.Append(result)
            wx.MessageBox(f"Se encontraron {len(results)} coincidencias.", "Resultados", wx.OK | wx.ICON_INFORMATION)
        else:
            self.results_list.Append("No se encontraron coincidencias.")

    def on_key_press(self, event):
        event.Skip()

    def on_choose_folder(self, event):
        dialog = wx.DirDialog(self, "Seleccionar Carpeta de Búsqueda", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            self.folder_path = dialog.GetPath()
            self.save_settings()
        dialog.Destroy()

    def save_settings(self):
        settings = {
            "folder_path": self.folder_path,
            "search_subfolders": self.subfolders_checkbox.GetValue(),
            "use_regex": self.regex_checkbox.GetValue()
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f)

    def load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.folder_path = settings.get("folder_path", ".")
                self.subfolders_checkbox.SetValue(settings.get("search_subfolders", False))
                self.regex_checkbox.SetValue(settings.get("use_regex", False))

if __name__ == "__main__":
    app = wx.App()
    frame = SearchFrame()
    frame.Show()
    app.MainLoop()
