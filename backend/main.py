# main.py
from fastapi import FastAPI
import sys
import os
from fastapi.middleware.cors import CORSMiddleware
sys.path.append(os.path.join(os.path.dirname(__file__)))
from app.routers.recommender import router

##Fastapi
app = FastAPI()

<<<<<<< HEAD

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

=======
>>>>>>> f063e3eb99d4db8be0eac97f67918a1e0fddf3ca
# Inclure les routeurs
app.include_router(router, tags=["recommender"])


@app.get("/")
def read_root_api():
    return {"message": "Bienvenue sur l'API de recommandation de films!"}
 

