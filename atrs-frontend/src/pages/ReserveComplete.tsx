/**
 * Reservation Complete page - migrated from reserveComplete.jsp
 */
import { useLocation, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { formatCurrency } from '../utils/formatters';

interface LocationState {
  reserveNo: string;
  totalFare: number;
}

export default function ReserveComplete() {
  const { t } = useTranslation('reserve');
  const location = useLocation();
  const state = location.state as LocationState | null;

  if (!state) {
    return (
      <div className="row">
        <div className="col-md-12">
          <div className="alert alert-warning">
            予約情報がありません。
            <Link to="/">トップページに戻る</Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="row">
      <section className="col-md-12">
        <h2 id="screen-title">{t('complete.title')}</h2>

        <div className="alert alert-success">
          <p>{t('complete.message')}</p>
        </div>

        <div className="panel panel-default">
          <div className="panel-body">
            <dl className="dl-horizontal">
              <dt>{t('complete.reserveNo')}</dt>
              <dd><strong className="text-primary">{state.reserveNo}</strong></dd>
              <dt>{t('complete.totalFare')}</dt>
              <dd><strong>{formatCurrency(state.totalFare)}</strong></dd>
            </dl>
          </div>
        </div>

        <div className="text-center">
          <Link to="/" className="btn btn-primary btn-lg">
            トップページに戻る
          </Link>
        </div>
      </section>
    </div>
  );
}
