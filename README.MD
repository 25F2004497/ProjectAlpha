================================================================================

&#x20;             PROJECT ALPHA — COMPLETE GUIDE \& DOCUMENTATION

&#x20;                  Trekking Management Application

================================================================================



Date Prepared : July 2026

Technology    : Flask | Jinja2 | HTML | CSS | Bootstrap (Pulse Theme) | SQLite

Port          : 8111





================================================================================

&#x20;SECTION 1 — DEFAULT LOGIN CREDENTIALS (DEMO ACCOUNTS)

================================================================================



&#x20; ROLE            USERNAME           PASSWORD         NOTES

&#x20; ──────────────  ─────────────────  ───────────────  ──────────────────────────

&#x20; Admin/Overseer  overseer           overseer         Pre-seeded superuser

&#x20; Staff/Master    mike\_master        password123      Pre-approved staff member

&#x20; User/Explorer   john\_explorer      password123      Regular trekker account



&#x20; \* The Overseer account is created automatically when the server boots.

&#x20; \* Staff and Explorer accounts are seeded via the seed script.

&#x20; \* New accounts can be registered via the /register page.





================================================================================

&#x20;SECTION 2 — PROJECT FOLDER STRUCTURE

================================================================================



&#x20; Project\_Alpha/

&#x20; │

&#x20; ├── run\_server.py              ← Main entry point. Boots the Flask app.

&#x20; │

&#x20; ├── database/

&#x20; │   └── schema.py              ← SQLAlchemy models (Wanderer, ExpeditionBase,

&#x20; │                                 ExpeditionLog). Defines the database tables.

&#x20; │

&#x20; ├── controllers/

&#x20; │   ├── auth.py                ← Blueprint for login, register, logout routes

&#x20; │   └── dashboard.py           ← Blueprint for overseer, master, explorer dashboards

&#x20; │

&#x20; ├── frontend\_views/            ← All Jinja2 HTML templates

&#x20; │   ├── layout.html            ← Base template (navbar, Bootstrap CDN, block structure)

&#x20; │   ├── login.html             ← Login form page

&#x20; │   ├── register.html          ← Registration form page

&#x20; │   ├── overseer\_dash.html     ← Admin dashboard (create treks, manage users)

&#x20; │   ├── master\_dash.html       ← Staff dashboard (update assigned treks)

&#x20; │   └── explorer\_dash.html     ← User dashboard (browse \& book treks, search)

&#x20; │

&#x20; ├── public\_assets/             ← Static files (CSS, images if any)

&#x20; │   └── css/

&#x20; │       └── style.css          ← (Optional) Extra styling overrides

&#x20; │

&#x20; ├── alpha\_store\_v2.sqlite3     ← SQLite database file (auto-created on first boot)

&#x20; │

&#x20; └── seed\_alpha\_v2.py           ← Script to populate demo data into the database





================================================================================

&#x20;SECTION 3 — FILE-BY-FILE EXPLANATION

================================================================================



&#x20; ┌──────────────────────────────────────────────────────────────────────────────┐

&#x20; │  run\_server.py  —  THE MAIN ENTRY POINT                                     │

&#x20; ├──────────────────────────────────────────────────────────────────────────────┤

&#x20; │  This is where everything starts. When you run `python run\_server.py`:      │

&#x20; │                                                                              │

&#x20; │  1. A Flask application object is created.                                  │

&#x20; │  2. The template folder is set to `frontend\_views/`.                        │

&#x20; │  3. The static folder is set to `public\_assets/`.                           │

&#x20; │  4. The SQLite database path is configured (alpha\_store\_v2.sqlite3).        │

&#x20; │  5. SQLAlchemy is initialised with `db.init\_app(app)`.                      │

&#x20; │  6. Two Blueprints are registered:                                          │

&#x20; │     - auth\_bp   (handles /login, /register, /logout)                        │

&#x20; │     - dash\_bp   (handles /dash/overseer, /dash/master, /dash/explorer)      │

&#x20; │  7. On first boot, it checks if the Overseer admin exists. If not, it       │

&#x20; │     creates the default admin account automatically.                        │

&#x20; │  8. The server starts on http://127.0.0.1:8111                              │

&#x20; └──────────────────────────────────────────────────────────────────────────────┘



&#x20; ┌──────────────────────────────────────────────────────────────────────────────┐

&#x20; │  database/schema.py  —  DATABASE MODELS                                     │

&#x20; ├──────────────────────────────────────────────────────────────────────────────┤

&#x20; │  Defines three SQLAlchemy models that map to SQLite tables:                 │

&#x20; │                                                                              │

&#x20; │  1. Wanderer (Table: 'wanderers')                                           │

&#x20; │     - id            : Primary key (auto-increment)                          │

&#x20; │     - alias          : Unique username                                      │

&#x20; │     - secret         : Hashed password (scrypt algorithm)                   │

&#x20; │     - role\_type      : 'explorer', 'master', or 'overseer'                 │

&#x20; │     - contact\_email  : Optional email field                                 │

&#x20; │     - active         : Boolean (False = banned/blacklisted)                 │

&#x20; │     - is\_approved    : Boolean (staff must be approved by admin)            │

&#x20; │     - hash\_secret()  : Method to hash a raw password before storing         │

&#x20; │     - verify\_secret(): Method to check a password against the hash          │

&#x20; │                                                                              │

&#x20; │  2. ExpeditionBase (Table: 'expeditions')                                   │

&#x20; │     - eid            : Primary key                                          │

&#x20; │     - title          : Name of the trek/expedition                          │

&#x20; │     - locale         : Location/region                                      │

&#x20; │     - challenge      : Difficulty level (Easy/Moderate/Hard)                │

&#x20; │     - max\_wanderers  : Total capacity                                       │

&#x20; │     - current\_slots  : Remaining available spots                            │

&#x20; │     - launch\_date    : Start date of the trek                               │

&#x20; │     - end\_date       : End date of the trek                                 │

&#x20; │     - current\_phase  : Status (Planning / Open / Closed / Finished)         │

&#x20; │     - master\_id      : Foreign key → assigned staff member                  │

&#x20; │                                                                              │

&#x20; │  3. ExpeditionLog (Table: 'expedition\_logs')                                │

&#x20; │     - log\_id         : Primary key                                          │

&#x20; │     - wanderer\_id    : Foreign key → the user who booked                    │

&#x20; │     - expedition\_id  : Foreign key → the trek that was booked               │

&#x20; │     - recorded\_at    : Timestamp of booking                                 │

&#x20; │                                                                              │

&#x20; │  RELATIONSHIPS:                                                              │

&#x20; │     ExpeditionBase.master  → links to the Wanderer who is assigned as staff │

&#x20; │     ExpeditionLog.wanderer → links to the Wanderer who made the booking     │

&#x20; │     ExpeditionLog.expedition → links to the booked ExpeditionBase           │

&#x20; └──────────────────────────────────────────────────────────────────────────────┘



&#x20; ┌──────────────────────────────────────────────────────────────────────────────┐

&#x20; │  controllers/auth.py  —  AUTHENTICATION ROUTES                              │

&#x20; ├──────────────────────────────────────────────────────────────────────────────┤

&#x20; │  This file handles user authentication. It is registered as a Flask         │

&#x20; │  Blueprint named 'auth'.                                                    │

&#x20; │                                                                              │

&#x20; │  ROUTES:                                                                     │

&#x20; │                                                                              │

&#x20; │  GET/POST  /login                                                           │

&#x20; │    - Displays the login form (GET) or processes login (POST).               │

&#x20; │    - On POST: queries Wanderer by alias, verifies password.                 │

&#x20; │    - If the account is banned (active=False), shows error.                  │

&#x20; │    - If the account is a staff awaiting approval, shows error.              │

&#x20; │    - On success: stores w\_id and role in Flask session.                     │

&#x20; │    - Redirects to the appropriate dashboard based on role.                  │

&#x20; │                                                                              │

&#x20; │  GET/POST  /register                                                        │

&#x20; │    - Displays the registration form (GET) or creates account (POST).        │

&#x20; │    - Checks if alias already exists. If yes, shows error.                   │

&#x20; │    - Explorer accounts are auto-approved and logged in immediately.         │

&#x20; │    - Master (staff) accounts require Overseer approval before login.        │

&#x20; │                                                                              │

&#x20; │  GET  /logout                                                               │

&#x20; │    - Clears the Flask session and redirects to /login.                       │

&#x20; └──────────────────────────────────────────────────────────────────────────────┘



&#x20; ┌──────────────────────────────────────────────────────────────────────────────┐

&#x20; │  controllers/dashboard.py  —  DASHBOARD ROUTES (ALL ROLES)                  │

&#x20; ├──────────────────────────────────────────────────────────────────────────────┤

&#x20; │  This file handles all three role-based dashboards. It is registered as     │

&#x20; │  a Blueprint named 'dash' with URL prefix '/dash'.                          │

&#x20; │                                                                              │

&#x20; │  OVERSEER (ADMIN) ROUTES:                                                    │

&#x20; │                                                                              │

&#x20; │  GET   /dash/overseer                                                       │

&#x20; │    - Fetches all expeditions, all non-overseer users, and all masters.      │

&#x20; │    - Renders the admin dashboard with full control panel.                   │

&#x20; │                                                                              │

&#x20; │  POST  /dash/add\_expedition                                                 │

&#x20; │    - Creates a new trek/expedition from form data.                          │

&#x20; │    - Optionally assigns a staff member (master) to the expedition.          │

&#x20; │    - Sets initial phase to 'Open'.                                          │

&#x20; │                                                                              │

&#x20; │  POST  /dash/approve/<wid>                                                  │

&#x20; │    - Approves a pending staff member (sets is\_approved = True).             │

&#x20; │                                                                              │

&#x20; │  POST  /dash/ban/<wid>                                                      │

&#x20; │    - Bans/blacklists a user or staff member (sets active = False).          │

&#x20; │                                                                              │

&#x20; │  MASTER (STAFF) ROUTES:                                                      │

&#x20; │                                                                              │

&#x20; │  GET   /dash/master                                                         │

&#x20; │    - Shows only the expeditions assigned to the logged-in master.           │

&#x20; │                                                                              │

&#x20; │  POST  /dash/update\_exp/<eid>                                               │

&#x20; │    - Allows the master to change the trek's phase (Open/Closed/Finished).   │

&#x20; │    - Allows the master to modify the available slot count.                  │

&#x20; │                                                                              │

&#x20; │  EXPLORER (USER) ROUTES:                                                     │

&#x20; │                                                                              │

&#x20; │  GET   /dash/explorer                                                       │

&#x20; │    - Shows all Open expeditions. Supports search by locale (?q=...).        │

&#x20; │    - Also shows the user's own booking history (ExpeditionLogs).            │

&#x20; │                                                                              │

&#x20; │  POST  /dash/join/<eid>                                                     │

&#x20; │    - Books the explorer into the expedition.                                │

&#x20; │    - Decrements the available slot count by 1.                              │

&#x20; │    - Creates an ExpeditionLog record as the booking receipt.                │

&#x20; └──────────────────────────────────────────────────────────────────────────────┘





================================================================================

&#x20;SECTION 4 — HOW THE DATABASE CONNECTION WORKS

================================================================================



&#x20; 1. In `database/schema.py`, an SQLAlchemy instance is created:

&#x20;      db = SQLAlchemy()



&#x20; 2. In `run\_server.py`, the Flask app's configuration is set:

&#x20;      app.config\['SQLALCHEMY\_DATABASE\_URI'] = 'sqlite:///alpha\_store\_v2.sqlite3'



&#x20; 3. The db object is then bound to the app:

&#x20;      db.init\_app(app)



&#x20; 4. When the server boots, `db.create\_all()` is called inside an

&#x20;    `app.app\_context()` block. This tells SQLAlchemy to read all the

&#x20;    Model classes (Wanderer, ExpeditionBase, ExpeditionLog) and create

&#x20;    the corresponding SQLite tables if they don't already exist.



&#x20; 5. The database file `alpha\_store\_v2.sqlite3` is automatically generated

&#x20;    in the Project\_Alpha root directory. You do NOT need to create it

&#x20;    manually — it is 100% programmatic.



&#x20; 6. All database operations (queries, inserts, updates) are handled via

&#x20;    SQLAlchemy's ORM. For example:

&#x20;      - Wanderer.query.filter\_by(alias='overseer').first()  → SELECT query

&#x20;      - db.session.add(new\_object)                          → INSERT

&#x20;      - db.session.commit()                                 → COMMIT transaction





================================================================================

&#x20;SECTION 5 — SETUP INSTRUCTIONS (HOW TO RUN FROM SCRATCH)

================================================================================



&#x20; PREREQUISITES:

&#x20;   - Python 3.10+ installed

&#x20;   - pip (Python package manager)



&#x20; STEP 1: Install required packages

&#x20;   Open a terminal in the Project\_Alpha folder and run:



&#x20;     pip install flask flask-sqlalchemy werkzeug



&#x20; STEP 2: Run the application

&#x20;   In the same terminal, run:



&#x20;     python run\_server.py



&#x20;   You should see:

&#x20;     "Project Alpha Server Booting on port 8111..."

&#x20;     \* Running on http://127.0.0.1:8111



&#x20; STEP 3: (Optional) Seed demo data

&#x20;   To populate dummy users, open a second terminal and run:



&#x20;     python seed\_alpha\_v2.py



&#x20;   This creates the demo accounts listed in Section 1.



&#x20; STEP 4: Open your browser

&#x20;   Navigate to:  http://127.0.0.1:8111



&#x20;   You will see the login page. Use any of the credentials from Section 1.





================================================================================

&#x20;SECTION 6 — PROJECT FLOW (HOW THE APP WORKS END-TO-END)

================================================================================



&#x20; ┌────────────────────────────────────────────────────────┐

&#x20; │                    APPLICATION FLOW                     │

&#x20; └────────────────────────────────────────────────────────┘



&#x20; User opens http://127.0.0.1:8111

&#x20;        │

&#x20;        ▼

&#x20; ┌─── LOGIN PAGE (/login) ───┐

&#x20; │  Enter Alias + Secret Key │

&#x20; │  Or click "Register"      │

&#x20; └───────────┬───────────────┘

&#x20;             │

&#x20;   ┌─────────┼──────────────────────┐

&#x20;   │         │                      │

&#x20;   ▼         ▼                      ▼

&#x20; OVERSEER   MASTER               EXPLORER

&#x20; (Admin)    (Staff)              (User/Trekker)

&#x20;   │         │                      │

&#x20;   ▼         ▼                      ▼

&#x20; /dash/     /dash/                /dash/

&#x20; overseer   master               explorer

&#x20;   │         │                      │

&#x20;   │         │                      ├── Search open expeditions by locale

&#x20;   │         │                      ├── Book an expedition (POST /dash/join/<eid>)

&#x20;   │         │                      └── View booking history

&#x20;   │         │

&#x20;   │         ├── View assigned expeditions

&#x20;   │         └── Update status (Open/Closed) \& modify slots

&#x20;   │

&#x20;   ├── Create new expeditions (with start + end dates)

&#x20;   ├── Assign a Master (staff) to any expedition

&#x20;   ├── Approve pending Master registrations

&#x20;   ├── Ban/Blacklist any user or staff

&#x20;   └── View all expeditions, users, and staff





================================================================================

&#x20;SECTION 7 — HOW TO PRESENT / DEMO THIS PROJECT

================================================================================



&#x20; STEP 1: PREPARATION

&#x20;   - Make sure Python and the required packages are installed.

&#x20;   - Delete the old database file (alpha\_store\_v2.sqlite3) if you want

&#x20;     a fresh start, or keep it if you've already added test data.

&#x20;   - Run `python run\_server.py` from the Project\_Alpha folder.



&#x20; STEP 2: SHOW THE LOGIN PAGE

&#x20;   - Open http://127.0.0.1:8111 in a browser.

&#x20;   - Point out the Bootstrap-based UI (Pulse theme).

&#x20;   - Show the login form and the "Register" link.



&#x20; STEP 3: DEMO ADMIN FLOW

&#x20;   - Log in as:  Alias = overseer  |  Secret = overseer

&#x20;   - On the Overseer Panel, demonstrate:

&#x20;     a) Creating a new expedition (fill in title, locale, challenge, dates).

&#x20;     b) Assigning a Master to the expedition using the dropdown.

&#x20;     c) Viewing the full personnel table with status badges.

&#x20;     d) Approving a pending staff member (if any exist).

&#x20;     e) Banning a user by clicking the "Ban" button.

&#x20;   - Log out.



&#x20; STEP 4: DEMO STAFF FLOW

&#x20;   - Log in as:  Alias = mike\_master  |  Secret = password123

&#x20;   - On the Master Panel, demonstrate:

&#x20;     a) Viewing the expeditions assigned to this master.

&#x20;     b) Changing the expedition status (e.g., from Open to Closed).

&#x20;     c) Modifying the available slot count.

&#x20;   - Log out.



&#x20; STEP 5: DEMO USER FLOW

&#x20;   - Log in as:  Alias = john\_explorer  |  Secret = password123

&#x20;   - On the Explorer Panel, demonstrate:

&#x20;     a) Browsing available (Open) expeditions.

&#x20;     b) Using the search bar to filter by locale.

&#x20;     c) Clicking "Join" to book an expedition.

&#x20;     d) Showing the booking appear under "My Logs".

&#x20;   - Log out.



&#x20; STEP 6: DEMO REGISTRATION

&#x20;   - Click "Register new Identity" on the login page.

&#x20;   - Create a new Explorer account → show it logs in immediately.

&#x20;   - Create a new Master account → show the "pending approval" message.

&#x20;   - Switch to the Overseer and approve the new Master.



&#x20; STEP 7: TALK ABOUT ARCHITECTURE

&#x20;   - Explain the Blueprint-based architecture.

&#x20;   - Explain how the database is created programmatically (no manual DB).

&#x20;   - Point out the three SQLAlchemy models and their relationships.

&#x20;   - Emphasise: NO JavaScript is used for any core functionality.

&#x20;   - Mention the Bootstrap Pulse theme for the frontend styling.





================================================================================

&#x20;SECTION 8 — TECHNOLOGY STACK SUMMARY

================================================================================



&#x20; Layer                Technology              Details

&#x20; ───────────────────  ──────────────────────  ───────────────────────────────

&#x20; Backend              Flask 3.x               Python micro-framework

&#x20; Templating           Jinja2                  Server-side rendering

&#x20; Frontend Styling     Bootstrap 5 (Pulse)     Bootswatch CDN theme

&#x20; Database             SQLite                  File-based, no external server

&#x20; ORM                  Flask-SQLAlchemy        Object-Relational Mapping

&#x20; Password Hashing     Werkzeug (scrypt)       Secure password storage

&#x20; Client-side JS       NONE                    No JavaScript for core logic





================================================================================

&#x20;SECTION 9 — IMPORTANT NOTES FOR SUBMISSION

================================================================================



&#x20; 1. The database (alpha\_store\_v2.sqlite3) is created PROGRAMMATICALLY

&#x20;    via db.create\_all(). You do NOT use DB Browser or any manual tool.



&#x20; 2. There is ZERO JavaScript used for core functionality. All form

&#x20;    submissions, navigation, and data operations are handled entirely

&#x20;    by Flask routes and Jinja2 templates.



&#x20; 3. The Overseer (Admin) account is auto-created on first server boot.

&#x20;    No manual database insertion is needed.



&#x20; 4. Bootstrap 5 is included via CDN in layout.html. The Pulse theme

&#x20;    from Bootswatch gives the application a clean, professional look.



&#x20; 5. All demos can be performed on localhost without any internet

&#x20;    connection (except for the Bootstrap CDN on first load — after

&#x20;    caching, it works offline too).





================================================================================

&#x20;                       END OF PROJECT ALPHA GUIDE

================================================================================



