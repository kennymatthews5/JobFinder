import requests
import sqlite3
import smtplib
from email.mime.text import MIMEText
import time
from dotenv import load_dotenv 
import os

load_dotenv('/Users/cashken/Desktop/JobFinder/job.env')
GEONAMES_API_URL = os.getenv("GEONAMES_API_URL")
GEONAMES_USERNAME = os.getenv("GEONAMES_USERNAME")
JOB_SEARCH_API_URL = os.getenv("JOB_SEARCH_API_URL")
API_KEY = os.getenv("API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

print(f"GEONAMES_API_URL: {GEONAMES_API_URL}")
print(f"GEONAMES_USERNAME: {GEONAMES_USERNAME}")


headers = {
     "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
}

######Function to Send email Notification

def send_email(job):
    sender_email = SENDER_EMAIL
    receiver_email = RECEIVER_EMAIL
    password = EMAIL_PASSWORD

    subject = f"New Job Alert: {job['title']} at {job['company']}"
    body = f"Location: {job['location']}\n\n{job['description']} \n\nApply here: {job['url']}"

    msg = MIMEText(body)
    msg["Subject"] = subject 
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
        
## Database Initilization 

def initialize_database():
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            description TEXT,
            url TEXT UNIQUE
        ) 
        ''')
    conn.commit()
    conn.close()
  

def insert_job(job):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO jobs (title, company, location, description, url)
            VALUES(?, ?, ?, ?, ? )''', (job["title"], job["company"], job["location"], job["description"], job["url"]))
        conn.commit()

    except sqlite3.IntegrityError:
        # The job already exists in the database
        pass
    except Exception as e:
        print(f"Error inserting job into database: {e}")
    finally:
        conn.close()

##### Search Job Function 

def search_jobs(job_title, location, include_remote=False):
    params = {
        "query": f"{job_title} in {location}",
        "page": 1,
        "num_pages": 1
    }

    jobs = []

    response = requests.get(JOB_SEARCH_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        print("Response Data:", data)  # Print the full response data
        jobs.extend(data.get("data", []))
    else:
        print(f"Error fetching jobs: {response.status_code} - {response.text}")
        return []  # Return an empty list if there's an error

    if include_remote:
        remote_params = {
            "query": job_title,
            "page": 1,
            "num_pages": 1,
            "remote_jobs_only": True
        }
        response = requests.get(JOB_SEARCH_API_URL, headers=headers, params=remote_params)
        if response.status_code == 200:
            data = response.json()
            print("Remote Response Data:", data)  # Print the full remote response data
            jobs.extend(data.get("data", []))
        else:
            print(f"Error fetching remote jobs: {response.status_code} - {response.text}")

    return jobs


def fetch_cities(query):
        # Parameters for the GeoNames API
    params = {
        "q": query,              # The query string to search for cities
        "maxRows": 10,           # Limit the number of cities returned
        "username": GEONAMES_USERNAME,  # Username for authentication
        "type": "json"           # Specify JSON format for the response
    }

    # Make the request to the GeoNames API
    response = requests.get(GEONAMES_API_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        # Extract city information from the response
        cities = [f"{item['name']}, {item.get('adminName1', '')}, {item.get('countryName', '')}" for item in data.get('geonames', [])]
        return cities
    else:
        print(f"Error fetching cities: {response.status_code} - {response.text}")


    response = requests.get(GEONAMES_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        cities = [f"{item['name']}, {item.get('adminName1', '')}, {item.get('countryName', '')}" for item in data.get('geonames', [])]
        return cities
    else:
        print(f"Error fetching cities: {response.status_code}")
        return []
