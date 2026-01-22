/**
 * Flight search form component - migrated from flightSearchForm.jsp
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useTranslation } from 'react-i18next';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { AIRPORTS, BOARDING_CLASSES, FLIGHT_TYPES } from '../../types';
import { toApiDateString } from '../../utils/formatters';

const searchSchema = z.object({
  flightType: z.enum(['RT', 'OW']),
  depAirportCd: z.string().min(1, 'Required'),
  arrAirportCd: z.string().min(1, 'Required'),
  outwardDate: z.date({ message: 'Required' }),
  homewardDate: z.date().optional(),
  boardingClassCd: z.enum(['N', 'S']),
}).refine((data) => data.depAirportCd !== data.arrAirportCd, {
  message: '出発空港と到着空港に同じ空港は指定できません。',
  path: ['arrAirportCd'],
}).refine((data) => {
  if (data.flightType === 'RT' && data.homewardDate && data.outwardDate) {
    return data.homewardDate >= data.outwardDate;
  }
  return true;
}, {
  message: '往路搭乗日以降である必要があります。',
  path: ['homewardDate'],
});

type SearchFormData = z.infer<typeof searchSchema>;

interface FlightSearchFormProps {
  onSearch?: (params: URLSearchParams) => void;
}

export default function FlightSearchForm({ onSearch }: FlightSearchFormProps) {
  const { t } = useTranslation('flight');
  const navigate = useNavigate();
  const [outwardDate, setOutwardDate] = useState<Date | null>(null);
  const [homewardDate, setHomewardDate] = useState<Date | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<SearchFormData>({
    resolver: zodResolver(searchSchema),
    defaultValues: {
      flightType: 'RT',
      depAirportCd: '',
      arrAirportCd: '',
      boardingClassCd: 'N',
    },
  });

  const flightType = watch('flightType');

  const handleOutwardDateChange = (date: Date | null) => {
    setOutwardDate(date);
    if (date) {
      setValue('outwardDate', date, { shouldValidate: true });
    }
  };

  const handleHomewardDateChange = (date: Date | null) => {
    setHomewardDate(date);
    if (date) {
      setValue('homewardDate', date, { shouldValidate: true });
    }
  };

  const onSubmit = (data: SearchFormData) => {
    const params = new URLSearchParams({
      flightType: data.flightType,
      depAirportCd: data.depAirportCd,
      arrAirportCd: data.arrAirportCd,
      outwardDate: toApiDateString(data.outwardDate),
      boardingClassCd: data.boardingClassCd,
    });

    if (data.flightType === 'RT' && data.homewardDate) {
      params.set('homewardDate', toApiDateString(data.homewardDate));
    }

    if (onSearch) {
      onSearch(params);
    } else {
      navigate(`/flights?${params.toString()}`);
    }
  };

  // Calculate date range (today + 90 days)
  const minDate = new Date();
  const maxDate = new Date();
  maxDate.setDate(maxDate.getDate() + 90);

  return (
    <div className="panel panel-default">
      <div className="panel-heading">ご希望の内容を入力してください。</div>

      <div className="panel-body">
        <form
          id="flights-search-form"
          className="form-horizontal"
          onSubmit={handleSubmit(onSubmit)}
        >
          {/* Flight Type */}
          <div className="form-group">
            <label className="col-md-4 control-label">{t('search.flightType')}</label>
            <div className="col-md-8">
              {FLIGHT_TYPES.map((ft) => (
                <label key={ft.code} className="radio-inline">
                  <input
                    type="radio"
                    value={ft.code}
                    {...register('flightType')}
                  />
                  {ft.name}
                </label>
              ))}
              {errors.flightType && (
                <span className="invalid">{errors.flightType.message}</span>
              )}
            </div>
          </div>

          {/* Airports */}
          <div className="form-group">
            <label className="col-md-4 control-label">{t('search.section')}</label>
            <div className="col-md-8">
              <select
                className="form-control"
                {...register('depAirportCd')}
              >
                <option value="">-- Select --</option>
                {AIRPORTS.map((airport) => (
                  <option key={airport.code} value={airport.code}>
                    {airport.name}
                  </option>
                ))}
              </select>
              <span
                className="glyphicon glyphicon-arrow-down"
                style={{ width: '100%', lineHeight: '34px', textAlign: 'center' }}
              ></span>
              <select
                className="form-control"
                {...register('arrAirportCd')}
              >
                <option value="">-- Select --</option>
                {AIRPORTS.map((airport) => (
                  <option key={airport.code} value={airport.code}>
                    {airport.name}
                  </option>
                ))}
              </select>
              {errors.depAirportCd && (
                <span className="invalid">{errors.depAirportCd.message}</span>
              )}
              {errors.arrAirportCd && (
                <span className="invalid">{errors.arrAirportCd.message}</span>
              )}
            </div>
          </div>

          {/* Outward Date */}
          <div className="form-group">
            <label className="col-md-4 control-label">{t('search.outwardDate')}</label>
            <div className="col-md-8">
              <DatePicker
                selected={outwardDate}
                onChange={handleOutwardDateChange}
                dateFormat="yyyy/MM/dd"
                minDate={minDate}
                maxDate={maxDate}
                className="form-control"
                placeholderText="yyyy/mm/dd"
              />
              {errors.outwardDate && (
                <span className="invalid">{errors.outwardDate.message}</span>
              )}
            </div>
          </div>

          {/* Homeward Date (only for round trip) */}
          {flightType === 'RT' && (
            <div className="form-group">
              <label className="col-md-4 control-label">{t('search.homewardDate')}</label>
              <div className="col-md-8">
                <DatePicker
                  selected={homewardDate}
                  onChange={handleHomewardDateChange}
                  dateFormat="yyyy/MM/dd"
                  minDate={outwardDate || minDate}
                  maxDate={maxDate}
                  className="form-control"
                  placeholderText="yyyy/mm/dd"
                />
                {errors.homewardDate && (
                  <span className="invalid">{errors.homewardDate.message}</span>
                )}
              </div>
            </div>
          )}

          {/* Boarding Class */}
          <div className="form-group">
            <label className="col-md-4 control-label">{t('search.boardingClass')}</label>
            <div className="col-md-8">
              {BOARDING_CLASSES.map((bc) => (
                <label key={bc.code} className="radio-inline">
                  <input
                    type="radio"
                    value={bc.code}
                    {...register('boardingClassCd')}
                  />
                  {bc.name}
                </label>
              ))}
              {errors.boardingClassCd && (
                <span className="invalid">{errors.boardingClassCd.message}</span>
              )}
            </div>
          </div>

          {/* Submit */}
          <div className="form-group">
            <div className="col-md-offset-4 col-md-8">
              <button
                type="submit"
                id="flights-search-button"
                className="btn btn-primary"
              >
                {t('search.submit')}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
