#include <math.h>

#define STATE_INPUT 1
#define STATE_INTEGRAL 2
#define STATE_TRIG_HIGH 3
#define STATE_TRIG_RAW 4

static double ngf_clamp(double x, double lo, double hi)
{
    if (x < lo)
        return lo;
    if (x > hi)
        return hi;
    return x;
}

static int ngf_schmitt(double raw, double prev_high, double vth, double vhyst)
{
    double half = 0.5 * fabs(vhyst);
    double rise = vth + half;
    double fall = vth - half;

    if (prev_high != 0.0)
        return raw > fall;
    return raw >= rise;
}

void ucm_ng_int_rst(ARGS)
{
    double in;
    double raw;
    double out;
    double partial;
    double *input_state;
    double *state;
    double *trig_high;
    double *prev_trig_high;
    double *trig_raw;
    int high;
    int prev_high;
    int do_reset;
    int err;

    if (INIT) {
        cm_analog_alloc(STATE_INPUT, sizeof(double));
        cm_analog_alloc(STATE_INTEGRAL, sizeof(double));
        cm_analog_alloc(STATE_TRIG_HIGH, sizeof(double));
        cm_analog_alloc(STATE_TRIG_RAW, sizeof(double));
    }

    input_state = (double *) cm_analog_get_ptr(STATE_INPUT, 0);
    state = (double *) cm_analog_get_ptr(STATE_INTEGRAL, 0);
    trig_high = (double *) cm_analog_get_ptr(STATE_TRIG_HIGH, 0);
    prev_trig_high = (double *) cm_analog_get_ptr(STATE_TRIG_HIGH, 1);
    trig_raw = (double *) cm_analog_get_ptr(STATE_TRIG_RAW, 0);

    raw = INPUT(rst);
    if (INIT) {
        *state = PARAM(ic);
        *trig_high = ngf_schmitt(raw, 0.0, PARAM(vth), PARAM(vhyst)) ? 1.0 : 0.0;
        *trig_raw = raw;
    }

    prev_high = (*prev_trig_high != 0.0);
    high = ngf_schmitt(raw, *trig_high, PARAM(vth), PARAM(vhyst));

    if (ANALYSIS != TRANSIENT || TIME == 0.0) {
        *trig_high = high ? 1.0 : 0.0;
        *trig_raw = raw;
        OUTPUT(out) = *state;
        PARTIAL(out, in) = 0.0;
        PARTIAL(out, rst) = 0.0;
        return;
    }

    in = PARAM(gain) * INPUT(in);

    do_reset = 0;
    if (PARAM(mode) == 0)
        do_reset = high;
    else if (PARAM(mode) == 1)
        do_reset = (!prev_high && high);
    else if (PARAM(mode) == 2)
        do_reset = (prev_high && !high);

    if (do_reset) {
        *state = PARAM(ic);
        out = PARAM(ic);
        partial = 0.0;
    } else {
        *input_state = in;
        if (PARAM(aw_enable)) {
            if (*state >= PARAM(hi) && in > 0.0)
                *input_state = 0.0;
            else if (*state <= PARAM(lo) && in < 0.0)
                *input_state = 0.0;
        }

        err = cm_analog_integrate(*input_state, state, &partial);
        if (err)
            cm_message_send(cm_message_get_errmsg());
        out = ngf_clamp(*state, PARAM(lo), PARAM(hi));
        *state = out;
        if (PARAM(aw_enable) && *input_state == 0.0)
            partial = 0.0;
    }

    *trig_high = high ? 1.0 : 0.0;
    *trig_raw = raw;

    OUTPUT(out) = out;
    PARTIAL(out, in) = partial * PARAM(gain);
    PARTIAL(out, rst) = 0.0;
}
