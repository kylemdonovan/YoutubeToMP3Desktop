import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QListWidget, QProgressBar, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal
import yt_dlp

class DownloaderThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()

    def __init__(self, urls, output_path):
        super().__init__()
        self.urls = urls
        self.output_path = output_path

    def run(self):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'verbose': True,  # Enable verbose logging
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(self.urls)

        self.finished_signal.emit()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            progress = int(float(d['_percent_str'].replace('%', '')))
            self.progress_signal.emit(progress)

class YouTubeDownloaderApp(QWidget):
    # Initializes default output path as a class attribute
    default_output_path = None

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.url_input = QLineEdit()
        self.add_button = QPushButton('Add URL')
        self.settings_button = QPushButton('Change Directory')
        self.url_list = QListWidget()
        self.download_button = QPushButton('Download')
        self.progress_bar = QProgressBar()

        layout.addWidget(self.url_input)
        layout.addWidget(self.add_button)
        layout.addWidget(self.settings_button)
        layout.addWidget(self.url_list)
        layout.addWidget(self.download_button)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.setWindowTitle('YouTube to MP3 Downloader')

        self.add_button.clicked.connect(self.add_url)
        self.download_button.clicked.connect(self.start_download)

        self.settings_button.clicked.connect(self.change_default_directory)
        self.resize(800, 800)

    def add_url(self):
        url = self.url_input.text()
        if url:
            self.url_list.addItem(url)
            self.url_input.clear()

    def start_download(self):
        urls = [self.url_list.item(i).text() for i in range(self.url_list.count())]
        if not urls:
            return

        output_path = self.default_output_path if self.default_output_path else None
        if not output_path:
            output_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")

        if output_path:
            self.downloader_thread = DownloaderThread(urls, output_path)
            self.downloader_thread.progress_signal.connect(self.update_progress)
            self.downloader_thread.finished_signal.connect(self.download_finished)
            self.downloader_thread.start()

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

    def download_finished(self):
        self.progress_bar.setValue(100)
        self.url_list.clear()

    def change_default_directory(self):
        new_dir = QFileDialog.getExistingDirectory(self, "Select Default Download Directory")
        if new_dir:
            self.default_output_path = new_dir  # Updates the default directory

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YouTubeDownloaderApp()
    ex.show()
    sys.exit(app.exec_())
