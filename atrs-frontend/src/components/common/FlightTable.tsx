/**
 * Flight table component for displaying search results
 */
import { useTranslation } from 'react-i18next';
import { formatTime, formatCurrency } from '../../utils/formatters';
import type { Flight, FareType, FlightSelection, BoardingClassCd, FareTypeCd } from '../../types';

interface FlightTableProps {
  flights: Flight[];
  direction: 'outward' | 'homeward';
  selectedFlight: FlightSelection | null;
  onSelect: (selection: FlightSelection) => void;
  boardingClassCd?: BoardingClassCd;
}

export default function FlightTable({
  flights,
  direction,
  selectedFlight,
  onSelect,
}: FlightTableProps) {
  const { t } = useTranslation('flight');

  if (flights.length === 0) {
    return (
      <div className="alert alert-info">
        {t('results.noResults')}
      </div>
    );
  }

  // Get unique fare types across all flights
  const fareTypeSet = new Set<FareTypeCd>();
  const fareTypeNames: Record<string, string> = {};
  
  flights.forEach((flight) => {
    flight.fare_types.forEach((ft) => {
      fareTypeSet.add(ft.fare_type_cd);
      fareTypeNames[ft.fare_type_cd] = ft.fare_type_name;
    });
  });

  const fareTypes = Array.from(fareTypeSet);

  const handleSelect = (flight: Flight, fareType: FareType) => {
    if (fareType.vacant_num <= 0) return;

    const selection: FlightSelection = {
      departure_date: flight.departure_date,
      flight_name: flight.flight_name,
      boarding_class_cd: flight.boarding_class_cd,
      fare_type_cd: fareType.fare_type_cd,
      departure_time: flight.departure_time,
      arrival_time: flight.arrival_time,
      departure_airport_name: flight.departure_airport_name,
      arrival_airport_name: flight.arrival_airport_name,
      fare: fareType.fare,
      fare_type_name: fareType.fare_type_name,
    };

    onSelect(selection);
  };

  const isSelected = (flight: Flight, fareType: FareType) => {
    return (
      selectedFlight?.flight_name === flight.flight_name &&
      selectedFlight?.fare_type_cd === fareType.fare_type_cd &&
      selectedFlight?.departure_date === flight.departure_date
    );
  };

  return (
    <table className="table flights-table">
      <thead>
        <tr>
          <th style={{ width: '64px' }}>{t('results.flightName')}</th>
          <th style={{ width: '88px' }}>{t('results.departure')}</th>
          <th style={{ width: '88px' }}>{t('results.arrival')}</th>
          {fareTypes.map((ft) => (
            <th key={ft} className="fare-header">
              {fareTypeNames[ft]}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {flights.map((flight) => (
          <tr key={`${flight.flight_name}-${flight.departure_date}`}>
            <th className="bg-primary">{flight.flight_name}</th>
            <th className="bg-primary">
              {formatTime(flight.departure_time)}
              <br />
              {flight.departure_airport_name}
            </th>
            <th className="bg-primary">
              {formatTime(flight.arrival_time)}
              <br />
              {flight.arrival_airport_name}
            </th>
            {fareTypes.map((ftCode) => {
              const fareType = flight.fare_types.find((ft) => ft.fare_type_cd === ftCode);
              
              if (!fareType) {
                return <td key={ftCode}>-</td>;
              }

              const selected = isSelected(flight, fareType);
              const available = fareType.vacant_num > 0;

              return (
                <td key={ftCode} className={selected ? 'selected' : ''}>
                  <label style={{ cursor: available ? 'pointer' : 'default' }}>
                    <input
                      type="radio"
                      name={`${direction}-flight-select`}
                      disabled={!available}
                      checked={selected}
                      onChange={() => handleSelect(flight, fareType)}
                    />
                    <br />
                    {formatCurrency(fareType.fare)}
                    <br />
                    {fareType.vacant_num > 10 ? (
                      '\u00A0'
                    ) : fareType.vacant_num > 0 ? (
                      <span className="label label-warning">
                        {t('results.seatsLeft', { count: fareType.vacant_num })}
                      </span>
                    ) : (
                      <span className="label label-default">{t('results.soldOut')}</span>
                    )}
                  </label>
                </td>
              );
            })}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
