import type { Config } from '../config.js';
import type {
  FlightSearchQuery,
  FlightResource,
  TicketReserveRequest,
  TicketReserveResponse,
} from './types.js';

/**
 * HTTP client for ATRS REST APIs
 */
export class AtrsApiClient {
  private baseUrl: string;
  private timeout: number;

  constructor(config: Config) {
    this.baseUrl = config.apiBaseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.timeout = config.timeout;
  }

  /**
   * Search for available flights
   * GET /flight
   */
  async searchFlights(query: FlightSearchQuery): Promise<FlightResource[]> {
    const params = new URLSearchParams({
      flightType: query.flightType,
      depAirportCd: query.depAirportCd,
      arrAirportCd: query.arrAirportCd,
      depDate: query.depDate,
      boardingClassCd: query.boardingClassCd,
    });

    const response = await this.fetch(`/flight?${params.toString()}`);

    if (!response.ok) {
      const error = await this.parseError(response);
      throw new Error(`Flight search failed: ${error}`);
    }

    return response.json() as Promise<FlightResource[]>;
  }

  /**
   * Reserve a ticket
   * POST /ticket
   */
  async reserveTicket(request: TicketReserveRequest): Promise<TicketReserveResponse> {
    const response = await this.fetch('/ticket', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await this.parseError(response);
      throw new Error(`Ticket reservation failed: ${error}`);
    }

    return response.json() as Promise<TicketReserveResponse>;
  }

  /**
   * Check if a reservation exists
   * GET /ticket/check?reserveNo=X
   */
  async checkReservation(reserveNo: string): Promise<boolean> {
    const params = new URLSearchParams({ reserveNo });
    const response = await this.fetch(`/ticket/check?${params.toString()}`);

    if (!response.ok) {
      const error = await this.parseError(response);
      throw new Error(`Reservation check failed: ${error}`);
    }

    return response.json() as Promise<boolean>;
  }

  /**
   * Check authentication status
   * GET /api/auth/status
   * Returns true if authenticated, false otherwise
   */
  async checkAuthStatus(): Promise<boolean> {
    const response = await this.fetch('/api/auth/status');
    return response.status === 200;
  }

  /**
   * Check if member exists
   * GET /api/member/available?membershipNumber=X
   * Returns true if member exists or number is empty
   */
  async checkMemberAvailable(membershipNumber: string): Promise<boolean> {
    const params = new URLSearchParams({ membershipNumber });
    const response = await this.fetch(`/api/member/available?${params.toString()}`);
    return response.status === 200;
  }

  /**
   * Internal fetch with timeout and base URL
   */
  private async fetch(path: string, options: RequestInit = {}): Promise<Response> {
    const url = `${this.baseUrl}${path}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
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
  private async parseError(response: Response): Promise<string> {
    try {
      const text = await response.text();
      const json = JSON.parse(text);
      if (json.messages && Array.isArray(json.messages)) {
        return json.messages.join(', ');
      }
      return text || `HTTP ${response.status}`;
    } catch {
      return `HTTP ${response.status} ${response.statusText}`;
    }
  }
}
