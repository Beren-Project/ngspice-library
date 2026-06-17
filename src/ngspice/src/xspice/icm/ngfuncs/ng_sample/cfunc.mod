#include <math.h>

#define STATE_HELD 1
#define STATE_TRIG_HIGH 2
#define STATE_TRIG_RAW 3

static int ngf_schmitt(double raw, double prev_high, double vth, double vhyst)
{
    double half = 0.5 * fabs(vhyst);
    double rise = vth + half;
    double fall = vth - half;

    if (prev_high != 0.0)
        return raw > fall;
    return raw >= rise;
}

void ucm_ng_sample(ARGS)
{
    double *held;
    double *trig_high;
    double *prev_trig_high;
    double *trig_raw;
    double raw;
    int high;
    int prev_high;
    int sample;

    if (INIT) {
        cm_analog_alloc(STATE_HELD, sizeof(double));
        cm_analog_alloc(STATE_TRIG_HIGH, sizeof(double));
        cm_analog_alloc(STATE_TRIG_RAW, sizeof(double));
    }

    held = (double *) cm_analog_get_ptr(STATE_HELD, 0);
    trig_high = (double *) cm_analog_get_ptr(STATE_TRIG_HIGH, 0);
    prev_trig_high = (double *) cm_analog_get_ptr(STATE_TRIG_HIGH, 1);
    trig_raw = (double *) cm_analog_get_ptr(STATE_TRIG_RAW, 0);

    raw = INPUT(trig);
    if (INIT) {
        *held = PARAM(ic);
        *trig_high = ngf_schmitt(raw, 0.0, PARAM(vth), PARAM(vhyst)) ? 1.0 : 0.0;
        *trig_raw = raw;
    }

    prev_high = (*prev_trig_high != 0.0);
    high = ngf_schmitt(raw, *trig_high, PARAM(vth), PARAM(vhyst));

    if (ANALYSIS != TRANSIENT || TIME == 0.0) {
        *trig_high = high ? 1.0 : 0.0;
        *trig_raw = raw;
        OUTPUT(out) = *held;
        PARTIAL(out, in) = 0.0;
        PARTIAL(out, trig) = 0.0;
        return;
    }

    sample = 0;
    if (PARAM(edge) == 1)
        sample = (!prev_high && high);
    else if (PARAM(edge) == 2)
        sample = (prev_high && !high);

    if (sample)
        *held = INPUT(in);

    *trig_high = high ? 1.0 : 0.0;
    *trig_raw = raw;

    OUTPUT(out) = *held;
    PARTIAL(out, in) = 0.0;
    PARTIAL(out, trig) = 0.0;
}
