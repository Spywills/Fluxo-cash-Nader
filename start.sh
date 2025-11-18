#!/bin/bash
uvicorn app.main_supabase:app --host 0.0.0.0 --port ${PORT:-8000}
