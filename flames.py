import math
import random
import tkinter as tk


COLORS = {
    "background": "#100d25",
    "card": "#1d1838",
    "entry": "#292247",
    "text": "#f8f4ff",
    "muted": "#c0b7d8",
    "pink": "#ff6b9d",
    "purple": "#aa8cff",
    "gold": "#ffd166",
}

MEANINGS = {
    "Friends": "A strong friendship is in the stars!",
    "Love": "A little romance might be in the stars!",
    "Affection": "A warm and caring connection!",
    "Marriage": "The classic FLAMES prediction says marriage!",
    "Enemies": "A playful rivalry is predicted!",
    "Siblings": "You might bicker like siblings!",
}


def clean_name(name):
    return [letter.lower() for letter in name if letter.isalpha()]


def calculate_flames(name1, name2):
    letters1 = clean_name(name1)
    letters2 = clean_name(name2)

    for letter in letters1.copy():
        if letter in letters2:
            letters1.remove(letter)
            letters2.remove(letter)

    count = len(letters1) + len(letters2)
    if count == 0:
        return count, [], None

    results = ["Friends", "Love", "Affection", "Marriage", "Enemies", "Siblings"]
    eliminated = []
    index = 0

    while len(results) > 1:
        index = (index + count - 1) % len(results)
        eliminated.append(results.pop(index))

    return count, eliminated, results[0]


class FlamesGame:
    def __init__(self, root):
        self.root = root
        self.root.title("FLAMES - Name Match Game")
        self.root.geometry("760x650")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["background"])

        self.canvas = tk.Canvas(
            root,
            width=760,
            height=650,
            bg=COLORS["background"],
            highlightthickness=0,
        )
        self.canvas.place(x=0, y=0)
        self.draw_background()

        self.card = tk.Frame(
            root,
            bg=COLORS["card"],
            padx=38,
            pady=30,
            highlightbackground="#443866",
            highlightthickness=1,
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=530, height=540)
        self.build_interface()
        self.animate_background()

    def draw_background(self):
        self.particles = []
        random.seed(12)
        for _ in range(42):
            x = random.randint(8, 752)
            y = random.randint(5, 645)
            size = random.choice([2, 3, 4])
            color = random.choice([COLORS["purple"], COLORS["pink"], "#514777"])
            item = self.canvas.create_oval(
                x, y, x + size, y + size, fill=color, outline=""
            )
            self.particles.append((item, random.choice([1, 2, 3])))

        self.draw_heart(72, 115, 18, COLORS["pink"])
        self.draw_heart(682, 520, 14, COLORS["purple"])
        self.draw_star(680, 115, 17, COLORS["gold"])
        self.draw_star(78, 530, 13, COLORS["purple"])

    def draw_heart(self, x, y, size, color):
        points = [
            x, y + size * 0.35,
            x - size, y - size * 0.35,
            x - size * 0.95, y - size * 0.95,
            x - size * 0.4, y - size,
            x, y - size * 0.48,
            x + size * 0.4, y - size,
            x + size * 0.95, y - size * 0.95,
            x + size, y - size * 0.35,
        ]
        self.canvas.create_polygon(
            points, smooth=True, fill=color, outline="", stipple="gray50"
        )

    def draw_star(self, x, y, size, color):
        points = []
        for point in range(10):
            angle = math.pi * point / 5 - math.pi / 2
            radius = size if point % 2 == 0 else size * 0.42
            points.extend((x + math.cos(angle) * radius, y + math.sin(angle) * radius))
        self.canvas.create_polygon(points, fill=color, outline="")

    def build_interface(self):
        tk.Label(
            self.card,
            text="✦  FLAMES  ✦",
            font=("Segoe UI", 27, "bold"),
            bg=COLORS["card"],
            fg=COLORS["pink"],
        ).pack(pady=(0, 3))

        tk.Label(
            self.card,
            text="A little name game, written in the stars",
            font=("Segoe UI", 10),
            bg=COLORS["card"],
            fg=COLORS["muted"],
        ).pack(pady=(0, 20))

        self.first_entry = self.add_name_entry("Your name")
        self.second_entry = self.add_name_entry("Their name")
        self.second_entry.bind("<Return>", lambda _event: self.start_game())

        self.play_button = tk.Button(
            self.card,
            text="✨  Reveal our FLAMES  ✨",
            command=self.start_game,
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["pink"],
            fg="#24152e",
            activebackground="#ff8ab0",
            activeforeground="#24152e",
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=10,
        )
        self.play_button.pack(fill="x", pady=(17, 15))

        self.status = tk.Label(
            self.card,
            text="Enter two names to see what the stars say...",
            font=("Segoe UI", 10),
            bg=COLORS["card"],
            fg=COLORS["muted"],
            wraplength=440,
            height=2,
        )
        self.status.pack()

        self.result = tk.Label(
            self.card,
            text="",
            font=("Segoe UI", 22, "bold"),
            bg=COLORS["card"],
            fg=COLORS["gold"],
            wraplength=440,
        )
        self.result.pack(pady=(2, 4))

        self.meaning = tk.Label(
            self.card,
            text="",
            font=("Segoe UI", 11),
            bg=COLORS["card"],
            fg=COLORS["text"],
            wraplength=440,
        )
        self.meaning.pack(pady=(0, 5))

        self.trail = tk.Label(
            self.card,
            text="",
            font=("Segoe UI", 9),
            bg=COLORS["card"],
            fg=COLORS["purple"],
            wraplength=440,
            justify="center",
        )
        self.trail.pack(pady=(2, 6))

        tk.Label(
            self.card,
            text="Just for fun — FLAMES isn't a real compatibility test.",
            font=("Segoe UI", 9, "italic"),
            bg=COLORS["card"],
            fg=COLORS["muted"],
        ).pack(side="bottom", pady=(12, 0))

    def add_name_entry(self, label):
        tk.Label(
            self.card,
            text=label,
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["card"],
            fg=COLORS["text"],
            anchor="w",
        ).pack(fill="x", pady=(7, 5))

        entry = tk.Entry(
            self.card,
            font=("Segoe UI", 12),
            bg=COLORS["entry"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground="#443866",
            highlightcolor=COLORS["purple"],
        )
        entry.pack(fill="x", ipady=9)
        return entry

    def start_game(self):
        name1 = self.first_entry.get().strip()
        name2 = self.second_entry.get().strip()

        if not clean_name(name1) or not clean_name(name2):
            self.status.config(text="Please enter two names containing letters.")
            self.result.config(text="")
            self.meaning.config(text="")
            self.trail.config(text="")
            return

        count, eliminated, outcome = calculate_flames(name1, name2)
        self.play_button.config(state="disabled")
        self.status.config(text=f"{name1} + {name2} ... the stars are counting!")
        self.result.config(text="")
        self.meaning.config(text="")
        self.trail.config(text="")

        if outcome is None:
            self.root.after(500, self.show_mystery)
            return

        self.root.after(
            300,
            lambda: self.reveal_step(count, eliminated, outcome, 0),
        )

    def reveal_step(self, count, eliminated, outcome, step):
        if step < len(eliminated):
            self.status.config(text=f"Counting {count} unmatched letters...")
            self.result.config(text=eliminated[step])
            self.root.after(
                450,
                lambda: self.reveal_step(count, eliminated, outcome, step + 1),
            )
            return

        self.status.config(text="The stars have made their playful prediction:")
        self.result.config(text=f"✦ {outcome.upper()} ✦")
        self.meaning.config(text=MEANINGS[outcome])
        self.trail.config(text="Elimination trail: " + "  →  ".join(eliminated))
        self.play_button.config(state="normal")
        self.play_button.config(text="✨  Play again  ✨")

    def show_mystery(self):
        self.status.config(text="Every letter matched!")
        self.result.config(text="A mystery ✨")
        self.meaning.config(text="The FLAMES stars couldn't choose a result this time.")
        self.trail.config(text="Try another pair of names!")
        self.play_button.config(state="normal")
        self.play_button.config(text="✨  Play again  ✨")

    def animate_background(self):
        for item, speed in self.particles:
            self.canvas.move(item, 0, -speed)
            x1, y1, x2, y2 = self.canvas.coords(item)
            if y2 < 0:
                x = random.randint(8, 752)
                self.canvas.coords(item, x, 650, x + (x2 - x1), 650 + (y2 - y1))
        self.root.after(70, self.animate_background)


if __name__ == "__main__":
    window = tk.Tk()
    FlamesGame(window)
    window.mainloop()
