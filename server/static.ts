import express, { type Express, type Request, type Response } from "express";
import fs from "fs";
import path from "path";

export function serveStatic(app: Express) {
  const distPath = path.resolve(__dirname, "public");
  const indexPath = path.resolve(distPath, "index.html");
  
  if (!fs.existsSync(distPath)) {
    throw new Error(
      `Could not find the build directory: ${distPath}, make sure to build the client first`,
    );
  }

  // Read index.html content once
  const indexHtml = fs.readFileSync(indexPath, "utf-8");

  // Serve static files first
  app.use(express.static(distPath));

  // Serve index.html for all client routes
  const serveIndex = (_req: Request, res: Response) => {
    res.setHeader("Content-Type", "text/html");
    res.send(indexHtml);
  };

  // Explicit client-side routes
  app.get("/admin", serveIndex);
  app.get("/contact", serveIndex);
  app.get("/about", serveIndex);
  app.get("/faq", serveIndex);
  app.get("/terms", serveIndex);
  app.get("/privacy", serveIndex);
  
  // Catch-all for other routes
  app.use((req, res, next) => {
    if (req.path.startsWith("/api")) {
      return next();
    }
    serveIndex(req, res);
  });
}