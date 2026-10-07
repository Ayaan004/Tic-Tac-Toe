"""
Tic Tac Toe — Professional Edition
A sleek, modern Tic Tac Toe game with animated GUI.
Built with CustomTkinter for a premium dark-mode experience.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import font as tkfont
import random
import math

# ──────────────────────────────────────────────
# Theme & Color Palette
# ──────────────────────────────────────────────
COLORS = {
    "bg_dark":       "#0F0F1A",
    "bg_card":       "#1A1A2E",
    "bg_cell":       "#16213E",
    "bg_cell_hover": "#1E2D4A",
    "accent_x":      "#E94560",      # Vibrant rose-red for X
    "accent_o":      "#0EA5E9",      # Bright sky-blue for O
    "accent_win":    "#22D3EE",      # Cyan glow for winning line
    "text_primary":  "#E2E8F0",
    "text_secondary":"#94A3B8",
    "text_muted":    "#475569",
    "border":        "#2A2A4A",
    "btn_hover":     "#2D2D5A",
    "btn_active":    "#3D3D6A",
    "gradient_start":"#6366F1",      # Indigo
    "gradient_end":  "#8B5CF6",      # Violet
    "draw_color":    "#FBBF24",      # Amber for draw
}


class TicTacToeApp(ctk.CTk):
    """Main application window for the Tic Tac Toe game."""

    def __init__(self):
        super().__init__()

        # ── Window Setup ──
        self.title("Tic Tac Toe — Pro Edition")
        self.geometry("520x780")
        self.minsize(480, 720)
        self.configure(fg_color=COLORS["bg_dark"])
        self.resizable(False, False)

        # ── Game State ──
        self.board = [""] * 9
        self.current_player = "X"
        self.game_active = True
        self.vs_ai = True
        self.ai_difficulty = "hard"   # easy | medium | hard
        self.scores = {"X": 0, "O": 0, "draws": 0}
        self.match_history = []       # Detailed match logs
        self.current_streak = {"player": None, "count": 0}
        self.winning_combo = None
        self.animation_ids = []
        self.score_window = None

        # ── Build UI ──
        self._build_header()
        self._build_mode_selector()
        self._build_scoreboard()
        self._build_grid()
        self._build_status_bar()
        self._build_controls()

    # ──────────────────────────────────────────
    # UI Construction
    # ──────────────────────────────────────────
    def _build_header(self):
        """Top title bar with gradient-style accent."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=24, pady=(18, 0))

        # Title
        title = ctk.CTkLabel(
            header_frame,
            text="TIC  TAC  TOE",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=COLORS["text_primary"],
        )
        title.pack(side="top")

        # Subtitle with accent line
        subtitle = ctk.CTkLabel(
            header_frame,
            text="P R O   E D I T I O N",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["gradient_start"],
        )
        subtitle.pack(side="top", pady=(0, 4))

        # Decorative accent bar
        accent_canvas = tk.Canvas(
            header_frame, height=3, bg=COLORS["bg_dark"],
            highlightthickness=0, bd=0,
        )
        accent_canvas.pack(fill="x", pady=(2, 0))
        accent_canvas.update_idletasks()
        w = max(accent_canvas.winfo_width(), 400)
        accent_canvas.create_rectangle(
            w * 0.2, 0, w * 0.8, 3,
            fill=COLORS["gradient_start"], outline=""
        )

    def _build_mode_selector(self):
        """Toggle between PvP and PvAI modes + difficulty selector."""
        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.pack(fill="x", padx=24, pady=(12, 0))

        inner = ctk.CTkFrame(mode_frame, fg_color=COLORS["bg_card"],
                             corner_radius=12, border_width=1,
                             border_color=COLORS["border"])
        inner.pack(fill="x")
        inner.grid_columnconfigure((0, 1, 2), weight=1)

        self.mode_var = ctk.StringVar(value="ai")

        self.btn_pvp = ctk.CTkButton(
            inner, text="👤  PvP", font=ctk.CTkFont(size=13),
            fg_color="transparent", hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_secondary"], corner_radius=8,
            command=lambda: self._set_mode("pvp"), height=36,
        )
        self.btn_pvp.grid(row=0, column=0, padx=6, pady=6, sticky="ew")

        self.btn_ai = ctk.CTkButton(
            inner, text="🤖  vs AI", font=ctk.CTkFont(size=13),
            fg_color=COLORS["gradient_start"], hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_primary"], corner_radius=8,
            command=lambda: self._set_mode("ai"), height=36,
        )
        self.btn_ai.grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        self.diff_menu = ctk.CTkOptionMenu(
            inner, values=["Easy", "Medium", "Hard"],
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["bg_cell"], button_color=COLORS["gradient_end"],
            button_hover_color=COLORS["btn_active"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_primary"],
            corner_radius=8, height=36,
            command=self._set_difficulty,
        )
        self.diff_menu.set("Hard")
        self.diff_menu.grid(row=0, column=2, padx=6, pady=6, sticky="ew")

    def _build_scoreboard(self):
        """Score display for X, draws, and O."""
        score_frame = ctk.CTkFrame(self, fg_color="transparent")
        score_frame.pack(fill="x", padx=24, pady=(12, 0))

        card = ctk.CTkFrame(score_frame, fg_color=COLORS["bg_card"],
                            corner_radius=12, border_width=1,
                            border_color=COLORS["border"])
        card.pack(fill="x")
        card.grid_columnconfigure((0, 1, 2), weight=1)

        # X score
        self.x_score_label = self._make_score_block(
            card, "X (YOU)", "0", COLORS["accent_x"], 0
        )
        # Draws
        self.draw_score_label = self._make_score_block(
            card, "DRAWS", "0", COLORS["draw_color"], 1
        )
        # O score
        self.o_score_label = self._make_score_block(
            card, "O (AI)", "0", COLORS["accent_o"], 2
        )

    def _make_score_block(self, parent, title, value, color, col):
        """Helper to create a score block widget."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(
            frame, text=title,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_muted"],
        ).pack()

        lbl = ctk.CTkLabel(
            frame, text=value,
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=color,
        )
        lbl.pack(pady=(2, 0))
        return lbl

    def _build_grid(self):
        """3×3 game grid using Canvas for custom rendering."""
        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.pack(padx=24, pady=(16, 0))

        self.grid_canvas = tk.Canvas(
            grid_frame,
            width=400, height=400,
            bg=COLORS["bg_card"],
            highlightthickness=0, bd=0,
        )
        self.grid_canvas.pack()

        # Rounded rectangle background
        self._round_rect(self.grid_canvas, 0, 0, 400, 400, 16,
                         fill=COLORS["bg_card"], outline=COLORS["border"], width=1)

        cell_size = 120
        gap = 10
        offset = (400 - 3 * cell_size - 2 * gap) // 2

        self.cell_coords = []
        for row in range(3):
            for col in range(3):
                x1 = offset + col * (cell_size + gap)
                y1 = offset + row * (cell_size + gap)
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                self.cell_coords.append((x1, y1, x2, y2))

                self._round_rect(
                    self.grid_canvas, x1, y1, x2, y2, 12,
                    fill=COLORS["bg_cell"], outline=COLORS["border"], width=1
                )

        # Bind clicks
        self.grid_canvas.bind("<Button-1>", self._on_grid_click)
        self.grid_canvas.bind("<Motion>", self._on_grid_hover)

        self.hover_cell = -1

    def _build_status_bar(self):
        """Status text below the grid and Retry button container."""
        self.status_container = ctk.CTkFrame(self, fg_color="transparent")
        self.status_container.pack(fill="x", padx=24, pady=(12, 0))

        self.status_label = ctk.CTkLabel(
            self.status_container,
            text="Your turn — place X",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=COLORS["text_secondary"],
        )
        self.status_label.pack()

        # Retry button appears after a draw or match
        self.retry_button = ctk.CTkButton(
            self.status_container,
            text="🔄  Play Again",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["gradient_start"],
            hover_color=COLORS["gradient_end"],
            text_color=COLORS["text_primary"],
            corner_radius=10,
            height=38,
            width=180,
            command=self._restart_game,
        )
        # Initially hidden until match ends

    def _build_controls(self):
        """Bottom control buttons: New Game, Score Menu, Reset."""
        ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=24, pady=(14, 20))
        ctrl_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_restart = ctk.CTkButton(
            ctrl_frame, text="🔄  New Game",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_primary"],
            border_width=1, border_color=COLORS["border"],
            corner_radius=10, height=42,
            command=self._restart_game,
        )
        self.btn_restart.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.btn_score_menu = ctk.CTkButton(
            ctrl_frame, text="📊  Score Menu",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["gradient_start"],
            hover_color=COLORS["gradient_end"],
            text_color=COLORS["text_primary"],
            corner_radius=10, height=42,
            command=self._open_score_menu,
        )
        self.btn_score_menu.grid(row=0, column=1, padx=4, sticky="ew")

        self.btn_reset = ctk.CTkButton(
            ctrl_frame, text="🗑  Reset Scores",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["btn_hover"],
            text_color=COLORS["text_secondary"],
            border_width=1, border_color=COLORS["border"],
            corner_radius=10, height=42,
            command=self._reset_scores,
        )
        self.btn_reset.grid(row=0, column=2, padx=(4, 0), sticky="ew")

    # ──────────────────────────────────────────
    # Canvas Helpers
    # ──────────────────────────────────────────
    def _round_rect(self, canvas, x1, y1, x2, y2, r, **kwargs):
        """Draw a rounded rectangle on a canvas."""
        points = [
            x1 + r, y1, x2 - r, y1,
            x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2,
            x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r,
            x1, y1 + r, x1, y1,
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)

    def _draw_x(self, cell_idx, color=None, animated=True):
        """Draw an X symbol in the given cell with optional animation."""
        color = color or COLORS["accent_x"]
        x1, y1, x2, y2 = self.cell_coords[cell_idx]
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        pad = 30
        line_width = 6
        tag = f"symbol_{cell_idx}"

        if animated:
            self._animate_x(cell_idx, cx, cy, pad, color, line_width, 0)
        else:
            self.grid_canvas.delete(tag)
            self.grid_canvas.create_line(
                cx - pad, cy - pad, cx + pad, cy + pad,
                fill=color, width=line_width, capstyle="round",
                tags=tag
            )
            self.grid_canvas.create_line(
                cx + pad, cy - pad, cx - pad, cy + pad,
                fill=color, width=line_width, capstyle="round",
                tags=tag
            )
            self.grid_canvas.tag_raise(tag)

    def _animate_x(self, cell_idx, cx, cy, pad, color, width, step):
        """Animate drawing an X stroke by stroke."""
        total_steps = 8
        tag = f"symbol_{cell_idx}"

        if step > total_steps:
            return

        frac = step / total_steps
        if frac <= 0.5:
            # First stroke
            t = frac * 2
            ex = cx - pad + 2 * pad * t
            ey = cy - pad + 2 * pad * t
            self.grid_canvas.delete(f"{tag}_1")
            self.grid_canvas.create_line(
                cx - pad, cy - pad, ex, ey,
                fill=color, width=width, capstyle="round",
                tags=(tag, f"{tag}_1")
            )
        else:
            # Second stroke
            t = (frac - 0.5) * 2
            ex = cx + pad - 2 * pad * t
            ey = cy - pad + 2 * pad * t
            self.grid_canvas.delete(f"{tag}_2")
            self.grid_canvas.create_line(
                cx + pad, cy - pad, ex, ey,
                fill=color, width=width, capstyle="round",
                tags=(tag, f"{tag}_2")
            )

        self.grid_canvas.tag_raise(tag)

        if step < total_steps:
            aid = self.after(25, self._animate_x, cell_idx, cx, cy, pad, color, width, step + 1)
            self.animation_ids.append(aid)

    def _draw_o(self, cell_idx, color=None, animated=True):
        """
        Draw an O symbol in the given cell.
        Uses create_oval to ensure 100% reliable rendering on all platforms.
        """
        color = color or COLORS["accent_o"]
        x1, y1, x2, y2 = self.cell_coords[cell_idx]
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        radius = 32
        line_width = 6
        tag = f"symbol_{cell_idx}"

        if animated:
            self._animate_o(cell_idx, cx, cy, radius, color, line_width, 1)
        else:
            self.grid_canvas.delete(tag)
            self.grid_canvas.create_oval(
                cx - radius, cy - radius, cx + radius, cy + radius,
                outline=color, width=line_width,
                tags=tag
            )
            self.grid_canvas.tag_raise(tag)

    def _animate_o(self, cell_idx, cx, cy, target_radius, color, width, step):
        """Animate drawing an O by smoothly expanding outward."""
        total_steps = 6
        tag = f"symbol_{cell_idx}"
        current_r = max(10, int(target_radius * (step / total_steps)))

        self.grid_canvas.delete(tag)
        self.grid_canvas.create_oval(
            cx - current_r, cy - current_r, cx + current_r, cy + current_r,
            outline=color, width=width,
            tags=tag
        )
        self.grid_canvas.tag_raise(tag)

        if step < total_steps:
            aid = self.after(20, self._animate_o, cell_idx, cx, cy, target_radius, color, width, step + 1)
            self.animation_ids.append(aid)

    def _highlight_winning_cells(self, combo):
        """Highlight winning cells with a glow effect."""
        for idx in combo:
            x1, y1, x2, y2 = self.cell_coords[idx]
            self._round_rect(
                self.grid_canvas, x1, y1, x2, y2, 12,
                fill="#1B2A4A", outline=COLORS["accent_win"], width=2
            )
            # Redraw symbol with highlight color
            if self.board[idx] == "X":
                self._draw_x(idx, color=COLORS["accent_win"], animated=False)
            else:
                self._draw_o(idx, color=COLORS["accent_win"], animated=False)

    # ──────────────────────────────────────────
    # Event Handlers
    # ──────────────────────────────────────────
    def _on_grid_click(self, event):
        """Handle click on the game grid."""
        if not self.game_active:
            return

        cell = self._get_cell_at(event.x, event.y)
        if cell == -1 or self.board[cell] != "":
            return

        self._make_move(cell)

    def _on_grid_hover(self, event):
        """Handle mouse hover for cell highlighting."""
        cell = self._get_cell_at(event.x, event.y)

        if cell == self.hover_cell:
            return

        # Restore previous hover cell
        if self.hover_cell != -1 and self.board[self.hover_cell] == "":
            x1, y1, x2, y2 = self.cell_coords[self.hover_cell]
            self._round_rect(
                self.grid_canvas, x1, y1, x2, y2, 12,
                fill=COLORS["bg_cell"], outline=COLORS["border"], width=1
            )

        self.hover_cell = cell

        # Highlight new empty cell
        if cell != -1 and self.board[cell] == "" and self.game_active:
            x1, y1, x2, y2 = self.cell_coords[cell]
            self._round_rect(
                self.grid_canvas, x1, y1, x2, y2, 12,
                fill=COLORS["bg_cell_hover"], outline=COLORS["gradient_start"], width=1
            )

    def _get_cell_at(self, mx, my):
        """Return the cell index at the given mouse coordinates, or -1."""
        for i, (x1, y1, x2, y2) in enumerate(self.cell_coords):
            if x1 <= mx <= x2 and y1 <= my <= y2:
                return i
        return -1

    # ──────────────────────────────────────────
    # Game Logic
    # ──────────────────────────────────────────
    WIN_COMBOS = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # cols
        (0, 4, 8), (2, 4, 6),              # diags
    ]

    def _make_move(self, cell):
        """Place the current player's mark and process the result."""
        self.board[cell] = self.current_player

        # Reset hover state for this cell
        if self.hover_cell == cell:
            self.hover_cell = -1

        # Clear any cell hover rect and draw standard cell background
        x1, y1, x2, y2 = self.cell_coords[cell]
        self._round_rect(
            self.grid_canvas, x1, y1, x2, y2, 12,
            fill=COLORS["bg_cell"], outline=COLORS["border"], width=1
        )

        # Draw symbol
        if self.current_player == "X":
            self._draw_x(cell)
        else:
            self._draw_o(cell)

        winner = self._check_winner()
        if winner:
            self.game_active = False
            self.winning_combo = self._get_winning_combo(winner)
            self.scores[winner] += 1
            self._update_scores()
            self._highlight_winning_cells(self.winning_combo)

            # Record streak
            if self.current_streak["player"] == winner:
                self.current_streak["count"] += 1
            else:
                self.current_streak = {"player": winner, "count": 1}

            # Record history
            mode_desc = f"vs AI ({self.ai_difficulty.capitalize()})" if self.vs_ai else "PvP"
            winner_desc = "You (X)" if (self.vs_ai and winner == "X") else (f"AI ({self.ai_difficulty.capitalize()})" if self.vs_ai else f"Player {winner}")
            self.match_history.append({
                "round": len(self.match_history) + 1,
                "winner": winner,
                "description": f"{winner_desc} Won",
                "mode": mode_desc
            })

            symbol_name = "X" if winner == "X" else "O"
            if self.vs_ai:
                msg = "🎉 You win!" if winner == "X" else "🤖 AI wins!"
            else:
                msg = f"🎉 Player {symbol_name} wins!"
            color = COLORS["accent_x"] if winner == "X" else COLORS["accent_o"]
            self.status_label.configure(text=msg, text_color=color)

            # Show retry button after match
            self.retry_button.pack(pady=(10, 0))
            return

        if "" not in self.board:
            self.game_active = False
            self.scores["draws"] += 1
            self._update_scores()
            self.current_streak = {"player": None, "count": 0}

            mode_desc = f"vs AI ({self.ai_difficulty.capitalize()})" if self.vs_ai else "PvP"
            self.match_history.append({
                "round": len(self.match_history) + 1,
                "winner": "Draw",
                "description": "Draw Match",
                "mode": mode_desc
            })

            self.status_label.configure(
                text="🤝 It's a draw!", text_color=COLORS["draw_color"]
            )

            # Show retry button after draw
            self.retry_button.pack(pady=(10, 0))
            return

        # Switch turns
        self.current_player = "O" if self.current_player == "X" else "X"
        self._update_status_text()

        # AI move
        if self.vs_ai and self.current_player == "O" and self.game_active:
            self.after(350, self._ai_move)

    def _check_winner(self):
        """Return 'X', 'O', or None."""
        for combo in self.WIN_COMBOS:
            a, b, c = combo
            if self.board[a] == self.board[b] == self.board[c] != "":
                return self.board[a]
        return None

    def _get_winning_combo(self, winner):
        """Return the first winning combination tuple."""
        for combo in self.WIN_COMBOS:
            a, b, c = combo
            if self.board[a] == self.board[b] == self.board[c] == winner:
                return combo
        return None

    def _update_status_text(self):
        """Update the status label with current turn info."""
        if self.vs_ai:
            if self.current_player == "X":
                self.status_label.configure(
                    text="Your turn — place X",
                    text_color=COLORS["accent_x"]
                )
            else:
                self.status_label.configure(
                    text="AI is thinking…",
                    text_color=COLORS["accent_o"]
                )
        else:
            color = COLORS["accent_x"] if self.current_player == "X" else COLORS["accent_o"]
            self.status_label.configure(
                text=f"Player {self.current_player}'s turn",
                text_color=color,
            )

    def _update_scores(self):
        """Refresh the scoreboard labels."""
        self.x_score_label.configure(text=str(self.scores["X"]))
        self.o_score_label.configure(text=str(self.scores["O"]))
        self.draw_score_label.configure(text=str(self.scores["draws"]))

    # ──────────────────────────────────────────
    # Score Menu / Scorecard Modal
    # ──────────────────────────────────────────
    def _open_score_menu(self):
        """Open a dedicated, professional score menu popup."""
        if self.score_window is not None and self.score_window.winfo_exists():
            self.score_window.focus()
            return

        self.score_window = ctk.CTkToplevel(self)
        self.score_window.title("Scorecard & Match Stats")
        self.score_window.geometry("440x560")
        self.score_window.resizable(False, False)
        self.score_window.configure(fg_color=COLORS["bg_dark"])
        self.score_window.transient(self)
        self.score_window.grab_set()

        # Center on parent window
        self.score_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 440) // 2
        y = self.winfo_y() + (self.winfo_height() - 560) // 2
        self.score_window.geometry(f"440x560+{x}+{y}")

        # Top Title
        title_frame = ctk.CTkFrame(self.score_window, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            title_frame,
            text="📊  MATCH SCORECARD",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack()

        ctk.CTkLabel(
            title_frame,
            text="Detailed breakdown and match history",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
        ).pack(pady=(2, 0))

        # Overall Stats Card
        stats_card = ctk.CTkFrame(
            self.score_window, fg_color=COLORS["bg_card"],
            corner_radius=12, border_width=1, border_color=COLORS["border"]
        )
        stats_card.pack(fill="x", padx=20, pady=(10, 10))
        stats_card.grid_columnconfigure((0, 1, 2), weight=1)

        total_games = self.scores["X"] + self.scores["O"] + self.scores["draws"]
        win_rate = int((self.scores["X"] / total_games * 100)) if total_games > 0 else 0

        # Row 1: X wins, Draws, O wins
        self._make_stat_item(stats_card, "PLAYER X", str(self.scores["X"]), COLORS["accent_x"], 0, 0)
        self._make_stat_item(stats_card, "DRAWS", str(self.scores["draws"]), COLORS["draw_color"], 0, 1)
        o_name = "AI (O)" if self.vs_ai else "PLAYER O"
        self._make_stat_item(stats_card, o_name, str(self.scores["O"]), COLORS["accent_o"], 0, 2)

        # Row 2: Total Matches, Win Rate, Streak
        streak_text = "-"
        if self.current_streak["count"] > 0:
            p = self.current_streak["player"]
            p_name = "You" if (self.vs_ai and p == "X") else p
            streak_text = f"🔥 {self.current_streak['count']} ({p_name})"

        sub_stats = ctk.CTkFrame(stats_card, fg_color="transparent")
        sub_stats.grid(row=1, column=0, columnspan=3, padx=12, pady=(4, 12), sticky="ew")
        sub_stats.grid_columnconfigure((0, 1, 2), weight=1)

        self._make_stat_badge(sub_stats, "Total Matches", str(total_games), 0)
        self._make_stat_badge(sub_stats, "X Win Rate", f"{win_rate}%", 1)
        self._make_stat_badge(sub_stats, "Current Streak", streak_text, 2)

        # Match History Section Header
        hist_header = ctk.CTkLabel(
            self.score_window,
            text="Match History Log",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        hist_header.pack(fill="x", padx=22, pady=(6, 4))

        # Scrollable Match History
        hist_frame = ctk.CTkScrollableFrame(
            self.score_window,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            height=180
        )
        hist_frame.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        if not self.match_history:
            ctk.CTkLabel(
                hist_frame,
                text="No matches played in this session yet.\nStart playing to log match results!",
                font=ctk.CTkFont(size=13),
                text_color=COLORS["text_muted"],
            ).pack(pady=40)
        else:
            for item in reversed(self.match_history):
                row = ctk.CTkFrame(hist_frame, fg_color=COLORS["bg_cell"], corner_radius=8)
                row.pack(fill="x", pady=4, padx=4)

                badge_color = (
                    COLORS["accent_x"] if item["winner"] == "X"
                    else (COLORS["accent_o"] if item["winner"] == "O" else COLORS["draw_color"])
                )

                lbl_round = ctk.CTkLabel(
                    row, text=f"Round #{item['round']}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLORS["text_muted"],
                    width=70, anchor="w"
                )
                lbl_round.pack(side="left", padx=(10, 4), pady=6)

                lbl_res = ctk.CTkLabel(
                    row, text=item["description"],
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=badge_color,
                    anchor="w"
                )
                lbl_res.pack(side="left", padx=4, pady=6)

                lbl_mode = ctk.CTkLabel(
                    row, text=item["mode"],
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS["text_secondary"],
                    anchor="e"
                )
                lbl_mode.pack(side="right", padx=(4, 10), pady=6)

        # Bottom Buttons inside modal
        modal_btns = ctk.CTkFrame(self.score_window, fg_color="transparent")
        modal_btns.pack(fill="x", padx=20, pady=(0, 16))
        modal_btns.grid_columnconfigure((0, 1), weight=1)

        def clear_and_refresh():
            self._reset_scores()
            self.match_history.clear()
            self.current_streak = {"player": None, "count": 0}
            if self.score_window is not None and self.score_window.winfo_exists():
                self.score_window.destroy()
            self._open_score_menu()

        btn_clear = ctk.CTkButton(
            modal_btns, text="🗑  Clear All Stats",
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["btn_hover"],
            text_color=COLORS["accent_x"],
            border_width=1, border_color=COLORS["border"],
            corner_radius=8, height=36,
            command=clear_and_refresh
        )
        btn_clear.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        btn_close = ctk.CTkButton(
            modal_btns, text="Close",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["gradient_start"],
            hover_color=COLORS["gradient_end"],
            text_color=COLORS["text_primary"],
            corner_radius=8, height=36,
            command=self.score_window.destroy
        )
        btn_close.grid(row=0, column=1, padx=(6, 0), sticky="ew")

    def _make_stat_item(self, parent, title, value, color, row, col):
        """Helper to create a single score block in the score modal."""
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=col, padx=8, pady=(10, 4), sticky="nsew")

        ctk.CTkLabel(
            f, text=title,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_muted"],
        ).pack()

        ctk.CTkLabel(
            f, text=value,
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=color,
        ).pack(pady=(2, 0))

    def _make_stat_badge(self, parent, title, value, col):
        """Helper to create small summary badges."""
        f = ctk.CTkFrame(parent, fg_color=COLORS["bg_cell"], corner_radius=6)
        f.grid(row=0, column=col, padx=4, pady=2, sticky="ew")

        ctk.CTkLabel(
            f, text=title, font=ctk.CTkFont(size=10),
            text_color=COLORS["text_muted"]
        ).pack(pady=(4, 0))

        ctk.CTkLabel(
            f, text=value, font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(0, 4))

    # ──────────────────────────────────────────
    # AI (Minimax with Alpha-Beta Pruning)
    # ──────────────────────────────────────────
    def _ai_move(self):
        """Compute and execute the AI's move."""
        if not self.game_active:
            return

        if self.ai_difficulty == "easy":
            move = self._ai_random()
        elif self.ai_difficulty == "medium":
            # 60% chance of optimal move
            move = self._ai_minimax() if random.random() < 0.6 else self._ai_random()
        else:
            move = self._ai_minimax()

        if move is not None:
            self._make_move(move)

    def _ai_random(self):
        """Pick a random empty cell."""
        empty = [i for i in range(9) if self.board[i] == ""]
        return random.choice(empty) if empty else None

    def _ai_minimax(self):
        """Find the best move using Minimax with alpha-beta pruning."""
        best_score = -math.inf
        best_move = None

        for i in range(9):
            if self.board[i] == "":
                self.board[i] = "O"
                score = self._minimax(self.board, 0, False, -math.inf, math.inf)
                self.board[i] = ""
                if score > best_score:
                    best_score = score
                    best_move = i

        return best_move

    def _minimax(self, board, depth, is_maximizing, alpha, beta):
        """Minimax algorithm with alpha-beta pruning."""
        winner = self._check_winner()
        if winner == "O":
            return 10 - depth
        if winner == "X":
            return depth - 10
        if "" not in board:
            return 0

        if is_maximizing:
            max_eval = -math.inf
            for i in range(9):
                if board[i] == "":
                    board[i] = "O"
                    eval_score = self._minimax(board, depth + 1, False, alpha, beta)
                    board[i] = ""
                    max_eval = max(max_eval, eval_score)
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        break
            return max_eval
        else:
            min_eval = math.inf
            for i in range(9):
                if board[i] == "":
                    board[i] = "X"
                    eval_score = self._minimax(board, depth + 1, True, alpha, beta)
                    board[i] = ""
                    min_eval = min(min_eval, eval_score)
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break
            return min_eval

    # ──────────────────────────────────────────
    # Mode & Controls
    # ──────────────────────────────────────────
    def _set_mode(self, mode):
        """Switch between PvP and AI modes."""
        self.vs_ai = (mode == "ai")

        if mode == "ai":
            self.btn_ai.configure(fg_color=COLORS["gradient_start"],
                                  text_color=COLORS["text_primary"])
            self.btn_pvp.configure(fg_color="transparent",
                                   text_color=COLORS["text_secondary"])
            self.diff_menu.configure(state="normal")
            self.o_score_label.master.winfo_children()[0].configure(text="O (AI)")
            self.x_score_label.master.winfo_children()[0].configure(text="X (YOU)")
        else:
            self.btn_pvp.configure(fg_color=COLORS["gradient_start"],
                                   text_color=COLORS["text_primary"])
            self.btn_ai.configure(fg_color="transparent",
                                  text_color=COLORS["text_secondary"])
            self.diff_menu.configure(state="disabled")
            self.o_score_label.master.winfo_children()[0].configure(text="O (P2)")
            self.x_score_label.master.winfo_children()[0].configure(text="X (P1)")

        self._restart_game()

    def _set_difficulty(self, value):
        """Update AI difficulty level."""
        self.ai_difficulty = value.lower()
        self._restart_game()

    def _restart_game(self):
        """Reset the board for a new game or retry."""
        # Hide retry button for active match
        self.retry_button.pack_forget()

        # Cancel pending animations
        for aid in self.animation_ids:
            try:
                self.after_cancel(aid)
            except ValueError:
                pass
        self.animation_ids.clear()

        self.board = [""] * 9
        self.current_player = "X"
        self.game_active = True
        self.winning_combo = None
        self.hover_cell = -1

        # Redraw grid
        self.grid_canvas.delete("all")
        self._round_rect(self.grid_canvas, 0, 0, 400, 400, 16,
                         fill=COLORS["bg_card"], outline=COLORS["border"], width=1)

        for x1, y1, x2, y2 in self.cell_coords:
            self._round_rect(
                self.grid_canvas, x1, y1, x2, y2, 12,
                fill=COLORS["bg_cell"], outline=COLORS["border"], width=1
            )

        self._update_status_text()

    def _reset_scores(self):
        """Reset all scores to zero and restart the game."""
        self.scores = {"X": 0, "O": 0, "draws": 0}
        self.current_streak = {"player": None, "count": 0}
        self._update_scores()
        self._restart_game()


# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = TicTacToeApp()
    app.mainloop()
