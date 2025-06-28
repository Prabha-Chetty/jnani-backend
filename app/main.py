from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import auth, students, courses, faculty, users, roles, permissions, events, library, classes, gallery
from app.routes import content as content_routes
from app.db.database import get_database
from app.services.user_service import create_default_admin
import os

app = FastAPI(
    title="Jnani Tuition Classes API",
    description="Backend API for Jnani Tuition Classes website and admin panel",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    db = get_database()
    if db is not None:
        create_default_admin(db)

# Create media directory if it doesn't exist
if not os.path.exists("media"):
    os.makedirs("media")

# Serve static files from the 'media' directory
app.mount("/media", StaticFiles(directory="media"), name="media")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3002", 
        "http://127.0.0.1:3000", 
        "http://127.0.0.1:3002",
        "https://jnanistudycentre.vercel.app",
        "https://jnani-frontend.vercel.app",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Public routes
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(students.router, prefix="/students", tags=["Students"])
app.include_router(courses.router, prefix="/courses", tags=["Courses"])
app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(library.router, prefix="/library", tags=["Library"])
app.include_router(classes.router, prefix="/classes", tags=["Classes"])
app.include_router(gallery.router, prefix="/gallery", tags=["Gallery"])
app.include_router(content_routes.public_router, prefix="/content", tags=["Content"])

# Admin-only routes
app.include_router(content_routes.admin_router, prefix="/admin/content", tags=["Content Management"])
app.include_router(faculty.router, prefix="/admin/faculties", tags=["Faculties"])
app.include_router(users.router, prefix="/admin/users", tags=["Users"])
app.include_router(roles.router, prefix="/admin/roles", tags=["Roles"])

@app.get("/")
async def root():
    return {"message": "Welcome to Jnani Study Centre API"}

@app.get("/health")
async def health_check():
    if get_database() is None:
        raise HTTPException(status_code=503, detail="Database connection failed")
    return {"status": "healthy", "database": "connected"} 