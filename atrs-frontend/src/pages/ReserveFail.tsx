/**
 * Reservation Failed page - migrated from reserveFail.jsp
 */
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export default function ReserveFail() {
  const { t } = useTranslation('reserve');

  return (
    <div className="row">
      <section className="col-md-12">
        <h2 id="screen-title">{t('fail.title')}</h2>

        <div className="alert alert-danger">
          <p>{t('fail.message')}</p>
        </div>

        <div className="text-center">
          <Link to="/flights" className="btn btn-primary btn-lg">
            空席照会に戻る
          </Link>
          <Link to="/" className="btn btn-default btn-lg" style={{ marginLeft: '10px' }}>
            トップページに戻る
          </Link>
        </div>
      </section>
    </div>
  );
}
