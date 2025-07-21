import csv
import random
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# Constants
DATA_FOLDER = "data"            # Folder where subject CSV files are stored

# Load questions from the selected subject file
def load_questions(subject):
    filepath = os.path.join(DATA_FOLDER, f"{subject.lower()}.csv")
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

# Generate paper based on subject type
def generate_paper(subject, questions):
    if subject.lower() == "computer":
        # Only MCQs, total 50 marks
        return random.sample([q for q in questions if q['type'] == 'mcq'], min(50, len(questions)))
    else:
        # 15 MCQs and 85 other questions (paragraph/diagram)
        mcqs = [q for q in questions if q['type'] == 'mcq'][:15]
        others = [q for q in questions if q['type'] in ['paragraph', 'diagram']]
        remaining = random.sample(others, min(85, len(others)))
        return mcqs + remaining

# Export the paper as a PDF file
def export_pdf(paper, subject, filename=None):
    filename = filename or f"Class12_{subject}_Paper.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    x_margin = 50
    y = height - 50

    # PDF Title Section
    c.setFont("Helvetica-Bold", 14)
    if subject.lower() == "computer":
        title_line = f"ધોરણ ૧૨ – {subject.capitalize()} (માત્ર MCQ પ્રશ્નપત્ર – 50 ગુણ)"
    else:
        title_line = f"ધોરણ ૧૨ – {subject.capitalize()} (મુલ્યાંકન પત્ર – 100 ગુણ)"
    c.drawString(x_margin, y, title_line)
    y -= 30
    c.setFont("Helvetica", 12)
    c.drawString(x_margin, y, "Most Important Question Paper")
    y -= 20
    c.drawString(x_margin, y, f"Generated on: {datetime.now().strftime('%d-%m-%Y %I:%M %p')}")
    y -= 40

    c.setFont("Helvetica", 11)

    # Add questions one by one
    for i, q in enumerate(paper, 1):
        question_text = f"{i}. {q['question']} ({q['rarity']})"
        lines = split_text(question_text, 90)
        for line in lines:
            c.drawString(x_margin, y, line)
            y -= 16
            if y < 60:
                c.showPage()
                y = height - 50

        # If it's an MCQ, add options
        if q['type'] == 'mcq':
            options = q['options'].split(',')
            for idx, opt in enumerate(options):
                c.drawString(x_margin + 20, y, f"({chr(65+idx)}) {opt.strip()}")
                y -= 16
                if y < 60:
                    c.showPage()
                    y = height - 50
        elif q['type'] == 'diagram':
            c.drawString(x_margin + 20, y, "(આ પ્રશ્ન માટે આંકડો દોરવો જરૂરી છે)")
            y -= 16
        y -= 10

    c.save()
    return filename

# Helper to split long lines into multiple lines for PDF
def split_text(text, max_length):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= max_length:
            current += " " + word if current else word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

# GUI to input subject and generate paper
def run_gui():
    def on_generate():
        subject = subject_var.get().strip().lower()
        if not subject:
            messagebox.showerror("Error", "Please enter a subject.")
            return
        try:
            questions = load_questions(subject)
            paper = generate_paper(subject, questions)
            filename = export_pdf(paper, subject)
            messagebox.showinfo("Success", f"PDF saved as '{filename}'")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Subject file '{subject}.csv' not found in 'data/' folder.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

    root = tk.Tk()
    root.title("Class 12 Question Paper Generator")

    tk.Label(root, text="Enter Subject Name:").pack(pady=5)
    subject_var = tk.StringVar()
    tk.Entry(root, textvariable=subject_var, width=30).pack(pady=5)

    tk.Button(root, text="Generate Question Paper", command=on_generate).pack(pady=10)

    root.mainloop()

# Start the app
if __name__ == "__main__":
    run_gui()
