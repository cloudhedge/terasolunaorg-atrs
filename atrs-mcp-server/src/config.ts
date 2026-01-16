/**
 * Configuration for ATRS MCP Server
 */
export interface Config {
  /** Base URL for ATRS API (e.g., http://localhost:8080/atrs) */
  apiBaseUrl: string;
  /** Request timeout in milliseconds */
  timeout: number;
  /** Optional credentials for auto-login */
  credentials?: {
    membershipNumber: string;
    password: string;
  };
}

/**
 * Load configuration from environment variables
 */
export function loadConfig(): Config {
  const apiBaseUrl = process.env.ATRS_API_BASE_URL || 'http://localhost:8080/atrs';
  const timeout = parseInt(process.env.ATRS_TIMEOUT || '30000', 10);

  // Optional auto-login credentials
  const membershipNumber = process.env.ATRS_USER;
  const password = process.env.ATRS_PASSWORD;
  const credentials =
    membershipNumber && password ? { membershipNumber, password } : undefined;

  return {
    apiBaseUrl,
    timeout,
    credentials,
  };
}
