import tkinter as tk
from tkinter import messagebox, ttk
from main import initialize_database, search_jobs, fetch_cities

# Initialize the database
initialize_database()

def create_gui():
    root = tk.Tk()
    root.title("Job Search Application")

    def on_city_search(event):
        query = city_combobox.get()
        if len(query) > 2:
            cities = fetch_cities(query)
            city_combobox["values"] = cities

    def start_job_search():
        job_title = job_title_entry.get()
        location = city_combobox.get()
        include_remote = remote_var.get()

        if not job_title or not location:
            messagebox.showerror("Input Error", "Please fill in both job title and location")
            return

        try:
            # Perform job search and get results directly
            jobs = search_jobs(job_title, location, include_remote)

            # Clear previous results
            results_box.delete('1.0', 'end')
            
            if not jobs:
                results_box.insert('end', "No jobs found matching your criteria.\n")
                return

            # Display results
            for job in jobs:
                try:
                    # Extract job details with proper error handling
                    job_details = (
                        f"{'=' * 80}\n"
                        f"Position: {job['job_title'] if 'job_title' in job else 'No title available'}\n"
                        f"Company: {job['employer_name'] if 'employer_name' in job else 'No company specified'}\n"
                        f"Location: {job['job_city'] if 'job_city' in job else ''} {job['job_state'] if 'job_state' in job else ''}\n"
                        f"Type: {job['job_employment_type'] if 'job_employment_type' in job else 'Not specified'}\n"
                        f"Apply: {job['job_apply_link'] if 'job_apply_link' in job else 'No URL provided'}\n"
                    )

                    # Add description if available
                    if 'job_description' in job and job['job_description']:
                        job_details += f"\nDescription:\n{job['job_description']}\n"

                    # Add benefits if available
                    if 'job_benefits' in job and job['job_benefits']:
                        benefits = ', '.join(job['job_benefits'])
                        job_details += f"\nBenefits: {benefits}\n"

                    # Add salary if available
                    if all(key in job for key in ['job_min_salary', 'job_max_salary']) and job['job_min_salary'] and job['job_max_salary']:
                        job_details += f"\nSalary Range: ${job['job_min_salary']} - ${job['job_max_salary']}\n"

                    job_details += f"\n{'=' * 80}\n\n"
                    
                    results_box.insert('end', job_details)
                except KeyError as e:
                    print(f"Error processing job listing: {e}")
                    continue

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            print(f"Search error: {e}")

    # Create main frame
    main_frame = tk.Frame(root, padx=20, pady=10)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Search frame for input fields
    search_frame = tk.Frame(main_frame)
    search_frame.pack(fill=tk.X, pady=(0, 10))

    # Job Title
    job_frame = tk.Frame(search_frame)
    job_frame.pack(side=tk.LEFT, padx=(0, 10))
    tk.Label(job_frame, text="Job Title:").pack()
    job_title_entry = tk.Entry(job_frame, width=30)
    job_title_entry.pack()

    # Location
    location_frame = tk.Frame(search_frame)
    location_frame.pack(side=tk.LEFT, padx=(0, 10))
    tk.Label(location_frame, text="Location:").pack()
    city_combobox = ttk.Combobox(location_frame, width=28)
    city_combobox.pack()
    city_combobox.set('Enter location')
    city_combobox.bind("<KeyRelease>", on_city_search)

    # Remote checkbox
    remote_var = tk.BooleanVar()
    remote_check = tk.Checkbutton(search_frame, text="Include Remote", variable=remote_var)
    remote_check.pack(side=tk.LEFT, padx=(0, 10))

    # Search button
    search_button = tk.Button(search_frame, text="Search", command=start_job_search, 
                            width=10, bg='#4a90e2', fg='white')
    search_button.pack(side=tk.LEFT, pady=5)

    # Results area
    results_frame = tk.Frame(main_frame)
    results_frame.pack(fill=tk.BOTH, expand=True)
    
    # Results label
    tk.Label(results_frame, text="Job Listings:", font=('Arial', 10, 'bold')).pack(anchor='w')
    
    # Text widget with scrollbar for results
    text_frame = tk.Frame(results_frame)
    text_frame.pack(fill=tk.BOTH, expand=True)
    
    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    results_box = tk.Text(text_frame, height=20, wrap=tk.WORD, 
                         yscrollcommand=scrollbar.set,
                         font=('Arial', 9))
    results_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=results_box.yview)

    # Set initial window size
    root.geometry("800x600")
    root.minsize(600, 400)

    root.mainloop()

if __name__ == "__main__":
    create_gui()