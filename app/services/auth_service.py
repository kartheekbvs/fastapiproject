from app.db import supabase
def create_user(data):
    response =( supabase.table("fastsignin").insert(data).execute())
    return response