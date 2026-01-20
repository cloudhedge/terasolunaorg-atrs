#!/usr/bin/env node
import { startServer } from './server.js';

startServer().catch((error) => {
  console.error('Failed to start ATRS MCP Server:', error);
  process.exit(1);
});
