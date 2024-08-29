from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty
import psycopg2
import time
import os

# Set window size and background to an aqua theme
Window.size = (1080, 720)
Window.clearcolor = (0.2, 0.6, 0.7, 1)

# Database connection setup
program_files_path = os.path.join(os.path.dirname(__file__), 'Program Files')
if not os.path.exists(program_files_path):
    os.makedirs(program_files_path)

database_link = psycopg2.connect(host='127.0.0.1', dbname='postgres', user='postgres', password='postgres', port='5432')
interact_with_database = database_link.cursor()

# Function stubs for menu operations
def add_new_info_to_a_table(instance):
    print("Adding new information...")

def update_tables(instance):
    print("Updating information...")

def display_information_menu(instance):
    print("Displaying information...")

def delete_information(instance):
    print("Deleting information...")

def display_existing_tables(instance):
    print("Displaying existing tables...")

def create_tables(instance):
    print("Creating extra tables...")

def delete_tables(instance):
    print("Deleting extra tables...")

def add_info_to_special_tables(instance):
    print("Adding info to extra tables...")

def manage_special_tables(instance):
    print("Managing special tables...")

def exit_program(instance):
    print("Exiting...")
    database_link.close()
    App.get_running_app().stop()

# Custom Button class with 3D effect, hover brightness change, and dynamic bold text
class CustomButton(Button):
    hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(CustomButton, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.font_name = "Roboto-Bold"
        self.font_size = self.height * 0.4
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def update_canvas(self, *args):
        self.font_size = self.height * 0.4
        with self.canvas.before:
            self.canvas.before.clear()
            Color(0, 0, 0, 0.25)
            RoundedRectangle(pos=(self.x + 3, self.y - 3), size=self.size, radius=[15])
            button_color = (0.2, 0.7, 0.6, 1) if not self.hovered else (0.3, 0.9, 0.8, 1)
            Color(*button_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
            Color(0.2, 1, 0.8, 1)
            RoundedRectangle(pos=(self.x, self.y + self.height - 10), size=(self.width, 10), radius=[15, 15, 0, 0])

    def on_mouse_pos(self, *args):
        pos = args[1]
        self.hovered = self.collide_point(*self.to_widget(*pos))
        self.update_canvas()

class AddInfoScreen(Screen):
    def __init__(self, **kwargs):
        super(AddInfoScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10, size_hint=(1, 1))
        self.add_widget(self.layout)
        self.build_initial_view()

    def build_initial_view(self):
        self.layout.clear_widgets()
        self.title_label = Label(text="Add Information to a Table", font_size=24, size_hint=(1, 0.1))
        self.layout.add_widget(self.title_label)

        # Display available tables
        self.tables = display_existing_tables()
        self.table_choice_label = Label(text="Select a Table:", size_hint=(1, 0.1))
        self.layout.add_widget(self.table_choice_label)

        # Display tables on screen as selectable buttons
        for index, table in enumerate(self.tables):
            btn = CustomButton(text=f"{index + 1}. {table}", size_hint=(1, 0.05))
            btn.bind(on_press=lambda x, table=table: self.handle_table_choice(table))
            self.layout.add_widget(btn)

    def handle_table_choice(self, table_choice):
        self.table_choice = table_choice
        if table_choice.lower() in ['back to main menu', 'back']:
            self.manager.current = 'menu'
            return

        # Call the appropriate function to add information to the selected table
        self.add_info_to_table()

    def add_info_to_table(self):
        self.layout.clear_widgets()
        self.inputs = {}

        # Create a scrollable area for the input fields
        scroll_view = ScrollView(size_hint=(1, 0.7))
        input_container = GridLayout(cols=1, spacing=10, size_hint_y=None)
        input_container.bind(minimum_height=input_container.setter('height'))

        # Retrieve column names dynamically from the selected table
        query = f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = '{self.table_choice}';
        """
        interact_with_database.execute(query)
        columns = [column[0] for column in interact_with_database.fetchall()]

        # Create input fields based on the number of columns, excluding IDs
        for column in columns:
            if column.lower() not in ['id', 'crimeid']:  # Exclude common ID fields
                input_layout = BoxLayout(orientation='vertical', size_hint=(1, None), height=120)
                
                # Create a label and input field for each column
                label = Label(text=column.capitalize(), size_hint=(1, 0.4), font_size=32, bold=True)
                input_field = TextInput(
                    hint_text=f"Enter {column.capitalize()}",
                    multiline=False,
                    size_hint=(1, 0.6),
                    font_size=50,
                    halign='left',
                )

                # Bind font size to adjust based on input field height
                input_field.bind(size=lambda s, w: setattr(s, 'font_size', s.height * 0.4))

                input_layout.add_widget(label)
                input_layout.add_widget(input_field)
                input_container.add_widget(input_layout)

                # Store the input field for later use
                self.inputs[column] = input_field

        # Add the input fields to the scrollable view
        scroll_view.add_widget(input_container)
        self.layout.add_widget(scroll_view)

        # Add Save and Back buttons at the bottom
        buttons_layout = BoxLayout(size_hint=(1, 0.08), spacing=10)
        
        # Back button
        back_button = CustomButton(text="Back", size_hint=(0.5, 1), background_color=(0.7, 0.2, 0.2, 1))
        back_button.bind(on_press=lambda x: self.build_initial_view())
        
        # Save button
        save_button = CustomButton(text="Save", size_hint=(0.5, 1))
        save_button.bind(on_press=self.show_save_confirmation)

        buttons_layout.add_widget(back_button)
        buttons_layout.add_widget(save_button)
        self.layout.add_widget(buttons_layout)

    def show_save_confirmation(self, instance):
        # Create the popup layout for confirmation
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        confirmation_label = Label(text='Are you sure you want to save this?', size_hint=(1, 0.7), font_size=32)
        popup_layout.add_widget(confirmation_label)

        # Buttons layout
        buttons_layout = BoxLayout(size_hint=(1, 0.3), spacing=10)

        # "Yes" button to confirm saving
        yes_button = CustomButton(text='Yes', size_hint=(0.5, 1))
        yes_button.bind(on_press=self.save_info)

        # "No" button to cancel saving
        no_button = CustomButton(text='No', size_hint=(0.5, 1), background_color=(1, 0.3, 0.3, 1))
        no_button.bind(on_press=lambda x: self.popup.dismiss())

        buttons_layout.add_widget(yes_button)
        buttons_layout.add_widget(no_button)
        popup_layout.add_widget(buttons_layout)

        # Create and open the popup
        self.popup = Popup(title='Save Confirmation', content=popup_layout, size_hint=(0.6, 0.4))
        self.popup.open()

    def save_info(self, instance):
        # Collect input data from text fields
        data = {column: input_field.text for column, input_field in self.inputs.items()}

        # Prepare the SQL query for insertion
        columns = ', '.join(data.keys())
        values_placeholder = ', '.join(['%s'] * len(data))
        query = f'INSERT INTO "{self.table_choice}" ({columns}) VALUES ({values_placeholder});'

        try:
            # Execute the insertion query with the collected data
            interact_with_database.execute(query, tuple(data.values()))
            database_link.commit()  # Commit the transaction to save data

            # Log the entry
            log_entry(None, f"New entry added to {self.table_choice}: {data}")

            # Update the title label to confirm the save
            self.title_label.text = f'New entry added to {self.table_choice}.'
        except Exception as e:
            # Display any errors encountered during the save process
            self.title_label.text = f'Error saving data: {str(e)}'

        # Close the popup
        self.popup.dismiss()

class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MainMenuScreen, self).__init__(**kwargs)
        layout = AnchorLayout()
        button_layout = GridLayout(cols=2, padding=10, spacing=10, size_hint=(0.7, 0.5))

        buttons = [
            ("Add Information", self.go_to_add_info),
            ("Update Information", update_tables),
            ("Display Information", display_information_menu),
            ("Delete Information", delete_information),
            ("Display Tables", display_existing_tables),
            ("Create Extra Tables", create_tables),
            ("Delete Extra Tables", delete_tables),
            ("Add Info to Extra Tables", add_info_to_special_tables),
            ("Delete from Extra Tables", manage_special_tables),
            ("Exit", exit_program),
        ]

        for label, action in buttons:
            btn = CustomButton(text=label, size_hint=(1, 1))
            btn.bind(on_press=action)
            button_layout.add_widget(btn)

        layout.add_widget(button_layout)
        self.add_widget(layout)

    def go_to_add_info(self, instance):
        self.manager.current = 'add_info'

class MyApp(App):
    def build(self):
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(MainMenuScreen(name='menu'))
        sm.add_widget(AddInfoScreen(name='add_info'))
        return sm
    
# Function stubs for menu operations
def display_existing_tables():
    interact_with_database.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    tables = interact_with_database.fetchall()

    tables = [table[0] for table in tables if table[0] != 'sqlite_sequence']

    predefined_order = ['Crimes', 'Evidence', 'Officers', 'Suspects']
    sorted_tables = sorted(tables, key=lambda x: (predefined_order.index(x) if x in predefined_order else len(predefined_order)))

    sorted_tables.append('Back to main menu')
    return sorted_tables







def log_entry(crime_id, message):                           # Function to create log entries in 'Program Files'
    case_folder = os.path.join(program_files_path, f'case_{crime_id}') # we let the code know where and under what name the files will be saved
    if not os.path.exists(case_folder):                     # if the file doesnt exist
        os.makedirs(case_folder)                            # create it

    with open(os.path.join(case_folder, 'log.txt'), 'a') as log_file:  # Open the log file in append mode
        log_file.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} - {message}\n')  # Write the log entry with a timestamp

def add_new_info_to_a_table():                              # Function to add new information to tables
    os.system('clear')
    print('To which table would you\nlike to add new information?\n_________________________')

    sorted_tables = display_existing_tables()
    table_choice = input('\nEnter a choice [number / item name]: ').capitalize()

    if table_choice.lower() == 'back to main menu' or table_choice.lower() == 'back':
        main_menu()
        return

    try:                                                    # Match input with table name or number
        table_index = int(table_choice) - 1                 # we will choose 1 for the 0 element so we have to bring it down by 1 to match the 0
        if 0 <= table_index < len(sorted_tables):           # if the user input was between 1-5 or the right word
            table_choice = sorted_tables[table_index]       # the user choice = the right item
        else:                                               
            raise ValueError                                # happens when we enter smth we are not supposed to and then...
    except ValueError:                                      # ...we go to this code
        if table_choice not in sorted_tables:               # if we choose smth other than 1-5 or some other bs
            print('Enter a valid choice')
            time.sleep(2)
            add_new_info_to_a_table()                       # the menu starts all over after giving a 2 second message
            return

    while True:                                             # if we entered our option correctly we continue to the appropriate option
        if table_choice == 'Crimes':                        # only Crimes table works with ID because its a bit more special than the others
            os.system('clear')
            crime_type = input('What type of crime is it?:          ')
            crime_date = input('When did the crime happen? (date):  ')
            crime_location = input('Where did the crime happen?:        ')
            interact_with_database.execute(f'INSERT INTO "Crimes" (Type, Date, Location) VALUES (%s, %s, %s) RETURNING crimeid;',
                                           (crime_type, crime_date, crime_location))
            crime_id = interact_with_database.fetchone()[0] # Get the last inserted row ID (CrimeID)   (chatgpt helped with this line)
            if save_confirmation():                         # the user gets asked if hes sure and if the answe is yes the info gets added to the table
                log_entry(crime_id, f'New crime added: {crime_type}, Date: {crime_date}, Location: {crime_location}')
            print('\nNew crime added.')
            time.sleep(3)
            add_new_info_to_a_table()                       # after all that we go back to the previous menu

        elif table_choice == 'Evidence':
            os.system('clear')
            evidence_type = input('What type of evidence is it?:                        ')
            evidence_description = input('Short description of the evidence:                   ')
            crime_indices = select_multiple_crimes()
            if crime_indices:
                for crime_id in crime_indices:
                    interact_with_database.execute(f'INSERT INTO "Evidence" (Type, Description, CrimeID) VALUES (%s, %s, %s);',
                                                   (evidence_type, evidence_description, crime_id))
                if save_confirmation():
                    for crime_id in crime_indices:
                        log_entry(crime_id, f'New evidence added: {evidence_type}, Description: {evidence_description}')
                print(f'\nNew evidence added to Crimes: {", ".join(map(str, crime_indices))}.')
            time.sleep(3)
            add_new_info_to_a_table()

        elif table_choice == 'Officers':
            os.system('clear')
            officers_name = input("Officers' first and last name:                      ")
            officers_rank = input("Officers' rank:                                     ")
            officers_department = input("Officers' department:                               ")
            crime_indices = select_multiple_crimes()
            if crime_indices:
                for crime_id in crime_indices:
                    interact_with_database.execute(f'INSERT INTO "Officers" (Name, Rank, Department, CrimeID) VALUES (%s, %s, %s, %s);',
                                                   (officers_name, officers_rank, officers_department, crime_id))
                if save_confirmation():
                    for crime_id in crime_indices:
                        log_entry(crime_id, f'Officer added: {officers_name}, Rank: {officers_rank}, Department: {officers_department}')
                print(f'\nNew officer added to Crimes: {", ".join(map(str, crime_indices))}.')
            time.sleep(3)
            add_new_info_to_a_table()

        elif table_choice == 'Suspects':
            os.system('clear')
            suspects_name = input('What is the name of the suspect?:                      ')
            suspects_age = input('How old is the suspect?:                               ')
            suspects_description = input('Short description of the suspect:                      ')
            crime_indices = select_multiple_crimes()
            if crime_indices:
                for crime_id in crime_indices:
                    interact_with_database.execute(f'INSERT INTO "Suspects" (Name, Age, Description, CrimeID) VALUES (%s, %s, %s, %s);', 
                                                   (suspects_name, suspects_age, suspects_description, crime_id))
                if save_confirmation():
                    for crime_id in crime_indices:
                        log_entry(crime_id, f'Suspect added: {suspects_name}, Age: {suspects_age}, Description: {suspects_description}')
                print(f'\nNew suspect added to Crimes: {", ".join(map(str, crime_indices))}.')
            time.sleep(3)
            add_new_info_to_a_table()

        elif table_choice.lower() == 'back to main menu' or table_choice.lower() == 'back':
            main_menu()

        else:
            print('Please enter a valid choice...')
            time.sleep(2)
            add_new_info_to_a_table()

def display_existing_tables():                              # Function to display existing tables ----- "information_schema.tables" stores information about the tables in the db
    interact_with_database.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';") 
    tables = interact_with_database.fetchall()

    tables = [table[0] for table in tables if table[0] != 'sqlite_sequence']

    predefined_order = ['Crimes', 'Evidence', 'Officers', 'Suspects']

    # Sort tables based on the predefined order, with others appearing afterward (chatgpt helped, didnt know this code was a thing)
    sorted_tables = sorted(tables, key=lambda x: (predefined_order.index(x) if x in predefined_order else len(predefined_order)))

    # Append "(not working)" to all tables after 'Suspects'
    suspect_index = sorted_tables.index('Suspects') if 'Suspects' in sorted_tables else len(sorted_tables)
    for i in range(suspect_index + 1, len(sorted_tables)):
        sorted_tables[i] += ' [not working]'

    sorted_tables.append('Back to main menu') #we add this option to the end of the list so we can use it

    for index, table in enumerate(sorted_tables, start=1): #we print the list of table names +back option on the screen with an index (1-5)
        print(f"{index}. {table}")

    return sorted_tables #we return a list of 5 elements and theirt index on the screen

def save_confirmation():
    answer = input('\nAre you sure you want to save this? (yes/no) \n')
    while True:
        if answer.lower() in ['yes', 'y']:
            database_link.commit()
            return True
        elif answer.lower() in ['no', 'n']:
            print('\nOperation cancelled, going to main menu...')
            wait_and_clear()
            main_menu()
            return False
        else:
            print('Enter a valid option...')
            wait_and_clear()
            save_confirmation()




def prepare_to_delete_crime():                              # A special function that works only with Crimes because 'Crimes' has more options than other tables
    os.system('clear')
    interact_with_database.execute('SELECT CrimeID, Type, Date, Location FROM "Crimes"') # returns all the requested info from the table
    crimes = interact_with_database.fetchall()              # allows us to access all the info in the form of a list in which each item is a tupple

    if not crimes:                                          # if the list of tupples is empty = []
        print('No crimes found. Returning to menu...')
        time.sleep(2)
        main_menu()
        return None

    print('Select a crime:\n')
    for index, crime in enumerate(crimes, start=1):         # for each tupple() in the list[] we print a tupple and add an index to it
        print(f"{index}. CrimeID: {crime[0]} | Type: {crime[1]} | Date: {crime[2]} | Location: {crime[3]}")

    choice = input(f'\nEnter the crime number [1-{len(crimes)}] or "back" to return: ') # user help if they dont know what to enter (1-4) + hidden back option

    if choice.lower() == 'back':
        delete_information()
        return None

    try:
        crime_index = int(choice) - 1
        if 0 <= crime_index < len(crimes):
            return crimes[crime_index]                      # Return the selected crime details
        else:
            raise ValueError
    except ValueError:
        print('Enter a valid crime number')
        time.sleep(2)
        return prepare_to_delete_crime()

def select_multiple_crimes():
    os.system('clear')
    interact_with_database.execute('SELECT CrimeID, Type, Date, Location FROM "Crimes"')
    crimes = interact_with_database.fetchall()

    if not crimes:
        print('No crimes found. Returning to menu...')
        time.sleep(2)
        main_menu()
        return []

    print('Select for which crimes:\n')
    for index, crime in enumerate(crimes, start=1):
        print(f"{index}. CrimeID: {crime[0]} | Type: {crime[1]} | Date: {crime[2]} | Location: {crime[3]}")

    choice = input(f'\nEnter the crime numbers [e.g., 1,3,5 for multiple choices] or "back" to return: ')

    if choice.lower() == 'back':
        return []

    try:
        crime_indices = [int(i.strip()) - 1 for i in choice.split(',')]
        valid_crimes = [crimes[i][0] for i in crime_indices if 0 <= i < len(crimes)]
        if not valid_crimes:
            raise ValueError
        return valid_crimes
    except ValueError:
        print('Enter valid crime numbers')
        time.sleep(2)
        return select_multiple_crimes()

def update_tables():
    os.system('clear')
    print('Which table would you\nlike to update?\n_________________________')
    sorted_tables = display_existing_tables()
    
    back_option_index = len(sorted_tables)                  # Calculate the index of the "Back to main menu" option

    table_choice = input('\nEnter a choice [number / item name] or "back" to return: ').capitalize()

    if table_choice.lower() == 'back':
        main_menu()
        return

    try:
        table_index = int(table_choice) - 1
        if 0 <= table_index < len(sorted_tables) - 1:
            table_choice = sorted_tables[table_index]
            if " [not working]" in table_choice:            # Check if the selected table is in the [not working] range
                raise ValueError
        elif table_index == back_option_index - 1:
            main_menu()
            return
        else:
            raise ValueError
    except ValueError:
        print('Choose a valid option')
        time.sleep(2)
        update_tables()
        return

    os.system('clear')
    interact_with_database.execute(f'SELECT crimeid, * FROM "{table_choice}"')    
    rows = interact_with_database.fetchall()

    if not rows:
        print(f'No records found in {table_choice}. Returning to menu...')
        time.sleep(2)
        main_menu()
        return

    column_names = [description[0] for description in interact_with_database.description]

    print(f'Select a record from the {table_choice} table to update or "back" to return:\n')     # Display the records for selection

    for index, row in enumerate(rows, start=1):
        row_display = [f"{col_name}: {value}" for col_name, value in zip(column_names[1:], row[1:])]
        print(f"{index}. " + " | ".join(row_display))

    record_choice = input(f'\nEnter the record number to update [1-{len(rows)}]: ')

    if record_choice.lower() == 'back':
        update_tables()
        return
    
    try:
        record_index = int(record_choice) - 1
        if 0 <= record_index < len(rows):
            selected_row = rows[record_index]
        else:
            raise ValueError
    except ValueError:
        print('Enter a valid record number')
        time.sleep(2)
        update_tables()
        return

    os.system('clear')
    print(f'Which field would you like to update in the selected record?\n')
    for index, column_name in enumerate(column_names[2:], start=1):  # Skip the first two columns (crimeid and primary key)
        print(f"{index}. {column_name.capitalize()}")

    field_choice = input(f'\nEnter the field number to update [1-{len(column_names) - 2}] or "back" to return: ')

    if field_choice.lower() == 'back':
        update_tables()
        return

    try:
        field_index = int(field_choice) - 1
        if 0 <= field_index < len(column_names) - 2:
            field_name = column_names[field_index + 2]      # Adjust for skipping the first two columns
        else:
            raise ValueError
    except ValueError:
        print('Enter a valid field number')
        time.sleep(2)
        update_tables()
        return

    new_value = input(f'Enter the new value for {field_name} or "back" to return: ')

    if new_value.lower() == 'back':
        update_tables()
        return

    try:                                                    # Update the record in the database
        interact_with_database.execute(f'UPDATE "{table_choice}" SET {field_name} = %s WHERE crimeid = %s', (new_value, selected_row[0]))
        if save_confirmation():
            log_entry(selected_row[0], f'Updated {field_name} to {new_value} in {table_choice} table')
        print(f'\nRecord updated successfully in {table_choice}.')
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")

    time.sleep(2)
    update_tables()

def displaying_function(table_choice):                      # Function to display information from tables
    os.system('clear')
    print(f'All {table_choice}')
    print('_________________________')

    interact_with_database.execute(f'SELECT * FROM "{table_choice}"') # Execute the query to fetch all rows from the chosen table
    rows = interact_with_database.fetchall()

    # Fetch column names to use as headers
    column_names = [description[0] for description in interact_with_database.description]

    # Find the maximum width of each column for pretty printing
    column_widths = [max(len(str(value)) for value in column) for column in zip(*([column_names] + rows))]

    # Create a format string for each row
    format_string = '  '.join(f'{{:<{width}}}' for width in column_widths)

    # Print the header row
    print(format_string.format(*column_names))
    print('-' * sum(column_widths))

    for row in rows:
        print(format_string.format(*row))

    input('\nPress Enter to continue ')
    display_information_menu()

def display_crimes_data(full_info=True):
    os.system('clear')

    if full_info:
        print('Displaying all crimes with corresponding data...\n')
    else:
        print('Displaying all crimes...\n')

    # Fetch all crimes
    interact_with_database.execute('SELECT CrimeID, Type, Date, Location FROM "Crimes"')
    crimes = interact_with_database.fetchall()

    for crime in crimes:
        crime_id, crime_type, crime_date, crime_location = crime
        print(f"Crime #{crime_id}:")
        print(f"  Type: {crime_type}")
        print(f"  Date: {crime_date}")
        print(f"  Location: {crime_location}")

        if full_info:
            # Fetch corresponding evidence
            interact_with_database.execute('SELECT Type, Description FROM "Evidence" WHERE crimeid = %s', (crime_id,))
            evidence = interact_with_database.fetchall()
            if evidence:
                print("  Evidence:")
                for ev in evidence:
                    print(f"    - Type: {ev[0]}, Description: {ev[1]}")
            else:
                print("  Evidence: None")

            # Fetch corresponding officers
            interact_with_database.execute('SELECT Name, Rank, Department FROM "Officers" WHERE CrimeID = %s', (crime_id,))
            officers = interact_with_database.fetchall()
            if officers:
                print("  Officers:")
                for officer in officers:
                    print(f"    - Name: {officer[0]}, Rank: {officer[1]}, Department: {officer[2]}")
            else:
                print("  Officers: None")

            # Fetch corresponding suspects
            interact_with_database.execute('SELECT Name, Age, Description FROM "Suspects" WHERE CrimeID = %s', (crime_id,))
            suspects = interact_with_database.fetchall()
            if suspects:
                print("  Suspects:")
                for suspect in suspects:
                    print(f"    - Name: {suspect[0]}, Age: {suspect[1]}, Description: {suspect[2]}")
            else:
                print("  Suspects: None")

        print("\n" + "-"*40 + "\n")  # Separator between crimes

    input('Press Enter to return to the menu ')
    display_information_menu()

def display_information_menu():
    os.system('clear')
    print('What would you like to display?\n_________________________')
    
    sorted_tables = display_existing_tables_option3()
    
    # Calculate the index of the "Back to main menu" option
    back_option_index = len(sorted_tables)

    choice = input('\nEnter a choice [number / table name] or "back" to return: ').strip().capitalize()

    if choice.lower() == 'back':
        main_menu()
        return

    try:
        choice_index = int(choice) - 1
        if choice_index == 0:  # Crimes [full]
            display_crimes_data(full_info=True)
            return
        elif choice_index == 1:  # Crimes [only]
            display_crimes_data(full_info=False)
            return
        elif 2 <= choice_index < back_option_index - 1:  # Other valid tables
            selected_table = sorted_tables[choice_index]
            displaying_function(selected_table)
        elif choice_index == back_option_index - 1:  # Back to main menu
            main_menu()
            return
        else:
            raise ValueError
    except ValueError:
        print('Choose a valid option...')
        time.sleep(2)
        display_information_menu()
        return

def delete_information():                                   # Function to delete specific information
    os.system('clear')
    print('What would you like to delete?\n_________________________')
    print('1. Crimes')
    print('2. Evidence')
    print('3. Officer')
    print('4. Suspect')
    print('5. Multiple records')
    print('6. Back to main menu')

    choice = input('\nEnter a choice [number]: ').strip()

    if choice == '1':
        delete_crime()
    elif choice == '2':
        delete_from_table('Evidence')
    elif choice == '3':
        delete_from_table('Officers')
    elif choice == '4':
        delete_from_table('Suspects')
    elif choice == '5':
        delete_multiple_records()
    elif choice == '6':
        main_menu()
    else:
        print('Enter a valid choice...')
        time.sleep(2)
        delete_information()

def delete_crime():                                         # Delete a crime with options
    os.system('clear')
    crime = prepare_to_delete_crime()
    if crime is not None:
        crime_id = crime[0]  # Get the CrimeID from the selected crime

        print('\nChoose an option:')
        print('1. Delete crime and all related information')
        print('2. Delete only the crime (leave related information)')

        choice = input('\nEnter your choice [1/2] or "back" to return: ').strip()

        if choice == '1':
            delete_confirmation()

            try:
                interact_with_database.execute('DELETE FROM "Evidence" WHERE crimeid = %s', (crime_id,))
                interact_with_database.execute('DELETE FROM "Officers" WHERE crimeid = %s', (crime_id,))
                interact_with_database.execute('DELETE FROM "Suspects" WHERE crimeid = %s', (crime_id,))
                interact_with_database.execute('DELETE FROM "Crimes" WHERE crimeid = %s', (crime_id,))
                if save_confirmation():
                    log_entry(crime_id, 'Crime and all related information deleted')
                print(f'\nCrime #{crime_id} and all related information deleted.')
            except psycopg2.Error as e:
                print(f"An error occurred: {e}")
        elif choice == '2':
            delete_confirmation()

            try:
                interact_with_database.execute('DELETE FROM "Crimes" WHERE crimeid = %s', (crime_id,))
                if save_confirmation():
                    log_entry(crime_id, 'Crime deleted, related information retained')
                print(f'\nCrime #{crime_id} deleted, but related information retained.')
            except psycopg2.Error as e:
                print(f"An error occurred: {e}")
        elif choice.lower() == 'back':
            delete_information()
            return
        else:
            print('Invalid choice. Returning to menu...')
            time.sleep(2)
            main_menu()

    go_to_menu()

def delete_from_table(table_name):                          # Delete specific records from a table
    os.system('clear')
    interact_with_database.execute(f'SELECT crimeid, * FROM "{table_name}"')
    rows = interact_with_database.fetchall()

    if not rows:
        print(f'No records found in {table_name}. Returning to menu...')
        time.sleep(2)
        main_menu()
        return

    column_names = [description[0] for description in interact_with_database.description]

    # Display the records for selection
    print(f'Select a record from the {table_name} table to delete or "back" to return:\n')
    for row in rows:
        row_display = [f"{col_name.capitalize()}: {str(value).capitalize()}" for col_name, value in zip(column_names[1:], row[1:])]
        print(" | ".join(row_display))

    record_choice = input(f'\nEnter the ID number you wish to delete [or multiple e.g 1,2,3] or "back" to return: ')

    if record_choice.lower() == 'back':
        delete_information()
        return

    delete_records_by_indices(table_name, record_choice)

def delete_records_by_indices(table_name, record_choice):
    try:
        indices = [int(i.strip()) - 1 for i in record_choice.split(',')]
        for index in indices:
            if index >= 0:
                interact_with_database.execute(f'DELETE FROM "{table_name}" WHERE crimeid = %s', (index + 1,))
        if save_confirmation():
            for index in indices:
                log_entry(index + 1, f'Record deleted from {table_name}')
        database_link.commit()
        print(f'\nSelected records deleted successfully from {table_name}.')
    except ValueError:
        print('Invalid input. Please enter valid numbers separated by commas.')
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")

    go_to_menu()

def delete_multiple_records():
    os.system('clear')
    print('From which table would you like to delete multiple records?\n_________________________')
    print('1. Crimes')
    print('2. Evidence')
    print('3. Officers')
    print('4. Suspects')
    print('5. Back to main menu')

    choice = input('\nEnter a choice [number]: ').strip()

    if choice == '1':
        delete_from_table('Crimes')
    elif choice == '2':
        delete_from_table('Evidence')
    elif choice == '3':
        delete_from_table('Officers')
    elif choice == '4':
        delete_from_table('Suspects')
    elif choice == '5':
        delete_information()
    else:
        print('Enter a valid choice...')
        time.sleep(2)
        delete_multiple_records()

def create_tables():                                        # Function to create tables
    os.system('clear')
    table_name = input("Enter a name for the table you want to create:                 ")
    number_of_columns = int(input("How many columns will the table have?                          "))
    columns = []

    for i in range(number_of_columns):
        column_name = input(f"Enter the name of column {i + 1}:                                    ")
        column_type = input(f"Enter a data type for column '{column_name}' [VARCHAR(255), INT, etc]:    ")
        columns.append(f"{column_name} {column_type}")

    columns_definition = ",\n        ".join(columns)

    create_a_table = f'''
    CREATE TABLE IF NOT EXISTS "{table_name}" (
        {columns_definition}
    );
    '''

    try:
        interact_with_database.execute(create_a_table)
        database_link.commit()
        print(f"\nTable '{table_name}' created successfully.")
        go_to_menu()
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")

def display_existing_tables():                              # Function to display existing tables ----- "information_schema.tables" stores information about the tables in the db
    interact_with_database.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';") 
    tables = interact_with_database.fetchall()

    tables = [table[0] for table in tables if table[0] != 'sqlite_sequence']

    predefined_order = ['Crimes', 'Evidence', 'Officers', 'Suspects']

    # Sort tables based on the predefined order, with others appearing afterward (chatgpt helped, didnt know this code was a thing)
    sorted_tables = sorted(tables, key=lambda x: (predefined_order.index(x) if x in predefined_order else len(predefined_order)))

    # Append "(not working)" to all tables after 'Suspects'
    suspect_index = sorted_tables.index('Suspects') if 'Suspects' in sorted_tables else len(sorted_tables)
    for i in range(suspect_index + 1, len(sorted_tables)):
        sorted_tables[i] += ' [not working]'

    sorted_tables.append('Back to main menu') #we add this option to the end of the list so we can use it

    for index, table in enumerate(sorted_tables, start=1): #we print the list of table names +back option on the screen with an index (1-5)
        print(f"{index}. {table}")

    return sorted_tables #we return a list of 5 elements and theirt index on the screen

def display_existing_tables_option3():
    interact_with_database.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    tables = interact_with_database.fetchall()

    tables = [table[0] for table in tables if table[0] != 'sqlite_sequence']

    predefined_order = ['Crimes', 'Evidence', 'Officers', 'Suspects']

    # Create a list with custom options for Crimes [full] and Crimes [only]
    final_sorted_tables = ['Crimes [full]', 'Crimes [only]']

    # Append other tables based on the predefined order
    final_sorted_tables += [table for table in predefined_order if table in tables and table != 'Crimes']

    # Append any remaining tables that are not part of the predefined order
    remaining_tables = [table for table in tables if table not in final_sorted_tables and table != 'Crimes']
    final_sorted_tables += remaining_tables

    final_sorted_tables.append('Back to main menu')  # Add the back option to the end of the list

    for index, table in enumerate(final_sorted_tables, start=1):  # Print the list of table names + back option on the screen with an index
        print(f"{index}. {table}")

    return final_sorted_tables  # Return the sorted list with indices

def delete_tables():                                        # Function to delete tables
    os.system('clear')

    sorted_tables = display_existing_tables()

    table_choice = input('\nChoose a table you wish to delete [number / item name] or "back" to return: ').strip().capitalize()

    if table_choice.lower() == 'back':
        main_menu()
        return

    try:
        table_index = int(table_choice) - 1
        if 0 <= table_index < len(sorted_tables):
            table_choice = sorted_tables[table_index]
        else:
            raise ValueError
    except ValueError:
        matching_table = next((table for table in sorted_tables if table.lower() == table_choice.lower()), None)
        if matching_table:
            table_choice = matching_table
        else:
            print('Please enter a valid choice...')
            time.sleep(2)
            delete_tables()
            return

    table_choice = table_choice.replace(" [not working]", "")

    if table_choice.capitalize() == 'Back to main menu' or table_choice.capitalize() == 'Back':
        main_menu()
    else:
        deleting_function(table_choice)

def deleting_function(table_choice):
    os.system('clear')
    delete_confirmation()
    try:
        interact_with_database.execute(f'DROP TABLE "{table_choice}"')
        database_link.commit()  # Commit the deletion to the database
        print(f"\nTable '{table_choice}' deleted.")
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    go_to_menu()

def delete_confirmation():
    answer = input('\nAre you sure you want to delete this? (yes/no) \n')
    while True:
        if answer.lower() in ['yes', 'y']:
            database_link.commit()
            break
        elif answer.lower() in ['no', 'n']:
            print('\nOperation cancelled, going to main menu...')
            wait_and_clear()
            main_menu()
        else:
            print('Enter a valid option...')
            wait_and_clear()
            delete_confirmation()

#Functions that work with tables created by us
def add_info_to_special_tables():
    os.system('clear')
    print('Add Info to Special Tables\n_________________________')

    special_tables = get_special_tables()
    
    if not special_tables:
        print("No special tables found.")
        time.sleep(2)
        main_menu()
        return
    
    for index, table in enumerate(special_tables, start=1):
        print(f"{index}. {table}")

    choice = input('\nEnter the number of the table you want to add information to or "back" to return: ').strip()

    if choice.lower() == 'back':
        main_menu()
        return

    try:
        table_index = int(choice) - 1
        if 0 <= table_index < len(special_tables):
            selected_table = special_tables[table_index]
            add_info_to_table(selected_table)
        else:
            raise ValueError
    except ValueError:
        print('Choose a valid option...')
        time.sleep(2)
        add_info_to_special_tables()
        return

def get_special_tables():
    interact_with_database.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    tables = interact_with_database.fetchall()

    tables = [table[0] for table in tables if table[0] not in ['Crimes', 'Evidence', 'Officers', 'Suspects', 'sqlite_sequence']]
    
    return tables

def add_info_to_table(table_name):
    os.system('clear')
    print(f"Adding Information to {table_name}\n_________________________")

    # Fetch column names for the selected table
    interact_with_database.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';")
    columns = interact_with_database.fetchall()

    new_record = {}
    for column in columns:
        column_name = column[0]
        user_input = input(f"Enter information for column '{column_name}': ").strip()
        new_record[column_name] = user_input

    # Insert the new record into the table
    columns_str = ', '.join(new_record.keys())
    values_str = ', '.join(f"%({key})s" for key in new_record.keys())

    try:
        interact_with_database.execute(f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({values_str})', new_record)
        # Commit the transaction to make the changes persistent
        interact_with_database.connection.commit()
        print(f'Information added to {table_name} successfully.')
    except Exception as e:
        interact_with_database.connection.rollback()  # Rollback in case of error
        print(f'An error occurred: {e}')
    
    time.sleep(2)
    main_menu()

def manage_special_tables():
    os.system('clear')
    print('Manage Special Tables\n_________________________')

    special_tables = get_special_tables()
    
    for index, table in enumerate(special_tables, start=1):
        print(f"{index}. {table}")

    choice = input('\nEnter the number of the table you want to manage or "back" to return: ').strip()

    if choice.lower() == 'back':
        main_menu()
        return

    try:
        table_index = int(choice) - 1
        if 0 <= table_index < len(special_tables):
            selected_table = special_tables[table_index]
            manage_table(selected_table)
        else:
            raise ValueError
    except ValueError:
        print('Choose a valid option...')
        time.sleep(2)
        manage_special_tables()
        return

def manage_table(table_name):
    os.system('clear')
    print(f'Manage Table: {table_name}\n_________________________')

    # Display all rows from the selected table
    interact_with_database.execute(f'SELECT * FROM "{table_name}"')
    rows = interact_with_database.fetchall()

    if not rows:
        print(f'No records found in {table_name}. Returning to menu...')
        time.sleep(2)
        main_menu()
        return

    for index, row in enumerate(rows, start=1):
        print(f"{index}. {row}")

    choice = input('\nEnter the number of the row you want to delete or "back" to return: ').strip()

    if choice.lower() == 'back':
        main_menu()
        return

    try:
        row_index = int(choice) - 1
        if 0 <= row_index < len(rows):
            delete_row_from_table(table_name, rows[row_index])
        else:
            raise ValueError
    except ValueError:
        print('Choose a valid option...')
        time.sleep(2)
        manage_table(table_name)
        return

def delete_row_from_table(table_name, row):
    os.system('clear')
    print(f'Deleting row from {table_name}\n_________________________')

    # Assuming the first column is the primary key
    try:
        # Execute the query to get the primary key column name
        interact_with_database.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}' ORDER BY ordinal_position LIMIT 1;")
        primary_key_column = interact_with_database.fetchone()[0]

        primary_key = row[0]

        # Delete the row based on the primary key
        interact_with_database.execute(f'DELETE FROM "{table_name}" WHERE {primary_key_column} = %s', (primary_key,))
        
        # Commit the transaction to save changes
        interact_with_database.connection.commit()

        print(f'Row deleted successfully from {table_name}.')
    except Exception as e:
        interact_with_database.connection.rollback()  # Rollback in case of error
        print(f'An error occurred: {e}')
    
    time.sleep(2)
    main_menu()

if __name__ == '__main__':
    MyApp().run()                                                # The program starts here

database_link.close()