/**
 * Reserve store for flight reservation flow
 */
import { create } from 'zustand';
import type { FlightSelection, Passenger, Gender, FlightType } from '../types';

export interface Representative {
  familyName: string;
  givenName: string;
  age: number;
  gender: Gender;
  tel: string;
  email: string;
  customerNo?: string;
}

interface ReserveState {
  // Data
  outwardFlight: FlightSelection | null;
  returnFlight: FlightSelection | null;
  passengers: Passenger[];
  representative: Representative | null;
  passengerCount: number;
  flightType: FlightType;
  
  // Actions
  setOutwardFlight: (flight: FlightSelection | null) => void;
  setReturnFlight: (flight: FlightSelection | null) => void;
  setPassengers: (passengers: Passenger[]) => void;
  setRepresentative: (rep: Representative | null) => void;
  setPassengerCount: (count: number) => void;
  setFlightType: (flightType: FlightType) => void;
  reset: () => void;
}

const initialState = {
  outwardFlight: null,
  returnFlight: null,
  passengers: [],
  representative: null,
  passengerCount: 1,
  flightType: 'RT' as FlightType,
};

export const useReserveStore = create<ReserveState>((set) => ({
  ...initialState,

  setOutwardFlight: (flight) => set({ outwardFlight: flight }),
  setReturnFlight: (flight) => set({ returnFlight: flight }),
  setPassengers: (passengers) => set({ passengers }),
  setRepresentative: (representative) => set({ representative }),
  setPassengerCount: (passengerCount) => set({ passengerCount }),
  setFlightType: (flightType) => set({ flightType }),
  reset: () => set(initialState),
}));
