"""
Database connection utilities for distributed Oracle database architecture.

Django ONLY connects to the central-db (146.190.236.185).
Oracle DB Links on central-db handle internal connections to regional nodes.
All queries use the central connection; Oracle routes them as needed.

DB Link mapping:
- @north_link → 10.110.0.3 (North-DB)
- @south_link → 10.110.0.4 (South-DB)
- @east_link  → 10.110.0.5 (East-DB)
"""

import oracledb
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
dotenv_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path, override=True)


# ========== DATABASE CONNECTION ==========
def get_central_connection():
    """
    Main connection to central headquarters database.
    All queries go through here. Oracle's DB Links handle routing to regional nodes.
    
    Connection details from .env:
    - DB_HOST: Central database IP (146.190.236.185)
    - DB_PORT: Oracle listener port (1521)
    - DB_SERVICE: Oracle service name (XEPDB1)
    - DB_USER: Database user (central_user)
    - DB_PASSWORD: Database password
    """
    db_host = os.getenv("DB_HOST", "MISSING")
    db_port = os.getenv("DB_PORT", "MISSING")
    db_service = os.getenv("DB_SERVICE", "MISSING")
    db_user = os.getenv("DB_USER", "MISSING")
    db_password = os.getenv("DB_PASSWORD", "MISSING")
    
    dsn = f"{db_host}:{db_port}/{db_service}"
    
    print(f"\n[DB CONNECTION DEBUG]")
    print(f"  Host: {db_host}")
    print(f"  Port: {db_port}")
    print(f"  Service: {db_service}")
    print(f"  User: {db_user}")
    print(f"  DSN: {dsn}\n")
    
    try:
        return oracledb.connect(
            user=db_user,
            password=db_password,
            dsn=dsn
        )
    except Exception as e:
        print(f"[DB ERROR] Connection failed!")
        print(f"  Host: {db_host}")
        print(f"  Port: {db_port}")
        print(f"  Service: {db_service}")
        print(f"  User: {db_user}")
        print(f"  DSN: {dsn}")
        raise


# ========== DB LINK HELPERS ==========
def get_db_link(region: str) -> str:
    """
    Get DB Link suffix for a region.
    
    Args:
        region: 'North', 'South', 'East', or None
    
    Returns:
        '@north_link', '@south_link', '@east_link', or ''
    """
    links = {
        'North': '@north_link',
        'South': '@south_link',
        'East': '@east_link'
    }
    return links.get(region, '')


def is_regional(region: str) -> bool:
    """Check if region is one of the distributed nodes"""
    return region in ['North', 'South', 'East']


# ========== QUERY EXECUTION HELPERS ==========
def execute_query(query: str, params: tuple = None):
    """
    Execute a SELECT query and return results as list of dicts.
    
    All queries go through central connection.
    Oracle's DB Links automatically route to regional nodes if needed.
    
    Args:
        query: SQL SELECT query
        params: Query parameters (tuple, optional)
    
    Returns:
        List of dicts (empty list if no results)
    """
    conn = get_central_connection()
    
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Get column names
        if cursor.description:
            columns = [col[0].lower() for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        else:
            results = []
    except Exception as e:
        print(f"Error executing query: {e}")
        results = []
    finally:
        cursor.close()
        conn.close()
    
    return results


def execute_dml(query: str, params: tuple = None) -> bool:
    """
    Execute INSERT / UPDATE / DELETE query and commit.
    
    Args:
        query: SQL DML query
        params: Query parameters (tuple, optional)
    
    Returns:
        True if successful, False if error
    """
    conn = get_central_connection()
    
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error executing DML: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def execute_query_one(query: str, params: tuple = None):
    """
    Execute SELECT and return first result as dict, or None.
    
    Args:
        query: SQL SELECT query
        params: Query parameters (tuple, optional)
    
    Returns:
        Dict or None
    """
    results = execute_query(query, params)
    return results[0] if results else None


def test_connection(region: str = None) -> dict:
    """
    Test connection to a database node.
    
    Args:
        region: 'North', 'South', 'East', or None (for central)
    
    Returns:
        {'connected': bool, 'message': str, 'count': int or None}
    """
    try:
        if region and is_regional(region):
            query = f"SELECT COUNT(*) as cnt FROM Trips{get_db_link(region)}"
        else:
            query = "SELECT COUNT(*) as cnt FROM Tourist_Basic"
        
        result = execute_query_one(query)
        count = result.get('cnt', 0) if result else 0
        
        return {
            'connected': True,
            'message': f'{region or "Central"} database connected successfully',
            'count': count
        }
    except Exception as e:
        return {
            'connected': False,
            'message': f'Error connecting: {str(e)}',
            'count': None
        }

