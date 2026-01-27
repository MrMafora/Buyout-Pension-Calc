import { drizzle } from "drizzle-orm/node-postgres";
import pg from "pg";
import * as schema from "@shared/schema";

const { Pool } = pg;

// We set this up to satisfy the template, but we will use MemStorage for this app
// as per requirements "You don't need a database".
// If DATABASE_URL is not set, we won't throw error immediately to allow 
// the app to run in memory-only mode if needed, but the template usually provisions it.

if (!process.env.DATABASE_URL) {
  console.warn("DATABASE_URL not set. Database features will be disabled.");
}

export const pool = new Pool({ connectionString: process.env.DATABASE_URL });
export const db = drizzle(pool, { schema });
