# Federal Buyout Calculator

## Overview

A web application for federal employees to evaluate buyout offers against their pension benefits. Users input their salary, years of service, age, and retirement system (FERS/CSRS) to compare lump-sum buyout payments with projected pension income. The calculator handles early retirement penalties, survivor benefit reductions, and state tax implications.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite with custom configuration for Replit integration
- **Routing**: Wouter (lightweight React router)
- **State Management**: TanStack React Query for server state
- **Forms**: React Hook Form with Zod validation
- **UI Components**: shadcn/ui component library built on Radix UI primitives
- **Styling**: Tailwind CSS with custom government-themed color palette
- **Animations**: Framer Motion for result reveals

### Backend Architecture
- **Runtime**: Node.js with Express 5
- **Language**: TypeScript compiled with tsx
- **API Pattern**: REST endpoints with Zod schema validation
- **Storage**: In-memory storage (MemStorage class) - no persistent database required for calculator logic
- **Build**: esbuild for production bundling with selective dependency bundling

### Shared Code
- **Location**: `/shared` directory contains types and API contracts
- **Schema**: Zod schemas define both validation rules and TypeScript types
- **Routes**: Type-safe API route definitions shared between client and server

### Key Design Decisions

1. **No Database Persistence**: Calculator is stateless; all computation happens per-request. Drizzle/Postgres are configured but unused since user data isn't stored.

2. **Type-Safe API Contract**: `shared/routes.ts` defines the complete API contract with Zod schemas, ensuring frontend and backend stay synchronized.

3. **Calculation Logic Server-Side**: Pension calculations (FERS/CSRS multipliers, early retirement penalties, survivor benefits) run on the server to keep business logic centralized.

4. **Component Library**: Using shadcn/ui provides accessible, customizable components without heavy dependencies.

## External Dependencies

### Core Runtime
- **PostgreSQL**: Provisioned but optional; the app uses in-memory storage
- **Environment**: Requires `DATABASE_URL` to be set (Replit auto-provisions)

### Key NPM Packages
- **drizzle-orm / drizzle-kit**: ORM for database schema management (configured but not actively used)
- **zod / drizzle-zod**: Schema validation and type generation
- **@tanstack/react-query**: Async state management
- **framer-motion**: Animation library
- **react-icons**: Social sharing icons

### Fonts (Google Fonts CDN)
- Inter (body text)
- Space Grotesk (headings)
- JetBrains Mono (monospace/numbers)

### Development Tools
- **Vite plugins**: Replit-specific plugins for error overlays and dev banners
- **esbuild**: Production server bundling