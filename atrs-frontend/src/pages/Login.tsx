/**
 * Login page - migrated from loginForm.jsp
 */
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useTranslation } from 'react-i18next';
import { useLogin } from '../api/auth';
import { useAuthStore } from '../stores/authStore';

const loginSchema = z.object({
  membershipNumber: z
    .string()
    .min(1, 'Required')
    .length(10, 'Must be 10 digits')
    .regex(/^\d+$/, 'Must be numeric'),
  password: z.string().min(1, 'Required'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function Login() {
  const { t } = useTranslation('auth');
  const { t: tErrors } = useTranslation('errors');
  const navigate = useNavigate();
  const loginMutation = useLogin();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      membershipNumber: '',
      password: '',
    },
  });

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  const onSubmit = async (data: LoginFormData) => {
    try {
      await loginMutation.mutateAsync({
        username: data.membershipNumber,
        password: data.password,
      });
      navigate('/');
    } catch {
      // Error handled by mutation
    }
  };

  return (
    <div className="row">
      <div className="col-md-offset-3 col-md-6">
        {loginMutation.isError && (
          <ul className="alert list-unstyled alert-danger">
            <li>{tErrors('E_AR_A1_2001')}</li>
          </ul>
        )}

        <div className="panel panel-default">
          <div className="panel-heading">{t('login.title')}</div>

          <div className="panel-body">
            <form id="login-form" onSubmit={handleSubmit(onSubmit)}>
              <div className="form-group">
                <label className="control-label" htmlFor="membershipNumber">
                  {t('login.membershipNumber')}
                </label>
                <input
                  type="text"
                  className="form-control"
                  maxLength={10}
                  id="membershipNumber"
                  {...register('membershipNumber')}
                />
                {errors.membershipNumber && (
                  <span className="invalid">{errors.membershipNumber.message}</span>
                )}
              </div>

              <div className="form-group">
                <label className="control-label" htmlFor="password">
                  {t('login.password')}
                </label>
                <input
                  type="password"
                  className="form-control"
                  id="password"
                  {...register('password')}
                />
                {errors.password && (
                  <span className="invalid">{errors.password.message}</span>
                )}
              </div>

              <button
                type="submit"
                id="login-btn"
                className="btn btn-default"
                disabled={isSubmitting || loginMutation.isPending}
              >
                {loginMutation.isPending ? '...' : t('login.submit')}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
