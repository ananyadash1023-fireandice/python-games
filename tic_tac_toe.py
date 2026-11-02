import math
import random
import tkinter as tk


COLORS = {
    "background": "#100d25",
    "card": "#1d1838",
    "cell": "#292247",
    "text": "#f8f4ff",
    "muted": "#c0b7d8",
    "pink": "#ff6b9d",
    "purple": "#aa8cff",
    "blue": "#67d5ff",
    "gold": "#ffd166",
    "green": "#72e0b0",
}

WINNING_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)


class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic-Tac-Toe - Cosmic Challenge")
        self.root.geometry("760x700")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["background"])

        self.canvas = tk.Canvas(
            root,
            width=760,
            height=700,
            bg=COLORS["background"],
            highlightthickness=0,
        )
        self.canvas.place(x=0, y=0)
        self.draw_background()

        self.card = tk.Frame(
            root,
            bg=COLORS["card"],
            padx=32,
            pady=22,
            highlightbackground="#443866",
            highlightthickness=1,
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=500, height=640)

        self.scores = {"X": 0, "O": 0}
        self.player_names = {"X": "Player 1", "O": "Player 2"}
        self.current_player = "X"
        self.board = [""] * 9
        self.game_active = False
        self.cells = []
        self.build_interface()
        self.animate_background()

    def draw_background(self):
        self.particles = []
        random.seed(27)
        for _ in range(52):
            x = random.randint(5, 755)
            y = random.randint(5, 695)
            size = random.choice((2, 2, 3, 4))
            color = random.choice(("#514777", COLORS["purple"], "#383154"))
            item = self.canvas.create_oval(
                x, y, x + size, y + size, fill=color, outline=""
            )
            self.particles.append((item, random.choice((1, 1, 2, 3))))

        self.draw_star(78, 115, 15, COLORS["gold"])
        self.draw_star(687, 134, 12, COLORS["pink"])
        self.draw_star(78, 588, 12, COLORS["purple"])
        self.draw_star(686, 576, 17, COLORS["blue"])
        self.canvas.create_text(
            115, 340, text="×", font=("Segoe UI", 43, "bold"),
            fill=COLORS["pink"], stipple="gray50"
        )
        self.canvas.create_text(
            647, 360, text="○", font=("Segoe UI", 43, "bold"),
            fill=COLORS["blue"], stipple="gray50"
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
            text="✦ TIC-TAC-TOE ✦",
            font=("Segoe UI", 24, "bold"),
            bg=COLORS["card"],
            fg=COLORS["purple"],
        ).pack(pady=(0, 2))
        tk.Label(
            self.card,
            text="Cosmic Challenge",
            font=("Segoe UI", 10),
            bg=COLORS["card"],
            fg=COLORS["muted"],
        ).pack(pady=(0, 12))

        players = tk.Frame(self.card, bg=COLORS["card"])
        players.pack(fill="x", pady=(0, 10))
        self.name_entries = {}
        for symbol, default_name, color in (
            ("X", "Player 1", COLORS["pink"]),
            ("O", "Player 2", COLORS["blue"]),
        ):
            section = tk.Frame(players, bg=COLORS["card"])
            section.pack(side="left", expand=True, fill="x", padx=5)
            tk.Label(
                section,
                text=f"{symbol} name",
                font=("Segoe UI", 9, "bold"),
                bg=COLORS["card"],
                fg=color,
                anchor="w",
            ).pack(fill="x", pady=(0, 4))
            entry = tk.Entry(
                section,
                font=("Segoe UI", 10),
                bg=COLORS["cell"],
                fg=COLORS["text"],
                insertbackground=COLORS["text"],
                relief="flat",
                highlightthickness=1,
                highlightbackground="#443866",
                highlightcolor=COLORS["purple"],
            )
            entry.insert(0, default_name)
            entry.pack(fill="x", ipady=7)
            self.name_entries[symbol] = entry

        self.score_label = tk.Label(
            self.card,
            text="X  0     •     O  0",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["card"],
            fg=COLORS["gold"],
        )
        self.score_label.pack(pady=(0, 8))

        self.status_label = tk.Label(
            self.card,
            text="Choose your names, then start the game!",
            font=("Segoe UI", 10),
            bg=COLORS["card"],
            fg=COLORS["text"],
            height=2,
        )
        self.status_label.pack()

        board_frame = tk.Frame(self.card, bg=COLORS["card"])
        board_frame.pack(pady=(7, 12))
        for row in range(3):
            for column in range(3):
                position = row * 3 + column
                button = tk.Button(
                    board_frame,
                    text="",
                    command=lambda pos=position: self.make_move(pos),
                    font=("Segoe UI", 30, "bold"),
                    bg=COLORS["cell"],
                    fg=COLORS["text"],
                    activebackground="#39305d",
                    activeforeground=COLORS["text"],
                    disabledforeground=COLORS["text"],
                    relief="flat",
                    cursor="hand2",
                    width=4,
                    height=1,
                    highlightthickness=1,
                    highlightbackground="#443866",
                )
                button.grid(row=row, column=column, padx=5, pady=5, ipadx=3, ipady=3)
                self.cells.append(button)

        controls = tk.Frame(self.card, bg=COLORS["card"])
        controls.pack(fill="x")
        self.start_button = tk.Button(
            controls,
            text="🚀  Start game",
            command=self.start_game,
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["purple"],
            fg="#201832",
            activebackground="#c0aaff",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=8,
        )
        self.start_button.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.reset_button = tk.Button(
            controls,
            text="↻  New round",
            command=self.new_round,
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["pink"],
            fg="#24152e",
            activebackground="#ff8ab0",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=8,
            state="disabled",
        )
        self.reset_button.pack(side="left", expand=True, fill="x", padx=(5, 0))

        self.message_label = tk.Label(
            self.card,
            text="Take turns by clicking any empty square.",
            font=("Segoe UI", 9),
            bg=COLORS["card"],
            fg=COLORS["muted"],
        )
        self.message_label.pack(pady=(12, 0))

    def start_game(self):
        self.player_names = {
            "X": self.name_entries["X"].get().strip() or "Player 1",
            "O": self.name_entries["O"].get().strip() or "Player 2",
        }
        self.scores = {"X": 0, "O": 0}
        self.update_score()
        self.new_round()
        self.start_button.config(state="disabled")
        self.name_entries["X"].config(state="disabled")
        self.name_entries["O"].config(state="disabled")
        self.message_label.config(text="First to get three in a row wins the round!")

    def new_round(self):
        self.board = [""] * 9
        self.current_player = "X"
        self.game_active = True
        for cell in self.cells:
            cell.config(
                text="",
                state="normal",
                bg=COLORS["cell"],
                fg=COLORS["text"],
            )
        self.reset_button.config(state="normal")
        self.update_status()

    def make_move(self, position):
        if not self.game_active or self.board[position]:
            return

        symbol = self.current_player
        self.board[position] = symbol
        self.cells[position].config(
            text=symbol,
            fg=COLORS["pink"] if symbol == "X" else COLORS["blue"],
            disabledforeground=COLORS["pink"] if symbol == "X" else COLORS["blue"],
            state="disabled",
        )

        winning_line = self.get_winning_line()
        if winning_line:
            self.game_active = False
            self.scores[symbol] += 1
            for index in winning_line:
                self.cells[index].config(bg="#493e68")
            self.status_label.config(
                text=f"🎉 {self.player_names[symbol]} wins this round!"
            )
            self.update_score()
            self.reset_button.config(text="↻  Play next round")
        elif all(self.board):
            self.game_active = False
            self.status_label.config(text="🤝 It's a cosmic draw!")
            self.reset_button.config(text="↻  Play next round")
        else:
            self.current_player = "O" if symbol == "X" else "X"
            self.update_status()

    def get_winning_line(self):
        for line in WINNING_LINES:
            first, second, third = line
            if self.board[first] and self.board[first] == self.board[second] == self.board[third]:
                return line
        return None

    def update_status(self):
        symbol = self.current_player
        color = COLORS["pink"] if symbol == "X" else COLORS["blue"]
        self.status_label.config(
            text=f"{self.player_names[symbol]}'s turn  ·  {symbol}",
            fg=color,
        )

    def update_score(self):
        self.score_label.config(
            text=(
                f"✕ {self.player_names['X']}: {self.scores['X']}"
                f"     •     ○ {self.player_names['O']}: {self.scores['O']}"
            )
        )

    def animate_background(self):
        for item, speed in self.particles:
            self.canvas.move(item, 0, -speed)
            x1, y1, x2, y2 = self.canvas.coords(item)
            if y2 < 0:
                x = random.randint(5, 755)
                self.canvas.coords(item, x, 700, x + (x2 - x1), 700 + (y2 - y1))
        self.root.after(70, self.animate_background)


if __name__ == "__main__":
    window = tk.Tk()
    TicTacToe(window)
    window.mainloop()
