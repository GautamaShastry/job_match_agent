# Job Match & Outreach Agent

An intelligent job matching system that uses AI agents to analyze resumes against job descriptions, compute compatibility scores, and generate personalized outreach materials. Built with smolagents and OpenAI's GPT models.

## 🎯 Features

- **Resume & Job Description Parsing**: Automatically extracts structured information from text-based resumes and job descriptions
- **Intelligent Match Scoring**: Computes compatibility scores (0-1 scale) based on skill overlap and requirements
- **Skill Gap Analysis**: Identifies overlapping skills and missing competencies
- **Personalized Outreach**: Generates tailored recruiter/hiring manager emails
- **Resume Optimization**: Provides concrete suggestions for resume improvements
- **Targeted Bullet Points**: Creates job-specific resume bullets ready for copy-paste
- **Audit Trail**: Maintains a JSONL log of all matching operations

## 📁 Project Structure
```
.
├── agent.py                 # Main agent orchestrator
├── requirements.txt         # Python dependencies
├── Satya_Bulusu_Resume.txt # Sample resume
├── jd.txt                   # Sample job description
├── runs_log.jsonl          # Execution history log
└── tools/                  # Tool modules
    ├── __init__.py
    ├── resume_tools.py     # Resume parsing functionality
    ├── job_tools.py        # Job description parsing
    ├── match_tools.py      # Matching algorithm
    ├── outreach_tools.py   # Email generation
    ├── json_tools.py       # JSON utilities
    └── improved_tools.py   # Advanced features (validation, suggestions)
```

## 🔧 Prerequisites

- Python 3.8+
- OpenAI API key

## 🚀 Setup

1. **Clone the repository**
```bash
   git clone <repository-url>
   cd job-match-agent
```

2. **Install dependencies**
```bash
   pip install -r requirements.txt
```

3. **Configure OpenAI API**
   
   Create a `.env` file in the project root:
```env
   OPENAI_API_KEY=your-openai-api-key-here
```
   
   Or set as environment variable:
```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
```

## 💻 Usage

### Basic Usage

Run the agent with the default resume and job description:
```bash
python agent.py
```

### Using Your Own Files

1. Replace `Satya_Bulusu_Resume.txt` with your resume
2. Replace `jd.txt` with your target job description
3. Run the agent:
```bash
   python agent.py
```

### Output

The agent will provide:

1. **Match Summary**
   - Score (0-1 scale)
   - List of overlapping skills
   - List of missing skills

2. **Detailed Explanation**
   - Human-readable analysis of the match

3. **Resume Optimization Suggestions**
   - Concrete edits to improve alignment
   - Skills to highlight
   - Terminology adjustments

4. **Targeted Resume Bullets**
   - Ready-to-use bullet points tailored to the job

5. **Outreach Email**
   - Personalized email template for recruiters/hiring managers

## 📊 How It Works

The agent follows this workflow:

1. **Parse Resume** → Extract candidate name, skills, and profile
2. **Parse Job Description** → Extract role title, location, required skills
3. **Compute Match** → Calculate skill overlap and gaps
4. **Validate Output** → Normalize and ensure data integrity
5. **Generate Deliverables**:
   - Draft outreach email
   - Explain match results
   - Suggest resume edits
   - Generate targeted bullets
6. **Log Results** → Append to `runs_log.jsonl` for tracking

## 🛠️ Available Tools

### Core Tools
- `parse_resume()` - Extracts structured data from resume text
- `parse_job_description()` - Extracts structured data from job descriptions
- `compute_match()` - Calculates compatibility scores

### Enhancement Tools
- `validate_match_output()` - Ensures data consistency
- `explain_match()` - Generates human-readable explanations
- `suggest_resume_edits()` - Provides tailoring recommendations
- `generate_targeted_bullets()` - Creates job-specific bullet points
- `draft_outreach_email()` - Generates personalized emails
- `log_run()` - Maintains audit trail

## 🎯 Skills Recognition

The system currently recognizes the following technical skills:
- **Languages**: Java, Python, C++, C#, JavaScript, TypeScript, SQL, HTML, CSS
- **Frameworks**: React, Angular, Vue, Spring Boot, Django, Flask, FastAPI, Node.js, Express
- **Databases**: MongoDB, PostgreSQL, MySQL
- **Cloud/DevOps**: Docker, Kubernetes, AWS, GCP, Azure
- **Other**: REST, GraphQL, Microservices

## 📈 Example Output
```
=== Job–Resume Match Summary ===
Match score: 0.71 (0–1 scale)

Overlapping skills:
  - aws
  - docker
  - flask
  - kubernetes
  - python

Missing skills (from job requirements):
  - azure
  - gcp

=== Generated Outreach Email ===
Subject: Interest in Associate AI Engineer

Hi,

I hope you're doing well. My name is Gautama Shastry Bulusu Venkata...
```

## 🔍 Logs

All runs are logged to `runs_log.jsonl` with:
- Timestamp
- Candidate name
- Role title
- Match score
- Skill analysis
- Email preview

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source. Please check the license file for details.

## 🐛 Known Issues

- Skills extraction is currently based on keyword matching
- Limited to English language resumes
- Requires OpenAI API access (costs apply)

## 🚧 Future Enhancements

- [ ] Support for more file formats (PDF, DOCX)
- [ ] Advanced NLP for context-aware skill extraction
- [ ] Cover letter generation
- [ ] Interview preparation suggestions
- [ ] Multi-language support
- [ ] Web interface
- [ ] Batch processing for multiple jobs/resumes

## 📧 Contact

For questions or support, please open an issue in the repository.