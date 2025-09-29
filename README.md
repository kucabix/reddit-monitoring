# Reddit Agent MVP - FastAPI + React + Shadcn/ui

A modern, mobile-responsive Reddit monitoring application built with FastAPI backend and React frontend using Shadcn/ui components.

## 🚀 Features

- **Mobile-First Design**: Responsive UI that works perfectly on all devices
- **Modern Tech Stack**: FastAPI + React + Next.js + Shadcn/ui + Tailwind CSS
- **Reddit Integration**: Search Reddit posts by keywords and subreddits
- **AI Analysis**: OpenAI-powered relevance scoring and content analysis
- **Google Docs Export**: Export results to Google Docs
- **Real-time Search**: Live search with progress indicators
- **Professional UI**: Beautiful, accessible components with dark/light mode support

## 🏗️ Architecture

```
reddit-agent-mvp/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Pydantic models
│   │   └── core/           # Configuration
│   └── requirements.txt
├── frontend/               # React + Next.js frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── app/           # Next.js app router
│   │   └── lib/           # Utilities
│   └── package.json
└── docker-compose.yml
```

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **Pydantic**: Data validation and serialization
- **PRAW**: Reddit API wrapper
- **OpenAI**: AI analysis and content scoring
- **Google APIs**: Google Docs integration

### Frontend
- **Next.js 14**: React framework with app router
- **Shadcn/ui**: Beautiful, accessible UI components
- **Tailwind CSS**: Utility-first CSS framework
- **TypeScript**: Type-safe development
- **Axios**: HTTP client for API calls

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Environment Variables
Create a `.env` file in the root directory:

```env
# Reddit API
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_user_agent
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Google Docs (optional)
GOOGLE_CREDENTIALS_FILE=path_to_credentials.json
```

### Run with Docker Compose

```bash
# Start both backend and frontend
docker-compose up

# Or run in background
docker-compose up -d
```

### Local Development

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📱 Mobile Responsiveness

The new architecture solves all mobile issues:

- **No Sidebar Scrolling Issues**: Uses modern React components with proper touch handling
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Touch-Friendly**: Shadcn/ui components are optimized for touch devices
- **Fast Performance**: Next.js optimizations and modern React patterns

## 🔧 API Endpoints

### Reddit API
- `POST /api/reddit/search` - Search Reddit posts
- `GET /api/reddit/health` - Check Reddit client status

### Analysis API
- `POST /api/analysis/analyze` - Analyze posts with AI
- `GET /api/analysis/health` - Check OpenAI client status

### Docs API
- `POST /api/docs/export` - Export to Google Docs
- `GET /api/docs/health` - Check Google Docs integration

## 🎨 UI Components

Built with Shadcn/ui for professional, accessible components:

- **Forms**: Input, Textarea, Select, Checkbox
- **Data Display**: Table, Card, Badge, Progress
- **Navigation**: Tabs, Accordion, Dialog
- **Feedback**: Toast, Alert, Loading states
- **Layout**: Responsive grid, mobile navigation

## 🔄 Migration from Streamlit

The new architecture provides:

1. **Better Mobile Experience**: No more scrolling issues
2. **Professional UI**: Modern, accessible design system
3. **Better Performance**: Fast API responses and optimized React
4. **Scalability**: Microservices architecture
5. **Developer Experience**: TypeScript, modern tooling

## 📊 Benefits Over Streamlit

| Feature | Streamlit | FastAPI + React |
|---------|-----------|-----------------|
| Mobile Support | ❌ Poor | ✅ Excellent |
| UI Components | ❌ Limited | ✅ Professional |
| Performance | ❌ Slow | ✅ Fast |
| Customization | ❌ Limited | ✅ Full Control |
| Scalability | ❌ Monolithic | ✅ Microservices |
| Developer Experience | ❌ Basic | ✅ Modern |

## 🚀 Next Steps

1. **Run the application**: `docker-compose up`
2. **Access the app**: http://localhost:3000
3. **API docs**: http://localhost:8000/docs
4. **Configure your API keys** in the `.env` file
5. **Start monitoring Reddit** with the beautiful new interface!

The mobile scrolling issues are completely resolved with this modern architecture! 🎉
