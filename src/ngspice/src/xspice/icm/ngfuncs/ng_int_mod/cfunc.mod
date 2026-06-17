#include <math.h>

#define STATE_INPUT 1
#define STATE_INTEGRAL 2

static double ngf_mod_wrap(double value, double ic, double modulus)
{
    double rel = value - ic;
    double wrapped = fmod(rel, modulus);

    if (wrapped < 0.0)
        wrapped += modulus;
    return ic + wrapped;
}

static double ngf_clamp_mod(double x, double lo, double hi)
{
    if (x < lo)
        return lo;
    if (x > hi)
        return hi;
    return x;
}

void ucm_ng_int_mod(ARGS)
{
    double *input_state;
    double *state;
    double partial;
    double value;
    int err;

    if (INIT) {
        cm_analog_alloc(STATE_INPUT, sizeof(double));
        cm_analog_alloc(STATE_INTEGRAL, sizeof(double));
    }

    input_state = (double *) cm_analog_get_ptr(STATE_INPUT, 0);
    state = (double *) cm_analog_get_ptr(STATE_INTEGRAL, 0);

    if (INIT)
        *state = PARAM(ic);

    if (ANALYSIS != TRANSIENT || TIME == 0.0) {
        OUTPUT(out) = ngf_clamp_mod(*state, PARAM(lo), PARAM(hi));
        PARTIAL(out, in) = 0.0;
        return;
    }

    *input_state = PARAM(gain) * INPUT(in);
    err = cm_analog_integrate(*input_state, state, &partial);
    if (err)
        cm_message_send(cm_message_get_errmsg());

    value = ngf_mod_wrap(*state, PARAM(ic), PARAM(modulus));
    value = ngf_clamp_mod(value, PARAM(lo), PARAM(hi));
    *state = value;

    OUTPUT(out) = value;
    PARTIAL(out, in) = partial * PARAM(gain);
}
