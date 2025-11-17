"""
Vercel Serverless Function Entry Point
"""
from app.main_supabase import app

# Vercel precisa de uma variável chamada 'app' ou 'handler'
handler = app
