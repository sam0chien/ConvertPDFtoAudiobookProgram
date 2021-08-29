from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog

import pdfplumber
from playsound import playsound
from pydub import AudioSegment

from polly import Polly


class UI:
    polly = Polly

    def __init__(self):
        # Create main root instance from Tk class defined in tkinter
        self.root = Tk()
        self.root.title('Convert PDF to Audiobook')
        self.root.geometry('500x500')  # setting default size of the root
        self.root.config(padx=10, pady=10)
        # Add Frame for text box and scroll bar
        self.frame = Frame(width=30, height=60)
        self.frame.pack(fill='both', expand=True)
        # Add Scroll Bar and align to the right
        self.scroll_bar = Scrollbar(self.frame)
        self.scroll_bar.pack(side='right', fill='y')
        # Create text box for displaying pdf content
        self.text_box = Text(self.frame, fg='gray', yscrollcommand=self.scroll_bar.set)
        self.text_box.insert(0.0, 'Welcome, you can simply type anything here for Polly or from your PDF file.')
        self.text_box.pack(side='left', fill='both', expand=True)
        # Create menu instance from Menu class
        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)
        # Add 'File' tab into menu defined above
        self.file_menu = Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label='File', menu=self.file_menu)
        # Add drop-downs to 'file_menu'
        self.file_menu.add_command(label='Open', command=self.open)
        self.file_menu.add_command(label='Clear', command=self.clear)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit', command=self.root.quit)
        # Add clear button for clearing content in text box
        self.clear_button = Button(text='Clear', command=self.clear, stat='disabled')
        self.clear_button.pack(side='left', pady=10, expand=True)
        # Add play button for playing audio
        self.play_button = Button(text='Play', command=self.speak, stat='disabled')
        self.play_button.pack(side='left', pady=10, expand=True)
        # Add open button for open PDF file
        self.open_button = Button(text='Open', command=self.open)
        self.open_button.pack(side='left', pady=10, expand=True)
        # Add exit button for exit program
        self.exit_button = Button(text='Exit', command=self.root.quit)
        self.exit_button.pack(side='left', pady=10, expand=True)
        # Initial text variable
        self.text = None
        # Polly client
        self.polly = Polly
        # Check whether text box is empty
        self.text_box.bind('<Key>', self.check)
        # Keep root open until close it manually
        self.root.mainloop()

    def open(self):
        # creating dialogue box
        file = filedialog.askopenfilename(
            initialdir='./input/',
            title='Open PDF file',
            filetypes=(
                ('PDF Files', '*.pdf'),
                ('All Files', '*.*')
            )
        )
        if file:
            self.convert(file)

    def convert(self, file):
        self.text_box.config(stat='normal')
        # reading pdf file by pdfplumber
        with pdfplumber.open(file) as pdf:
            # getting total number of pages
            total_pages = len(pdf.pages)
            # looping through all the pages, collecting text from each page and showing it on text box
            for page in range(total_pages):
                content = pdf.pages[page].extract_text()
                self.text_box.insert('end', content)
        if pdf:
            self.play_button.config(stat='normal')
            self.clear_button.config(stat='normal')
            self.text_box.config(fg='white')

    def speak(self):
        # Get whole content in text box
        self.text = self.text_box.get(1.0, 'end')
        if self.text_box.compare('end-1c', '!=', '0.0'):
            aws_profile = simpledialog.askstring('Your AWS credential profile', 'Please visit "~/.aws/credentials"')
            self.polly = Polly(aws_profile)
            try:
                # Prevent following Polly error
                # (TextLengthExceededException)
                # when calling the SynthesizeSpeech operation: Maximum text length has been exceeded
                total_characters = len(self.text)
                # Initialize variable to avoid TypeError when concatenating
                speech = AudioSegment.empty()
                if total_characters > 2500:
                    for i in range(0, total_characters, 2500):
                        text_resize = self.text[i:i + 2500]
                        result = self.polly.convert(text_resize)
                        # Concatenate each chunk together
                        speech += AudioSegment.from_mp3(result)
                else:
                    result = self.polly.convert(self.text)
                    speech = AudioSegment.from_mp3(result)
                # Save MP3 file
                speech.export('output/final-speech.mp3', format='mp3')
                # Play MP3 file
                playsound('output/final-speech.mp3', block=False)
            except:
                messagebox.showerror('Oops!', result)
        else:
            messagebox.showinfo('Uh...', 'No content to speak.')

    def clear(self):
        # Disable buttons
        self.text_box.delete(1.0, 'end')
        self.play_button.config(stat='disabled')
        self.clear_button.config(stat='disabled')

    def check(self, event):
        self.text_box.config(fg='white')
        # Check whether text box is not empty
        if self.text_box.compare('end-1c', '!=', '0.0'):
            self.play_button.config(stat='normal')
            self.clear_button.config(stat='normal')
        else:
            self.play_button.config(stat='disabled')
            self.clear_button.config(stat='disabled')
