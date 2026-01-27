# Federal Buyout Calculator

## Overview

A web application for federal employees to evaluate buyout offers against their pension benefits. Users input their salary, years of service, age, and retirement system (FERS/CSRS) to compare lump-sum buyout payments with projected pension income. The calculator handles early retirement penalties, survivor benefit reductions, state tax implications, special provisions for law enforcement/firefighters/air traffic controllers, military buyback credits, and deferred retirement options.

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

5. **Centralized Configuration**: `shared/config.ts` contains all variable rates (tax rates, pension multipliers, severance parameters) with a last-updated date. This makes annual updates simple - just modify one file when new rates are published each October/November.

### Data Update Process

All variable rates are stored in `shared/config.ts`:
- **Tax Rates**: Federal (22%), Social Security (6.2%), Medicare (1.45%), SS wage base ($184,500)
- **Pension Multipliers**: FERS (1.0%/1.1%), CSRS (1.5%/1.75%/2.0%), CSRS max 80%
- **Special Provisions**: LEO/Firefighter/ATC multipliers (1.7% first 20 years, 1.0% thereafter)
- **Military Buyback**: 3% deposit rate for buying back military service time
- **Early Retirement**: 5% penalty per year under MRA
- **Survivor Benefits**: Partial (5%), Full (10%) reduction
- **Severance**: OPM formula parameters
- **Data Sources**: Links to official OPM, IRS, SSA documentation

To update for a new year:
1. Check official sources in October/November for new rates
2. Update values in `shared/config.ts`
3. Update `lastUpdated` and `dataYear` fields
4. Restart the application

## Contact Form

The `/contact` page allows users to submit questions to support@fedbuyout.com. Currently, form submissions are logged to the server console. 

**To enable email sending:** Set up Resend or SendGrid integration to send emails to support@fedbuyout.com. The endpoint `/api/contact` is ready for integration - just add the email sending logic.

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