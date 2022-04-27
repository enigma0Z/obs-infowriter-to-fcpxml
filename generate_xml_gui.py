#!/usr/bin/env python3

import sys
import os
from PyQt6.QtWidgets import \
    QMainWindow, QPushButton, QApplication, QVBoxLayout, \
    QHBoxLayout, QLineEdit,   QWidget,      QSpacerItem, \
    QTableWidget, QTableWidgetItem

from PyQt6 import QtGui

from PyQt6.QtCore import Qt

from generate_xml import process_files

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Convert to FCPXMLD')
        self.setGeometry(100, 100, 500, 200)
        self.setCentralWidget(Container())

class Container(QWidget):
    def __init__(self):
        super().__init__()

        self.setAcceptDrops(True)

        self.file_list = []

        layout = QVBoxLayout()

        self.output_title = QLineEdit()
        self.output_title.setPlaceholderText('Output Title')
        layout.addWidget(self.output_title)

        self.file_table = QTableWidget(self)
        self.file_table.setColumnCount(2)
        self.file_table.setHorizontalHeaderLabels(['Video File', 'Log File'])
        self.file_table.setColumnWidth(0, 230)
        self.file_table.setColumnWidth(1, 230)

        layout.addSpacerItem(QSpacerItem(10, 10))
        self.reset_button = QPushButton('Reset')
        self.process_button = QPushButton('Process')

        self.reset_button.clicked.connect(self.reset_button_clicked)
        self.process_button.clicked.connect(self.process_button_clicked)

        layout.addWidget(self.file_table)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.process_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
    
    def dragEnterEvent(self, e: QtGui.QDragEnterEvent) -> None:
        if e.mimeData().hasFormat('text/uri-list'):
            e.accept()
        else:
            e.ignore()
    
    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        file_list = [u.toString() for u in e.mimeData().urls()]

        self.file_table.setRowCount(0)

        self.file_list = []
        if (len(file_list) % 2 != 0):
            print('File list must contain an even number of files')
            e.ignore()
            return super().dropEvent(e)

        e.accept()

        os.chdir(os.path.dirname(file_list[0].removeprefix('file://')))

        for i in range(0, len(file_list), 2):
            video_file = file_list[i]
            log_file = file_list[i+1]
            self.file_list.append((video_file.removeprefix('file://'), log_file.removeprefix('file://')))

        print(len(self.file_list))
        self.file_table.setRowCount(len(self.file_list))

        row_index = 0
        for video, log in self.file_list:
            print(video, log)
            video_item = QTableWidgetItem(os.path.basename(video))
            video_item.setFlags(video_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.file_table.setItem(row_index, 0, video_item)

            log_item = QTableWidgetItem(os.path.basename(log))
            log_item.setFlags(log_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.file_table.setItem(row_index, 1, log_item)

            row_index += 1

        self.file_table.setVerticalHeaderLabels([])

        return super().dropEvent(e)
    
    def reset_button_clicked(self):
        self.file_table.setRowCount(0)
        self.file_list = []
        self.output_title.setText('')

    def process_button_clicked(self):
        if (self.output_title.text() == ''):
            print('Cannot process without a title')
            return
        
        if (self.file_list == []):
            print('Cannot process without a file list')
            return 

        print(self.output_title.text(), self.file_list)
        process_files(self.output_title.text(), self.file_list)
        self.reset_button_clicked()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    app.exec()