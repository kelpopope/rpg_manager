# 🛡️ RPG Campaign Manager

> A modern web application for managing tabletop RPG campaigns with real-time character management, inventory tracking, and comprehensive statistics aggregation.

## 📋 Project Overview

**RPG Campaign Manager** is a full-stack web application built with FastAPI and MongoDB that enables Game Masters to:
- Create and manage character profiles with detailed stats
- Track inventory and equipment
- Monitor character health and apply damage/healing
- View comprehensive guild statistics via MongoDB aggregation
- Manage user authentication with secure password hashing
- Organize campaigns and character relationships

**Technology Stack:**
- **Backend:** FastAPI (Python)
- **Database:** MongoDB (NoSQL)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Authentication:** bcrypt (Password hashing)
- **ORM/Validation:** Pydantic
- **Async Driver:** Motor (AsyncIO MongoDB Driver)

**Key Features:**
✅ RESTful API with 10 endpoints  
✅ MongoDB compound indexing for optimization  
✅ Advanced update operators ($inc, $push, $pull, $set)  
✅ Aggregation pipeline for analytics  
✅ Secure authentication system  
✅ Responsive medieval-themed UI  

---

## 🏗️ System Architecture

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Static)                      │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │  index.html  │ dashboard.html │ create.html stats.html │ │
│  │  (Login)     │  (Character    │ (New Hero) (Analytics) │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/JSON
┌──────────────────────────▼──────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ ENDPOINTS (10 Routes)                                   │ │
│  │ • POST   /characters/ (Create)                          │ │
│  │ • GET    /characters/ (Read All)                        │ │
│  │ • PUT    /characters/{id}/damage (Damage)              │ │
│  │ • POST   /characters/{id}/items (Add Item)             │ │
│  │ • GET    /stats/classes (Aggregation)                  │ │
│  │ • DELETE /characters/{id} (Delete)                     │ │
│  │ • POST   /auth/register (Register)                     │ │
│  │ • POST   /auth/login (Login)                           │ │
│  │ • PUT    /characters/{id}/heal (Heal)                  │ │
│  │ • DELETE /characters/{id}/items/{item_name} (Remove)   │ │
│  └─────────────────────────────────────────────────────────┘ │
│                       ↓                                      │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ BUSINESS LOGIC & VALIDATION                             │ │
│  │ • Password hashing (bcrypt)                             │ │
│  │ • Data validation (Pydantic models)                     │ │
│  │ • Business rules enforcement                            │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │ TCP/27017
┌──────────────────────────▼──────────────────────────────────┐
│             MongoDB Database (rpg_database)                 │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ characters   │ users        │ (campaigns - future)     │ │
│  │ Collection   │ Collection   │                          │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Registration/Login Flow**
   ```
   User Input → Validation (Pydantic) → Password Hashing (bcrypt) → MongoDB Storage
   ```

2. **Character Management Flow**
   ```
   Create Form → Character Model → Validation → MongoDB Insert → Return with ID
   ```

3. **Battle System Flow**
   ```
   Damage Request → Validation → $inc Update → MongoDB → Response
   ```

4. **Analytics Flow**
   ```
   Stats Request → Aggregation Pipeline → Group/Sort/Project → JSON Response
   ```

---

## 🗄️ Database Schema

### MongoDB Collections

#### **1. Characters Collection**
```json
{
  "_id": ObjectId("..."),
  "name": "Aragorn",
  "character_class": "Warrior",
  "level": 5,
  "stats": {
    "strength": 15,
    "dexterity": 10,
    "intelligence": 8,
    "hp_current": 45,
    "hp_max": 50
  },
  "inventory": [
    {
      "name": "Iron Sword",
      "type": "Weapon",
      "value": 250,
      "effect_value": 15
    },
    {
      "name": "Healing Potion",
      "type": "Potion",
      "value": 50,
      "effect_value": 25
    }
  ],
  "campaign_id": "64e5f8c9d4e2b9a1c3f4e5g6",
  "user_id": "64e5f8c9d4e2b9a1c3f4e5h7"
}
```

**Field Specifications:**
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `_id` | ObjectId | Unique identifier | Auto-generated |
| `name` | String | Character name | min_length: 2 |
| `character_class` | String | Class type | "Warrior", "Mage", "Rogue", "Cleric" |
| `level` | Integer | Character level | 1 ≤ level |
| `stats.strength` | Integer | Strength attribute | 1-20 |
| `stats.dexterity` | Integer | Dexterity attribute | 1-20 |
| `stats.intelligence` | Integer | Intelligence attribute | 1-20 |
| `stats.hp_current` | Integer | Current health points | ≥ 0 |
| `stats.hp_max` | Integer | Maximum health points | ≥ hp_current |
| `inventory` | Array | Array of items | Max items: unlimited |
| `campaign_id` | String | Parent campaign | Optional |
| `user_id` | String | Owning Game Master | Optional |

#### **2. Users Collection**
```json
{
  "_id": ObjectId("..."),
  "username": "game_master_1",
  "email": "gm@example.com",
  "password_hash": "$2b$12$..."
}
```

**Field Specifications:**
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `_id` | ObjectId | Unique identifier | Auto-generated |
| `username` | String | Login username | min_length: 3, unique |
| `email` | String | Email address | Valid email format |
| `password_hash` | String | Hashed password | bcrypt hash |

#### **3. Inventory Items (Embedded in Character)**
```json
{
  "name": "Iron Sword",
  "type": "Weapon|Potion|Armor|Loot",
  "value": 250,
  "effect_value": 15
}
```

**Item Types:**
- **Weapon**: Offensive items (effect_value = damage bonus)
- **Potion**: Consumables (effect_value = healing amount)
- **Armor**: Defensive items (effect_value = defense bonus)
- **Loot**: Treasure/collectibles (effect_value = optional)

---

## 🔍 MongoDB Queries

### 1. **Create Character**
```javascript
db.characters.insertOne({
  name: "Aragorn",
  character_class: "Warrior",
  level: 1,
  stats: {
    strength: 10,
    dexterity: 10,
    intelligence: 10,
    hp_current: 20,
    hp_max: 20
  },
  inventory: [],
  campaign_id: null,
  user_id: null
})
```

### 2. **Get All Characters**
```javascript
db.characters.find({})
// Returns all characters with converted string IDs
```

### 3. **Apply Damage (Atomic Update with $inc)**
```javascript
db.characters.updateOne(
  { "_id": ObjectId("64e5f8c9d4e2b9a1c3f4e5g6") },
  { "$inc": { "stats.hp_current": -15 } }  // Decrease HP by 15
)
```
**Why $inc?** Atomic operation prevents race conditions in concurrent requests

### 4. **Add Item to Inventory ($push)**
```javascript
db.characters.updateOne(
  { "_id": ObjectId("64e5f8c9d4e2b9a1c3f4e5g6") },
  { 
    "$push": { 
      "inventory": {
        "name": "Iron Sword",
        "type": "Weapon",
        "value": 250,
        "effect_value": 15
      }
    }
  }
)
```
**Why $push?** Safely appends items without retrieving entire array

### 5. **Analytics - Class Statistics (Aggregation Pipeline)**
```javascript
db.characters.aggregate([
  {
    "$group": {
      "_id": "$character_class",
      "average_level": { "$avg": "$level" },
      "total_heroes": { "$sum": 1 },
      "max_strength": { "$max": "$stats.strength" }
    }
  },
  {
    "$sort": { "total_heroes": -1 }
  },
  {
    "$project": {
      "class_name": "$_id",
      "_id": 0,
      "average_level": { "$round": ["$average_level", 1] },
      "total_heroes": 1,
      "max_strength": 1
    }
  }
])
```

**Pipeline Stages:**
1. **$group** - Aggregate by character_class
2. **$sort** - Sort by popularity (total_heroes descending)
3. **$project** - Reshape output fields

### 6. **Heal Character ($set)**
```javascript
db.characters.updateOne(
  { "_id": ObjectId("64e5f8c9d4e2b9a1c3f4e5g6") },
  { "$set": { "stats.hp_current": 50 } }  // Set exact value
)
```
**Why $set?** When updating with calculated values (after applying capped healing)

### 7. **Remove Item from Inventory ($pull)**
```javascript
db.characters.updateOne(
  { "_id": ObjectId("64e5f8c9d4e2b9a1c3f4e5g6") },
  { "$pull": { "inventory": { "name": "Iron Sword" } } }
)
```
**Why $pull?** Removes specific array elements matching criteria

### 8. **Delete Character**
```javascript
db.characters.deleteOne(
  { "_id": ObjectId("64e5f8c9d4e2b9a1c3f4e5g6") }
)
```

### 9. **Find User by Username (Auth)**
```javascript
db.users.findOne({ "username": "game_master_1" })
```

### 10. **Check Duplicate User (Validation)**
```javascript
db.users.findOne({ "username": username })
// Returns null if user doesn't exist
```

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### 1. **Create Character**
```http
POST /characters/
Content-Type: application/json

{
  "name": "Aragorn",
  "character_class": "Warrior",
  "level": 1,
  "stats": {
    "strength": 15,
    "dexterity": 10,
    "intelligence": 8,
    "hp_current": 20,
    "hp_max": 20
  },
  "inventory": []
}
```
**Response:** `200 OK`
```json
{
  "name": "Aragorn",
  "character_class": "Warrior",
  "level": 1,
  "stats": { ... },
  "inventory": []
}
```

### 2. **Get All Characters**
```http
GET /characters/
```
**Response:** `200 OK`
```json
[
  {
    "_id": "64e5f8c9d4e2b9a1c3f4e5g6",
    "name": "Aragorn",
    "character_class": "Warrior",
    "level": 5,
    "stats": { ... },
    "inventory": [ ... ]
  },
  ...
]
```

### 3. **Apply Damage**
```http
PUT /characters/{id}/damage
Content-Type: application/json

?damage=15
```
**Response:** `200 OK`
```json
{
  "message": "Character received 15 damage"
}
```

**Error Responses:**
- `400 Bad Request` - Damage ≤ 0
- `404 Not Found` - Character not found
- `200 OK` - Character already dead

### 4. **Add Item to Inventory**
```http
POST /characters/{id}/items
Content-Type: application/json

{
  "name": "Iron Sword",
  "type": "Weapon",
  "value": 250,
  "effect_value": 15
}
```
**Response:** `200 OK`
```json
{
  "message": "Item Iron Sword added to backpack!"
}
```

**Error Responses:**
- `404 Not Found` - Character not found

### 5. **Get Class Statistics**
```http
GET /stats/classes
```
**Response:** `200 OK`
```json
[
  {
    "class_name": "Warrior",
    "average_level": 4.5,
    "total_heroes": 8,
    "max_strength": 18
  },
  {
    "class_name": "Mage",
    "average_level": 3.2,
    "total_heroes": 5,
    "max_strength": 12
  }
]
```

### 6. **Delete Character**
```http
DELETE /characters/{id}
```
**Response:** `200 OK`
```json
{
  "message": "Character deleted permanently"
}
```

**Error Responses:**
- `404 Not Found` - Character not found

### 7. **User Registration**
```http
POST /auth/register?password=SecurePass123
Content-Type: application/json

{
  "username": "game_master_1",
  "email": "gm@example.com"
}
```
**Response:** `200 OK`
```json
{
  "message": "User successfully registered!"
}
```

**Error Responses:**
- `400 Bad Request` - User already exists

### 8. **User Login**
```http
POST /auth/login?username=game_master_1&password=SecurePass123
```
**Response:** `200 OK`
```json
{
  "message": "Login successful! Welcome, Game Master."
}
```

**Error Responses:**
- `400 Bad Request` - Invalid username or password

### 9. **Heal Character**
```http
PUT /characters/{id}/heal
?amount=25
```
**Response:** `200 OK`
```json
{
  "message": "Hero healed. Current health: 45"
}
```

**Error Responses:**
- `404 Not Found` - Character not found

**Note:** Healing is capped at max_hp (excess healing is ignored)

### 10. **Remove Item from Inventory**
```http
DELETE /characters/{id}/items/{item_name}
```
**Response:** `200 OK`
```json
{
  "message": "Item Iron Sword removed from inventory"
}
```

---

## ⚡ Indexing and Optimization Strategy

### 1. **Compound Index (Characters Collection)**
```javascript
db.characters.createIndex([("name", 1), ("character_class", 1)])
```

**Purpose:** Optimize queries filtering by both name AND class simultaneously

**Created in:** `startup_db_client()` event handler

**Performance Impact:**
- **Before Index:** Full collection scan O(n)
- **After Index:** Index-based lookup O(log n)
- **Use Case:** Finding characters by name+class combination

### 2. **Why This Index?**
```javascript
// Query that benefits from index:
db.characters.find({ 
  "name": "Aragorn", 
  "character_class": "Warrior" 
})
```

### 3. **Additional Recommended Indexes** (Future Implementation)

#### **User Authentication Index**
```javascript
db.users.createIndex([("username", 1)], { unique: true })
```
- **Benefit:** O(log n) lookup during login
- **Uniqueness:** Prevents duplicate usernames

#### **Campaign Lookup Index**
```javascript
db.characters.createIndex([("campaign_id", 1)])
```
- **Benefit:** Fast retrieval of all characters in a campaign
- **Pattern:** Common for filtering by campaign

#### **User Ownership Index**
```javascript
db.characters.createIndex([("user_id", 1)])
```
- **Benefit:** Get all characters owned by a Game Master
- **Pattern:** Common for user dashboard

### 4. **Query Optimization Techniques**

| Optimization | Implementation | Benefit |
|--------------|-----------------|---------|
| **Compound Index** | `[name, character_class]` | Supports multi-field WHERE clauses |
| **Atomic Updates** | `$inc`, `$push`, `$pull` | Avoids read-modify-write race conditions |
| **Projection** | Select only needed fields | Reduces network transfer |
| **Aggregation Pipeline** | Multi-stage processing | Efficient server-side analytics |
| **Connection Pooling** | Motor AsyncIOMotorClient | Concurrent request handling |

### 5. **Performance Metrics**

```
Startup: Compound index created on (name, character_class)
Expected Query Speed: < 10ms for character lookups
Concurrent Connections: Handled by Motor async driver
Database Size: Scales efficiently for 1000+ characters
```

---

## 👥 Student Contributions

### Project Structure

This project demonstrates comprehensive full-stack development covering:
- **Backend Architecture** - FastAPI RESTful API design
- **Database Design** - MongoDB schema and normalization
- **Authentication** - Secure user management with bcrypt
- **Advanced Updates** - MongoDB operators ($inc, $push, $pull, $set)
- **Aggregation** - Server-side data analytics pipeline
- **Frontend** - Interactive web interface with vanilla JavaScript
- **DevOps** - Database indexing and optimization

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MongoDB 4.4+
- pip package manager

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd rpg_manager

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows

# Install dependencies
pip install fastapi motor pydantic passlib python-multipart email-validator

# Start MongoDB
mongod

# Run the application
uvicorn main:app --reload
```

### Access the Application
- **Frontend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs (Swagger UI)

---

## 📚 Project Files

```
rpg_manager/
├── main.py              # FastAPI application & endpoints
├── models.py            # Pydantic data models
├── README.md            # This file
├── static/
│   ├── index.html       # Login/Registration page
│   ├── dashboard.html   # Character management hub
│   ├── create.html      # New character form
│   └── stats.html       # Analytics/Statistics page
└── __pycache__/         # Python cache
```

---

## 🔐 Security Considerations

1. **Password Storage:** bcrypt hashing with automatic salt generation
2. **Input Validation:** Pydantic model validation on all inputs
3. **Error Messages:** Generic messages for auth failures (no username enumeration)
4. **Database:** Local MongoDB (production: add SSL/TLS)
5. **Future:** JWT tokens, rate limiting, CORS configuration

---

**Last Updated:** January 2026  
