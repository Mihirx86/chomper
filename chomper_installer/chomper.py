"""
Chomper Ad Blocker Installer
A GUI application for installing the Chomper ad blocker extension on Chromium-based browsers.
"""

import os
import sys
import shutil
import subprocess
import json
import webbrowser
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ----------------------
# Configuration
# ----------------------
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Window dimensions
WINDOW_WIDTH = 750
WINDOW_HEIGHT = 650

# Color scheme
COLORS = {
    "primary": "#667eea",
    "primary_dark": "#5a67d8",
    "secondary": "#764ba2",
    "success": "#48bb78",
    "warning": "#ed8936",
    "error": "#f56565",
    "dark_bg": "#0f172a",
    "light_bg": "#f8fafc",
    "card_dark": "#1e293b",
    "card_light": "#ffffff",
    "text_dark": "#f1f5f9",
    "text_light": "#334155",
    "border": "#e2e8f0"
}

# Extension configuration
EXTENSION_NAME = "chomper-ad-blocker"
INSTALL_PATH = os.path.join(os.environ["USERPROFILE"], "Documents", EXTENSION_NAME)

# Browser detection
BROWSERS = {
    "Google Chrome": {
        "paths": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ],
        "color": "#4285F4",
        "icon": "chrome"
    },
    "Microsoft Edge": {
        "paths": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ],
        "color": "#0078D4",
        "icon": "edge"
    },
    "Brave Browser": {
        "paths": [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        ],
        "color": "#FB542B",
        "icon": "brave"
    },
    "Opera": {
        "paths": [
            r"C:\Program Files\Opera\launcher.exe",
            r"C:\Program Files\Opera\opera.exe",
        ],
        "color": "#FF1B2D",
        "icon": "opera"
    },
    "Vivaldi": {
        "paths": [
            r"C:\Program Files\Vivaldi\Application\vivaldi.exe",
        ],
        "color": "#EF3939",
        "icon": "vivaldi"
    }
}

def detect_browsers():
    """Detect installed Chromium-based browsers."""
    detected = []
    for name, info in BROWSERS.items():
        for path in info["paths"]:
            if os.path.exists(path):
                detected.append(name)
                break
    return detected

# ----------------------
# Modern UI Components
# ----------------------
class ModernCard(ctk.CTkFrame):
    """Modern card component with shadow effect."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            fg_color=COLORS["card_light"] if ctk.get_appearance_mode() == "Light" else COLORS["card_dark"]
        )

class ProgressSteps(ctk.CTkFrame):
    """Progress indicator showing current step."""
    def __init__(self, master, steps, **kwargs):
        super().__init__(master, **kwargs)
        self.steps = steps
        self.current_step = 0
        self.configure(fg_color="transparent")
        self.create_widgets()
    
    def create_widgets(self):
        for i, step in enumerate(self.steps):
            # Step container
            step_frame = ctk.CTkFrame(self, fg_color="transparent")
            step_frame.grid(row=0, column=i*2, padx=10)
            
            # Step circle
            circle = ctk.CTkLabel(
                step_frame,
                text=str(i+1),
                width=30,
                height=30,
                corner_radius=15,
                font=ctk.CTkFont(size=12, weight="bold")
            )
            circle.pack()
            
            # Step label
            label = ctk.CTkLabel(
                step_frame,
                text=step,
                font=ctk.CTkFont(size=11)
            )
            label.pack(pady=(5, 0))
            
            # Store references
            setattr(self, f"circle_{i}", circle)
            setattr(self, f"label_{i}", label)
            
            # Connector line
            if i < len(self.steps) - 1:
                line = ctk.CTkFrame(self, width=30, height=2, fg_color=COLORS["border"])
                line.grid(row=0, column=i*2+1, padx=5)
        
        self.update_step(0)
    
    def update_step(self, step):
        """Update visual state for current step."""
        self.current_step = step
        for i in range(len(self.steps)):
            circle = getattr(self, f"circle_{i}")
            label = getattr(self, f"label_{i}")
            
            if i == step:
                circle.configure(fg_color=COLORS["primary"], text_color="white")
                label.configure(text_color=COLORS["primary"])
            elif i < step:
                circle.configure(fg_color=COLORS["success"], text_color="white")
                label.configure(text_color=COLORS["success"])
            else:
                circle.configure(fg_color="#e2e8f0", text_color="#94a3b8")
                label.configure(text_color="#94a3b8")

# ----------------------
# Main Application
# ----------------------
class ChomperAdBlockerInstaller:
    """Main installer application."""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Chomper Ad Blocker - Installer")
        
        # Configure window
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.center_window()
        self.root.resizable(False, False)
        
        # Set minimum size
        self.root.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Application state
        self.current_page = 0
        self.selected_browser = tk.StringVar(value="")
        self.install_complete = False
        
        # Progress steps
        self.progress_steps = ProgressSteps(
            self.root,
            steps=["Welcome", "Install", "Select Browser", "Enable", "Complete"]
        )
        self.progress_steps.pack(pady=(20, 10))
        
        # Main content frame
        self.content_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Create pages
        self.pages = []
        self.create_welcome_page()
        self.create_install_page()
        self.create_browser_selection_page()
        self.create_instructions_page()
        self.create_completion_page()
        
        # Show first page
        self.show_page(0)
    
    def center_window(self):
        """Center window on screen."""
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
    
    def create_welcome_page(self):
        """Welcome page with app introduction."""
        page = ModernCard(self.content_frame)
        
        # Logo/Header
        header_frame = ctk.CTkFrame(page, fg_color="transparent")
        header_frame.pack(pady=(40, 20))
        
        # Title with gradient effect simulation
        title = ctk.CTkLabel(
            header_frame,
            text="Chomper Ad Blocker",
            font=ctk.CTkFont(size=42, weight="bold", family="Segoe UI"),
            text_color=COLORS["primary"]
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Who is Chomper? A tiny creature that voraciously devours ads on the web.",
            font=ctk.CTkFont(size=16),
            text_color=COLORS["secondary"]
        )
        subtitle.pack(pady=(0, 30))
        
        # Features in grid
        features_frame = ctk.CTkFrame(page, fg_color="transparent")
        features_frame.pack(pady=(0, 30), padx=40)
        
        features = [
            ("🦷", "Always Hungry", "Chews through video ads"),
            ("🛡️", "House-Trained", "Does not collect user data"),
            ("🎯", "Picky Eater", "Targets ads only"),
            ("⚙️", "Easy to Feed", "Quick installation")
        ]

        for i, (icon, title_text, desc) in enumerate(features):
            if i % 2 == 0:
                row_frame = ctk.CTkFrame(features_frame, fg_color="transparent")
                row_frame.pack(pady=10)
            
            feature_card = ModernCard(row_frame, width=250, height=80)
            feature_card.pack(side="left", padx=10, fill="both", expand=True)
            
            icon_label = ctk.CTkLabel(
                feature_card,
                text=icon,
                font=ctk.CTkFont(size=24)
            )
            icon_label.place(x=15, y=20)
            
            title_label = ctk.CTkLabel(
                feature_card,
                text=title_text,
                font=ctk.CTkFont(size=13, weight="bold")
            )
            title_label.place(x=60, y=20)
            
            desc_label = ctk.CTkLabel(
                feature_card,
                text=desc,
                font=ctk.CTkFont(size=11)
            )
            desc_label.place(x=60, y=45)
        
        # Start button
        start_btn = ctk.CTkButton(
            page,
            text="Get Started →",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            width=200,
            corner_radius=8,
            command=lambda: self.show_page(1),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            text_color="white"
        )
        start_btn.pack(pady=(10, 40))
        
        self.pages.append(page)
    
    def create_install_page(self):
        """Installation page."""
        page = ModernCard(self.content_frame)
        
        # Title
        title = ctk.CTkLabel(
            page,
            text="📦 Installation",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(40, 20))
        
        # Description
        desc = ctk.CTkLabel(
            page,
            text="Chomper will be installed to your Documents folder",
            font=ctk.CTkFont(size=13)
        )
        desc.pack(pady=(0, 30))
        
        # Installation path display
        path_card = ModernCard(page, height=60)
        path_card.pack(fill="x", padx=40, pady=10)
        
        path_text = ctk.CTkLabel(
            path_card,
            text=f"📁 {INSTALL_PATH}",
            font=ctk.CTkFont(size=12, family="Consolas"),
            anchor="w"
        )
        path_text.pack(padx=20, pady=15, fill="x")
        
        # Install button
        self.install_btn = ctk.CTkButton(
            page,
            text="Install Now",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            width=200,
            corner_radius=8,
            command=self.perform_installation,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            text_color="white"
        )
        self.install_btn.pack(pady=20)
        
        # Status indicator
        self.status_frame = ctk.CTkFrame(page, fg_color="transparent", height=40)
        self.status_frame.pack(pady=(10, 30))
        
        self.status_icon = ctk.CTkLabel(self.status_frame, text="", font=ctk.CTkFont(size=16))
        self.status_icon.pack(side="left", padx=(0, 10))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready to install",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left")
        
        # Next button (initially hidden)
        self.next_btn_page2 = ctk.CTkButton(
            page,
            text="Continue →",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            width=200,
            corner_radius=8,
            command=lambda: self.show_page(2),
            state="disabled",
            fg_color=COLORS["success"],
            hover_color="#38a169",
            text_color="white"
        )
        self.next_btn_page2.pack(pady=(0, 40))
        
        self.pages.append(page)
    
    def create_browser_selection_page(self):
        """Browser selection page."""
        page = ModernCard(self.content_frame)
        
        # Title
        title = ctk.CTkLabel(
            page,
            text="🌐 Select Browser",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(40, 10))
        
        # Description
        desc = ctk.CTkLabel(
            page,
            text="Choose your preferred browser to enable Chomper",
            font=ctk.CTkFont(size=13)
        )
        desc.pack(pady=(0, 30))
        
        # Browser selection frame
        browser_frame = ctk.CTkScrollableFrame(page, width=450, height=200)
        browser_frame.pack(padx=20, pady=10)
        
        # Detect browsers
        self.detected_browsers = detect_browsers()
        
        if not self.detected_browsers:
            warning_card = ModernCard(browser_frame, height=100)
            warning_card.pack(fill="x", pady=10)
            
            warning_label = ctk.CTkLabel(
                warning_card,
                text="⚠️ No Chromium browsers detected\n\nPlease install one of the supported browsers first",
                font=ctk.CTkFont(size=12),
                justify="center"
            )
            warning_label.pack(pady=30)
        else:
            for browser in self.detected_browsers:
                browser_card = ModernCard(browser_frame, height=60)
                browser_card.pack(fill="x", pady=5)
                
                # Make entire card clickable
                browser_card.bind("<Button-1>", lambda e, b=browser: self.select_browser(b))
                
                # Browser name with colored dot
                color_dot = ctk.CTkLabel(
                    browser_card,
                    text="●",
                    text_color=BROWSERS[browser]["color"],
                    font=ctk.CTkFont(size=20)
                )
                color_dot.place(x=20, y=20)
                
                browser_name = ctk.CTkLabel(
                    browser_card,
                    text=browser,
                    font=ctk.CTkFont(size=13, weight="bold")
                )
                browser_name.place(x=50, y=20)
                
                # Radio button
                radio = ctk.CTkRadioButton(
                    browser_card,
                    text="",
                    variable=self.selected_browser,
                    value=browser,
                    width=20,
                    height=20,
                    fg_color=BROWSERS[browser]["color"],
                    hover_color=BROWSERS[browser]["color"]
                )
                radio.place(x=250, y=20)
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(page, fg_color="transparent")
        nav_frame.pack(pady=30)
        
        back_btn = ctk.CTkButton(
            nav_frame,
            text="← Back",
            font=ctk.CTkFont(size=13),
            height=40,
            width=100,
            corner_radius=6,
            command=lambda: self.show_page(1),
            fg_color="#e2e8f0",
            hover_color="#cbd5e0",
            text_color="#475569"
        )
        back_btn.pack(side="left", padx=(0, 10))
        
        self.next_btn_page3 = ctk.CTkButton(
            nav_frame,
            text="Continue →",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            width=100,
            corner_radius=6,
            command=self.open_browser_extension_page,
            state="disabled" if not self.detected_browsers else "normal",
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            text_color="white"
        )
        self.next_btn_page3.pack(side="left")
        
        self.pages.append(page)
    
    def select_browser(self, browser):
        """Select browser when card is clicked."""
        self.selected_browser.set(browser)
        self.next_btn_page3.configure(state="normal")
    
    def create_instructions_page(self):
        """Instructions page."""
        page = ModernCard(self.content_frame)
        # Title
        title = ctk.CTkLabel(
            page,
            text="🔧 Enable Extension",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(40, 20))
        # Steps
        steps_card = ModernCard(page)
        steps_card.pack(fill="both", expand=True, padx=30, pady=10)
        # Steps without descriptions
        steps = [
            "1. Open Browser Extensions",
            "2. Enable Developer Mode",
            "3. Click Load Unpacked",
            f"4. Select Folder: {INSTALL_PATH}",
            "5. Pin Chomper"
        ]
        for i, step_text in enumerate(steps):
            step_frame = ctk.CTkFrame(steps_card, fg_color="transparent")
            step_frame.pack(fill="x", padx=20, pady=15)
            number = ctk.CTkLabel(
                step_frame,
                text=str(i+1),
                width=30,
                height=30,
                corner_radius=15,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=COLORS["primary"],
                text_color="white"
            )
            number.pack(side="left", padx=(0, 20))
            step_label = ctk.CTkLabel(
                step_frame,
                text=step_text,
                font=ctk.CTkFont(size=14),
                anchor="w",
                justify="left"
            )
            step_label.pack(side="left", fill="x", expand=True)
        # Action button
        action_btn = ctk.CTkButton(
            page,
            text="Open Browser & Continue →",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            width=250,
            corner_radius=8,
            command=self.open_google_and_continue,
            fg_color=COLORS["success"],
            hover_color="#38a169",
            text_color="white"
        )
        action_btn.pack(pady=30)
        self.pages.append(page)
    
    def create_completion_page(self):
        """Completion page."""
        page = ModernCard(self.content_frame)
        
        # Success icon
        success_icon = ctk.CTkLabel(
            page,
            text="✅",
            font=ctk.CTkFont(size=64)
        )
        success_icon.pack(pady=(50, 20))
        
        # Title
        title = ctk.CTkLabel(
            page,
            text="Installation Complete!",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(pady=(0, 10))
        
        # Message
        message = ctk.CTkLabel(
            page,
            text="Chomper is now ready to block ads in your browser",
            font=ctk.CTkFont(size=14)
        )
        message.pack(pady=(0, 40))
        
        # Tips (Scrollable)
        tips_card = ctk.CTkFrame(page, height=180, fg_color=COLORS["card_light"] if ctk.get_appearance_mode() == "Light" else COLORS["card_dark"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        tips_card.pack(fill="x", padx=40, pady=10)

        tips_title = ctk.CTkLabel(
            tips_card,
            text="💡 Quick Tips",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        tips_title.pack(pady=(15, 10))

        # Scrollable frame for tips
        tips_scroll = ctk.CTkScrollableFrame(tips_card, height=110, fg_color="transparent")
        tips_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        tips = [
            "📌 Pinning the Extension ",
            "• Click the puzzle (🧩) icon in your browser toolbar",
            "• Locate \"Chomper Ad Blocker\"", # Updated name
            "• Click the pin icon to keep it visible",
            "",

            "🔄 Reloading the Extension:",
            "• Open the Extensions page",
            "• Find \"Chomper Ad Blocker\"", # Updated name
            "• Click the Reload icon",
            "",

            "⚙️ Troubleshooting:",
            "• Ads still showing?",
            "• Ensure Chomper is enabled in the Extensions page",
            " → Reload the webpage",
            "",
            "• Want to remove the extension?",    
            " → Delete it from the Extensions page",
            "• Ads still blocked after turning OFF the ad blocker?",
            " → Clear browser history and site data, then reload",
            "",
        ]

        for tip in tips:
            tip_label = ctk.CTkLabel(
                tips_scroll,
                text=tip,
                font=ctk.CTkFont(size=12)
            )
            tip_label.pack(anchor="w", padx=10, pady=2)
        
        # Close button
        close_btn = ctk.CTkButton(
            page,
            text="Finish",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            width=150,
            corner_radius=8,
            command=self.root.quit,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            text_color="white"
        )
        close_btn.pack(pady=30)
        
        self.pages.append(page)
    
    def show_page(self, page_index):
        """Show specified page."""
        for page in self.pages:
            page.pack_forget()
        
        self.current_page = page_index
        self.pages[page_index].pack(fill="both", expand=True)
        self.progress_steps.update_step(page_index)
    
    def perform_installation(self):
        """Perform the installation."""
        try:
            self.install_btn.configure(state="disabled", text="Installing...")
            self.status_icon.configure(text="⏳")
            self.status_label.configure(text="Copying extension files...")
            self.root.update()
            
            # Get source directory
            base_dir = os.path.dirname(os.path.abspath(__file__))
            extension_src_dir = os.path.join(base_dir, EXTENSION_NAME)
            
            if getattr(sys, 'frozen', False):
                extension_src_dir = os.path.join(os.path.dirname(sys.executable), EXTENSION_NAME)
                if not os.path.exists(extension_src_dir):
                    extension_src_dir = os.path.join(sys._MEIPASS, EXTENSION_NAME)
            
            # Verify source
            if not os.path.exists(extension_src_dir):
                raise FileNotFoundError(f"Extension folder not found: {extension_src_dir}")
            
            # Clean previous installation
            if os.path.exists(INSTALL_PATH):
                shutil.rmtree(INSTALL_PATH)
            
            # Copy files
            shutil.copytree(extension_src_dir, INSTALL_PATH)
            
            # Verify
            if os.path.exists(os.path.join(INSTALL_PATH, 'manifest.json')):
                self.status_icon.configure(text="✅", text_color=COLORS["success"])
                self.status_label.configure(
                    text="Installation successful!",
                    text_color=COLORS["success"]
                )
                self.install_complete = True
                self.next_btn_page2.configure(state="normal")
            else:
                raise Exception("Files not copied properly")
            
        except Exception as e:
            self.status_icon.configure(text="❌", text_color=COLORS["error"])
            self.status_label.configure(
                text=f"Error: {str(e)}",
                text_color=COLORS["error"]
            )
            messagebox.showerror("Installation Error", f"Failed to install: {str(e)}")
            self.install_btn.configure(state="normal", text="Try Again")
    
    def open_browser_extension_page(self):
        """Open browser extensions page."""
        browser_name = self.selected_browser.get()
        
        if not browser_name:
            messagebox.showwarning("No Selection", "Please select a browser first.")
            return
        
        browser_path = None
        for path in BROWSERS[browser_name]["paths"]:
            if os.path.exists(path):
                browser_path = path
                break
        
        if browser_path:
            try:
                subprocess.Popen([browser_path, "--new-tab", "chrome://extensions"])
                self.show_page(3)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open browser: {str(e)}")
        else:
            messagebox.showerror("Error", f"Could not find {browser_name}")
    
    def open_google_and_continue(self):
        """Open Google and show completion."""
        try:
            browser_name = self.selected_browser.get()
            for path in BROWSERS[browser_name]["paths"]:
                if os.path.exists(path):
                    subprocess.Popen([path, "--new-tab", "https://www.google.com"])
                    break
        except:
            pass
        
        self.show_page(4)
    
    def run(self):
        """Start application."""
        self.root.mainloop()

# ----------------------
# Entry Point
# ----------------------
if __name__ == "__main__":
    app = ChomperAdBlockerInstaller()
    app.run()