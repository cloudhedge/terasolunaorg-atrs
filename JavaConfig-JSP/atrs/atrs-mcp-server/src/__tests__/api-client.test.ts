/**
 * Tests for api-client.ts — error handling.
 */

import { describe, it, expect } from "vitest";
import { AxiosError, AxiosHeaders } from "axios";
import { handleApiError } from "../api-client.js";

/** Helper to build a fake AxiosError with a response. */
function makeAxiosResponseError(
  status: number,
  data: unknown
): AxiosError {
  const headers = new AxiosHeaders();
  const config = { headers } as AxiosError["config"];
  const error = new AxiosError(
    `Request failed with status code ${status}`,
    String(status),
    config,
    {},
    {
      status,
      statusText: "",
      headers: {},
      config,
      data,
    }
  );
  return error;
}

/** Helper to build a fake AxiosError with a code but no response. */
function makeAxiosNetworkError(code: string): AxiosError {
  const headers = new AxiosHeaders();
  const config = { headers } as AxiosError["config"];
  const error = new AxiosError("Network error", code, config);
  return error;
}

describe("handleApiError", () => {
  // ── HTTP status codes ──────────────────────────────────────────────────

  it("should handle 400 Bad Request with string body", () => {
    const err = makeAxiosResponseError(400, "Invalid depDate format");
    const msg = handleApiError(err);
    expect(msg).toContain("400 Bad Request");
    expect(msg).toContain("Invalid depDate format");
    expect(msg).toContain("Check input values");
  });

  it("should handle 400 Bad Request with object body", () => {
    const err = makeAxiosResponseError(400, { message: "Bad input" });
    const msg = handleApiError(err);
    expect(msg).toContain("400 Bad Request");
    expect(msg).toContain("Bad input");
  });

  it("should handle 404 Not Found", () => {
    const err = makeAxiosResponseError(404, "");
    const msg = handleApiError(err);
    expect(msg).toContain("404 Not Found");
    expect(msg).toContain("Verify IDs/codes");
  });

  it("should handle 409 Conflict", () => {
    const err = makeAxiosResponseError(409, "Duplicate reservation");
    const msg = handleApiError(err);
    expect(msg).toContain("409 Conflict");
    expect(msg).toContain("Duplicate reservation");
  });

  it("should handle 500 Server Error", () => {
    const err = makeAxiosResponseError(500, "Internal error");
    const msg = handleApiError(err);
    expect(msg).toContain("500 Server Error");
    expect(msg).toContain("ATRS backend error");
    expect(msg).toContain("Ensure the ATRS application is running");
  });

  it("should handle other status codes generically", () => {
    const err = makeAxiosResponseError(422, "Unprocessable entity");
    const msg = handleApiError(err);
    expect(msg).toContain("Error (422)");
    expect(msg).toContain("Unprocessable entity");
  });

  // ── Network errors ─────────────────────────────────────────────────────

  it("should handle ECONNREFUSED", () => {
    const err = makeAxiosNetworkError("ECONNREFUSED");
    const msg = handleApiError(err);
    expect(msg).toContain("Cannot connect to ATRS");
    expect(msg).toContain("Ensure the application is running");
  });

  it("should handle ECONNABORTED (timeout)", () => {
    const err = makeAxiosNetworkError("ECONNABORTED");
    const msg = handleApiError(err);
    expect(msg).toContain("timed out");
    expect(msg).toContain("heavy load");
  });

  // ── Non-Axios errors ───────────────────────────────────────────────────

  it("should handle generic Error objects", () => {
    const msg = handleApiError(new Error("Something broke"));
    expect(msg).toBe("Error: Something broke");
  });

  it("should handle string errors", () => {
    const msg = handleApiError("raw string error");
    expect(msg).toBe("Error: raw string error");
  });

  it("should handle null/undefined", () => {
    const msg = handleApiError(null);
    expect(msg).toBe("Error: null");
  });
});
