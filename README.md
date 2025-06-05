# QRM Chatbot Knowledge Base

WooCommerce knowledge base crawler for AI-powered customer service chatbots. Extracts product data, categories, and shipping information from WooCommerce sites and stores them in vector databases for semantic search.

## 🚀 Features

- **🔄 Multi-Site Crawling**: Support for multiple WooCommerce stores
- **📦 Product Extraction**: Complete product catalog with variations
- **🗂️ Category Management**: Product categories and hierarchies  
- **🚚 Shipping Data**: Zones, methods, and cost calculations
- **🔍 Vector Search**: ChromaDB for semantic product search
- **🤖 AI-Ready**: OpenAI embeddings for natural language queries
- **📊 Sitemap Integration**: Automatic crawling via Yoast SEO sitemaps

## 📋 Prerequisites

- Python 3.12+
- WooCommerce API credentials
- OpenAI API key
- MySQL (production) or SQLite (development)

## 🛠️ Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-username/qrm-chatbot-knowledge-base.git
cd qrm-chatbot-knowledge-base
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration
```bash
cp .env.example .env
# Edit .env with your credentials
```

## ⚙️ Configuration

### Environment Variables

```bash
# Multi-Site Configuration
SITE_STORE1_URL=https://massloadedvinyl.com.au/
SITE_STORE1_CONSUMER_KEY=ck_your_consumer_key
SITE_STORE1_CONSUMER_SECRET=cs_your_consumer_secret

# Database (MySQL for production)
MYSQL_HOST=localhost
MYSQL_USER=your_mysql_user  
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=chatbot_knowledge_base

# OpenAI for embeddings
OPENAI_API_KEY=sk-your-api-key

# ChromaDB vector storage
CHROMA_PERSIST_DIRECTORY=./data/chroma
```

### WooCommerce API Setup

1. Go to WooCommerce → Settings → Advanced → REST API
2. Create new API key with **Read** permissions
3. Add credentials to `.env` file

## 🚀 Usage

### Basic Crawling
```bash
# Crawl specific site
python main.py --site-name store1

# Custom sitemap URL
python main.py --site-name store1 --sitemap-url "https://site.com/product-sitemap.xml"
```

### Multi-Site Management
```bash
# Crawl multiple sites
python main.py --site-name store1
python main.py --site-name store2
python main.py --site-name store3
```

### Scheduling (Production)
```bash
# Add to crontab for weekly updates
0 2 * * 0 /path/to/venv/bin/python /path/to/crawler/main.py --site-name store1
```

## 📊 Data Storage

### Database Schema
- **Sites**: Store configurations and metadata
- **Products**: Complete product catalog with variations
- **Categories**: Product categorization 
- **Shipping**: Zones, methods, and costs
- **Crawl Logs**: Execution history and statistics

### Vector Embeddings
- **ChromaDB**: Semantic search capabilities
- **OpenAI Embeddings**: Natural language understanding
- **Per-Site Collections**: Isolated data per store

## 🔧 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   WooCommerce   │    │    Crawler       │    │   Knowledge     │
│      API        │───▶│   (Python)       │───▶│     Base        │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                          │
┌─────────────────┐           │                          │
│   Yoast SEO     │───────────┘                          │
│   Sitemap       │                                      │
└─────────────────┘                                      │
                                                         │
┌─────────────────┐    ┌──────────────────┐             │
│     MySQL       │◀───│    SQLAlchemy    │◀────────────┘
│   Database      │    │      ORM         │              
└─────────────────┘    └──────────────────┘              
                                                         
┌─────────────────┐    ┌──────────────────┐             │
│   ChromaDB      │◀───│   OpenAI API     │◀────────────┘
│   Vectors       │    │   Embeddings     │
└─────────────────┘    └──────────────────┘
```

## 📈 Monitoring

### Health Checks
```bash
# Test basic functionality
python test_basic.py

# Check database connection
python -c "from src.storage import DataStorage; print('✅ Database OK')"
```

### Logs
- Crawl execution logs in `logs/`
- Error tracking in database
- Performance metrics per site

## 🔧 Development

### Running Tests
```bash
pytest tests/
```

### Adding New Sites
1. Add environment variables for new site
2. Run crawler with new site name
3. Verify data in database and ChromaDB

### Debugging
```bash
# Debug configuration
python debug_config.py

# Verbose crawling
python main.py --site-name store1 --verbose
```

## 🚀 Deployment

### Production Checklist
- [ ] Use MySQL database
- [ ] Set up secure API credentials
- [ ] Configure automated backups
- [ ] Set up monitoring and alerts
- [ ] Schedule regular crawling
- [ ] Implement log rotation

### Docker Deployment
```bash
# Build image
docker build -t qrm-knowledge-base .

# Run crawler
docker run --env-file .env qrm-knowledge-base python main.py --site-name store1
```

## 🤝 Integration

This knowledge base is designed to work with:
- **[QRM Chatbot API](https://github.com/your-username/qrm-chatbot-api)** - FastAPI backend for chat functionality
- **QRM WordPress Plugin** - Frontend chat widget for WooCommerce sites

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/qrm-chatbot-knowledge-base/issues)
- **Documentation**: [Wiki](https://github.com/your-username/qrm-chatbot-knowledge-base/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/qrm-chatbot-knowledge-base/discussions)