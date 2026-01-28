from fastapi import FastAPI, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from models import Character, Item, Stats, User 
from passlib.context import CryptContext 
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

app = FastAPI(title="RPG Campaign Manager")
# Mount the static files folder (html, css, js)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Main page - redirects to index.html
@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

# Configuration for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function: encrypt password
def get_password_hash(password):
    return pwd_context.hash(password)

# Function: verify password (compare what user entered with what is in the DB)
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Database connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.rpg_database

# --- STARTUP AND INDEXES (6 points) ---
@app.on_event("startup")
async def startup_db_client():
    # Creating a Compound Index.
    # This will speed up the search if we look for a character by Name and Class simultaneously.
    await db.characters.create_index([("name", 1), ("character_class", 1)])
    print("MongoDB Indexes Created!")

@app.get("/")
async def root():
    return {"message": "RPG System Online"}

# --- ENDPOINT 1: Create Character (Create) ---
@app.post("/characters/", response_model=Character)
async def create_character(character: Character):
    character_dict = character.dict()
    
    # Write to MongoDB
    new_character = await db.characters.insert_one(character_dict)
    
    # MongoDB returned the ID of the created object, but we don't necessarily need to return it yet
    return character

# --- ENDPOINT 2: Get all characters (Read List) ---
@app.get("/characters/")
async def get_characters():
    characters = []
    # Search for everyone in the collection and convert IDs to strings (to avoid errors)
    cursor = db.characters.find({})
    async for document in cursor:
        document["_id"] = str(document["_id"]) # Important!
        characters.append(document)
    return characters

# --- ENDPOINT 3: Receive Damage (Advanced Update: $inc) ---
@app.put("/characters/{id}/damage")
async def take_damage(id: str, damage: int):
    # Business Logic: Cannot deal negative damage
    if damage <= 0:
        raise HTTPException(status_code=400, detail="Damage must be greater than 0")

    # Search for character
    char = await db.characters.find_one({"_id": ObjectId(id)})
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Business Logic: Check if they are alive
    if char["stats"]["hp_current"] <= 0:
         return {"message": "Character is already dead..."}

    # ADVANCED UPDATE: Using $inc to decrease health atomically
    await db.characters.update_one(
        {"_id": ObjectId(id)},
        {"$inc": {"stats.hp_current": -damage}} # Decrease hp_current
    )
    
    return {"message": f"Character received {damage} damage"}

# --- ENDPOINT 4: Find Item (Advanced Update: $push) ---
@app.post("/characters/{id}/items")
async def add_item(id: str, item: Item):
    # ADVANCED UPDATE: Using $push to add an object to the inventory array
    result = await db.characters.update_one(
        {"_id": ObjectId(id)},
        {"$push": {"inventory": item.dict()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Character not found")
        
    return {"message": f"Item {item.name} added to backpack!"}

# --- ENDPOINT 5: Server Statistics (Aggregation - 10 points) ---
@app.get("/stats/classes")
async def get_class_stats():
    # Pipeline is a data processing conveyor
    pipeline = [
        # 1. $match: (Optional) We could filter only living ones, but let's take all
        
        # 2. $group: Group characters by their class (Warrior, Mage...)
        {
            "$group": {
                "_id": "$character_class",             # Group by field character_class
                "average_level": {"$avg": "$level"},   # Calculate average level
                "total_heroes": {"$sum": 1},           # Count number of heroes
                "max_strength": {"$max": "$stats.strength"} # Find the strongest one
            }
        },
        
        # 3. $sort: Sort by number of heroes (from popular to rare)
        {
            "$sort": {"total_heroes": -1}
        },
        
        # 4. $project: Nicely rename fields for output (not required, but useful)
        {
            "$project": {
                "class_name": "$_id",
                "_id": 0,
                "average_level": {"$round": ["$average_level", 1]}, # Round to 1 decimal place
                "total_heroes": 1,
                "max_strength": 1
            }
        }
    ]
    
    # Run aggregation
    results = await db.characters.aggregate(pipeline).to_list(length=None)
    return results

# --- ENDPOINT 6: Delete Character (Completing CRUD) ---
@app.delete("/characters/{id}")
async def delete_character(id: str):
    result = await db.characters.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
         raise HTTPException(status_code=404, detail="Character not found")
    return {"message": "Character deleted permanently"}

# --- ENDPOINT 7: Registration (Security - 4 points) ---
@app.post("/auth/register")
async def register(user: User, password: str):
    # 1. Check if such a user already exists
    existing_user = await db.users.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this name already exists")
    
    # 2. Prepare data
    user_dict = user.dict()
    # IMPORTANT: Encrypt password before saving!
    user_dict["password_hash"] = get_password_hash(password)
    
    # 3. Save to MongoDB
    await db.users.insert_one(user_dict)
    
    return {"message": "User successfully registered!"}

# --- ENDPOINT 8: Login ---
@app.post("/auth/login")
async def login(username: str, password: str):
    # 1. Find user by name
    user = await db.users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    # 2. Verify password (compare entered with encrypted in DB)
    if not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    # If everything is OK - let them in
    return {"message": "Login successful! Welcome, Game Master."}

# --- ENDPOINT 9: Healing (Business Logic + Update) ---
@app.put("/characters/{id}/heal")
async def heal_character(id: str, amount: int):
    # 1. First find the character to know their max health
    char = await db.characters.find_one({"_id": ObjectId(id)})
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    
    current_hp = char["stats"]["hp_current"]
    max_hp = char["stats"]["hp_max"]
    
    # 2. Logic: Cannot heal above maximum
    new_hp = current_hp + amount
    if new_hp > max_hp:
        new_hp = max_hp # Trim excess healing
        
    # 3. Update ($set, since we calculated the exact value)
    await db.characters.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"stats.hp_current": new_hp}}
    )
    
    return {"message": f"Hero healed. Current health: {new_hp}"}

# --- ENDPOINT 10: Remove Item (Advanced Update: $pull) ---
@app.delete("/characters/{id}/items/{item_name}")
async def remove_item(id: str, item_name: str):
    # $pull is MongoDB magic. It finds an element in the array 
    # that matches the condition and removes it.
    result = await db.characters.update_one(
        {"_id": ObjectId(id)},
        {"$pull": {"inventory": {"name": item_name}}}
    )
    
    if result.modified_count == 0:
         return {"message": "Item not found or hero does not exist"}
         
    return {"message": f"Item {item_name} removed from inventory"}