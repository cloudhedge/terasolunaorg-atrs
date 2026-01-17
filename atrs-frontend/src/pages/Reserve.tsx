/**
 * Reservation Form page - migrated from reserveForm.jsp
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm, FormProvider } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useTranslation } from 'react-i18next';
import { useReserveStore } from '../stores/reserveStore';
import { useAuthStore } from '../stores/authStore';
import { formatDateWithWeekday, formatTime, formatCurrency } from '../utils/formatters';
import { GENDERS, BOARDING_CLASSES } from '../types';
import type { Gender } from '../types';

const passengerSchema = z.object({
  familyName: z.string().min(1, 'Required'),
  givenName: z.string().min(1, 'Required'),
  age: z.number().min(0).max(150),
  gender: z.enum(['M', 'F']),
  customerNo: z.string().optional(),
});

const representativeSchema = z.object({
  familyName: z.string().min(1, 'Required'),
  givenName: z.string().min(1, 'Required'),
  age: z.number().min(0).max(150),
  gender: z.enum(['M', 'F']),
  tel: z.string().min(1, 'Required'),
  email: z.string().email('Invalid email'),
  customerNo: z.string().optional(),
});

const reserveFormSchema = z.object({
  passengers: z.array(passengerSchema).min(1).max(6),
  representative: representativeSchema,
});

type ReserveFormData = z.infer<typeof reserveFormSchema>;

export default function Reserve() {
  const { t } = useTranslation('reserve');
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuthStore();
  const { outwardFlight, returnFlight, setPassengers, setRepresentative } = useReserveStore();

  const [passengerCount, setPassengerCount] = useState(1);

  // Redirect if no flights selected
  if (!outwardFlight) {
    navigate('/flights');
    return null;
  }

  const defaultPassenger = {
    familyName: '',
    givenName: '',
    age: 0,
    gender: 'M' as Gender,
    customerNo: '',
  };

  const defaultRepresentative = isAuthenticated && user
    ? {
        familyName: user.name?.split(' ')[0] || '',
        givenName: user.name?.split(' ')[1] || '',
        age: 30,
        gender: 'M' as Gender,
        tel: '',
        email: user.email || '',
        customerNo: user.membershipNumber,
      }
    : {
        familyName: '',
        givenName: '',
        age: 0,
        gender: 'M' as Gender,
        tel: '',
        email: '',
        customerNo: '',
      };

  const methods = useForm<ReserveFormData>({
    resolver: zodResolver(reserveFormSchema),
    defaultValues: {
      passengers: [defaultPassenger],
      representative: defaultRepresentative,
    },
  });

  const { register, handleSubmit, formState: { errors }, watch, setValue } = methods;

  const handleAddPassenger = () => {
    if (passengerCount < 6) {
      const currentPassengers = watch('passengers');
      setValue('passengers', [...currentPassengers, defaultPassenger]);
      setPassengerCount(passengerCount + 1);
    }
  };

  const handleCopyToRepresentative = () => {
    const passenger1 = watch('passengers.0');
    setValue('representative.familyName', passenger1.familyName);
    setValue('representative.givenName', passenger1.givenName);
    setValue('representative.age', passenger1.age);
    setValue('representative.gender', passenger1.gender);
    setValue('representative.customerNo', passenger1.customerNo);
  };

  const onSubmit = (data: ReserveFormData) => {
    // Save to store
    setPassengers(data.passengers.map(p => ({
      family_name: p.familyName,
      given_name: p.givenName,
      age: p.age,
      gender: p.gender,
      customer_no: p.customerNo,
    })));
    
    setRepresentative({
      familyName: data.representative.familyName,
      givenName: data.representative.givenName,
      age: data.representative.age,
      gender: data.representative.gender,
      tel: data.representative.tel,
      email: data.representative.email,
      customerNo: data.representative.customerNo,
    });

    navigate('/reserve/confirm');
  };

  const handleBack = () => {
    navigate(-1);
  };

  return (
    <div className="row">
      <section className="col-md-12">
        <h2 id="screen-title">{t('title')}</h2>

        {/* Selected Flights Table */}
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
              {outwardFlight && (
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
              )}
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

        <FormProvider {...methods}>
          <form className="form-horizontal passengers" onSubmit={handleSubmit(onSubmit)}>
            {/* Passengers */}
            <section>
              <h3>{t('customerInfo')}</h3>

              {Array.from({ length: passengerCount }).map((_, index) => (
                <div key={index} id={`passenger${index + 1}`}>
                  <h4>{t('passenger', { index: index + 1 })}</h4>

                  <div className="form-group">
                    <label className="col-md-2 control-label">{t('fields.name')}</label>
                    <div className="col-md-6">
                      <div className="input-group inline-half">
                        <label className="input-group-addon">{t('fields.familyName')}</label>
                        <input
                          className="form-control"
                          maxLength={10}
                          {...register(`passengers.${index}.familyName`)}
                        />
                      </div>
                      <div className="input-group inline-half">
                        <label className="input-group-addon">{t('fields.givenName')}</label>
                        <input
                          className="form-control"
                          maxLength={10}
                          {...register(`passengers.${index}.givenName`)}
                        />
                      </div>
                      {errors.passengers?.[index]?.familyName && (
                        <span className="invalid">{errors.passengers[index]?.familyName?.message}</span>
                      )}
                    </div>
                  </div>

                  <div className="form-group">
                    <label className="col-md-2 control-label">{t('fields.age')}</label>
                    <div className="col-md-3">
                      <input
                        type="number"
                        className="form-control"
                        {...register(`passengers.${index}.age`, { valueAsNumber: true })}
                      />
                      {errors.passengers?.[index]?.age && (
                        <span className="invalid">{errors.passengers[index]?.age?.message}</span>
                      )}
                    </div>
                  </div>

                  <div className="form-group">
                    <label className="col-md-2 control-label">{t('fields.gender')}</label>
                    <div className="col-md-4 form-inline">
                      {GENDERS.map((g) => (
                        <label key={g.code} className="radio-inline">
                          <input
                            type="radio"
                            value={g.code}
                            {...register(`passengers.${index}.gender`)}
                          />
                          {g.name}
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="form-group">
                    <label className="col-md-2 control-label">{t('fields.membershipNumber')}</label>
                    <div className="col-md-3">
                      <input
                        className="form-control"
                        maxLength={10}
                        {...register(`passengers.${index}.customerNo`)}
                      />
                    </div>
                  </div>
                </div>
              ))}

              {passengerCount < 6 && (
                <div className="form-group">
                  <div className="col-md-offset-2 col-md-8">
                    <button type="button" className="btn btn-default" onClick={handleAddPassenger}>
                      {t('addPassenger')}
                    </button>
                  </div>
                </div>
              )}
            </section>

            {/* Representative */}
            <section id="representative">
              <h3>{t('representative')}</h3>

              {!isAuthenticated && (
                <>
                  <div className="form-group">
                    <label className="col-md-2 control-label">{t('fields.name')}</label>
                    <div className="col-md-8">
                      <div className="input-group inline-half">
                        <label className="input-group-addon">{t('fields.familyName')}</label>
                        <input
                          className="form-control"
                          maxLength={10}
                          {...register('representative.familyName')}
                        />
                      </div>
                      <div className="input-group inline-half">
                        <label className="input-group-addon">{t('fields.givenName')}</label>
                        <input
                          className="form-control"
                          maxLength={10}
                          {...register('representative.givenName')}
                        />
                      </div>
                    </div>
                  </div>

                  <div className="form-group">
                    <label className="col-md-2 control-label">{t('fields.age')}</label>
                    <div className="col-md-3">
                      <input
                        type="number"
                        className="form-control"
                        {...register('representative.age', { valueAsNumber: true })}
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label className="col-md-2 control-label">{t('fields.gender')}</label>
                    <div className="col-md-8 form-inline">
                      {GENDERS.map((g) => (
                        <label key={g.code} className="radio-inline">
                          <input
                            type="radio"
                            value={g.code}
                            {...register('representative.gender')}
                          />
                          {g.name}
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="form-group">
                    <label className="col-md-2 control-label">{t('fields.membershipNumber')}</label>
                    <div className="col-md-3">
                      <input
                        className="form-control"
                        maxLength={10}
                        {...register('representative.customerNo')}
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label className="col-md-2 control-label">{t('fields.tel')}</label>
                    <div className="col-md-8">
                      <input
                        className="form-control"
                        {...register('representative.tel')}
                        placeholder="03-1234-5678"
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label className="col-md-2 control-label">{t('fields.email')}</label>
                    <div className="col-md-8">
                      <input
                        type="email"
                        className="form-control"
                        {...register('representative.email')}
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <div className="col-md-offset-2 col-md-8">
                      <button type="button" className="btn btn-default" onClick={handleCopyToRepresentative}>
                        {t('copyFromPassenger1')}
                      </button>
                    </div>
                  </div>
                </>
              )}

              {isAuthenticated && user && (
                <div>
                  <div className="form-group">
                    <label className="col-md-2 control-label">{t('fields.name')}</label>
                    <div className="col-md-8">
                      <p className="form-control-static">{user.name}</p>
                    </div>
                  </div>
                  <div className="form-group">
                    <label className="col-md-2 control-label">{t('fields.membershipNumber')}</label>
                    <div className="col-md-8">
                      <p className="form-control-static">{user.membershipNumber}</p>
                    </div>
                  </div>
                </div>
              )}
            </section>

            {/* Buttons */}
            <div className="text-center btns-block">
              <button type="submit" className="btn btn-primary btn-lg btns-block-rightest-btn">
                {t('confirm')}
              </button>
              <button type="button" className="btn btn-default btn-lg" onClick={handleBack}>
                {t('backToSearch')}
              </button>
            </div>
          </form>
        </FormProvider>
      </section>
    </div>
  );
}
