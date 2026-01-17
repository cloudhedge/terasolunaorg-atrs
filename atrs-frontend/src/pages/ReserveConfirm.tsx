/**
 * Reservation Confirm page - migrated from reserveConfirm.jsp
 */
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useReserveStore } from '../stores/reserveStore';
import { useCreateReservation } from '../api/tickets';
import { formatDateWithWeekday, formatTime, formatCurrency } from '../utils/formatters';
import { GENDERS, BOARDING_CLASSES } from '../types';

export default function ReserveConfirm() {
  const { t } = useTranslation('reserve');
  const navigate = useNavigate();
  const {
    outwardFlight,
    returnFlight,
    passengers,
    representative,
  } = useReserveStore();

  const createReservation = useCreateReservation();

  // Redirect if no data
  if (!outwardFlight || !representative) {
    navigate('/flights');
    return null;
  }

  // Calculate total fare
  const passengerCount = passengers.length || 1;
  const outwardFare = outwardFlight.fare || 0;
  const returnFare = returnFlight?.fare || 0;
  const totalFare = (outwardFare + returnFare) * passengerCount;

  const handleConfirm = async () => {
    try {
      // Build flights array
      const flights = [
        {
          departure_date: outwardFlight.departure_date,
          flight_name: outwardFlight.flight_name,
          boarding_class_cd: outwardFlight.boarding_class_cd,
          fare_type_cd: outwardFlight.fare_type_cd,
        },
      ];

      if (returnFlight) {
        flights.push({
          departure_date: returnFlight.departure_date,
          flight_name: returnFlight.flight_name,
          boarding_class_cd: returnFlight.boarding_class_cd,
          fare_type_cd: returnFlight.fare_type_cd,
        });
      }

      const result = await createReservation.mutateAsync({
        flights,
        passengers,
        rep_family_name: representative.familyName,
        rep_given_name: representative.givenName,
        rep_age: representative.age,
        rep_gender: representative.gender,
        rep_tel: representative.tel,
        rep_mail: representative.email,
        rep_customer_no: representative.customerNo,
      });

      // Navigate to complete page with result
      navigate('/reserve/complete', {
        state: {
          reserveNo: result.reserve_no,
          totalFare: result.total_fare,
        },
      });
    } catch (error) {
      navigate('/reserve/fail');
    }
  };

  const handleBack = () => {
    navigate(-1);
  };

  return (
    <div className="row">
      <section className="col-md-12">
        <h2 id="screen-title">{t('title')} - 確認</h2>

        {/* Selected Flights */}
        <section>
          <h3>{t('selectedFlights')}</h3>
          <table className="table table-bordered">
            <thead>
              <tr>
                <th>{t('table.direction')}</th>
                <th>{t('table.date')}</th>
                <th>{t('table.flightName')}</th>
                <th>{t('table.departure')}</th>
                <th>{t('table.arrival')}</th>
                <th>{t('table.route')}</th>
                <th>{t('table.boardingClass')}</th>
                <th>{t('table.fareType')}</th>
                <th>{t('table.fare')}</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>{t('directions.outward')}</td>
                <td>{formatDateWithWeekday(outwardFlight.departure_date)}</td>
                <td>{outwardFlight.flight_name}</td>
                <td>{formatTime(outwardFlight.departure_time || '')}</td>
                <td>{formatTime(outwardFlight.arrival_time || '')}</td>
                <td>
                  {outwardFlight.departure_airport_name}
                  <span className="glyphicon glyphicon-arrow-right"></span>
                  {outwardFlight.arrival_airport_name}
                </td>
                <td>{BOARDING_CLASSES.find(b => b.code === outwardFlight.boarding_class_cd)?.name}</td>
                <td>{outwardFlight.fare_type_name}</td>
                <td>{formatCurrency(outwardFlight.fare || 0)}</td>
              </tr>
              {returnFlight && (
                <tr>
                  <td>{t('directions.homeward')}</td>
                  <td>{formatDateWithWeekday(returnFlight.departure_date)}</td>
                  <td>{returnFlight.flight_name}</td>
                  <td>{formatTime(returnFlight.departure_time || '')}</td>
                  <td>{formatTime(returnFlight.arrival_time || '')}</td>
                  <td>
                    {returnFlight.departure_airport_name}
                    <span className="glyphicon glyphicon-arrow-right"></span>
                    {returnFlight.arrival_airport_name}
                  </td>
                  <td>{BOARDING_CLASSES.find(b => b.code === returnFlight.boarding_class_cd)?.name}</td>
                  <td>{returnFlight.fare_type_name}</td>
                  <td>{formatCurrency(returnFlight.fare || 0)}</td>
                </tr>
              )}
            </tbody>
          </table>
        </section>

        {/* Passengers */}
        <section>
          <h3>{t('customerInfo')}</h3>
          <table className="table table-bordered">
            <thead>
              <tr>
                <th>#</th>
                <th>{t('fields.name')}</th>
                <th>{t('fields.age')}</th>
                <th>{t('fields.gender')}</th>
                <th>{t('fields.membershipNumber')}</th>
              </tr>
            </thead>
            <tbody>
              {passengers.map((p, i) => (
                <tr key={i}>
                  <td>{i + 1}</td>
                  <td>{p.family_name} {p.given_name}</td>
                  <td>{p.age}</td>
                  <td>{GENDERS.find(g => g.code === p.gender)?.name}</td>
                  <td>{p.customer_no || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        {/* Representative */}
        <section>
          <h3>{t('representative')}</h3>
          <dl className="dl-horizontal">
            <dt>{t('fields.name')}</dt>
            <dd>{representative.familyName} {representative.givenName}</dd>
            <dt>{t('fields.age')}</dt>
            <dd>{representative.age}</dd>
            <dt>{t('fields.gender')}</dt>
            <dd>{GENDERS.find(g => g.code === representative.gender)?.name}</dd>
            <dt>{t('fields.tel')}</dt>
            <dd>{representative.tel}</dd>
            <dt>{t('fields.email')}</dt>
            <dd>{representative.email}</dd>
            {representative.customerNo && (
              <>
                <dt>{t('fields.membershipNumber')}</dt>
                <dd>{representative.customerNo}</dd>
              </>
            )}
          </dl>
        </section>

        {/* Total */}
        <section>
          <h3>合計金額</h3>
          <p className="lead">
            <strong>{formatCurrency(totalFare)}</strong>
            <small> ({passengerCount}名様)</small>
          </p>
        </section>

        {/* Buttons */}
        <div className="text-center btns-block">
          <button
            type="button"
            className="btn btn-primary btn-lg btns-block-rightest-btn"
            onClick={handleConfirm}
            disabled={createReservation.isPending}
          >
            {createReservation.isPending ? '処理中...' : '予約確定'}
          </button>
          <button type="button" className="btn btn-default btn-lg" onClick={handleBack}>
            戻る
          </button>
        </div>

        {createReservation.isError && (
          <div className="alert alert-danger" style={{ marginTop: '20px' }}>
            予約処理中にエラーが発生しました。
          </div>
        )}
      </section>
    </div>
  );
}
