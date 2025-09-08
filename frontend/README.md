# Frontend Application

React-based frontend for the SEO and GEO optimization multi-agent system.

## Tech Stack

- React (with TypeScript)
- Vite for build tooling
- Tailwind CSS for styling
- Zustand for state management
- WebSocket/SSE for real-time updates

## Directory Structure

```
src/
├── api/               # API client and services
│   ├── client.ts
│   ├── services/
│   └── types/
├── streams/          # SSE/WebSocket real-time communication
├── stores/           # Zustand state management
├── pages/            # Page components
│   ├── Dashboard/
│   ├── Analysis/
│   ├── Results/
│   └── KPI/
├── features/         # Business feature modules
│   ├── batch-analysis/
│   ├── agent-flow/
│   └── optimization/
├── components/       # Reusable UI components
├── hooks/            # Custom React hooks
├── types/           # TypeScript type definitions
├── utils/           # Utility functions
└── i18n/            # Internationalization config
```

## Development

1. Install dependencies:
```bash
npm install
# or use the setup script:
./setup.sh
```

2. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Building

```bash
# Production build
npm run build

# Preview production build
npm run preview
```

## Testing

```bash
# Run unit tests
npm test

# Run tests in watch mode
npm test:watch
```

## Environment Variables

- Copy `.env.development` for local development
- Production deployments use `.env.production`
- See config documentation for available options

## Docker

```bash
# Build container
docker build -t frontend .

# Run container
docker run -p 3000:3000 frontend
```

## Contributing

- Follow the component structure in `src/components`
- Add types for all new code in `src/types`
- Include tests for new features
- Use feature directories for complex functionality
