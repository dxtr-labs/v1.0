#!/usr/bin/env python3
"""
Update agent_expectations directly in the database
"""

import sqlite3
import json

def update_agent_in_database():
    """Update the agent_expectations in the SQLite database"""
    print("🔧 UPDATING AGENT IN DATABASE")
    print("=" * 60)
    
    # Try both database locations
    db_paths = [
        r"c:\Users\sugua\Desktop\redo\workflow.db",
        r"c:\Users\sugua\Desktop\redo\backend\workflow.db"
    ]
    
    for db_path in db_paths:
        try:
            print(f"📁 Trying database: {db_path}")
            
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if agents table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%agent%';")
            tables = cursor.fetchall()
            
            print(f"📋 Agent-related tables: {tables}")
            
            if tables:
                table_name = tables[0][0]  # Get the first agent table
                
                # Check the table structure
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                print(f"📊 Table structure:")
                for col in columns:
                    print(f"   {col[1]} ({col[2]})")
                
                # Check for agent_expectations column
                has_expectations = any('expectation' in col[1].lower() for col in columns)
                print(f"📝 Has expectations column: {has_expectations}")
                
                # List current agents
                cursor.execute(f"SELECT * FROM {table_name};")
                agents = cursor.fetchall()
                
                print(f"\n📋 Current agents ({len(agents)}):")
                for i, agent in enumerate(agents):
                    print(f"   Agent {i+1}: {agent}")
                
                if agents and has_expectations:
                    # Find the agent_expectations column index
                    expectations_col_index = None
                    for i, col in enumerate(columns):
                        if 'expectation' in col[1].lower():
                            expectations_col_index = i
                            break
                    
                    if expectations_col_index is not None:
                        # Update the first agent with Roomify context
                        agent_id = agents[0][0]  # Assuming first column is ID
                        
                        roomify_context = """CEO: Pranay
Company: Roomify 
Product: Mobile/web application for room finding and roommate matching
Business: Technology startup in the housing/accommodation sector
Value Proposition: Simplifies the process of finding rooms and compatible roommates
Target Market: Students, young professionals, people relocating
Key Features: Room search, roommate matching, secure communication platform"""

                        expectations_col_name = columns[expectations_col_index][1]
                        
                        print(f"\n📤 Updating agent {agent_id} with Roomify context...")
                        print(f"Column: {expectations_col_name}")
                        
                        cursor.execute(f"UPDATE {table_name} SET {expectations_col_name} = ? WHERE {columns[0][1]} = ?;", 
                                     (roomify_context, agent_id))
                        
                        conn.commit()
                        
                        # Verify the update
                        cursor.execute(f"SELECT {expectations_col_name} FROM {table_name} WHERE {columns[0][1]} = ?;", (agent_id,))
                        updated_expectations = cursor.fetchone()
                        
                        if updated_expectations and 'Roomify' in str(updated_expectations[0]):
                            print("✅ Agent updated successfully!")
                            print(f"New expectations: {str(updated_expectations[0])[:100]}...")
                            conn.close()
                            return True
                        else:
                            print("❌ Update verification failed")
                    else:
                        print("❌ Could not find expectations column index")
                else:
                    print("❌ No agents found or no expectations column")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error with {db_path}: {e}")
    
    return False

def test_updated_agent():
    """Test the updated agent"""
    print(f"\n📧 TESTING UPDATED AGENT")
    print("=" * 60)
    
    import requests
    
    base_url = "http://localhost:8002"
    
    # Login
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "aitest@example.com",
        "password": "testpass123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    session_token = login_response.json().get("session_token")
    headers = {"Cookie": f"session_token={session_token}"}
    
    # Test message
    test_message = """i am ceo pranay, draft a sales pitch email for our app roomify and send to slakshanand1105@gmail.com"""
    
    print(f"📤 Testing: {test_message}")
    
    try:
        response = requests.post(f"{base_url}/api/chat/mcpai",
            json={"message": test_message},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            message = result.get('message', '')
            email_content = result.get('email_content', '')
            
            print(f"\n📧 EMAIL ANALYSIS:")
            print("=" * 40)
            
            content_to_check = email_content or message
            
            has_roomify = 'roomify' in content_to_check.lower()
            has_pranay = 'pranay' in content_to_check.lower()
            has_app_info = 'app' in content_to_check.lower() or 'application' in content_to_check.lower()
            not_generic = 'high-quality solutions for our clients' not in content_to_check
            
            print(f"✅ Contains Roomify: {'YES' if has_roomify else 'NO'}")
            print(f"✅ Contains Pranay: {'YES' if has_pranay else 'NO'}")
            print(f"✅ Has app context: {'YES' if has_app_info else 'NO'}")
            print(f"✅ Not generic template: {'YES' if not_generic else 'NO'}")
            
            success = has_roomify and has_pranay and has_app_info and not_generic
            
            if success:
                print(f"\n🎉 SUCCESS! Email now uses Roomify context!")
                print(f"\n📝 EMAIL PREVIEW:")
                print("-" * 40)
                print(content_to_check[:300])
                print("-" * 40)
            else:
                print(f"\n⚠️ Still needs improvement")
                print(f"Content preview: {content_to_check[:200]}...")
            
            return success
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 DATABASE AGENT UPDATE SESSION")
    print("=" * 70)
    
    # Update agent in database
    update_success = update_agent_in_database()
    
    if update_success:
        print(f"\n🔄 Restarting backend to load updated agent...")
        # Note: User should restart the backend server to reload agent data
        
        # Test the updated agent
        test_success = test_updated_agent()
        
        print(f"\n🏁 FINAL RESULTS:")
        print("=" * 30)
        print(f"Database update: {'✅ SUCCESS' if update_success else '❌ FAILED'}")
        print(f"Email improvement: {'✅ SUCCESS' if test_success else '❌ NEEDS RESTART'}")
        
        if not test_success:
            print(f"\n⚠️ IMPORTANT: Restart the backend server to load updated agent data!")
            print(f"1. Stop the current backend server")
            print(f"2. Run: python main.py")
            print(f"3. Test the email generation again")
        
    else:
        print(f"\n❌ Failed to update agent in database")
