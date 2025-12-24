import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

class PianoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Piano Wave Visualizer")
        self.root.geometry("1000x600")
        
        self.fs = 44100
        self.duration = 0.05
        self.t = np.linspace(0, self.duration, int(self.fs * self.duration))
        
        self.octave = 4
        self.current_wave = None
        
        self.held_notes = set()
        self.held_buttons = {}
        
        self.base_frequencies = [
            16.35, 17.32, 18.35, 19.45, 20.60, 21.83, 23.12, 24.50, 25.96, 27.50, 29.14, 30.87
        ]
        self.setup_wave_display()
        self.setup_controls()
        self.setup_piano()
        
    def get_frequency(self, note_index):
        """Get frequency for a note in the current octave"""
        base_freq = self.base_frequencies[note_index]
        return base_freq * (2 ** self.octave)
    
    def triangle_wave(self, frequency, t):
        """Generate a continuous triangle wave"""
        phase = t * frequency
        triangle = 2 * np.abs(2 * (phase - np.floor(phase + 0.5))) - 1
        return triangle
    
    def generate_wave(self, frequency):
        """Generate a continuous triangle wave"""
        return self.triangle_wave(frequency, self.t)
    
    def generate_chord_wave(self, frequencies):
        """Generate a combined wave from multiple frequencies (chord)"""
        if not frequencies:
            return np.zeros_like(self.t)
        
        wave = np.zeros_like(self.t)
        for freq in frequencies:
            wave += self.triangle_wave(freq, self.t)
        
        if np.max(np.abs(wave)) > 0:
            wave = wave / np.max(np.abs(wave))
        
        return wave
    
    def setup_wave_display(self):
        """Setup the wave visualization display"""
        wave_frame = tk.Frame(self.root, bg='#1a1a1a', height=200)
        wave_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        
        self.fig, self.ax = plt.subplots(figsize=(10, 3), facecolor='#1a1a1a')
        self.ax.set_facecolor('#1a1a1a')
        self.ax.set_xlim(0, self.duration * 1000)
        self.ax.set_ylim(-1.2, 1.2)
        self.ax.tick_params(colors='white', labelsize=8)
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.set_xlabel('Time (ms)', color='white', fontsize=10)
        self.ax.set_ylabel('Amplitude', color='white', fontsize=10)
        self.ax.set_title('Sound Wave Visualization', color='white', fontsize=12, pad=10)
        self.ax.grid(True, alpha=0.3, color='gray')
        
        self.line, = self.ax.plot([], [], color='#00ff88', linewidth=1.5)
        
        self.canvas = FigureCanvasTkAgg(self.fig, wave_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_wave_display(self, wave, note_names):
        """Update the wave display with new data"""
        time_ms = self.t * 1000
        
        self.line.set_data(time_ms, wave)
        if isinstance(note_names, list):
            title = f'Chord: {", ".join(note_names)}' if len(note_names) > 1 else f'Note: {note_names[0]}'
        else:
            title = f'Note: {note_names}'
        self.ax.set_title(title, color='white', fontsize=12, pad=10)
        self.canvas.draw()
        self.current_wave = wave
    
    def setup_controls(self):
        """Setup control panel with octave input"""
        control_frame = tk.Frame(self.root, bg='#2a2a2a', height=80)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        octave_label = tk.Label(control_frame, text="Octave:", bg='#2a2a2a', fg='white', font=('Arial', 12))
        octave_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        self.octave_var = tk.StringVar(value=str(self.octave))
        octave_entry = tk.Entry(control_frame, textvariable=self.octave_var, width=5, font=('Arial', 12))
        octave_entry.pack(side=tk.LEFT, padx=5)
        octave_entry.bind('<Return>', self.on_octave_change)
        
        octave_button = tk.Button(control_frame, text="Update", command=self.on_octave_change, 
                                 bg='#00ff88', fg='black', font=('Arial', 10), padx=10)
        octave_button.pack(side=tk.LEFT, padx=5)
        
        info_label = tk.Label(control_frame, 
                             text="Left click: play & release | Right click: hold (shaded)", 
                             bg='#2a2a2a', fg='white', font=('Arial', 10))
        info_label.pack(side=tk.RIGHT, padx=20)
    
    def on_octave_change(self, event=None):
        """Handle octave change"""
        try:
            new_octave = int(self.octave_var.get())
            if 0 <= new_octave <= 8:
                self.octave = new_octave
                self.update_piano_labels()
            else:
                self.octave_var.set(str(self.octave))
        except ValueError:
            self.octave_var.set(str(self.octave))
    
    def update_piano_labels(self):
        """Update piano key labels when octave changes"""
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        white_keys = [0, 2, 4, 5, 7, 9, 11] * 2
        
        for i, (btn, note_idx) in enumerate(self.white_buttons):
            octave_offset = i // 7
            note_name = note_names[white_keys[i]]
            full_note_name = f"{note_name}{self.octave + octave_offset}"
            btn.config(text=full_note_name)
            
            btn.unbind('<Button-1>')
            btn.unbind('<Button-3>')
            btn.bind('<Button-1>', lambda e, idx=note_idx, name=full_note_name, b=btn: 
                     self.play_note_left_click(idx, name, b))
            btn.bind('<Button-3>', lambda e, idx=note_idx, name=full_note_name, b=btn: 
                     self.hold_note_right_click(idx, name, b))
        
        black_note_indices = [1, 3, 6, 8, 10] * 2
        for i, (btn, note_idx) in enumerate(self.black_buttons):
            octave_offset = i // 5
            note_name = note_names[black_note_indices[i]]
            full_note_name = f"{note_name}{self.octave + octave_offset}"
            btn.config(text=full_note_name)
            
            btn.unbind('<Button-1>')
            btn.unbind('<Button-3>')
            btn.bind('<Button-1>', lambda e, idx=note_idx, name=full_note_name, b=btn: 
                     self.play_note_left_click(idx, name, b))
            btn.bind('<Button-3>', lambda e, idx=note_idx, name=full_note_name, b=btn: 
                     self.hold_note_right_click(idx, name, b))
    
    def setup_piano(self):
        """Setup the piano keyboard"""
        piano_frame = tk.Frame(self.root, bg='#2a2a2a', height=250)
        piano_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        white_keys = [0, 2, 4, 5, 7, 9, 11] * 2
        
        self.white_buttons = []
        self.black_buttons = []
        
        white_key_frame = tk.Frame(piano_frame, bg='#2a2a2a')
        white_key_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 10))
        
        for i, note_idx in enumerate(white_keys):
            octave_offset = i // 7
            note_name = note_names[note_idx]
            full_note_name = f"{note_name}{self.octave + octave_offset}"
            global_note_idx = note_idx + octave_offset * 12
            
            btn = tk.Button(white_key_frame, text=full_note_name, width=6, height=8,
                           bg='white', fg='black', font=('Arial', 10, 'bold'),
                           relief=tk.RAISED, bd=2)
            
            btn.bind('<Button-1>', lambda e, idx=global_note_idx, name=full_note_name, b=btn: 
                     self.play_note_left_click(idx, name, b))
            btn.bind('<Button-3>', lambda e, idx=global_note_idx, name=full_note_name, b=btn: 
                     self.hold_note_right_click(idx, name, b))
            
            btn.pack(side=tk.LEFT, padx=1)
            self.white_buttons.append((btn, global_note_idx))
        
        black_key_canvas = tk.Canvas(piano_frame, bg='#2a2a2a', height=120, highlightthickness=0)
        black_key_canvas.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(10, 0))
        
        black_key_positions = [0, 1, 3, 4, 5, 7, 8, 10, 11, 12]
        black_note_indices = [1, 3, 6, 8, 10] * 2
        
        def update_black_positions(event=None):
            """Update black key positions based on white key layout"""
            canvas_width = black_key_canvas.winfo_width()
            if canvas_width < 10 or not self.white_buttons:
                return
            
            white_key_width_pixels = self.white_buttons[0][0].winfo_reqwidth() if len(self.white_buttons) > 0 else 50
            
            total_white_width = white_key_width_pixels * 14
            start_x = (canvas_width - total_white_width) / 2 + 20
            
            black_key_canvas.delete("all")
            self.black_buttons.clear()
            
            for pos_idx, white_key_pos in enumerate(black_key_positions):
                note_idx = black_note_indices[pos_idx]
                octave_offset = pos_idx // 5
                note_name = note_names[note_idx]
                full_note_name = f"{note_name}{self.octave + octave_offset}"
                
                x_pos = start_x + white_key_pos * white_key_width_pixels + white_key_width_pixels * 0.6
                
                global_note_idx = note_idx + octave_offset * 12
                
                btn = tk.Button(black_key_canvas, text=full_note_name, width=4, height=5,
                               bg='#1a1a1a', fg='white', font=('Arial', 8, 'bold'),
                               relief=tk.RAISED, bd=2)
                
                btn.bind('<Button-1>', lambda e, idx=global_note_idx, name=full_note_name, b=btn: 
                         self.play_note_left_click(idx, name, b))
                btn.bind('<Button-3>', lambda e, idx=global_note_idx, name=full_note_name, b=btn: 
                         self.hold_note_right_click(idx, name, b))
                
                black_key_canvas.create_window(x_pos, 10, window=btn, anchor='n')
                self.black_buttons.append((btn, global_note_idx))
        
        black_key_canvas.bind('<Configure>', update_black_positions)
        self.root.after(100, update_black_positions)
    
    def get_note_frequency(self, note_index):
        """Convert note index to frequency"""
        note_in_octave = note_index % 12
        octave_offset = note_index // 12
        base_frequency = self.get_frequency(note_in_octave)
        return base_frequency * (2 ** octave_offset)
    
    def update_display_from_held_notes(self):
        """Update the wave display based on currently held notes"""
        if not self.held_notes:
            wave = np.zeros_like(self.t)
            self.update_wave_display(wave, "No notes")
            return
        
        frequencies = []
        note_names = []
        for note_index, note_name in self.held_notes:
            freq = self.get_note_frequency(note_index)
            frequencies.append(freq)
            note_names.append(note_name)
        
        wave = self.generate_chord_wave(frequencies)
        self.update_wave_display(wave, note_names)
    
    def play_note_left_click(self, note_index, note_name, button):
        """Left click: play note and release"""
        frequency = self.get_note_frequency(note_index)
        wave = self.generate_wave(frequency)
        self.update_wave_display(wave, [note_name])
    
    def hold_note_right_click(self, note_index, note_name, button):
        """Right click: toggle hold note (add/remove from held notes)"""
        if (note_index, note_name) in self.held_notes:
            self.release_note(note_index, button)
        else:
            self.held_notes.add((note_index, note_name))
            self.held_buttons[note_index] = button
            
            if button.cget('bg') == 'white':
                button.config(bg='#cccccc')
            else:
                button.config(bg='#444444')
            
            self.update_display_from_held_notes()
    
    def release_note(self, note_index, button):
        """Release a held note"""
        note_to_remove = None
        for idx, name in self.held_notes:
            if idx == note_index:
                note_to_remove = (idx, name)
                break
        
        if note_to_remove:
            self.held_notes.remove(note_to_remove)
        
        if note_index in self.held_buttons:
            del self.held_buttons[note_index]
        
        current_bg = button.cget('bg')
        if current_bg in ['#cccccc', '#444444']:
            note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            note_in_octave = note_index % 12
            if note_in_octave in [0, 2, 4, 5, 7, 9, 11]:
                button.config(bg='white')
            else:
                button.config(bg='#1a1a1a')
        
        self.update_display_from_held_notes()

def main():
    root = tk.Tk()
    app = PianoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
