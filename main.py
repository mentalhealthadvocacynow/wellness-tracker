import sqlite3
import hashlib
import secrets
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivymd.uix.list import TwoLineListItem, MDList 
from kivy.uix.scrollview import ScrollView 
from kivy.utils import platform
from datetime import datetime

# --- Database Helper Functions ---

# Define the local database file path
DB_FILE = 'mobile_tracker.db'

def get_db_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

def create_tables():
    """Initializes the User and CheckIn tables if they don't exist."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # 1. User Table - Updated to store salt with password
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        );
    ''')
    
    # 2. CheckIn Data Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            date_posted TEXT NOT NULL,
            mood_score INTEGER NOT NULL,
            stress_level INTEGER NOT NULL,
            anxiety_level INTEGER NOT NULL,
            gratitude_1 TEXT,
            gratitude_2 TEXT,
            gratitude_3 TEXT,
            thought_patterns TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    ''')
    conn.commit()
    conn.close()

# Call this once when the app starts
create_tables()

# --- Security Helper Functions ---

def hash_password(password):
    """Generates a secure hash with salt for a given password."""
    salt = secrets.token_hex(32)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return password_hash.hex(), salt

def verify_password(password, stored_hash, salt):
    """Verifies a password against stored hash and salt."""
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return password_hash.hex() == stored_hash

# --- Kivy Screens ---

class LoginScreen(MDScreen):
    """Screen for user login and registration."""
    username_input = ObjectProperty(None)
    password_input = ObjectProperty(None)
    status_label = ObjectProperty(None)

    def login(self):
        username = self.username_input.text.strip()
        password = self.password_input.text
        
        if not username or not password:
            self.status_label.text = "Error: Username and Password required."
            return

        try:
            conn = get_db_connection()
            user = conn.execute("SELECT id, password_hash, salt FROM users WHERE username = ?", (username,)).fetchone()
            conn.close()

            if user and verify_password(password, user['password_hash'], user['salt']):
                # Set current user in app
                app = MDApp.get_running_app()
                app.current_user_id = user['id']
                self.status_label.text = "Login successful!"
                # Switch to the Check-in Screen
                self.manager.current = 'checkin'
            else:
                self.status_label.text = "Error: Invalid username or password."
        except Exception as e:
            self.status_label.text = f"Login error: {str(e)}"

    def register(self):
        username = self.username_input.text.strip()
        password = self.password_input.text
        
        if not username or not password:
            self.status_label.text = "Error: Username and Password required."
            return
        
        if len(password) < 6:
            self.status_label.text = "Error: Password must be at least 6 characters."
            return

        try:
            password_hash, salt = hash_password(password)
            conn = get_db_connection()
            conn.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)", 
                         (username, password_hash, salt))
            conn.commit()
            conn.close()
            self.status_label.text = "Registration successful! You can now log in."
        except sqlite3.IntegrityError:
            self.status_label.text = "Error: Username already taken."
        except Exception as e:
            self.status_label.text = f"Registration error: {str(e)}"

class CheckInScreen(MDScreen):
    """Screen for the daily mental health data input."""
    # Object properties linked to widgets in the KV file
    mood_slider = ObjectProperty(None)
    stress_slider = ObjectProperty(None)
    anxiety_slider = ObjectProperty(None)
    gratitude_1 = ObjectProperty(None)
    gratitude_2 = ObjectProperty(None)
    gratitude_3 = ObjectProperty(None)
    thought_patterns = ObjectProperty(None)
    save_status = ObjectProperty(None)

    def save_checkin(self):
        app = MDApp.get_running_app()
        
        if app.current_user_id is None:
            self.save_status.text = "Error: Not logged in. Please log in first."
            self.manager.current = 'login'
            return

        # 1. Capture and validate data from widgets
        gratitude_1_text = self.gratitude_1.text.strip()
        gratitude_2_text = self.gratitude_2.text.strip()
        gratitude_3_text = self.gratitude_3.text.strip()
        
        if not all([gratitude_1_text, gratitude_2_text, gratitude_3_text]):
            self.save_status.text = "Please fill in all 3 gratitude items."
            return

        data = {
            'user_id': app.current_user_id,
            'date_posted': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'mood_score': int(self.mood_slider.value),
            'stress_level': int(self.stress_slider.value),
            'anxiety_level': int(self.anxiety_slider.value),
            'gratitude_1': gratitude_1_text,
            'gratitude_2': gratitude_2_text,
            'gratitude_3': gratitude_3_text,
            'thought_patterns': self.thought_patterns.text.strip(),
        }

        # 2. Save to database
        try:
            conn = get_db_connection()
            conn.execute("""
                INSERT INTO checkins (user_id, date_posted, mood_score, stress_level, anxiety_level, 
                                      gratitude_1, gratitude_2, gratitude_3, thought_patterns)
                VALUES (:user_id, :date_posted, :mood_score, :stress_level, :anxiety_level, 
                        :gratitude_1, :gratitude_2, :gratitude_3, :thought_patterns)
            """, data)
            conn.commit()
            conn.close()
            
            self.save_status.text = "Check-in saved successfully!"
            # Clear the text inputs after saving
            self.gratitude_1.text = ''
            self.gratitude_2.text = ''
            self.gratitude_3.text = ''
            self.thought_patterns.text = ''
            
            # Reset sliders to middle values
            self.mood_slider.value = 5
            self.stress_slider.value = 5
            self.anxiety_slider.value = 5

        except Exception as e:
            self.save_status.text = f"Save Error: {str(e)}"

    def go_to_dataview(self):
        self.manager.current = 'dataview'
    
    def logout(self):
        app = MDApp.get_running_app()
        app.current_user_id = None
        self.manager.current = 'login'

class DataViewScreen(MDScreen):
    """Screen to display a list of all saved check-ins."""
    data_list = ObjectProperty(None)

    def on_enter(self):
        """Called every time the screen is displayed."""
        self.load_data()

    def load_data(self):
        app = MDApp.get_running_app()
        if app.current_user_id is None:
            return

        # Clear previous entries
        self.data_list.clear_widgets()

        try:
            conn = get_db_connection()
            # Fetch the most recent 10 check-ins
            checkins = conn.execute("""
                SELECT date_posted, mood_score, stress_level, anxiety_level 
                FROM checkins 
                WHERE user_id = ? 
                ORDER BY date_posted DESC 
                LIMIT 10
            """, (app.current_user_id,)).fetchall()
            conn.close()

            if not checkins:
                self.data_list.add_widget(
                    TwoLineListItem(text="No Check-ins Found", secondary_text="Enter data on the Check-in screen.")
                )
                return

            # Populate the list with fetched data
            for row in checkins:
                try:
                    # Format the date nicely for the list item
                    date_obj = datetime.strptime(row['date_posted'], '%Y-%m-%d %H:%M:%S')
                    main_text = f"Check-in: {date_obj.strftime('%b %d, %I:%M %p')}"
                    secondary_text = (
                        f"Mood: {row['mood_score']} | Stress: {row['stress_level']} | Anxiety: {row['anxiety_level']}"
                    )

                    item = TwoLineListItem(
                        text=main_text,
                        secondary_text=secondary_text
                    )
                    self.data_list.add_widget(item)
                except ValueError:
                    # Handle date parsing errors
                    item = TwoLineListItem(
                        text="Invalid date format",
                        secondary_text=f"Mood: {row['mood_score']} | Stress: {row['stress_level']} | Anxiety: {row['anxiety_level']}"
                    )
                    self.data_list.add_widget(item)
                    
        except Exception as e:
            self.data_list.add_widget(
                TwoLineListItem(text="Error Loading Data", secondary_text=f"Error: {str(e)}")
            )

    def go_to_checkin(self):
        self.manager.current = 'checkin'

    def logout(self):
        app = MDApp.get_running_app()
        app.current_user_id = None
        self.manager.current = 'login'

class WellnessTrackerApp(MDApp):
    """The main application class."""
    # Use app property instead of global variable
    current_user_id = NumericProperty(None, allownone=True)
    
    def build(self):
        # Define the primary color palette for the whole app
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # The ScreenManager remains the same
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(CheckInScreen(name='checkin'))
        sm.add_widget(DataViewScreen(name='dataview'))
        return sm

if __name__ == '__main__':
    WellnessTrackerApp().run()
