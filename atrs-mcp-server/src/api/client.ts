import type { Config } from '../config.js';
import type {
  FlightSearchQuery,
  FlightResource,
  TicketReserveRequest,
  TicketReserveResponse,
  ApiError,
} from './types.js';

/**
 * HTTP client for ATRS REST APIs
 * Base URL: /api/v1/*
 */
export class AtrsApiClient {
  private baseUrl: string;
  private timeout: number;
  private authHeader?: string;

  constructor(config: Config) {
    this.baseUrl = config.apiBaseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.timeout = config.timeout;

    // Auto-login if credentials provided
    if (config.credentials) {
      this.setCredentials(
        config.credentials.membershipNumber,
        config.credentials.password
      );
    }
  }

  /**
   * Set Basic Auth credentials for all subsequent requests
   */
  setCredentials(membershipNumber: string, password: string): void {
    const encoded = Buffer.from(`${membershipNumber}:${password}`).toString(
      'base64'
    );
    this.authHeader = `Basic ${encoded}`;
  }

  /**
   * Clear stored credentials
   */
  clearCredentials(): void {
    this.authHeader = undefined;
  }

  /**
   * Check if credentials are set
   */
  isAuthenticated(): boolean {
    return this.authHeader !== undefined;
  }

  /**
   * Search for available flights
   * GET /api/v1/flight
   */
  async searchFlights(query: FlightSearchQuery): Promise<FlightResource[]> {
    const params = new URLSearchParams({
      flightType: query.flightType,
      depAirportCd: query.depAirportCd,
      arrAirportCd: query.arrAirportCd,
      depDate: query.depDate,
      boardingClassCd: query.boardingClassCd,
    });

    const response = await this.fetch(`/api/v1/flight?${params.toString()}`);

    if (!response.ok) {
      const error = await this.parseError(response);
      throw new Error(`Flight search failed: ${error.code} - ${error.message}`);
    }

    return response.json();
  }

  /**
   * Reserve a ticket
   * POST /api/v1/ticket
   */
  async reserveTicket(
    request: TicketReserveRequest
  ): Promise<TicketReserveResponse> {
    const response = await this.fetch('/api/v1/ticket', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await this.parseError(response);
      throw new Error(`Reservation failed: ${error.code} - ${error.message}`);
    }

    return response.json();
  }

  /**
   * Check if a reservation exists
   * GET /api/v1/ticket/check?reserveNo=X
   */
  async checkReservation(reserveNo: string): Promise<boolean> {
    const params = new URLSearchParams({ reserveNo });
    const response = await this.fetch(
      `/api/v1/ticket/check?${params.toString()}`
    );

    if (!response.ok) {
      const error = await this.parseError(response);
      throw new Error(
        `Reservation check failed: ${error.code} - ${error.message}`
      );
    }

    return response.json();
  }

  /**
   * Check authentication status
   * Returns true if credentials are set (REST API uses Basic Auth per-request)
   */
  async checkAuthStatus(): Promise<boolean> {
    return this.isAuthenticated();
  }

  /**
   * Check if a membership number is valid
   * GET /api/member/available?membershipNumber=X
   */
  async checkMember(membershipNumber: string): Promise<boolean> {
    const params = new URLSearchParams({ membershipNumber });
    const response = await this.fetch(
      `/api/member/available?${params.toString()}`
    );
    return response.status === 200;
  }

  /**
   * Internal fetch with timeout, base URL, and auth header
   */
  private async fetch(
    path: string,
    options: RequestInit = {}
  ): Promise<Response> {
    const url = `${this.baseUrl}${path}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    // Merge headers with auth header if set
    const headers = new Headers(options.headers);
    if (this.authHeader) {
      headers.set('Authorization', this.authHeader);
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal,
      });
      return response;
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error(`Request timeout after ${this.timeout}ms`);
      }
      throw error;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * Parse error response
   */
  private async parseError(response: Response): Promise<ApiError> {
    try {
      return await response.json();
    } catch {
      return {
        code: `HTTP_${response.status}`,
        message: response.statusText,
      };
    }
  }
}
