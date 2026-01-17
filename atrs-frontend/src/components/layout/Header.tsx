/**
 * Header component - migrated from header.jsp
 */
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../../stores/authStore';
import { useLogout, useMe } from '../../api/auth';

export default function Header() {
  const { t } = useTranslation();
  const { isAuthenticated, user } = useAuthStore();
  const logoutMutation = useLogout();
  
  // Fetch user info when authenticated
  useMe();

  const handleLogout = (e: React.MouseEvent) => {
    e.preventDefault();
    logoutMutation.mutate();
  };

  return (
    <header id="header">
      <div className="container">
        <h1>
          <Link to="/">
            <span className="sr-only">Airline Ticket Reservation System</span>
          </Link>
        </h1>
        <nav>
          <ul className="vertical-middle-box">
            <li>
              <Link to="/flights">{t('nav.domestic')}</Link>
            </li>
          </ul>
        </nav>

        <div className="header-right-menu">
          {!isAuthenticated ? (
            <div className="vertical-middle-box">
              <Link id="member-registration" className="btn btn-primary" to="/member/register">
                {t('nav.register')}
              </Link>
              <Link id="login" className="btn btn-default" to="/login">
                <span className="glyphicon glyphicon-user"></span>
                {t('nav.login')}
              </Link>
            </div>
          ) : (
            <div className="vertical-middle-box">
              <div className="dropdown">
                <span
                  id="name"
                  className="btn btn-default dropdown-toggle"
                  data-toggle="dropdown"
                >
                  {t('welcome')}&nbsp;
                  <span>{user?.name}</span>
                  &nbsp;{t('sama')}&nbsp;
                  <span className="caret"></span>
                </span>
                <ul className="dropdown-menu">
                  <li>
                    <Link id="member-information-change" to="/member/update">
                      {t('nav.memberUpdate')}
                    </Link>
                  </li>
                  <li>
                    <Link id="create-history-report" to="/history/create">
                      {t('nav.historyReport')}
                    </Link>
                  </li>
                  <li>
                    <Link id="download-history-report" to="/history/download">
                      {t('nav.historyDownload')}
                    </Link>
                  </li>
                  <li>
                    <a
                      id="logout"
                      href="#"
                      onClick={handleLogout}
                    >
                      {t('nav.logout')}
                    </a>
                  </li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
