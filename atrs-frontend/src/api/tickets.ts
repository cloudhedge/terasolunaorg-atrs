/**
 * Tickets/Reservation API hooks
 */
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from './client';
import type { ReservationRequest, ReservationResponse } from '../types';

export function useCreateReservation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request: ReservationRequest) => {
      return api.post<ReservationResponse>('/tickets', request);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reservations'] });
    },
  });
}
