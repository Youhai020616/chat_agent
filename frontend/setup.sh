#!/bin/bash

# Frontend Project Setup Script
# SEO & GEO Optimization System - Frontend

set -e

echo "🚀 Starting frontend project setup..."

# Create frontend directory if not exists
mkdir -p frontend
cd frontend

# Initialize Vite + React + TypeScript project
echo "📦 Initializing Vite + React + TypeScript..."
npm create vite@latest . -- --template react-ts -y

# Install core dependencies
echo "📦 Installing core dependencies..."
npm install \
  axios \
  react-router-dom \
  zustand \
  @tanstack/react-query \
  react-hook-form \
  @headlessui/react \
  @heroicons/react \
  recharts \
  reactflow \
  react-i18next \
  i18next \
  clsx \
  date-fns

# Install dev dependencies
echo "📦 Installing dev dependencies..."
npm install -D \
  @types/node \
  @typescript-eslint/eslint-plugin \
  @typescript-eslint/parser \
  eslint \
  eslint-config-prettier \
  eslint-plugin-react \
  eslint-plugin-react-hooks \
  prettier \
  tailwindcss \
  postcss \
  autoprefixer \
  @vitejs/plugin-react \
  vitest \
  @testing-library/react \
  @testing-library/jest-dom \
  @testing-library/user-event \
  husky \
  lint-staged

# Initialize Tailwind CSS
echo "🎨 Setting up Tailwind CSS..."
npx tailwindcss init -p

# Create Tailwind config
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
      },
      animation: {
        'spin-slow': 'spin 3s linear infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
EOF

# Update Vite config
cat > vite.config.ts << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@api': path.resolve(__dirname, './src/api'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@stores': path.resolve(__dirname, './src/stores'),
      '@types': path.resolve(__dirname, './src/types'),
      '@utils': path.resolve(__dirname, './src/utils'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/events': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
EOF

# Create TypeScript config
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    
    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    
    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    
    /* Path mapping */
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@api/*": ["./src/api/*"],
      "@components/*": ["./src/components/*"],
      "@pages/*": ["./src/pages/*"],
      "@hooks/*": ["./src/hooks/*"],
      "@stores/*": ["./src/stores/*"],
      "@types/*": ["./src/types/*"],
      "@utils/*": ["./src/utils/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
EOF

# Create project structure
echo "📁 Creating project structure..."
mkdir -p src/{api,components,pages,hooks,stores,types,utils,styles,i18n,features,streams}
mkdir -p src/api/{services,types}
mkdir -p src/components/{ui,layout,charts,forms}
mkdir -p src/pages/{Dashboard,Analysis,Results,KPI,Settings,Auth}
mkdir -p src/features/{batch-analysis,agent-flow,optimization,reporting}
mkdir -p src/streams/hooks
mkdir -p src/i18n/locales
mkdir -p public/assets
mkdir -p tests

# Create environment files
cat > .env.development << 'EOF'
VITE_API_BASE_URL=http://localhost:8000/v1
VITE_SSE_URL=http://localhost:8000/events
VITE_WS_URL=ws://localhost:8000/ws
EOF

cat > .env.production << 'EOF'
VITE_API_BASE_URL=https://api.seo-geo.com/v1
VITE_SSE_URL=https://api.seo-geo.com/events
VITE_WS_URL=wss://api.seo-geo.com/ws
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
coverage/

# Production
dist/
build/

# Misc
.DS_Store
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*

# Editor
.vscode/
.idea/
*.swp
*.swo
*~

# TypeScript
*.tsbuildinfo
EOF

# Create ESLint config
cat > .eslintrc.json << 'EOF'
{
  "env": {
    "browser": true,
    "es2021": true
  },
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react-hooks/recommended",
    "prettier"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaFeatures": {
      "jsx": true
    },
    "ecmaVersion": 12,
    "sourceType": "module"
  },
  "plugins": ["react", "@typescript-eslint"],
  "rules": {
    "react/react-in-jsx-scope": "off",
    "react/prop-types": "off",
    "@typescript-eslint/explicit-module-boundary-types": "off",
    "@typescript-eslint/no-explicit-any": "warn"
  },
  "settings": {
    "react": {
      "version": "detect"
    }
  }
}
EOF

# Create Prettier config
cat > .prettierrc << 'EOF'
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "arrowParens": "always",
  "endOfLine": "lf"
}
EOF

# Setup Husky for pre-commit hooks
echo "🐺 Setting up Husky..."
npx husky-init && npm install

# Create lint-staged config
cat > .lintstagedrc.json << 'EOF'
{
  "*.{js,jsx,ts,tsx}": ["eslint --fix", "prettier --write"],
  "*.{css,md,json}": ["prettier --write"]
}
EOF

# Update package.json scripts
npx json -I -f package.json -e 'this.scripts["lint"] = "eslint src --ext .ts,.tsx"'
npx json -I -f package.json -e 'this.scripts["format"] = "prettier --write src/**/*.{ts,tsx,css}"'
npx json -I -f package.json -e 'this.scripts["test"] = "vitest"'
npx json -I -f package.json -e 'this.scripts["test:ui"] = "vitest --ui"'
npx json -I -f package.json -e 'this.scripts["test:coverage"] = "vitest --coverage"'
npx json -I -f package.json -e 'this.scripts["type-check"] = "tsc --noEmit"'

# Create basic styles
cat > src/styles/globals.css << 'EOF'
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

@layer base {
  body {
    @apply bg-gray-50 text-gray-900 dark:bg-gray-900 dark:text-gray-100;
  }
}

@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors;
  }
  
  .card {
    @apply bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700;
  }
}
EOF

# Create sample API client
cat > src/api/client.ts << 'EOF'
import axios, { AxiosInstance } from 'axios';

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
EOF

# Create README
cat > README.md << 'EOF'
# SEO & GEO Optimization System - Frontend

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm test
```

## 📁 Project Structure

```
src/
├── api/          # API client and services
├── components/   # Reusable UI components
├── pages/        # Page components
├── features/     # Feature modules
├── hooks/        # Custom React hooks
├── stores/       # Zustand stores
├── types/        # TypeScript types
├── utils/        # Utility functions
├── styles/       # Global styles
└── i18n/         # Internationalization
```

## 🛠 Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand + React Query
- **Routing**: React Router v6
- **Forms**: React Hook Form
- **Charts**: Recharts
- **Testing**: Vitest + React Testing Library

## 📝 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier
- `npm test` - Run tests
- `npm run type-check` - Check TypeScript types

## 🔧 Environment Variables

Create `.env.local` for local development:

```env
VITE_API_BASE_URL=http://localhost:8000/v1
VITE_SSE_URL=http://localhost:8000/events
VITE_WS_URL=ws://localhost:8000/ws
```

## 📚 Documentation

- [Architecture](../docs/architecture/frontend-architecture.md)
- [API Specification](../docs/api/api-specification.md)
EOF

echo "✅ Frontend project setup complete!"
echo ""
echo "Next steps:"
echo "1. cd frontend"
echo "2. npm run dev"
echo "3. Open http://localhost:3000"
echo ""
echo "Happy coding! 🎉"
