"""Redscape New Identity - Synthetic Persona Generator"""
from flask import Blueprint, render_template, request, send_file, jsonify
import requests
import random
import os
from pathlib import Path
from datetime import datetime, timedelta
from PIL import Image
from io import BytesIO
import base64

identity_bp = Blueprint('identity', __name__)

# Gender-specific data pools
FIRST_NAMES_MALE = ['James', 'Robert', 'John', 'Michael', 'David', 'William', 'Richard', 'Joseph', 'Thomas', 'Charles', 'Daniel', 'Matthew', 'Anthony', 'Mark', 'Donald', 'Steven', 'Paul', 'Andrew', 'Joshua', 'Kenneth', 'Kevin', 'Brian', 'George', 'Timothy', 'Ronald', 'Edward', 'Jason', 'Jeffrey', 'Ryan', 'Jacob', 'Gary', 'Nicholas', 'Eric', 'Jonathan', 'Stephen', 'Larry', 'Justin', 'Scott', 'Brandon', 'Benjamin', 'Samuel', 'Frank', 'Gregory', 'Raymond', 'Alexander', 'Patrick', 'Jack', 'Dennis', 'Jerry', 'Tyler']
FIRST_NAMES_FEMALE = ['Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen', 'Nancy', 'Lisa', 'Betty', 'Margaret', 'Sandra', 'Ashley', 'Kimberly', 'Emily', 'Donna', 'Michelle', 'Dorothy', 'Carol', 'Amanda', 'Melissa', 'Deborah', 'Stephanie', 'Rebecca', 'Laura', 'Sharon', 'Cynthia', 'Kathleen', 'Amy', 'Shirley', 'Angela', 'Helen', 'Anna', 'Brenda', 'Pamela', 'Nicole', 'Emma', 'Samantha', 'Katherine', 'Christine', 'Debra', 'Rachel', 'Catherine', 'Carolyn', 'Janet', 'Ruth', 'Maria']
LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores', 'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts', 'Gomez', 'Phillips', 'Evans', 'Turner', 'Diaz', 'Parker', 'Cruz', 'Edwards', 'Collins', 'Reyes', 'Stewart', 'Morris', 'Morales', 'Murphy', 'Cook', 'Rogers', 'Gutierrez', 'Cooper', 'Peterson', 'Bailey', 'Reed', 'Kelly', 'Howard', 'Ramos', 'Kim', 'Cox', 'Ward', 'Richardson', 'Watson', 'Brooks', 'Chavez', 'Wood', 'James', 'Bennett', 'Gray', 'Mendoza', 'Ruiz', 'Hughes', 'Price', 'Alvarez', 'Castillo', 'Sanders', 'Patel', 'Myers', 'Long', 'Ross', 'Foster', 'Jimenez', 'Powell', 'Jenkins', 'Perry', 'Russell', 'Sullivan', 'Bell', 'Coleman', 'Butler', 'Henderson', 'Barnes', 'Gonzales', 'Fisher', 'Vasquez', 'Simmons', 'Romero', 'Jordan', 'Patterson', 'Alexander', 'Hamilton', 'Graham', 'Reynolds', 'Griffin', 'Wallace', 'Moreno', 'West', 'Cole', 'Hayes', 'Bryant', 'Herrera', 'Gibson', 'Ellis', 'Tran', 'Medina', 'Aguilar', 'Stevens', 'Murray', 'Ford', 'Castro', 'Marshall', 'Owens', 'Harrison', 'Fernandez', 'McDonald', 'Woods', 'Washington', 'Kennedy', 'Wells', 'Vargas', 'Henry', 'Chen', 'Freeman', 'Webb', 'Tucker', 'Guzman', 'Burns', 'Crawford', 'Olson', 'Simpson', 'Porter', 'Hunter', 'Gordon', 'Mendez', 'Silva', 'Shaw', 'Snyder', 'Mason', 'Dixon', 'Munoz', 'Hunt']

OCCUPATIONS = ['Software Engineer', 'Data Analyst', 'Marketing Manager', 'Sales Representative', 'Product Manager', 'UX Designer', 'Financial Analyst', 'Human Resources Manager', 'Operations Manager', 'Business Development Manager', 'Project Manager', 'Content Writer', 'Graphic Designer', 'Systems Administrator', 'Network Engineer', 'Database Administrator', 'Cybersecurity Analyst', 'Cloud Architect', 'DevOps Engineer', 'Mobile Developer', 'Web Developer', 'Quality Assurance Engineer', 'Technical Support Specialist', 'IT Consultant', 'Research Scientist', 'Lab Technician', 'Medical Assistant', 'Nurse Practitioner', 'Pharmacy Technician', 'Physical Therapist', 'Occupational Therapist', 'Speech Therapist', 'Dietitian', 'Nutritionist', 'Psychologist', 'Social Worker', 'Counselor', 'Teacher', 'Professor', 'Librarian', 'Archivist', 'Curator', 'Journalist', 'Editor', 'Copywriter', 'Public Relations Specialist', 'Event Planner', 'Real Estate Agent', 'Insurance Agent', 'Financial Advisor', 'Accountant', 'Bookkeeper', 'Auditor', 'Tax Preparer', 'Lawyer', 'Paralegal', 'Legal Assistant', 'Court Reporter', 'Judge', 'Police Officer', 'Detective', 'Firefighter', 'Paramedic', 'Emergency Medical Technician', 'Security Guard', 'Private Investigator', 'Chef', 'Restaurant Manager', 'Bartender', 'Barista', 'Server', 'Host', 'Hotel Manager', 'Concierge', 'Travel Agent', 'Tour Guide', 'Flight Attendant', 'Pilot', 'Aircraft Mechanic', 'Truck Driver', 'Delivery Driver', 'Uber Driver', 'Taxi Driver', 'Bus Driver', 'Train Conductor', 'Ship Captain', 'Mechanic', 'Auto Body Technician', 'Electrician', 'Plumber', 'Carpenter', 'Welder', 'Mason', 'Roofer', 'Landscaper', 'Gardener', 'Farmer', 'Rancher', 'Fisherman', 'Forester', 'Park Ranger', 'Environmental Scientist', 'Geologist', 'Meteorologist', 'Astronomer', 'Physicist', 'Chemist', 'Biologist', 'Zoologist', 'Marine Biologist', 'Botanist', 'Ecologist', 'Anthropologist', 'Archaeologist', 'Historian', 'Sociologist', 'Sociologist', 'Economist', 'Political Scientist', 'Philosopher', 'Linguist', 'Translator', 'Interpreter', 'Writer', 'Author', 'Poet', 'Playwright', 'Screenwriter', 'Producer', 'Director', 'Actor', 'Musician', 'Composer', 'Singer', 'Dancer', 'Choreographer', 'Artist', 'Illustrator', 'Photographer', 'Videographer', 'Filmmaker', 'Filmmaker', 'Animator', 'Game Designer', 'Sound Designer', 'Voice Actor', 'Model', 'Fashion Designer', 'Interior Designer', 'Architect', 'Urban Planner', 'Civil Engineer', 'Mechanical Engineer', 'Electrical Engineer', 'Chemical Engineer', 'Aerospace Engineer', 'Biomedical Engineer', 'Environmental Engineer', 'Industrial Engineer', 'Materials Engineer', 'Nuclear Engineer', 'Petroleum Engineer', 'Mining Engineer', 'Marine Engineer', 'Naval Architect', 'Surveyor', 'Cartographer', 'Drafter', 'CAD Technician', '3D Modeler', 'Technical Writer', 'Instructional Designer', 'Curriculum Developer', 'Corporate Trainer', 'Life Coach', 'Executive Coach', 'Career Counselor', 'Recruiter', 'Talent Acquisition Specialist', 'Compensation Analyst', 'Benefits Administrator', 'Payroll Specialist', 'Office Manager', 'Administrative Assistant', 'Executive Assistant', 'Virtual Assistant', 'Receptionist', 'Data Entry Clerk', 'File Clerk', 'Mail Carrier', 'Postal Worker', 'Courier', 'Messenger', 'Warehouse Worker', 'Inventory Manager', 'Supply Chain Manager', 'Logistics Coordinator', 'Purchasing Agent', 'Buyer', 'Procurement Specialist', 'Vendor Manager', 'Contract Administrator', 'Facilities Manager', 'Property Manager', 'Building Superintendent', 'Maintenance Worker', 'Janitor', 'Housekeeper', 'Maid', 'Laundry Worker', 'Dry Cleaner', 'Tailor', 'Seamstress', 'Cobbler', 'Jeweler', 'Watchmaker', 'Furniture Maker', 'Upholsterer', 'Restorer', 'Conservator', 'Auctioneer', 'Appraiser', 'Insurance Adjuster', 'Claims Examiner', 'Underwriter', 'Loan Officer', 'Mortgage Broker', 'Investment Banker', 'Stockbroker', 'Trader', 'Portfolio Manager', 'Wealth Manager', 'Risk Analyst', 'Compliance Officer', 'Regulatory Affairs Specialist', 'Government Relations Specialist', 'Lobbyist', 'Diplomat', 'Foreign Service Officer', 'Intelligence Analyst', 'Military Officer', 'Enlisted Personnel', 'Veteran Affairs Specialist', 'Nonprofit Director', 'Fundraising Manager', 'Grant Writer', 'Volunteer Coordinator', 'Community Organizer', 'Activist', 'Politician', 'Campaign Manager', 'Pollster', 'Political Consultant', 'Speechwriter', 'Press Secretary', 'Communications Director', 'Spokesperson', 'Brand Manager', 'Creative Director', 'Art Director', 'Media Planner', 'Media Buyer', 'Digital Marketing Specialist', 'SEO Specialist', 'SEM Specialist', 'Social Media Manager', 'Content Strategist', 'Email Marketing Specialist', 'Affiliate Marketing Manager', 'E-commerce Manager', 'Webmaster', 'Domain Investor', 'Cryptocurrency Trader', 'Blockchain Developer', 'Smart Contract Auditor', 'NFT Artist', 'Metaverse Architect', 'Virtual Reality Developer', 'Augmented Reality Developer', 'AI Researcher', 'Machine Learning Engineer', 'NLP Engineer', 'Computer Vision Engineer', 'Robotics Engineer', 'Automation Specialist', 'IoT Developer', 'Embedded Systems Engineer', 'Firmware Engineer', 'Hardware Engineer', 'Chip Designer', 'Semiconductor Engineer', 'Optical Engineer', 'Acoustic Engineer', 'Thermal Engineer', 'Reliability Engineer', 'Safety Engineer', 'Quality Engineer', 'Lean Six Sigma Consultant', 'Process Improvement Specialist', 'Change Management Consultant', 'Management Consultant', 'Strategy Consultant', 'IT Consultant', 'Healthcare Consultant', 'Education Consultant', 'Legal Consultant', 'Financial Consultant', 'HR Consultant', 'Marketing Consultant', 'Operations Consultant', 'Sustainability Consultant', 'Diversity Consultant', 'Ethics Consultant', 'Crisis Management Consultant', 'Reputation Management Consultant', 'Crisis Communications Specialist', 'Public Affairs Specialist', 'Corporate Communications Manager', 'Internal Communications Manager', 'Employee Engagement Manager', 'Corporate Social Responsibility Manager', 'Sustainability Manager', 'Environmental Health and Safety Manager', 'Risk Manager', 'Security Manager', 'Information Security Manager', 'Chief Information Security Officer', 'Chief Technology Officer', 'Chief Information Officer', 'Chief Data Officer', 'Chief Digital Officer', 'Chief Marketing Officer', 'Chief Financial Officer', 'Chief Operating Officer', 'Chief Executive Officer', 'Chief Human Resources Officer', 'Chief Legal Officer', 'General Counsel', 'Corporate Secretary', 'Board Member', 'Investor', 'Venture Capitalist', 'Angel Investor', 'Private Equity Associate', 'Hedge Fund Manager', 'Mutual Fund Manager', 'Pension Fund Manager', 'Insurance Fund Manager', 'Real Estate Investor', 'Property Developer', 'Construction Manager', 'General Contractor', 'Subcontractor', 'Estimator', 'Scheduler', 'Cost Engineer', 'Quantity Surveyor', 'Building Inspector', 'Code Enforcement Officer', 'Zoning Administrator', 'Planning Commissioner', 'Economic Development Director', 'Tourism Director', 'Convention Center Manager', 'Sports Arena Manager', 'Theater Manager', 'Museum Director', 'Gallery Owner', 'Art Dealer', 'Antiques Dealer', 'Rare Book Dealer', 'Stamp Dealer', 'Coin Dealer', 'Wine Merchant', 'Spirits Merchant', 'Beer Distributor', 'Coffee Roaster', 'Tea Merchant', 'Spice Merchant', 'Cheesemonger', 'Butcher', 'Fishmonger', 'Baker', 'Pastry Chef', 'Chocolatier', 'Ice Cream Maker', 'Caterer', 'Personal Chef', 'Nutrition Coach', 'Fitness Trainer', 'Yoga Instructor', 'Pilates Instructor', 'Dance Instructor', 'Martial Arts Instructor', 'Swimming Coach', 'Tennis Coach', 'Golf Pro', 'Ski Instructor', 'Scuba Instructor', 'Rock Climbing Guide', 'Adventure Tour Guide', 'Wilderness Guide', 'Survival Instructor', 'Hunting Guide', 'Fishing Guide', 'Dog Trainer', 'Horse Trainer', 'Riding Instructor', 'Veterinarian', 'Veterinary Technician', 'Animal Behaviorist', 'Zookeeper', 'Aquarist', 'Wildlife Rehabilitator', 'Conservation Officer', 'Animal Control Officer', 'Humane Society Worker', 'Pet Groomer', 'Pet Sitter', 'Dog Walker', 'Pet Store Owner', 'Breeder', 'Kennel Owner', 'Stable Manager', 'Beekeeper', 'Sericulturist', 'Aquaculturist', 'Hydroponic Farmer', 'Vertical Farmer', 'Organic Farmer', 'Biodynamic Farmer', 'Permaculture Designer', 'Seed Saver', 'Heirloom Preservationist', 'Food Scientist', 'Food Safety Inspector', 'Flavor Chemist', 'Sensory Analyst', 'Food Stylist', 'Food Photographer', 'Recipe Developer', 'Test Kitchen Chef', 'Culinary Instructor', 'Food Critic', 'Restaurant Critic', 'Wine Critic','Travel Writer', 'Lifestyle Blogger', 'Fashion Blogger', 'Tech Blogger', 'Parenting Blogger', 'Health Blogger', 'Fitness Blogger', 'Finance Blogger', 'DIY Blogger', 'Food Blogger']

COMPANIES = ['TechCorp Industries', 'Global Solutions Inc', 'Summit Enterprises', 'Horizon Dynamics', 'Nexus Innovations', 'Velocity Systems', 'Apex Strategies', 'Pinnacle Group', 'Meridian Partners', 'Quantum Services', 'Synergy Works', 'Fusion Technologies', 'Catalyst Ventures', 'Momentum Labs', 'Elevate Consulting', 'Blueprint Studios', 'Atlas Logistics', 'Zenith Holdings', 'Odyssey Travel', 'Prism Analytics', 'Vertex Security', 'Axiom Financial', 'Beacon Healthcare', 'Cedar Education', 'Driftwood Media', 'Ember Energy', 'Frost Engineering', 'Granite Construction', 'Ironwood Manufacturing', 'Jasper Communications', 'Kinetic Sports', 'Lunar Entertainment', 'Nova Biotech', 'Orbit Aerospace', 'Polaris Defense', 'Quartz Pharmaceuticals', 'Ridge Mining', 'Solaris Renewables', 'Titan Shipping', 'Umbrella Insurance', 'Vanguard Investments', 'Willow Environmental', 'Xenon Research', 'Yarrow Agriculture', 'Zephyr Aviation']

EDUCATION_LEVELS = ['High School Diploma', 'Associate Degree', 'Bachelor of Arts', 'Bachelor of Science', 'Master of Arts', 'Master of Science', 'MBA', 'PhD', 'MD', 'JD', 'Professional Certificate', 'Trade Certification']

SKILLS_POOL = ['Project Management', 'Data Analysis', 'Public Speaking', 'Strategic Planning', 'Team Leadership', 'Budget Management', 'Contract Negotiation', 'Risk Assessment', 'Quality Assurance', 'Process Improvement', 'Client Relations', 'Stakeholder Management', 'Cross-functional Collaboration', 'Agile Methodologies', 'Scrum Framework', 'Lean Six Sigma', 'Change Management', 'Crisis Management', 'Media Relations', 'Content Strategy', 'Brand Development', 'Market Research', 'Competitive Analysis', 'Financial Modeling', 'Forecasting', 'Business Intelligence', 'KPI Development', 'Performance Metrics', 'Talent Acquisition', 'Employee Development', 'Compensation Strategy', 'Benefits Administration', 'Labor Relations', 'Diversity & Inclusion', 'Workplace Culture', 'Digital Transformation', 'Cloud Migration', 'Cybersecurity Frameworks', 'Network Architecture', 'Database Design', 'API Development', 'Microservices Architecture', 'DevOps Practices', 'CI/CD Pipelines', 'Container Orchestration', 'Infrastructure as Code', 'Test Automation', 'User Experience Design', 'Accessibility Standards', 'Mobile Development', 'Web Development', 'Full Stack Development', 'Machine Learning', 'Natural Language Processing', 'Computer Vision', 'Predictive Analytics', 'Big Data Technologies', 'Data Visualization', 'Business Intelligence Tools', 'ERP Systems', 'CRM Platforms', 'Supply Chain Software', 'Inventory Management', 'Procurement Systems', 'Logistics Optimization', 'Fleet Management', 'Warehouse Operations', 'International Trade', 'Customs Compliance', 'Import/Export Documentation', 'Foreign Exchange', 'Hedging Strategies', 'Mergers & Acquisitions', 'Due Diligence', 'Valuation Modeling', 'Investment Analysis', 'Portfolio Management', 'Retirement Planning', 'Estate Planning', 'Tax Strategy', 'Audit Procedures', 'Forensic Accounting', 'Fraud Investigation', 'Internal Controls', 'Regulatory Compliance', 'Corporate Governance', 'Intellectual Property', 'Patent Law', 'Contract Law', 'Employment Law', 'Environmental Law', 'Immigration Law', 'Real Estate Law', 'Litigation Support', 'Alternative Dispute Resolution', 'Arbitration', 'Mediation', 'Lobbying', 'Grassroots Organizing', 'Policy Analysis', 'Legislative Affairs', 'Campaign Strategy', 'Voter Outreach', 'Public Opinion Research', 'Crisis Communications', 'Reputation Management', 'Thought Leadership', 'Executive Communications', 'Investor Relations', 'Board Relations', 'Shareholder Communications', 'Annual Report Production', 'Sustainability Reporting', 'ESG Strategy', 'Carbon Footprint Analysis', 'Life Cycle Assessment', 'Circular Economy', 'Social Impact Measurement', 'Nonprofit Governance', 'Grant Management', 'Fund Development', 'Donor Relations', 'Volunteer Management', 'Program Evaluation', 'Community Engagement', 'Civic Innovation', 'Social Entrepreneurship', 'Impact Investing', 'Microfinance', 'Community Development', 'Economic Development', 'Workforce Development', 'Career Counseling', 'Job Placement', 'Skills Training', 'Apprenticeship Programs', 'Labor Market Analysis', 'Demographic Research', 'Census Analysis', 'Survey Methodology', 'Statistical Analysis', 'Research Design', 'Academic Publishing', 'Peer Review', 'Curriculum Development', 'Instructional Design', 'E-Learning Development', 'Learning Management Systems', 'Competency Mapping', 'Assessment Design', 'Accreditation Standards', 'Institutional Research', 'Student Affairs', 'Enrollment Management', 'Financial Aid', 'Registrar Services', 'Library Science', 'Information Architecture', 'Knowledge Management', 'Records Management', 'Archival Preservation', 'Digital Preservation', 'Metadata Standards', 'Cataloging', 'Collection Development', 'Reference Services', 'Information Literacy', 'Research Support', 'Scholarly Communication', 'Open Access', 'Data Management', 'Research Data Services', 'GIS Mapping', 'Spatial Analysis', 'Remote Sensing', 'Cartography', 'Geodesy', 'Surveying', 'Photogrammetry', 'Lidar Technology', 'Drone Operations', 'Unmanned Aerial Systems', 'Satellite Imagery', 'GPS Technology', 'Navigation Systems', 'Transportation Planning', 'Traffic Engineering', 'Urban Design', 'Landscape Architecture', 'Historic Preservation', 'Conservation Planning', 'Environmental Planning', 'Regional Planning', 'Comprehensive Planning', 'Zoning Administration', 'Land Use Law', 'Property Law', 'Real Estate Development', 'Property Management', 'Asset Management', 'Facilities Planning', 'Space Planning', 'Move Management', 'Sustainability Consulting', 'Energy Auditing', 'Commissioning', 'Building Diagnostics', 'Forensic Engineering', 'Failure Analysis', 'Root Cause Analysis', 'Reliability Engineering', 'Maintainability Engineering', 'Human Factors Engineering', 'Ergonomics', 'Safety Engineering', 'Industrial Hygiene', 'Toxicology', 'Risk Assessment', 'Emergency Preparedness', 'Business Continuity', 'Disaster Recovery', 'Crisis Response', 'Incident Command', 'Search and Rescue', 'Fire Science', 'Arson Investigation', 'Fire Prevention', 'Fire Protection Engineering', 'Security Engineering', 'Physical Security', 'Electronic Security', 'Access Control', 'Surveillance Systems', 'Intrusion Detection', 'Alarm Systems', 'Security Operations', 'Guard Force Management', 'Executive Protection', 'Close Protection', 'Threat Assessment', 'Vulnerability Assessment', 'Penetration Testing', 'Red Teaming', 'Intelligence Analysis', 'Counterintelligence', 'Counterterrorism', 'Homeland Security', 'Border Security', 'Port Security', 'Aviation Security', 'Maritime Security', 'Critical Infrastructure Protection', 'Cyber Threat Intelligence', 'Digital Forensics', 'Incident Response', 'Malware Analysis', 'Reverse Engineering', 'Exploit Development', 'Vulnerability Research', 'Bug Bounty Hunting', 'Security Research', 'Privacy Engineering', 'Cryptography', 'Blockchain Security', 'Smart Contract Security', 'DeFi Security', 'NFT Security', 'Web3 Security', 'Quantum Computing', 'Quantum Cryptography', 'Post-Quantum Cryptography', 'Homomorphic Encryption', 'Zero-Knowledge Proofs', 'Secure Multi-Party Computation', 'Differential Privacy', 'Federated Learning', 'Edge Computing', 'Fog Computing', 'Distributed Systems', 'Peer-to-Peer Networks', 'Mesh Networks', 'Software-Defined Networking', 'Network Function Virtualization', '5G Technology', '6G Research', 'Terahertz Communications', 'Optical Communications', 'Undersea Cables', 'Satellite Communications', 'Deep Space Communications', 'Radio Astronomy', 'Radar Systems', 'Sonar Systems', 'Electronic Warfare', 'Signals Intelligence', 'Communications Intelligence', 'Imagery Intelligence', 'Measurement and Signature Intelligence', 'Technical Intelligence', 'Human Intelligence', 'Counterintelligence', 'Covert Operations', 'Special Operations', 'Special Forces', 'Psychological Operations', 'Civil Affairs', 'Information Operations', 'Cyber Operations', 'Electronic Warfare', 'Space Operations', 'Nuclear Operations', 'Chemical Operations', 'Biological Operations', 'Radiological Operations', 'Explosive Ordnance Disposal', 'Bomb Disposal', 'Mine Clearance', 'Demining', 'Peacekeeping', 'Peacebuilding', 'Conflict Resolution', 'Mediation', 'Negotiation', 'Diplomacy', 'Track II Diplomacy', 'Public Diplomacy', 'Cultural Diplomacy', 'Sports Diplomacy', 'Science Diplomacy', 'Health Diplomacy', 'Environmental Diplomacy', 'Water Diplomacy', 'Energy Diplomacy', 'Food Diplomacy', 'Trade Diplomacy', 'Investment Diplomacy', 'Development Diplomacy', 'Humanitarian Diplomacy', 'Migration Diplomacy', 'Consular Services', 'Passport Services', 'Visa Services', 'Citizenship Services', 'Notary Services', 'Legalization Services', 'Authentication Services', 'Document Translation', 'Certified Translation', 'Interpretation Services', 'Conference Interpretation', 'Community Interpretation', 'Medical Interpretation', 'Legal Interpretation', 'Sign Language Interpretation', 'Video Relay Services', 'Captioning Services', 'Transcription Services', 'Subtitling Services', 'Dubbing Services', 'Voiceover Services', 'Audio Description', 'Audio Books', 'Podcasting', 'Radio Broadcasting', 'Television Broadcasting', 'Streaming Media', 'Video Production', 'Film Production', 'Documentary Production', 'Animation Production', 'Game Production', 'Interactive Media', 'Virtual Reality', 'Augmented Reality', 'Mixed Reality', 'Extended Reality', 'Spatial Computing', 'Holographic Computing', 'Brain-Computer Interfaces', 'Neural Interfaces', 'Neurotechnology', 'Neuroscience', 'Cognitive Science', 'Psychology', 'Clinical Psychology', 'Counseling Psychology', 'School Psychology', 'Industrial-Organizational Psychology', 'Forensic Psychology', 'Sports Psychology', 'Health Psychology', 'Neuropsychology', 'Geropsychology', 'Pediatric Psychology', 'Rehabilitation Psychology', 'Addiction Psychology', 'Trauma Psychology', 'Disaster Psychology', 'Military Psychology', 'Aviation Psychology', 'Space Psychology', 'Environmental Psychology', 'Consumer Psychology', 'Political Psychology', 'Media Psychology', 'Cyberpsychology', 'Positive Psychology', 'Transpersonal Psychology', 'Existential Psychology', 'Humanistic Psychology', 'Gestalt Psychology', 'Psychoanalysis', 'Psychodynamic Therapy', 'Cognitive Behavioral Therapy', 'Dialectical Behavior Therapy', 'Acceptance and Commitment Therapy', 'Mindfulness-Based Therapy', 'Somatic Experiencing', 'EMDR', 'Hypnotherapy', 'Art Therapy', 'Music Therapy', 'Dance Movement Therapy', 'Drama Therapy', 'Play Therapy', 'Animal-Assisted Therapy', 'Nature-Based Therapy', 'Wilderness Therapy', 'Adventure Therapy', 'Equine-Assisted Therapy', 'Therapeutic Recreation', 'Rehabilitation Counseling', 'Vocational Rehabilitation', 'Psychiatric Rehabilitation', 'Community Mental Health']

CITIES = ['New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX', 'Phoenix, AZ', 'Philadelphia, PA', 'San Antonio, TX', 'San Diego, CA', 'Dallas, TX', 'San Jose, CA', 'Austin, TX', 'Seattle, WA', 'Denver, CO', 'Boston, MA', 'Portland, OR', 'Miami, FL', 'Atlanta, GA', 'Minneapolis, MN', 'Nashville, TN', 'Charlotte, NC']

UNIVERSITIES = ['State University', 'City College', 'Tech Institute', 'National University', 'Metropolitan University', 'Riverside College', 'Lakeside University', 'Northern State University', 'Southern Tech', 'Eastern College', 'Western University', 'Central State University', 'Valley College', 'Coastal University', 'Highland Institute', 'Summit University', 'Pioneer College', 'Heritage University', 'Liberty College', 'Union University']


def _generate_person_data(gender):
    """Generate synthetic identity data based on detected gender"""
    if gender.lower() == 'woman' or gender.lower() == 'female':
        first_name = random.choice(FIRST_NAMES_FEMALE)
    else:
        first_name = random.choice(FIRST_NAMES_MALE)
    
    last_name = random.choice(LAST_NAMES)
    
    # Age between 24 and 58
    age = random.randint(24, 58)
    birth_year = datetime.now().year - age
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    dob = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
    
    occupation = random.choice(OCCUPATIONS)
    
    # Email
    email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{random.choice(['gmail.com', 'outlook.com', 'proton.me', 'yahoo.com', 'icloud.com'])}"
    
    # Phone
    phone = f"+1 ({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
    
    city = random.choice(CITIES)
    
    # Education
    edu_level = random.choice(EDUCATION_LEVELS)
    university = random.choice(UNIVERSITIES)
    grad_year = birth_year + random.randint(22, 26)
    
    # Skills - pick 6-9
    skills = random.sample(SKILLS_POOL, random.randint(6, 9))
    
    # Work history - 2 to 3 jobs
    num_jobs = random.randint(2, 3)
    work_history = []
    current_year = datetime.now().year
    year_pointer = current_year
    
    for i in range(num_jobs):
        job_occupation = occupation if i == 0 else random.choice(OCCUPATIONS)
        company = random.choice(COMPANIES)
        duration = random.randint(2, 5)
        end_year = year_pointer
        start_year = end_year - duration
        year_pointer = start_year
        period = f"{start_year} - {'Present' if i == 0 else end_year}"
        work_history.append({
            'title': job_occupation,
            'company': company,
            'period': period,
            'description': f"Led key initiatives and managed cross-functional teams at {company}."
        })
    
    return {
        'first_name': first_name,
        'last_name': last_name,
        'full_name': f"{first_name} {last_name}",
        'gender': gender,
        'age': age,
        'dob': dob,
        'occupation': occupation,
        'email': email,
        'phone': phone,
        'city': city,
        'education': {
            'level': edu_level,
            'university': university,
            'grad_year': grad_year
        },
        'skills': skills,
        'work_history': work_history,
        'generated_at': datetime.now().isoformat()
    }


def _fetch_and_analyze():
    """Fetch a face from thispersondoesnotexist and assign random gender"""
    url = "https://thispersondoesnotexist.com/"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
    
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    
    img_bytes = resp.content
    
    # Save to temp
    temp_dir = Path.home() / ".redscape" / "data" / "identities"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    img_path = temp_dir / f"face_{timestamp}.jpg"
    
    with open(img_path, 'wb') as f:
        f.write(img_bytes)
    
    # Random gender (thispersondoesnotexist has no API for gender)
    gender = random.choice(['Man', 'Woman'])
    
    # Convert image to base64 for embedding
    img_b64 = base64.b64encode(img_bytes).decode('utf-8')
    
    return {
        'image_path': str(img_path),
        'image_b64': img_b64,
        'gender': gender
    }


@identity_bp.route('/api/identity/generate')
def generate_identity():
    """Generate a new synthetic identity with face + data"""
    try:
        face_data = _fetch_and_analyze()
        person = _generate_person_data(face_data['gender'])
        person['image_b64'] = face_data['image_b64']
        person['image_path'] = face_data['image_path']
        return jsonify(person)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@identity_bp.route('/api/identity/pdf', methods=['POST'])
def generate_pdf():
    """Generate a downloadable PDF CV from identity data"""
    from weasyprint import HTML
    
    data = request.get_json()
    
    html_content = _build_cv_html(data)
    
    pdf_bytes = HTML(string=html_content).write_pdf()
    
    pdf_io = BytesIO(pdf_bytes)
    pdf_io.seek(0)
    
    filename = f"CV_{data.get('full_name', 'identity').replace(' ', '_')}.pdf"
    
    return send_file(
        pdf_io,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


def _build_cv_html(data):
    """Build the CV HTML for PDF rendering"""
    skills_html = ''.join([f'<li>{s}</li>' for s in data.get('skills', [])])
    
    work_html = ''
    for job in data.get('work_history', []):
        work_html += f"""
        <div class="job">
            <div class="job-header">
                <span class="job-title">{job['title']}</span>
                <span class="job-period">{job['period']}</span>
            </div>
            <div class="job-company">{job['company']}</div>
            <div class="job-desc">{job['description']}</div>
        </div>
        """
    
    edu = data.get('education', {})
    img_src = f"data:image/jpeg;base64,{data.get('image_b64', '')}"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        @page {{ size: A4; margin: 2cm; }}
        body {{ font-family: 'Helvetica', 'Arial', sans-serif; color: #222; line-height: 1.5; }}
        .header {{ display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #8b0000; padding-bottom: 15px; margin-bottom: 20px; }}
        .header-left {{ flex: 1; }}
        .header-left h1 {{ font-size: 28px; margin: 0; color: #1a1a1a; }}
        .header-left .title {{ font-size: 16px; color: #8b0000; margin-top: 5px; }}
        .header-right img {{ width: 120px; height: 120px; object-fit: cover; border: 2px solid #8b0000; border-radius: 4px; }}
        .contact {{ margin: 15px 0; font-size: 13px; color: #555; }}
        .contact span {{ margin-right: 15px; }}
        .section {{ margin: 20px 0; }}
        .section h2 {{ font-size: 16px; color: #8b0000; border-bottom: 1px solid #ccc; padding-bottom: 5px; text-transform: uppercase; letter-spacing: 1px; }}
        .job {{ margin: 12px 0; }}
        .job-header {{ display: flex; justify-content: space-between; }}
        .job-title {{ font-weight: bold; font-size: 14px; }}
        .job-period {{ color: #888; font-size: 12px; }}
        .job-company {{ color: #8b0000; font-size: 13px; margin: 2px 0; }}
        .job-desc {{ font-size: 12px; color: #555; }}
        ul.skills {{ columns: 2; list-style: square; padding-left: 20px; font-size: 13px; }}
        .edu {{ font-size: 13px; }}
        .edu .degree {{ font-weight: bold; }}
    </style>
    </head>
    <body>
        <div class="header">
            <div class="header-left">
                <h1>{data.get('full_name', '')}</h1>
                <div class="title">{data.get('occupation', '')}</div>
                <div class="contact">
                    <span>✉ {data.get('email', '')}</span>
                    <span>☎ {data.get('phone', '')}</span><br>
                    <span>⚲ {data.get('city', '')}</span>
                    <span>DOB: {data.get('dob', '')}</span>
                </div>
            </div>
            <div class="header-right">
                <img src="{img_src}" alt="Photo">
            </div>
        </div>
        
        <div class="section">
            <h2>Profile</h2>
            <p>Experienced {data.get('occupation', 'professional')} based in {data.get('city', '')} with a proven track record of delivering results across multiple organizations.</p>
        </div>
        
        <div class="section">
            <h2>Experience</h2>
            {work_html}
        </div>
        
        <div class="section">
            <h2>Education</h2>
            <div class="edu">
                <span class="degree">{edu.get('level', '')}</span> — {edu.get('university', '')} ({edu.get('grad_year', '')})
            </div>
        </div>
        
        <div class="section">
            <h2>Skills</h2>
            <ul class="skills">{skills_html}</ul>
        </div>
    </body>
    </html>
    """
```