⚔️ RPG Campaign Manager
Project Overview
The RPG Campaign Manager is a full-stack web application designed for Game Masters (GMs) to manage player characters in tabletop role-playing games. It allows for real-time tracking of character statistics, inventory management, and provides analytical insights into the hero party. The system is built with a focus on high-performance data handling and a responsive "Dark Fantasy" user interface.

System Architecture
The application follows a classic Client-Server architecture with a focus on asynchronous operations:

Frontend: A responsive web interface built with HTML5, CSS3, and Vanilla JavaScript. It uses the Fetch API to communicate with the backend.

Backend: Developed using FastAPI (Python 3.14.2). It serves as a RESTful API, handling business logic, data validation (Pydantic), and security.

Database: MongoDB serves as the primary NoSQL data store, running on localhost:27017. It was chosen for its flexibility in handling nested data structures like character inventories.

Database Schema Description
The database consists of two main collections:

users: Stores Game Master accounts. Passwords are secured using the bcrypt hashing algorithm (v3.2.0).

characters: The primary data collection.

Embedded Documents: Character stats (HP, Strength, etc.) and the inventory list are embedded within the character document. This ensures that all related data is retrieved in a single read operation, optimizing performance for real-time gameplay.

Referenced Documents: The user_id field acts as a reference to the users collection, linking characters to their respective creators.

MongoDB Queries
The project demonstrates proficiency in advanced MongoDB operators and data manipulation:

Atomic Updates:

$inc: Used to decrease hp_current when a character takes damage, ensuring atomic updates without race conditions.

$push: Used to add new item objects into the inventory array.

$pull: Used to remove items from the array by their unique name.

Data Consistency: A $set operator is used during healing to update health values after validating they do not exceed the maximum (hp_max).

Aggregation Pipeline: A multi-stage pipeline is used for the /stats/classes endpoint:

$group: Groups characters by character_class.

$avg / $max: Calculates average levels and maximum strength per class.

$sort: Orders classes by popularity (total heroes).

$project: Rounds values and renames fields for frontend presentation.

API Documentation
The API is self-documenting via Swagger UI (OpenAPI).

Docs URL: http://127.0.0.1:8000/docs

Key Endpoints:

POST /auth/register: GM registration.

GET /characters/: Retrieve the hero party.

PUT /characters/{id}/damage: Update nested health values.

GET /stats/classes: Retrieve aggregated class analytics.

Indexing and Optimization Strategy
To ensure the application scales efficiently, a Compound Index was implemented:

Index: db.characters.create_index([("name", 1), ("character_class", 1)]).

Strategy: By indexing both name and class, we optimize the most common query patterns. This changes the search complexity from a full collection scan (COLLSCAN) to a fast index scan (IXSCAN), significantly reducing latency as the database grows. The index is initialized automatically during the application startup event.

Contribution of Each Student
[Your Name]: Designed the MongoDB schema, implemented the FastAPI backend logic (including aggregation and security), and developed the interactive "Dark Fantasy" frontend dashboard.

Installation and Setup
Environment: Create a virtual environment using python -m venv venv.

Activation: Run .\venv\Scripts\activate.

Dependencies: Install via pip install fastapi uvicorn motor pydantic email-validator passlib bcrypt==3.2.0.

Run: Execute uvicorn main:app --reload.
