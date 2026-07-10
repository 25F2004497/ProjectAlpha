================================================================================
              PROJECT ALPHA — COMPLETE GUIDE & DOCUMENTATION
                   Trekking Management Application
================================================================================

Date Prepared : July 2026
Technology    : Flask | Jinja2 | HTML | CSS | Bootstrap (Pulse Theme) | SQLite
Port          : 8111


================================================================================
 SECTION 1 — DEFAULT LOGIN CREDENTIALS (DEMO ACCOUNTS)
================================================================================

  ROLE            USERNAME           PASSWORD         NOTES
  ──────────────  ─────────────────  ───────────────  ──────────────────────────
  Admin/Overseer  overseer           overseer         Pre-seeded superuser
  Staff/Master    mike_master        password123      Pre-approved staff member
  User/Explorer   john_explorer      password123      Regular trekker account

  * The Overseer account is created automatically when the server boots.
  * Staff and Explorer accounts are seeded via the seed script.
  * New accounts can be registered via the /register page.


================================================================================
 SECTION 2 — PROJECT FOLDER STRUCTURE
================================================================================

  Project_Alpha/
  │
  ├── run_server.py              ← Main entry point. Boots the Flask app.
  │
  ├── database/
  │   └── schema.py              ← SQLAlchemy models (Wanderer, ExpeditionBase,
  │                                 ExpeditionLog). Defines the database tables.
  │
  ├── controllers/
  │   ├── auth.py                ← Blueprint for login, register, logout routes
  │   └── dashboard.py           ← Blueprint for overseer, master, explorer dashboards
  │
  ├── frontend_views/            ← All Jinja2 HTML templates
  │   ├── layout.html            ← Base template (navbar, Bootstrap CDN, block structure)
  │   ├── login.html             ← Login form page
  │   ├── register.html          ← Registration form page
  │   ├── overseer_dash.html     ← Admin dashboard (create treks, manage users)
  │   ├── master_dash.html       ← Staff dashboard (update assigned treks)
  │   └── explorer_dash.html     ← User dashboard (browse & book treks, search)
  │
  ├── public_assets/             ← Static files (CSS, images if any)
  │   └── css/
  │       └── style.css          ← (Optional) Extra styling overrides
  │
  ├── alpha_store_v2.sqlite3     ← SQLite database file (auto-created on first boot)
  │
  └── seed_alpha_v2.py           ← Script to populate demo data into the database


================================================================================
 SECTION 3 — FILE-BY-FILE EXPLANATION
================================================================================

  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  run_server.py  —  THE MAIN ENTRY POINT                                     │
  ├──────────────────────────────────────────────────────────────────────────────┤
  │  This is where everything starts. When you run `python run_server.py`:      │
  │                                                                              │
  │  1. A Flask application object is created.                                  │
  │  2. The template folder is set to `frontend_views/`.                        │
  │  3. The static folder is set to `public_assets/`.                           │
  │  4. The SQLite database path is configured (alpha_store_v2.sqlite3).        │
  │  5. SQLAlchemy is initialised with `db.init_app(app)`.                      │
  │  6. Two Blueprints are registered:                                          │
  │     - auth_bp   (handles /login, /register, /logout)                        │
  │     - dash_bp   (handles /dash/overseer, /dash/master, /dash/explorer)      │
  │  7. On first boot, it checks if the Overseer admin exists. If not, it       │
  │     creates the default admin account automatically.                        │
  │  8. The server starts on http://127.0.0.1:8111                              │
  └──────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  database/schema.py  —  DATABASE MODELS                                     │
  ├──────────────────────────────────────────────────────────────────────────────┤
  │  Defines three SQLAlchemy models that map to SQLite tables:                 │
  │                                                                              │
  │  1. Wanderer (Table: 'wanderers')                                           │
  │     - id            : Primary key (auto-increment)                          │
  │     - alias          : Unique username                                      │
  │     - secret         : Hashed password (scrypt algorithm)                   │
  │     - role_type      : 'explorer', 'master', or 'overseer'                 │
  │     - contact_email  : Optional email field                                 │
  │     - active         : Boolean (False = banned/blacklisted)                 │
  │     - is_approved    : Boolean (staff must be approved by admin)            │
  │     - hash_secret()  : Method to hash a raw password before storing         │
  │     - verify_secret(): Method to check a password against the hash          │
  │                                                                              │
  │  2. ExpeditionBase (Table: 'expeditions')                                   │
  │     - eid            : Primary key                                          │
  │     - title          : Name of the trek/expedition                          │
  │     - locale         : Location/region                                      │
  │     - challenge      : Difficulty level (Easy/Moderate/Hard)                │
  │     - max_wanderers  : Total capacity                                       │
  │     - current_slots  : Remaining available spots                            │
  │     - launch_date    : Start date of the trek                               │
  │     - end_date       : End date of the trek                                 │
  │     - current_phase  : Status (Planning / Open / Closed / Finished)         │
  │     - master_id      : Foreign key → assigned staff member                  │
  │                                                                              │
  │  3. ExpeditionLog (Table: 'expedition_logs')                                │
  │     - log_id         : Primary key                                          │
  │     - wanderer_id    : Foreign key → the user who booked                    │
  │     - expedition_id  : Foreign key → the trek that was booked               │
  │     - recorded_at    : Timestamp of booking                                 │
  │                                                                              │
  │  RELATIONSHIPS:                                                              │
  │     ExpeditionBase.master  → links to the Wanderer who is assigned as staff │
  │     ExpeditionLog.wanderer → links to the Wanderer who made the booking     │
  │     ExpeditionLog.expedition → links to the booked ExpeditionBase           │
  └──────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  controllers/auth.py  —  AUTHENTICATION ROUTES                              │
  ├──────────────────────────────────────────────────────────────────────────────┤
  │  This file handles user authentication. It is registered as a Flask         │
  │  Blueprint named 'auth'.                                                    │
  │                                                                              │
  │  ROUTES:                                                                     │
  │                                                                              │
  │  GET/POST  /login                                                           │
  │    - Displays the login form (GET) or processes login (POST).               │
  │    - On POST: queries Wanderer by alias, verifies password.                 │
  │    - If the account is banned (active=False), shows error.                  │
  │    - If the account is a staff awaiting approval, shows error.              │
  │    - On success: stores w_id and role in Flask session.                     │
  │    - Redirects to the appropriate dashboard based on role.                  │
  │                                                                              │
  │  GET/POST  /register                                                        │
  │    - Displays the registration form (GET) or creates account (POST).        │
  │    - Checks if alias already exists. If yes, shows error.                   │
  │    - Explorer accounts are auto-approved and logged in immediately.         │
  │    - Master (staff) accounts require Overseer approval before login.        │
  │                                                                              │
  │  GET  /logout                                                               │
  │    - Clears the Flask session and redirects to /login.                       │
  └──────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  controllers/dashboard.py  —  DASHBOARD ROUTES (ALL ROLES)                  │
  ├──────────────────────────────────────────────────────────────────────────────┤
  │  This file handles all three role-based dashboards. It is registered as     │
  │  a Blueprint named 'dash' with URL prefix '/dash'.                          │
  │                                                                              │
  │  OVERSEER (ADMIN) ROUTES:                                                    │
  │                                                                              │
  │  GET   /dash/overseer                                                       │
  │    - Fetches all expeditions, all non-overseer users, and all masters.      │
  │    - Renders the admin dashboard with full control panel.                   │
  │                                                                              │
  │  POST  /dash/add_expedition                                                 │
  │    - Creates a new trek/expedition from form data.                          │
  │    - Optionally assigns a staff member (master) to the expedition.          │
  │    - Sets initial phase to 'Open'.                                          │
  │                                                                              │
  │  POST  /dash/approve/<wid>                                                  │
  │    - Approves a pending staff member (sets is_approved = True).             │
  │                                                                              │
  │  POST  /dash/ban/<wid>                                                      │
  │    - Bans/blacklists a user or staff member (sets active = False).          │
  │                                                                              │
  │  MASTER (STAFF) ROUTES:                                                      │
  │                                                                              │
  │  GET   /dash/master                                                         │
  │    - Shows only the expeditions assigned to the logged-in master.           │
  │                                                                              │
  │  POST  /dash/update_exp/<eid>                                               │
  │    - Allows the master to change the trek's phase (Open/Closed/Finished).   │
  │    - Allows the master to modify the available slot count.                  │
  │                                                                              │
  │  EXPLORER (USER) ROUTES:                                                     │
  │                                                                              │
  │  GET   /dash/explorer                                                       │
  │    - Shows all Open expeditions. Supports search by locale (?q=...).        │
  │    - Also shows the user's own booking history (ExpeditionLogs).            │
  │                                                                              │
  │  POST  /dash/join/<eid>                                                     │
  │    - Books the explorer into the expedition.                                │
  │    - Decrements the available slot count by 1.                              │
  │    - Creates an ExpeditionLog record as the booking receipt.                │
  └──────────────────────────────────────────────────────────────────────────────┘


================================================================================
 SECTION 4 — HOW THE DATABASE CONNECTION WORKS
================================================================================

  1. In `database/schema.py`, an SQLAlchemy instance is created:
       db = SQLAlchemy()

  2. In `run_server.py`, the Flask app's configuration is set:
       app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alpha_store_v2.sqlite3'

  3. The db object is then bound to the app:
       db.init_app(app)

  4. When the server boots, `db.create_all()` is called inside an
     `app.app_context()` block. This tells SQLAlchemy to read all the
     Model classes (Wanderer, ExpeditionBase, ExpeditionLog) and create
     the corresponding SQLite tables if they don't already exist.

  5. The database file `alpha_store_v2.sqlite3` is automatically generated
     in the Project_Alpha root directory. You do NOT need to create it
     manually — it is 100% programmatic.

  6. All database operations (queries, inserts, updates) are handled via
     SQLAlchemy's ORM. For example:
       - Wanderer.query.filter_by(alias='overseer').first()  → SELECT query
       - db.session.add(new_object)                          → INSERT
       - db.session.commit()                                 → COMMIT transaction


================================================================================
 SECTION 5 — SETUP INSTRUCTIONS (HOW TO RUN FROM SCRATCH)
================================================================================

  PREREQUISITES:
    - Python 3.10+ installed
    - pip (Python package manager)

  STEP 1: Install required packages
    Open a terminal in the Project_Alpha folder and run:

      pip install flask flask-sqlalchemy werkzeug

  STEP 2: Run the application
    In the same terminal, run:

      python run_server.py

    You should see:
      "Project Alpha Server Booting on port 8111..."
      * Running on http://127.0.0.1:8111

  STEP 3: (Optional) Seed demo data
    To populate dummy users, open a second terminal and run:

      python seed_alpha_v2.py

    This creates the demo accounts listed in Section 1.

  STEP 4: Open your browser
    Navigate to:  http://127.0.0.1:8111

    You will see the login page. Use any of the credentials from Section 1.


================================================================================
 SECTION 6 — PROJECT FLOW (HOW THE APP WORKS END-TO-END)
================================================================================

  ┌────────────────────────────────────────────────────────┐
  │                    APPLICATION FLOW                     │
  └────────────────────────────────────────────────────────┘

  User opens http://127.0.0.1:8111
         │
         ▼
  ┌─── LOGIN PAGE (/login) ───┐
  │  Enter Alias + Secret Key │
  │  Or click "Register"      │
  └───────────┬───────────────┘
              │
    ┌─────────┼──────────────────────┐
    │         │                      │
    ▼         ▼                      ▼
  OVERSEER   MASTER               EXPLORER
  (Admin)    (Staff)              (User/Trekker)
    │         │                      │
    ▼         ▼                      ▼
  /dash/     /dash/                /dash/
  overseer   master               explorer
    │         │                      │
    │         │                      ├── Search open expeditions by locale
    │         │                      ├── Book an expedition (POST /dash/join/<eid>)
    │         │                      └── View booking history
    │         │
    │         ├── View assigned expeditions
    │         └── Update status (Open/Closed) & modify slots
    │
    ├── Create new expeditions (with start + end dates)
    ├── Assign a Master (staff) to any expedition
    ├── Approve pending Master registrations
    ├── Ban/Blacklist any user or staff
    └── View all expeditions, users, and staff


================================================================================
 SECTION 7 — HOW TO PRESENT / DEMO THIS PROJECT
================================================================================

  STEP 1: PREPARATION
    - Make sure Python and the required packages are installed.
    - Delete the old database file (alpha_store_v2.sqlite3) if you want
      a fresh start, or keep it if you've already added test data.
    - Run `python run_server.py` from the Project_Alpha folder.

  STEP 2: SHOW THE LOGIN PAGE
    - Open http://127.0.0.1:8111 in a browser.
    - Point out the Bootstrap-based UI (Pulse theme).
    - Show the login form and the "Register" link.

  STEP 3: DEMO ADMIN FLOW
    - Log in as:  Alias = overseer  |  Secret = overseer
    - On the Overseer Panel, demonstrate:
      a) Creating a new expedition (fill in title, locale, challenge, dates).
      b) Assigning a Master to the expedition using the dropdown.
      c) Viewing the full personnel table with status badges.
      d) Approving a pending staff member (if any exist).
      e) Banning a user by clicking the "Ban" button.
    - Log out.

  STEP 4: DEMO STAFF FLOW
    - Log in as:  Alias = mike_master  |  Secret = password123
    - On the Master Panel, demonstrate:
      a) Viewing the expeditions assigned to this master.
      b) Changing the expedition status (e.g., from Open to Closed).
      c) Modifying the available slot count.
    - Log out.

  STEP 5: DEMO USER FLOW
    - Log in as:  Alias = john_explorer  |  Secret = password123
    - On the Explorer Panel, demonstrate:
      a) Browsing available (Open) expeditions.
      b) Using the search bar to filter by locale.
      c) Clicking "Join" to book an expedition.
      d) Showing the booking appear under "My Logs".
    - Log out.

  STEP 6: DEMO REGISTRATION
    - Click "Register new Identity" on the login page.
    - Create a new Explorer account → show it logs in immediately.
    - Create a new Master account → show the "pending approval" message.
    - Switch to the Overseer and approve the new Master.

  STEP 7: TALK ABOUT ARCHITECTURE
    - Explain the Blueprint-based architecture.
    - Explain how the database is created programmatically (no manual DB).
    - Point out the three SQLAlchemy models and their relationships.
    - Emphasise: NO JavaScript is used for any core functionality.
    - Mention the Bootstrap Pulse theme for the frontend styling.


================================================================================
 SECTION 8 — TECHNOLOGY STACK SUMMARY
================================================================================

  Layer                Technology              Details
  ───────────────────  ──────────────────────  ───────────────────────────────
  Backend              Flask 3.x               Python micro-framework
  Templating           Jinja2                  Server-side rendering
  Frontend Styling     Bootstrap 5 (Pulse)     Bootswatch CDN theme
  Database             SQLite                  File-based, no external server
  ORM                  Flask-SQLAlchemy        Object-Relational Mapping
  Password Hashing     Werkzeug (scrypt)       Secure password storage
  Client-side JS       NONE                    No JavaScript for core logic


================================================================================
 SECTION 9 — IMPORTANT NOTES FOR SUBMISSION
================================================================================

  1. The database (alpha_store_v2.sqlite3) is created PROGRAMMATICALLY
     via db.create_all(). You do NOT use DB Browser or any manual tool.

  2. There is ZERO JavaScript used for core functionality. All form
     submissions, navigation, and data operations are handled entirely
     by Flask routes and Jinja2 templates.

  3. The Overseer (Admin) account is auto-created on first server boot.
     No manual database insertion is needed.

  4. Bootstrap 5 is included via CDN in layout.html. The Pulse theme
     from Bootswatch gives the application a clean, professional look.

  5. All demos can be performed on localhost without any internet
     connection (except for the Bootstrap CDN on first load — after
     caching, it works offline too).


================================================================================
                        END OF PROJECT ALPHA GUIDE
================================================================================
