/**
 * Shared API client for ATRS REST endpoints.
 * Centralised HTTP calls, error handling, and response formatting.
 */

import axios, { AxiosError } from "axios";
import { API_BASE_URL, REQUEST_TIMEOUT } from "./constants.js";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

/**
 * Generic API request wrapper with typed response.
 */
export async function makeApiRequest<T>(
  endpoint: string,
  method: "GET" | "POST" = "GET",
  data?: unknown,
  params?: Record<string, unknown>
): Promise<T> {
  const response = await client.request<T>({
    url: endpoint,
    method,
    data,
    params,
  });
  return response.data;
}

/**
 * Convert an unknown error into an actionable user-facing message.
 */
export function handleApiError(error: unknown): string {
  if (error instanceof AxiosError) {
    if (error.response) {
      const status = error.response.status;
      const body =
        typeof error.response.data === "string"
          ? error.response.data
          : JSON.stringify(error.response.data, null, 2);

      switch (status) {
        case 400:
          return `Error (400 Bad Request): Invalid parameters.\n${body}\nCheck input values and try again.`;
        case 404:
          return "Error (404 Not Found): The requested resource does not exist. Verify IDs/codes are correct.";
        case 409:
          return `Error (409 Conflict): ${body}`;
        case 500:
          return `Error (500 Server Error): ATRS backend error.\n${body}\nEnsure the ATRS application is running.`;
        default:
          return `Error (${status}): ${body}`;
      }
    }
    if (error.code === "ECONNREFUSED") {
      return `Error: Cannot connect to ATRS at ${API_BASE_URL}. Ensure the application is running.`;
    }
    if (error.code === "ECONNABORTED") {
      return "Error: Request timed out. The ATRS server may be under heavy load.";
    }
  }
  return `Error: ${error instanceof Error ? error.message : String(error)}`;
}
