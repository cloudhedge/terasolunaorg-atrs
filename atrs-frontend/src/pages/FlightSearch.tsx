/**
 * Flight Search page - migrated from flightSearch.jsp
 */
import { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useFlightSearch } from '../api/flights';
import FlightSearchForm from '../components/common/FlightSearchForm';
import FlightTable from '../components/common/FlightTable';
import { useReserveStore } from '../stores/reserveStore';
import type { FlightSearchCriteria, BoardingClassCd, FlightType } from '../types';
import { formatDateWithWeekday } from '../utils/formatters';

export default function FlightSearch() {
  const { t } = useTranslation('flight');
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  const {
    outwardFlight,
    returnFlight,
    setOutwardFlight,
    setReturnFlight,
    setFlightType,
    reset,
  } = useReserveStore();

  // Parse search params
  const flightType = (searchParams.get('flightType') || 'RT') as FlightType;
  const depAirportCd = searchParams.get('depAirportCd') || '';
  const arrAirportCd = searchParams.get('arrAirportCd') || '';
  const outwardDate = searchParams.get('outwardDate') || '';
  const homewardDate = searchParams.get('homewardDate') || '';
  const boardingClassCd = (searchParams.get('boardingClassCd') || 'N') as BoardingClassCd;

  // Build search criteria for outward
  const outwardCriteria: FlightSearchCriteria | null = outwardDate
    ? {
        departureDate: outwardDate,
        depAirportCd,
        arrAirportCd,
        boardingClassCd,
        flightType,
      }
    : null;

  // Build search criteria for homeward (swap airports)
  const homewardCriteria: FlightSearchCriteria | null =
    flightType === 'RT' && homewardDate
      ? {
          departureDate: homewardDate,
          depAirportCd: arrAirportCd, // Swap
          arrAirportCd: depAirportCd, // Swap
          boardingClassCd,
          flightType,
        }
      : null;

  const outwardQuery = useFlightSearch(outwardCriteria);
  const homewardQuery = useFlightSearch(homewardCriteria);

  // Reset store when search params change
  useEffect(() => {
    reset();
    setFlightType(flightType);
  }, [searchParams, reset, setFlightType, flightType]);

  const handleReserve = () => {
    // Validate selections
    if (!outwardFlight) {
      alert(t('errors:validation.selectOutwardFlight'));
      return;
    }

    if (flightType === 'RT' && !returnFlight) {
      alert(t('errors:validation.selectHomewardFlight'));
      return;
    }

    // Navigate to reservation form
    navigate('/reserve');
  };

  const hasSearchParams = outwardDate && depAirportCd && arrAirportCd;

  return (
    <div className="row">
      <section className="col-md-12">
        <h2 id="screen-title">{t('search.title')}</h2>
        <div className="alert alert-info">
          <ul>
            <li>{t('search.maxSeats')}</li>
          </ul>
        </div>
      </section>

      <section className="col-md-4">
        <FlightSearchForm />
      </section>

      <section className="col-md-8">
        {hasSearchParams && (
          <>
            {/* Outward Flights */}
            <section id="outward-flights">
              <h2>{t('results.outward')}</h2>
              <ul className="pager pager-top text-left">
                <li>
                  <span id="outward-flight-date" className="pager-current-date">
                    {outwardDate && formatDateWithWeekday(outwardDate)}
                  </span>
                </li>
              </ul>

              {outwardQuery.isLoading && (
                <div className="loading-spinner">{t('common:loading')}</div>
              )}

              {outwardQuery.isError && (
                <ul className="alert alert-danger list-unstyled">
                  <li>{t('errors:network.error')}</li>
                </ul>
              )}

              {outwardQuery.data && (
                <FlightTable
                  flights={outwardQuery.data}
                  direction="outward"
                  selectedFlight={outwardFlight}
                  onSelect={setOutwardFlight}
                  boardingClassCd={boardingClassCd}
                />
              )}
            </section>

            {/* Homeward Flights (only for round trip) */}
            {flightType === 'RT' && homewardDate && (
              <section id="homeward-flights">
                <h2>{t('results.homeward')}</h2>
                <ul className="pager pager-top text-left">
                  <li>
                    <span id="homeward-flight-date" className="pager-current-date">
                      {homewardDate && formatDateWithWeekday(homewardDate)}
                    </span>
                  </li>
                </ul>

                {homewardQuery.isLoading && (
                  <div className="loading-spinner">{t('common:loading')}</div>
                )}

                {homewardQuery.isError && (
                  <ul className="alert alert-danger list-unstyled">
                    <li>{t('errors:network.error')}</li>
                  </ul>
                )}

                {homewardQuery.data && (
                  <FlightTable
                    flights={homewardQuery.data}
                    direction="homeward"
                    selectedFlight={returnFlight}
                    onSelect={setReturnFlight}
                    boardingClassCd={boardingClassCd}
                  />
                )}
              </section>
            )}

            {/* Reserve Button */}
            <div className="text-center" style={{ marginTop: '20px' }}>
              <button
                id="reserve-flights-button"
                className="btn btn-primary btn-lg"
                onClick={handleReserve}
                disabled={!outwardFlight || (flightType === 'RT' && !returnFlight)}
              >
                {t('search.selectFlights')}
              </button>
            </div>
          </>
        )}
      </section>
    </div>
  );
}
