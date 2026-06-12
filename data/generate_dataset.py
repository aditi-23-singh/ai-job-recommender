import pandas as pd
import random
import json

random.seed(42)

COMPANIES = [
    "Google", "Microsoft", "Amazon", "Meta", "Apple", "NVIDIA", "Intel",
    "Qualcomm", "Infosys", "TCS", "Wipro", "HCL Technologies", "Accenture",
    "Samsung R&D", "Texas Instruments", "Broadcom", "Marvell", "Synopsys",
    "Cadence", "Adobe", "Salesforce", "Stripe", "Flipkart", "Swiggy",
    "Zomato", "Razorpay", "PhonePe", "Goldman Sachs", "JPMorgan", "HDFC Bank",
    "ISRO", "DRDO", "L&T Technology Services", "Bosch", "Cognizant",
]

LOCATIONS = [
    "Bangalore, India", "Hyderabad, India", "Pune, India", "Chennai, India",
    "Mumbai, India", "Delhi NCR, India", "Noida, India",
    "San Francisco, CA", "Seattle, WA", "New York, NY",
    "Remote", "Hybrid - Bangalore", "Hybrid - Hyderabad",
]

JOB_TEMPLATES = [
    {
        "title": "Software Development Engineer",
        "industry": "Technology",
        "experience_level": "Mid-level",
        "experience_min": 2, "experience_max": 5,
        "required_skills": ["Python", "Data Structures", "Algorithms", "SQL", "Git"],
        "nice_to_have": ["Docker", "Kubernetes", "AWS"],
        "description": "Design and maintain scalable software systems in an Agile environment. Strong fundamentals in data structures and algorithms required.",
    },
    {
        "title": "Machine Learning Engineer",
        "industry": "Technology",
        "experience_level": "Mid-level",
        "experience_min": 2, "experience_max": 6,
        "required_skills": ["Python", "Machine Learning", "Scikit-learn", "SQL", "Statistics"],
        "nice_to_have": ["PyTorch", "TensorFlow", "MLOps", "Spark", "AWS"],
        "description": "Build production ML systems. Work on feature engineering, model training, evaluation, and deployment.",
    },
    {
        "title": "Deep Learning Research Engineer",
        "industry": "Technology / AI",
        "experience_level": "Senior",
        "experience_min": 3, "experience_max": 8,
        "required_skills": ["Python", "Deep Learning", "PyTorch", "Neural Networks", "NLP"],
        "nice_to_have": ["CUDA", "Transformers", "Reinforcement Learning", "MLOps"],
        "description": "Prototype novel architectures, run large-scale experiments. Distributed training on GPUs highly valued.",
    },
    {
        "title": "Data Engineer",
        "industry": "Technology / Data",
        "experience_level": "Mid-level",
        "experience_min": 2, "experience_max": 5,
        "required_skills": ["Python", "SQL", "Spark", "Airflow", "Data Pipeline"],
        "nice_to_have": ["Kafka", "dbt", "AWS", "Hadoop", "Tableau"],
        "description": "Build and maintain reliable data pipelines. Ensure data quality and performance of data infrastructure.",
    },
    {
        "title": "VLSI Design Engineer",
        "industry": "Semiconductor",
        "experience_level": "Entry/Mid",
        "experience_min": 0, "experience_max": 4,
        "required_skills": ["Verilog", "VLSI", "RTL", "FPGA", "SystemVerilog"],
        "nice_to_have": ["Cadence", "Synopsys", "Timing Analysis", "DFT"],
        "description": "Design and verify digital logic blocks for SoCs. Write RTL, perform synthesis, work with physical design teams.",
    },
    {
        "title": "Embedded Systems Engineer",
        "industry": "Electronics",
        "experience_level": "Mid-level",
        "experience_min": 2, "experience_max": 6,
        "required_skills": ["Embedded Systems", "C++", "RTOS", "Firmware", "Microcontroller"],
        "nice_to_have": ["STM32", "CAN Bus", "I2C", "SPI", "ARM Cortex"],
        "description": "Develop firmware for embedded devices. Write optimised C/C++ for bare-metal and RTOS environments.",
    },
    {
        "title": "GPU Software Engineer",
        "industry": "Technology / HPC",
        "experience_level": "Senior",
        "experience_min": 3, "experience_max": 8,
        "required_skills": ["CUDA", "C++", "GPU Programming", "Python", "Parallel Computing"],
        "nice_to_have": ["OpenCL", "Triton", "Deep Learning", "PyTorch", "Linux"],
        "description": "Write high-performance CUDA kernels. Optimise memory bandwidth and kernel launch overhead for AI workloads.",
    },
    {
        "title": "Backend Software Engineer",
        "industry": "Technology",
        "experience_level": "Mid-level",
        "experience_min": 2, "experience_max": 5,
        "required_skills": ["Python", "REST API", "SQL", "Docker", "Git"],
        "nice_to_have": ["FastAPI", "Django", "Redis", "AWS", "Kubernetes"],
        "description": "Build scalable backend services. Design APIs, optimise database queries, write automated tests.",
    },
    {
        "title": "Full Stack Engineer",
        "industry": "Technology",
        "experience_level": "Mid-level",
        "experience_min": 2, "experience_max": 5,
        "required_skills": ["JavaScript", "React", "Node.js", "SQL", "Git"],
        "nice_to_have": ["TypeScript", "GraphQL", "Docker", "AWS", "CSS"],
        "description": "Own features end-to-end from database to UI. Work in a modern React stack.",
    },
    {
        "title": "DevOps Engineer",
        "industry": "Technology",
        "experience_level": "Senior",
        "experience_min": 3, "experience_max": 7,
        "required_skills": ["Kubernetes", "Docker", "Terraform", "Linux", "CI/CD"],
        "nice_to_have": ["AWS", "Helm", "Prometheus", "Ansible", "Python"],
        "description": "Automate infrastructure provisioning, improve developer experience, ensure reliability at scale.",
    },
    {
        "title": "Data Scientist",
        "industry": "Technology / Finance",
        "experience_level": "Mid-level",
        "experience_min": 1, "experience_max": 5,
        "required_skills": ["Python", "Machine Learning", "Statistics", "SQL", "Pandas"],
        "nice_to_have": ["R", "TensorFlow", "Tableau", "Spark", "NLP"],
        "description": "Turn raw data into business decisions. Own experiments from hypothesis to model deployment.",
    },
    {
        "title": "NLP Engineer",
        "industry": "Technology / AI",
        "experience_level": "Senior",
        "experience_min": 3, "experience_max": 8,
        "required_skills": ["Python", "NLP", "Transformers", "PyTorch", "Machine Learning"],
        "nice_to_have": ["BERT", "LLM", "FastAPI", "MLOps", "Elasticsearch"],
        "description": "Build conversational AI systems. Fine-tune large language models, design RAG pipelines.",
    },
    {
        "title": "Site Reliability Engineer",
        "industry": "Technology",
        "experience_level": "Senior",
        "experience_min": 4, "experience_max": 8,
        "required_skills": ["Linux", "Python", "Kubernetes", "CI/CD", "Monitoring"],
        "nice_to_have": ["Go", "Terraform", "AWS", "Prometheus", "Grafana"],
        "description": "Keep production systems reliable. Automate toil, define SLOs, lead post-mortems.",
    },
    {
        "title": "Quantitative Analyst",
        "industry": "Finance",
        "experience_level": "Mid-level",
        "experience_min": 2, "experience_max": 6,
        "required_skills": ["Python", "Statistics", "Machine Learning", "SQL", "Data Structures"],
        "nice_to_have": ["R", "MATLAB", "Spark", "Deep Learning", "Time Series"],
        "description": "Develop quantitative models for pricing, risk, and alpha generation. Backtest strategies.",
    },
    {
        "title": "Firmware Engineer",
        "industry": "Electronics / IoT",
        "experience_level": "Entry/Mid",
        "experience_min": 0, "experience_max": 4,
        "required_skills": ["Embedded Systems", "C++", "RTOS", "Firmware", "Bluetooth"],
        "nice_to_have": ["STM32", "WiFi", "MQTT", "PCB Design", "Python"],
        "description": "Develop firmware for IoT devices. Work with BLE, WiFi protocols and OTA update mechanisms.",
    },
]

EXTRA_SENTENCES = [
    "We offer competitive compensation and an inclusive culture.",
    "You will work with a world-class engineering team.",
    "Mentorship programs and continuous learning are core to our values.",
    "Flexible work arrangements available.",
    "Regular hackathons and innovation sprints.",
    "Strong growth trajectory with leadership opportunities.",
]

def generate_jobs(n_per_template=35):
    jobs = []
    job_id = 1
    for template in JOB_TEMPLATES:
        for _ in range(n_per_template):
            company  = random.choice(COMPANIES)
            location = random.choice(LOCATIONS)
            remote   = "Remote" in location
            sal_base = random.randint(6, 40) * 100_000

            jobs.append({
                "id":               job_id,
                "title":            template["title"],
                "company":          company,
                "location":         location,
                "industry":         template["industry"],
                "experience_level": template["experience_level"],
                "experience_min":   template["experience_min"],
                "experience_max":   template["experience_max"],
                "required_skills":  "|".join(template["required_skills"]),
                "nice_to_have_skills": "|".join(template["nice_to_have"]),
                "description":      template["description"] + " " + random.choice(EXTRA_SENTENCES),
                "salary_min":       sal_base,
                "salary_max":       int(sal_base * 1.4),
                "job_type":         random.choice(["Full-time", "Full-time", "Full-time", "Contract"]),
                "remote":           remote,
                "source":           "synthetic",
            })
            job_id += 1

    random.shuffle(jobs)
    for i, job in enumerate(jobs):
        job["id"] = i + 1
    return jobs

if __name__ == "__main__":
    jobs = generate_jobs(n_per_template=35)
    df   = pd.DataFrame(jobs)
    df.to_csv("jobs_dataset.csv", index=False)
    print(f"Generated {len(jobs)} jobs → saved to jobs_dataset.csv")
    print(df[["title", "company", "location"]].head(10))