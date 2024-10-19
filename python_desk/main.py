import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QTextEdit, QWidget, QVBoxLayout, QGridLayout,
    QScrollArea, QPushButton, QSizePolicy, QStackedWidget, QHBoxLayout, QDialog,
    QLineEdit, QMessageBox
)
from PyQt6.QtGui import QPixmap, QWindow
from PyQt6.QtCore import QSize, Qt
import scrape_chapters
import threading

def clear_layout(grid_layout: QGridLayout):
    while grid_layout.count():
        item = grid_layout.takeAt(0)
        if (item):
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Input Dialog")
        self.setFixedSize(700, 150)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel("Enter webnovel URL and wait a few seconds :)")
        self.label.setStyleSheet("font-size: 20px; margin-bottom: 10px;")
        layout.addWidget(self.label)

        self.input_field = QLineEdit(self)
        self.input_field.setFixedSize(650, 40)
        self.input_field.setStyleSheet("margin-bottom: 10px;")
        layout.addWidget(self.input_field)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.get_started)
        self.ok_button.setFixedSize(300, 30)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setFixedSize(300, 30)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def get_input(self):
        return self.input_field.text()

    def get_started(self):
        webnovel_link = str(self.input_field.text())
        scrape_chapters.initialise(webnovel_link, '../novels/')
        self.accept()

class ChapterView(QWidget):
    def __init__(self, go_back_callback):
        super().__init__()

        self.novel_name = ""
        self.chapter_no = 0

        base_layout = QVBoxLayout(self)
        self.chapter_title: QLabel = QLabel()
        self.chapter_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chapter_title.setStyleSheet("font-size: 36px; font-weight: bold; margin-top: 30px; margin-bottom: -10px;")
        base_layout.addWidget(self.chapter_title)

        buttons_layout = QHBoxLayout()

        prev_button = QPushButton('Previous Chapter')
        prev_button.clicked.connect(self.prev_chapter)
        prev_button.setFixedHeight(70)
        prev_button.setStyleSheet("font-size: 30px; font-weight: bold;")
        self.back_to_novel = QPushButton('Back to Novel Page')
        self.back_to_novel.setFixedHeight(70)
        self.back_to_novel.setStyleSheet("font-size: 30px; font-weight: bold;")
        next_button = QPushButton('Next Chapter')
        next_button.clicked.connect(self.next_chapter)
        next_button.setFixedHeight(70)
        next_button.setStyleSheet("font-size: 30px; font-weight: bold;")

        buttons_layout.addWidget(prev_button)
        buttons_layout.addWidget(self.back_to_novel)
        buttons_layout.addWidget(next_button)

        base_layout.addLayout(buttons_layout)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll_content = QVBoxLayout()

        self.chapter_content: QTextEdit = QTextEdit()
        self.chapter_content.setReadOnly(True)
        self.chapter_content.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.chapter_content.setStyleSheet("font-size: 30px;")
        scroll_content.addWidget(self.chapter_content)
        scroll.setLayout(scroll_content)
        base_layout.addWidget(scroll)

    def set_chapter_content(self, novel_name, chapter_no, show_novel_view):
        if (self.novel_name == novel_name and self.chapter_no == chapter_no):
            return

        chapter_path = f'../novels/{novel_name}/{chapter_no}'
        self.novel_name = novel_name
        self.chapter_no = chapter_no
        self.back_to_novel.clicked.connect(lambda: show_novel_view(novel_name))
        if os.path.isfile(chapter_path):
            with open(chapter_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_contents = f.readlines()
                self.chapter_title.setText(file_contents[0])
                self.chapter_content.setPlainText('\n\n'.join(file_contents[1:]))
            with open(f'../novels/{self.novel_name}/start', 'w') as f:
                f.write(str(self.chapter_no))
        else:
            self.chapter_title.setText("Chapter Doesnt exists")
            self.chapter_content.setText("nope")

    def next_chapter(self):
        chapter_path = f'../novels/{self.novel_name}/{self.chapter_no+1}'
        if os.path.isfile(chapter_path):
            with open(chapter_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_contents = f.readlines()
                self.chapter_title.setText(file_contents[0])
                self.chapter_content.setText('\n'.join(file_contents[1:]))
                self.chapter_no += 1
            with open(f'../novels/{self.novel_name}/start', 'w') as f:
                f.write(str(self.chapter_no));

    def prev_chapter(self):
        chapter_path = f'../novels/{self.novel_name}/{self.chapter_no-1}'
        if os.path.isfile(chapter_path):
            with open(chapter_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_contents = f.readlines()
                self.chapter_title.setText(file_contents[0])
                self.chapter_content.setPlainText('\n'.join(file_contents[1:]))
                self.chapter_no -= 1
            with open(f'../novels/{self.novel_name}/start', 'w') as f:
                f.write(str(self.chapter_no));

class NovelView(QWidget):
    def __init__(self, go_back_callback):
        super().__init__()

        self.novel_name = ""
        self.open_chapter_function = go_back_callback
        self.download_thread = threading.Thread(target=scrape_chapters.downloadChapters, args=[f"https://readnovelfull.com/{self.novel_name}.html", "../novels"])
        self.stop_event = threading.Event()

        baseLayout = QHBoxLayout(self)
        self.novel_title_label = QLabel()
        baseLayout.addWidget(self.novel_title_label)

        novel_info = QVBoxLayout()

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        novel_info.addWidget(self.image_label)

        self.download_button = QPushButton("Download")
        self.download_button.setFixedSize(QSize(300, 50))
        self.download_button.setStyleSheet("font-size: 15px; font-weight: bold; background:purple;")
        self.download_button.clicked.connect(self.download_chapters)

        start_button = QPushButton("Start")
        start_button.setFixedSize(QSize(300, 50))
        start_button.setStyleSheet("font-size: 15px; font-weight: bold; background:blue;")
        start_button.clicked.connect(self.start_reading)
        
        continue_button = QPushButton("Continue")
        continue_button.setFixedSize(QSize(300, 50))
        continue_button.setStyleSheet("font-size: 15px; font-weight: bold; background:violet;")
        continue_button.clicked.connect(self.continue_reading)
        
        goBack_button = QPushButton("Go Back")
        goBack_button.setFixedSize(QSize(300, 50))
        goBack_button.setStyleSheet("font-size: 15px; font-weight: bold; background:orange;")
        goBack_button.clicked.connect(go_back_callback)

        novel_info.addWidget(self.download_button)
        novel_info.addWidget(start_button)
        novel_info.addWidget(continue_button)
        novel_info.addWidget(goBack_button)
        novel_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.chapters_grid = QGridLayout(scroll_content)
        self.chapters_grid.setAlignment(Qt.AlignmentFlag.AlignJustify)
        scroll.setWidget(scroll_content)

        baseLayout.addLayout(novel_info)
        baseLayout.addWidget(scroll)

    def start_reading(self):
        with open(f'../novels/{self.novel_name}/start', 'w') as f:
            f.write('1')
        self.open_chapter_function(self.novel_name, 1)

    def continue_reading(self):
        start_file = f'../novels/{self.novel_name}/start'
        if (os.path.exists(start_file)):
            with open(start_file, 'r') as f:
                curr = int(f.read())
                self.open_chapter_function(self.novel_name, curr)
        else:
            self.start_reading()

    def download_chapters(self):
        if self.download_thread and self.download_thread.is_alive():
            self.stop_event.set()
            self.download_button.setText("Download")
            self.download_button.setStyleSheet("font-size: 15px; font-weight: bold; background:purple;")
            self.download_thread.join()
        else:
            self.stop_event.clear()
            self.download_button.setText("Cancel")
            self.download_button.setStyleSheet("font-size: 15px; font-weight: bold; background:red;")
            self.download_thread = threading.Thread(
                target=scrape_chapters.downloadChapters,
                args=[f"https://readnovelfull.com/{self.novel_name}.html", "../novels", self.stop_event]
            )
            self.download_thread.start()

    def set_novel(self, novel_name, show_chapter_view):
        if (self.novel_name == novel_name):
            return
        clear_layout(self.chapters_grid)
        self.open_chapter_function = show_chapter_view
        self.novel_name = novel_name
        image_path = f"../novels/{novel_name}/image.jpg"
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap.scaledToWidth(300, Qt.TransformationMode.SmoothTransformation))
        else:
            self.image_label.setText("Image not found")
        self.set_chapters_grid()

    def set_chapters_grid(self):
        clear_layout(self.chapters_grid)
        index_path = f"../novels/{self.novel_name}/index"
        with open(index_path, 'r', encoding='utf-8', errors='ignore') as f:
            i = 0
            chapter = f.readline()
            while chapter:
                chapter_button = QPushButton()
                chapter_button.setText(chapter)
                chapter_button.clicked.connect(lambda _, temp=i+1: self.open_chapter_function(self.novel_name, temp))
                chapter_button.setFixedSize(510, 70)
                chapter_button.setStyleSheet("font-size: 15px;")
                self.chapters_grid.addWidget(chapter_button, i//3, i%3)
                i += 1
                chapter = f.readline()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget()
        self.stacked_widget = QStackedWidget()

        self.main_view = QWidget()
        self.main_layout = QVBoxLayout(self.main_view)

        heading = QLabel("Novel Directory Viewer")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading.setStyleSheet("font-size: 36px; font-weight: bold; margin-bottom: 20px;")
        self.main_layout.addWidget(heading)
        
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.grid_layout = QGridLayout(scroll_content)
        scroll.setWidget(scroll_content)
        self.main_layout.addWidget(scroll)

        self.stacked_widget.addWidget(self.main_view)
        
        self.novel_view = NovelView(self.go_back_to_home)
        self.stacked_widget.addWidget(self.novel_view)
        self.chapter_view = ChapterView(self.go_back_to_home)
        self.stacked_widget.addWidget(self.chapter_view)

        self.setCentralWidget(self.stacked_widget)

        novel_dir = '../novels'

        self.load_novel_subdirs(novel_dir)

    def load_novel_subdirs(self, novel_dir):
        if not os.path.exists(novel_dir):
            return

        clear_layout(self.grid_layout)

        subdirs = [f for f in os.listdir(novel_dir) if os.path.isdir(os.path.join(novel_dir, f))]

        row, col = 0, 0
        for subdir in subdirs:
            card_widget = self.create_card(os.path.join(novel_dir, subdir), subdir)

            self.grid_layout.addWidget(card_widget, row, col)

            col += 1
            if col > 2:
                col = 0
                row += 1

        card_widget = QPushButton()
        card_widget.setFixedSize(300, 420)
        card_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        card_layout = QVBoxLayout(card_widget)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel('+')
        label.setFixedSize(260, 100)
        label.setStyleSheet("font-size: 70px; margin-bottom:30px")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(label, 1, Qt.AlignmentFlag.AlignCenter)
        card_widget.clicked.connect(self.open_input_dialog)

        self.grid_layout.addWidget(card_widget, row, col)

    def create_card(self, subdir_path, subdir_name):
        card_widget = QPushButton()
        card_widget.setFixedSize(300, 420)
        card_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        card_layout = QVBoxLayout(card_widget)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        novel_title = ' '.join(x.capitalize() for x in subdir_name.split('-'))
        label = QLabel(novel_title)
        label.setWordWrap(True)
        label.setFixedSize(260, 40)
        label.setStyleSheet("font-size: 15px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(label, 1, Qt.AlignmentFlag.AlignCenter)

        image_path = os.path.join(subdir_path, 'image.jpg')
        image_label = QLabel()

        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            image_label.setPixmap(pixmap.scaled(270, 390, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
            image_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
            card_layout.addWidget(image_label)

        card_widget.clicked.connect(lambda: self.show_novel_view(subdir_name))

        return card_widget

    def show_chapter_view(self, novel_name, chapter_no):
        self.chapter_view.set_chapter_content(novel_name, chapter_no, self.show_novel_view)
        self.stacked_widget.setCurrentWidget(self.chapter_view)

    def show_novel_view(self, novel_name):
        self.novel_view.set_novel(novel_name, self.show_chapter_view)
        self.stacked_widget.setCurrentWidget(self.novel_view)

    def go_back_to_home(self):
        self.stacked_widget.setCurrentWidget(self.main_view)

    def open_input_dialog(self):
        dialog = InputDialog(self)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            user_input = dialog.get_input()
            QMessageBox.information(self, "Webnovel Added!", f"You entered: {user_input}")
            self.load_novel_subdirs('../novels')
        else:
            QMessageBox.information(self, "Cancelled", "Dialog was cancelled.")

if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.setWindowTitle("Novel Directory Viewer")
    window.showMaximized()

    app.exec()