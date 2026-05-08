# Getting Started with MahabharataOS

> An AI-powered pipeline that converts raw thoughts into publish-ready LinkedIn posts without losing your voice.

---

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Node.js 18+ (`node --version`)
- Python 3.10+ (`python --version`)
- Git

### Step 1: Clone & Install Backend

```bash
git clone https://github.com/clowNox/MahabharataOS.git
cd MahabharataOS/backend

# Install Python dependencies
pip install -r requirements.txt

# Create .env file (if needed)
cat > .env << EOF
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
EOF
```

### Step 2: Start Backend Server

```bash
# From backend/ directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend running at `http://localhost:8000`  
✅ API docs at `http://localhost:8000/docs`

### Step 3: Install & Start Frontend

```bash
# From frontend/ directory
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start dev server
npm run dev
```

✅ Frontend running at `http://localhost:3000`

---

## 🎯 First Task: Create & Execute

### 1. Open Dashboard
Navigate to `http://localhost:3000`

### 2. Add Your API Keys
1. Click **Settings** (top-right)
2. Paste your OpenAI API key (minimum required)
3. Save

> 💡 Keys are stored securely in your browser (not sent to server)

### 3. Create a Task
1. Click **"New Task"** or scroll to form
2. Enter a raw thought:
   ```
   Just realized how much better my decision-making got 
   once I stopped overthinking and trusted my gut. 
   Built an entire feature in 2 days this way.
   ```
3. Click **"Submit"**

### 4. Execute the Task
1. Click on your new task in the list
2. Click **"Execute"** button
3. Watch real-time logs as the system:
   - Interprets your intent (CEO Engine)
   - Assesses risk (Risk Engine)
   - Plans delegation (Delegation Engine)
   - Generates drafts (Media Engine)
   - Reviews quality (QA Layer)

### 5. Review Results
- See the generated LinkedIn post options
- View the full execution pipeline
- Click **"Approve"** to save as final output

---

## 📂 Project Structure

```
MahabharataOS/
├── backend/                    # Python FastAPI server
│   ├── app/
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── api/               # API routes
│   │   │   ├── routes.py      # Task & campaign endpoints
│   │   │   ├── character_router.py
│   │   │   └── event_router.py
│   │   ├── engines/           # AI processing engines
│   │   │   ├── ceo_engine_v2.py          # Decision logic
│   │   │   ├── delegation_engine_v2.py   # Task planning
│   │   │   ├── media_agent_v2.py         # Content generation
│   │   │   ├── risk_engine.py            # Risk assessment
│   │   │   ├── orchestrator.py           # Main orchestration
│   │   │   └── ...
│   │   ├── models/            # Data models
│   │   │   ├── domain.py      # Task, Campaign
│   │   │   └── orchestration.py
│   │   ├── db/                # Database layer
│   │   │   ├── task_repo.py   # Task persistence
│   │   │   ├── character_repo.py
│   │   │   └── event_repo.py
│   │   └── services/          # Business logic
│   │       ├── scheduler.py    # Task scheduling
│   │       ├── memory.py       # Chronicle/memory
│   │       └── vault.py        # Key storage
│   ├── requirements.txt
│   ├── standalone_worker.py
│   └── mahabharata.db
│
├── frontend/                   # React/Next.js UI
│   ├── src/
│   │   ├── app/               # Next.js pages
│   │   │   ├── page.tsx       # Dashboard
│   │   │   ├── layout.tsx     # Root layout
│   │   │   ├── tasks/         # Task pages
│   │   │   ├── campaigns/     # Campaign pages
│   │   │   └── settings/      # Settings page
│   │   ├── components/        # React components
│   │   │   ├── task-form.tsx
│   │   │   ├── task-list.tsx
│   │   │   ├── task-detail.tsx
│   │   │   └── ...
│   │   ├── lib/               # Utilities
│   │   │   ├── api.ts         # API client
│   │   │   └── storage.ts     # Local storage
│   │   └── types/             # TypeScript types
│   │       └── index.ts
│   ├── package.json
│   ├── next.config.ts
│   └── tsconfig.json
│
├── GETTING_STARTED.md          # This file
├── FRONTEND_TASKLIST.md        # Frontend roadmap
└── README.md                   # Project overview
```

---

## 🔧 Configuration

### Environment Variables

#### Backend (`.env` in `backend/` directory)
```bash
# LLM API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...
GEMINI_API_KEY=...

# Database (optional)
DATABASE_URL=sqlite:///mahabharata.db

# Server
HOST=0.0.0.0
PORT=8000
```

#### Frontend (`.env.local` in `frontend/` directory)
```bash
# API Server URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Analytics, etc.
NEXT_PUBLIC_ANALYTICS_ID=...
```

---

## 🛠️ Development

### Backend Development

```bash
cd backend

# Install dev dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio  # for testing

# Run with auto-reload
uvicorn app.main:app --reload

# Run tests
pytest

# Check API docs
open http://localhost:8000/docs
```

**Useful Backend Endpoints:**
- `POST /api/tasks` - Create task
- `POST /api/tasks/{id}/execute` - Execute with streaming
- `GET /api/tasks` - List all tasks
- `GET /api/tasks/{id}` - Get task details
- `GET /api/tasks/{id}/latest_run` - Get latest execution
- `POST /api/campaigns/generate` - Generate campaign
- `POST /vault/save` - Store API key

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server with hot reload
npm run dev

# Run linter
npm run lint

# Build for production
npm run build

# Start production server
npm run start
```

**Key Components:**
- `app/page.tsx` - Main dashboard
- `app/tasks/page.tsx` - Task list
- `app/tasks/[id]/page.tsx` - Task detail & execution
- `components/task-form.tsx` - Create task form
- `lib/api.ts` - All API calls

---

## 🧪 Testing

### Manual Testing Checklist

```
☐ Backend
  ☐ Health check: GET /health
  ☐ Create task: POST /api/tasks
  ☐ Execute task: POST /api/tasks/{id}/execute
  ☐ Streaming works: Watch execution logs
  ☐ Error handling: Try with invalid API key

☐ Frontend
  ☐ Pages load: /, /tasks, /settings
  ☐ Form validation: Try empty submit
  ☐ Create task: Submit form
  ☐ Task list: See your task
  ☐ Execute task: Watch logs stream
  ☐ API key storage: Stored in localStorage
  ☐ Error states: Network error handling
  ☐ Mobile: Test on small screen

☐ Integration
  ☐ Create → Execute roundtrip
  ☐ Status updates in real-time
  ☐ Results display correctly
  ☐ Multiple keys work (OpenAI, Anthropic, etc)
```

### Running Tests

```bash
# Frontend tests (coming soon)
cd frontend
npm test

# Backend tests
cd backend
pytest
pytest -v  # verbose
pytest --cov  # coverage
```

---

## 🚢 Deployment

### Backend Deployment (Production)

#### Option 1: Heroku
```bash
heroku create mahabharata-os-api
heroku config:set OPENAI_API_KEY=sk-...
git push heroku main
```

#### Option 2: Docker
```bash
# Build image
docker build -t mahabharata-os-backend ./backend

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  mahabharata-os-backend
```

#### Option 3: AWS/GCP/Azure
- Deploy to Cloud Run, Elastic Beanstalk, App Service
- Use managed databases (PostgreSQL recommended for production)

### Frontend Deployment (Production)

#### Option 1: Vercel (Recommended for Next.js)
```bash
# Connect GitHub repo to Vercel
# Set environment variables:
# NEXT_PUBLIC_API_URL=https://api.yourdomain.com
# Auto-deploys on git push
```

#### Option 2: Netlify
```bash
npm run build
netlify deploy --prod --dir=.next
```

#### Option 3: Docker/Self-hosted
```bash
# From frontend/
npm run build
docker build -t mahabharata-os-frontend .
docker run -p 3000:3000 mahabharata-os-frontend
```

---

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
rm -rf venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Check port
lsof -i :8000  # Kill if needed: kill -9 <PID>
```

### Frontend Won't Load
```bash
# Check Node version
node --version  # Should be 18+

# Clear cache
rm -rf .next node_modules
npm install
npm run dev

# Check API URL
echo $NEXT_PUBLIC_API_URL  # Should be set correctly
```

### API Key Not Working
```bash
# Check in browser DevTools > Application > Local Storage
# Should see: mahabharata_api_keys

# Verify key format:
# OpenAI: sk-...
# Anthropic: sk-ant-...
# Tavily: tvly-...
```

### Streaming Logs Not Showing
```bash
# Check backend logs:
uvicorn app.main:app --reload --log-level=debug

# Check frontend network tab (DevTools)
# Should see EventStream responses

# Verify CORS:
# Backend should have allow_origins=["*"]
```

---

## 📚 API Reference

### Create Task
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "X-OpenAI-Key: sk-..." \
  -d '{
    "title": "LinkedIn Post",
    "original_prompt": "Your raw thought here"
  }'
```

### Execute Task
```bash
curl -X POST http://localhost:8000/api/tasks/{task_id}/execute \
  -H "X-OpenAI-Key: sk-..."
```

### List Tasks
```bash
curl http://localhost:8000/api/tasks
```

### Get Task Details
```bash
curl http://localhost:8000/api/tasks/{task_id}
```

### Full API Documentation
Visit: `http://localhost:8000/docs` (Swagger UI)

---

## 💡 Tips & Best Practices

### Working with the System
1. **Start with simple prompts** - Let the system learn your voice
2. **Review CEO Engine output** - Understand how it interprets your intent
3. **Check risk assessments** - Know what the system flags
4. **Iterate on drafts** - Use multiple options, pick the best
5. **Save API keys** - Avoid re-entering them each time

### Performance
1. **Use shorter prompts** - Faster processing
2. **Batch tasks** - Create multiple tasks, execute later
3. **Schedule campaigns** - Let the system run them autonomously
4. **Monitor logs** - Identify bottlenecks

### Security
1. **Never commit API keys** - Use .env files (add to .gitignore)
2. **Rotate keys regularly** - Update your API keys quarterly
3. **Limit key scope** - Use keys with minimal required permissions
4. **Use HTTPS in production** - Encrypt all traffic
5. **Validate all inputs** - Don't trust user-provided data

---

## 🤝 Contributing

To contribute:

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes and commit: `git commit -m "Add my feature"`
3. Push: `git push origin feature/my-feature`
4. Open a Pull Request
5. Wait for review and merge

**Code Standards:**
- Follow existing code style
- Write tests for new features
- Update documentation
- Keep commits small and focused

---

## 📞 Support

- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions
- **Documentation:** See `README.md` and inline comments
- **API Docs:** `http://localhost:8000/docs`

---

## 📄 License

MIT License - see LICENSE file

---

## 🎯 Next Steps

1. ✅ **Setup complete?** Go to `http://localhost:3000`
2. 🔑 **Add API key** in Settings
3. 📝 **Create your first task**
4. ⚡ **Execute it** and watch it work
5. 🎉 **Celebrate!** You're using MahabharataOS

---

**Happy building! 🚀**
