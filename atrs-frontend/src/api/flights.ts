/**
 * Flights API hooks with TanStack Query
 */
import { useQuery } from '@tanstack/react-query';
import { api } from './client';
import type { Flight, FlightSearchCriteria, BoardingClassCd, FlightType } from '../types';

export function useFlightSearch(criteria: FlightSearchCriteria | null) {
  return useQuery({
    queryKey: ['flights', criteria],
    queryFn: async () => {
      if (!criteria) return [];

      const params = new URLSearchParams({
        departure_date: criteria.departureDate,
        dep_airport_cd: criteria.depAirportCd,
        arr_airport_cd: criteria.arrAirportCd,
        boarding_class_cd: criteria.boardingClassCd,
        flight_type: criteria.flightType,
      });

      return api.get<Flight[]>(`/flights?${params}`);
    },
    enabled: !!criteria,
    retry: 1,
  });
}

// Helper function to format search params for API call
export function buildFlightSearchParams(
  departureDate: string,
  depAirportCd: string,
  arrAirportCd: string,
  boardingClassCd: BoardingClassCd,
  flightType: FlightType = 'OW'
): FlightSearchCriteria {
  return {
    departureDate,
    depAirportCd,
    arrAirportCd,
    boardingClassCd,
    flightType,
  };
}
