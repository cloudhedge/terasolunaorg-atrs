/**
 * Configuration for ATRS MCP Server
 */
export interface Config {
  /** Base URL for ATRS API (default: http://localhost:8080/atrs/) */
  apiBaseUrl: string;
  /** Request timeout in milliseconds */
  timeout: number;
}

/**
 * Load configuration from environment variables
 */
export function loadConfig(): Config {
  const apiBaseUrl = process.env.ATRS_API_BASE_URL || 'http://localhost:8080/atrs';
  const timeout = parseInt(process.env.ATRS_TIMEOUT || '30000', 10);

  return {
    apiBaseUrl,
    timeout,
  };
}
