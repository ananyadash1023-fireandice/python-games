import csv
import random
import tkinter as tk
from decimal import Decimal
from pathlib import Path


BACKGROUND = "#101426"
PANEL = "#1b2238"
TILE_BACK = "#303c5a"
TEXT = "#f3f5ff"
MUTED = "#aab5d0"
ACCENT = "#75dfbd"
PINK = "#ff7894"
BLUE = "#83caff"
GOLD = "#ffd166"

SOURCE_RECORDS = (
    {"id": "C01", "name": "  ADA LOVELACE  ", "email": " ADA.LOVELACE@EXAMPLE.COM ", "amount": " $1,245.50 "},
    {"id": "C02", "name": " grace hopper ", "email": " Grace.Hopper@Example.com ", "amount": " $980.00 "},
    {"id": "C03", "name": "KATHERINE JOHNSON ", "email": " KATHERINE.JOHNSON@EXAMPLE.COM ", "amount": " $2,410.75 "},
    {"id": "C04", "name": " alan turing  ", "email": "ALAN.TURING@EXAMPLE.COM ", "amount": " $1,125.25 "},
    {"id": "C05", "name": "  MARY JACKSON", "email": " mary.jackson@EXAMPLE.COM ", "amount": " $760.00 "},
    {"id": "C06", "name": "DONALD KNUTH  ", "email": " DONALD.KNUTH@EXAMPLE.COM ", "amount": " $3,050.50 "},
    {"id": "C07", "name": " radia perlman ", "email": " Radia.Perlman@Example.com ", "amount": " $1,890.00 "},
    {"id": "C08", "name": "MARGARET HAMILTON ", "email": " MARGARET.HAMILTON@EXAMPLE.COM ", "amount": " $2,200.25 "},
)


def transform_record(record):
    return {
        "id": record["id"].strip(),
        "name": record["name"].strip().title(),
        "email": record["email"].strip().lower(),
        "amount": Decimal(
            record["amount"].strip().replace("$", "").replace(",", "")
        ),
    }


def write_warehouse(records, path):
    with Path(path).open("w", newline="", encoding="utf-8") as warehouse_file:
        writer = csv.DictWriter(
            warehouse_file,
            fieldnames=("id", "name", "email", "amount"),
        )
        writer.writeheader()
        for record in records:
            writer.writerow({
                **record,
                "amount": f"{record['amount']:.2f}",
            })


class ETLMemoryMatch:
    def __init__(self, root):
        self.root = root
        self.root.title("ETL Memory Match - Data Detective")
        self.root.geometry("1040x760")
        self.root.minsize(900, 690)
        self.root.configure(bg=BACKGROUND)

        self.hide_job = None
        self.hint_job = None
        self.selection = []
        self.matched_ids = set()
        self.extracted_records = []
        self.transformed_records = []
        self.loaded = False

        self.build_interface()
        self.new_game()
        self.root.after(350, self.show_instructions)
        self.animate_stars()

    def build_interface(self):
        self.background_canvas = tk.Canvas(
            self.root, bg=BACKGROUND, highlightthickness=0
        )
        self.background_canvas.place(relwidth=1, relheight=1)
        self.stars = []
        random.seed(23)
        for _ in range(45):
            x = random.randint(0, 1040)
            y = random.randint(0, 760)
            size = random.choice((2, 3, 4))
            star = self.background_canvas.create_oval(
                x, y, x + size, y + size, fill="#514777", outline=""
            )
            self.stars.append((star, random.choice((1, 1, 2))))

        header = tk.Frame(self.root, bg=BACKGROUND, padx=18, pady=12)
        header.pack(fill="x")
        tk.Label(
            header,
            text="✦  ETL MEMORY MATCH  ✦",
            font=("Segoe UI", 22, "bold"),
            bg=BACKGROUND,
            fg=ACCENT,
        ).pack()
        tk.Label(
            header,
            text="Match each messy source record to its cleaned version.",
            font=("Segoe UI", 10),
            bg=BACKGROUND,
            fg=MUTED,
        ).pack(pady=(3, 0))

        content = tk.Frame(self.root, bg=BACKGROUND, padx=18, pady=6)
        content.pack(fill="both", expand=True)
        self.board_frame = tk.Frame(content, bg=BACKGROUND)
        self.board_frame.pack(side="left", fill="both", expand=True, padx=(0, 14))

        self.sidebar = tk.Frame(
            content,
            bg=PANEL,
            padx=14,
            pady=13,
            width=280,
            highlightbackground="#35415f",
            highlightthickness=1,
        )
        self.sidebar.pack(side="right", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="THE ETL PIPELINE",
            font=("Segoe UI", 12, "bold"),
            bg=PANEL,
            fg=ACCENT,
        ).pack(anchor="w", pady=(0, 8))
        self.stage_labels = {}
        for stage, title, explanation in (
            ("extract", "1. EXTRACT", "Match each raw record with its cleaned pair."),
            ("transform", "2. TRANSFORM", "Standardize names, emails, and amounts."),
            ("load", "3. LOAD", "Save the clean data as a CSV warehouse."),
        ):
            section = tk.Frame(self.sidebar, bg="#26314b", padx=9, pady=7)
            section.pack(fill="x", pady=3)
            tk.Label(
                section,
                text=title,
                font=("Segoe UI", 9, "bold"),
                bg="#26314b",
                fg=TEXT,
            ).pack(anchor="w")
            tk.Label(
                section,
                text=explanation,
                font=("Segoe UI", 8),
                bg="#26314b",
                fg=MUTED,
                wraplength=230,
                justify="left",
            ).pack(anchor="w", pady=(2, 3))
            status = tk.Label(
                section,
                text="Not complete",
                font=("Segoe UI", 8, "bold"),
                bg="#26314b",
                fg=BLUE,
            )
            status.pack(anchor="w")
            self.stage_labels[stage] = status

        self.stats_label = tk.Label(
            self.sidebar,
            text="Pairs found: 0 / 8     Moves: 0",
            font=("Segoe UI", 9, "bold"),
            bg=PANEL,
            fg=GOLD,
        )
        self.stats_label.pack(pady=(9, 7))

        self.transform_button = tk.Button(
            self.sidebar,
            text="🧹  Transform records",
            command=self.transform_data,
            state="disabled",
            font=("Segoe UI", 9, "bold"),
            bg="#7867b4",
            fg="white",
            activebackground="#9582d4",
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=7,
        )
        self.transform_button.pack(fill="x", pady=3)
        self.load_button = tk.Button(
            self.sidebar,
            text="📦  Load CSV warehouse",
            command=self.load_warehouse,
            state="disabled",
            font=("Segoe UI", 9, "bold"),
            bg="#388b78",
            fg="white",
            activebackground="#4ba993",
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=7,
        )
        self.load_button.pack(fill="x", pady=3)
        tk.Button(
            self.sidebar,
            text="💡  Give me a hint",
            command=self.show_hint,
            font=("Segoe UI", 9, "bold"),
            bg="#35415f",
            fg=TEXT,
            activebackground="#465577",
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=7,
        ).pack(fill="x", pady=(3, 0))
        tk.Button(
            self.sidebar,
            text="📘  How to play",
            command=self.show_instructions,
            font=("Segoe UI", 9, "bold"),
            bg="#35415f",
            fg=TEXT,
            activebackground="#465577",
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=7,
        ).pack(fill="x", pady=(3, 0))

        tk.Label(
            self.sidebar,
            text="SELECTED DATA",
            font=("Segoe UI", 9, "bold"),
            bg=PANEL,
            fg=ACCENT,
        ).pack(anchor="w", pady=(12, 4))
        self.preview = tk.Label(
            self.sidebar,
            text="Turn over a tile to inspect its record.",
            font=("Consolas", 8),
            bg=PANEL,
            fg=TEXT,
            justify="left",
            anchor="nw",
            wraplength=245,
        )
        self.preview.pack(fill="x", anchor="nw")

        self.status_label = tk.Label(
            self.root,
            text="",
            font=("Segoe UI", 9),
            bg=BACKGROUND,
            fg=TEXT,
            anchor="w",
            padx=20,
            pady=8,
        )
        self.status_label.pack(fill="x", side="bottom")
        footer = tk.Frame(self.root, bg=BACKGROUND, padx=20, pady=7)
        footer.pack(fill="x", side="bottom")
        tk.Button(
            footer,
            text="🔄  New game",
            command=self.new_game,
            font=("Segoe UI", 9, "bold"),
            bg="#26314b",
            fg=TEXT,
            activebackground="#3a4868",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
        ).pack(side="left")
        tk.Label(
            footer,
            text="Each matching pair is one record moving from the source into the ETL pipeline.",
            font=("Segoe UI", 8),
            bg=BACKGROUND,
            fg=MUTED,
        ).pack(side="left", padx=10)

    def show_instructions(self):
        from tkinter import messagebox

        messagebox.showinfo(
            "How to play ETL Memory Match",
            "GOAL\n"
            "Find all eight pairs. Each pair is the same customer record shown "
            "once as messy source data and once as cleaned data.\n\n"
            "HOW TO PLAY\n"
            "1. Click any tile to turn it over and inspect the record.\n"
            "2. Click another tile. Match the same customer ID, with one RAW "
            "tile and one CLEAN tile.\n"
            "3. Keep matching until all eight records are extracted.\n"
            "4. Click Transform records to clean the source data.\n"
            "5. Click Load CSV warehouse to save the results in "
            "etl_warehouse.csv beside this game.\n\n"
            "ETL means Extract, Transform, Load. Use Give me a hint if you need help!",
        )

    def new_game(self):
        if self.hide_job is not None:
            self.root.after_cancel(self.hide_job)
            self.hide_job = None
        if self.hint_job is not None:
            self.root.after_cancel(self.hint_job)
            self.hint_job = None

        self.selection = []
        self.matched_ids = set()
        self.extracted_records = []
        self.transformed_records = []
        self.loaded = False
        self.moves = 0
        self.records_by_id = {record["id"]: record for record in SOURCE_RECORDS}

        self.tiles = []
        for record in SOURCE_RECORDS:
            self.tiles.append({"id": record["id"], "kind": "RAW", "face_up": False})
            self.tiles.append({"id": record["id"], "kind": "CLEAN", "face_up": False})
        random.shuffle(self.tiles)

        self.transform_button.config(state="disabled")
        self.load_button.config(state="disabled")
        self.stage_labels["extract"].config(text="0 / 8 records matched", fg=BLUE)
        self.stage_labels["transform"].config(text="Waiting for extraction", fg=BLUE)
        self.stage_labels["load"].config(text="Waiting for transformation", fg=BLUE)
        self.preview.config(text="Turn over a tile to inspect its record.")
        self.status_label.config(text="Find a RAW and CLEAN tile with the same customer ID.")
        self.render_tiles()
        self.update_stats()

    def render_tiles(self):
        for child in self.board_frame.winfo_children():
            child.destroy()

        self.tile_buttons = []
        for index, tile in enumerate(self.tiles):
            row, column = divmod(index, 4)
            if tile["face_up"] or tile["id"] in self.matched_ids:
                record = self.records_by_id[tile["id"]]
                clean = transform_record(record)
                is_raw = tile["kind"] == "RAW"
                lines = (
                    f"{tile['id']}\nRAW\n"
                    f"{record['name'].strip()}\n"
                    f"{record['email'].strip()}"
                    if is_raw
                    else f"{tile['id']}\nCLEAN\n"
                    f"{clean['name']}\n"
                    f"{clean['email']}"
                )
                bg = "#fff4e8" if is_raw else "#e8f7ff"
                fg = "#a84054" if is_raw else "#255d86"
                if tile["id"] in self.matched_ids:
                    bg = "#dff7eb" if is_raw else "#e3f2ff"
                button_text = lines
            else:
                button_text = "✦\nDATA"
                bg = TILE_BACK
                fg = "#d9e3ff"

            button = tk.Button(
                self.board_frame,
                text=button_text,
                command=lambda tile_index=index: self.flip_tile(tile_index),
                font=("Segoe UI", 9, "bold"),
                bg=bg,
                fg=fg,
                activebackground="#e2dbff",
                activeforeground=fg,
                relief="flat",
                cursor="hand2",
                width=20,
                height=6,
                wraplength=145,
                justify="center",
                highlightthickness=2,
                highlightbackground="#394766",
            )
            button.grid(row=row, column=column, padx=5, pady=5, sticky="nsew")
            self.tile_buttons.append(button)

        for row in range(4):
            self.board_frame.grid_rowconfigure(row, weight=1)
        for column in range(4):
            self.board_frame.grid_columnconfigure(column, weight=1)

    def flip_tile(self, index):
        if self.loaded or self.hide_job is not None or len(self.selection) >= 2:
            return
        tile = self.tiles[index]
        if tile["face_up"] or tile["id"] in self.matched_ids:
            return

        tile["face_up"] = True
        self.selection.append(index)
        self.show_record(tile)
        self.render_tiles()

        if len(self.selection) == 2:
            self.moves += 1
            first, second = (self.tiles[position] for position in self.selection)
            if first["id"] == second["id"] and first["kind"] != second["kind"]:
                self.matched_ids.add(first["id"])
                self.extracted_records.append(self.records_by_id[first["id"]])
                self.selection = []
                self.stage_labels["extract"].config(
                    text=f"{len(self.matched_ids)} / 8 records matched",
                    fg=ACCENT if len(self.matched_ids) == len(SOURCE_RECORDS) else BLUE,
                )
                self.status_label.config(
                    text=f"Match! Record {first['id']} was extracted from the source."
                )
                if len(self.matched_ids) == len(SOURCE_RECORDS):
                    self.transform_button.config(state="normal")
                    self.stage_labels["transform"].config(text="Ready to transform", fg=ACCENT)
                    self.status_label.config(
                        text="All records extracted! Click Transform records to continue."
                    )
            else:
                self.status_label.config(
                    text="Not a pair. Match the same ID: one RAW tile and one CLEAN tile."
                )
                self.hide_job = self.root.after(1000, self.hide_unmatched)
            self.update_stats()

    def hide_unmatched(self):
        self.hide_job = None
        for index in self.selection:
            self.tiles[index]["face_up"] = False
        self.selection = []
        self.render_tiles()

    def show_record(self, tile):
        record = self.records_by_id[tile["id"]]
        clean = transform_record(record)
        if tile["kind"] == "RAW":
            details = (
                f"ID: {record['id']}  |  RAW SOURCE\n"
                f"Name: {record['name']!r}\n"
                f"Email: {record['email']!r}\n"
                f"Amount: {record['amount']!r}"
            )
        else:
            details = (
                f"ID: {clean['id']}  |  CLEAN COPY\n"
                f"Name: {clean['name']}\n"
                f"Email: {clean['email']}\n"
                f"Amount: ${clean['amount']:,.2f}"
            )
        self.preview.config(text=details)

    def show_hint(self):
        if self.loaded:
            self.status_label.config(text="You finished the ETL pipeline. Start a new game to play again.")
            return
        if len(self.matched_ids) == len(SOURCE_RECORDS):
            self.status_label.config(text="All records are extracted. Transform them, then load the CSV.")
            return
        if len(self.selection) == 1:
            tile = self.tiles[self.selection[0]]
            other_kind = "CLEAN" if tile["kind"] == "RAW" else "RAW"
            self.status_label.config(
                text=f"Look for the {other_kind} tile with the same ID: {tile['id']}."
            )
            return
        if self.selection:
            self.status_label.config(text="Wait for the unmatched cards to turn back over.")
            return

        available_ids = [
            record_id for record_id in self.records_by_id
            if record_id not in self.matched_ids
        ]
        hint_id = random.choice(available_ids)
        positions = [
            index + 1 for index, tile in enumerate(self.tiles)
            if tile["id"] == hint_id
        ]
        self.status_label.config(
            text=f"Hint: tiles {positions[0]} and {positions[1]} are a pair "
            f"(record {hint_id}: match RAW with CLEAN)."
        )

    def transform_data(self):
        if len(self.matched_ids) != len(SOURCE_RECORDS):
            self.status_label.config(text="Match all eight record pairs before transforming.")
            return
        self.transformed_records = [
            transform_record(record) for record in self.extracted_records
        ]
        self.transform_button.config(state="disabled")
        self.load_button.config(state="normal")
        self.stage_labels["transform"].config(
            text="8 records cleaned and standardized", fg=ACCENT
        )
        self.stage_labels["load"].config(text="Ready to load", fg=ACCENT)
        self.status_label.config(
            text="Transformation complete: trimmed names, normalized emails, parsed amounts."
        )
        if self.transformed_records:
            self.show_record({
                "id": self.transformed_records[0]["id"],
                "kind": "CLEAN",
            })

    def load_warehouse(self):
        if not self.transformed_records:
            self.status_label.config(text="Transform the records before loading the warehouse.")
            return

        warehouse_path = Path(__file__).with_name("etl_warehouse.csv")
        try:
            write_warehouse(self.transformed_records, warehouse_path)
        except OSError as error:
            self.status_label.config(text=f"Could not write the warehouse: {error}")
            return

        self.loaded = True
        self.load_button.config(state="disabled")
        self.stage_labels["load"].config(text="8 records saved to CSV", fg=ACCENT)
        self.status_label.config(
            text=f"🎉 ETL complete! Your warehouse file is {warehouse_path.name}."
        )

    def update_stats(self):
        self.stats_label.config(
            text=f"Pairs found: {len(self.matched_ids)} / 8     Moves: {self.moves}"
        )

    def animate_stars(self):
        for star, speed in self.stars:
            self.background_canvas.move(star, 0, -speed)
            x1, y1, x2, y2 = self.background_canvas.coords(star)
            if y2 < 0:
                x = random.randint(0, 1040)
                self.background_canvas.coords(star, x, 760, x + (x2 - x1), 760 + (y2 - y1))
        self.root.after(80, self.animate_stars)


if __name__ == "__main__":
    window = tk.Tk()
    ETLMemoryMatch(window)
    window.mainloop()
