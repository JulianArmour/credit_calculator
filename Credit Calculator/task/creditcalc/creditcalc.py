import math
import argparse
import sys


def annuity_present(n, i):
    effective = math.pow(1 + i, n)
    return i * effective / (effective - 1)


def present_annuity(n, i):
    return 1 / annuity_present(n, i)


def payments(annuity, present, i):
    return math.ceil(math.log(annuity / (annuity - i * present), 1 + i))


def nominal_monthly_i(nominal_yearly_i):
    return nominal_yearly_i / (12 * 100)


def diff_payment(period, principal, no_periods, i):
    return math.ceil(principal / no_periods
                     + i * principal * (1 - (period - 1) / no_periods))


def diff_payments(principal, no_periods, i):
    periods = range(1, 1 + no_periods)
    return [diff_payment(period, principal, no_periods, i) for period in periods]


def calc_periods_remaining(principal, payment, monthly_interest):
    no_payments = payments(payment, principal, monthly_interest)
    years_remaining = no_payments // 12
    months_remaining = no_payments - 12 * years_remaining
    return years_remaining, months_remaining


def calc_annuity(principal, no_payments, yr_interest):
    monthly_interest = nominal_monthly_i(yr_interest)
    return math.ceil(principal * annuity_present(no_payments, monthly_interest))


def calc_principal(payment, no_payments, yr_interest):
    monthly_interest = nominal_monthly_i(yr_interest)
    return math.ceil(payment * present_annuity(no_payments, monthly_interest))


def format_diff_payments(diff_pmts):
    pmt_stings = [f'Month {i}: paid out {pmt}' for i, pmt in enumerate(diff_pmts)]
    return '\n'.join(pmt_stings)


def format_annuity(no_years, no_months):
    years_txt = 'year' if no_years == 1 else 'years'
    months_txt = 'month' if no_months == 1 else 'months'
    if not no_years:
        return f'You need {no_months} {months_txt} to repay this credit!'
    if not no_months:
        return f'You need {no_years} {years_txt} to repay this credit!'
    return f'you need {no_years} {years_txt} and {no_months} {months_txt} to repay this credit!'


def invalid_diff_args(arguments):
    return None in (arguments.principal, arguments.periods)


def invalid_annuity_args(arguments):
    return list(vars(arguments).values()).count(None) != 1


def overpayment(principal, *pmts):
    return sum(pmts) - principal


def invalid_program_arguments(arguments):
    return len(vars(arguments)) != 5 \
           or arguments.type not in ('annuity', 'diff') \
           or not arguments.interest \
           or arguments.type == 'diff' and invalid_diff_args(arguments) \
           or arguments.type == 'annuity' and invalid_annuity_args(arguments)


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--type')
arg_parser.add_argument('--principal', type=int)
arg_parser.add_argument('--payment', type=int)
arg_parser.add_argument('--periods', type=int)
arg_parser.add_argument('--interest', type=float)
args = arg_parser.parse_args()

if invalid_program_arguments(args):
    print('Incorrect parameters.')
    sys.exit()

monthly_i = nominal_monthly_i(args.interest)
over_pmt = 0
if args.type == 'diff':
    differential_pmts = diff_payments(args.principal, args.periods, monthly_i)
    over_pmt = overpayment(args.principal, *differential_pmts)
    print(format_diff_payments(differential_pmts))
    print()
elif args.type == 'annuity':
    if not args.payment:
        monthly_pmt = math.ceil(args.principal * annuity_present(args.periods, monthly_i))
        over_pmt = overpayment(args.principal, args.periods * monthly_pmt)
        print(f'Your annuity payment = {math.ceil(monthly_pmt)}!')
    elif not args.principal:
        credit_principal = math.ceil(args.payment * present_annuity(args.periods, monthly_i))
        over_pmt = overpayment(credit_principal, args.periods * args.payment)
        print(f'Your credit principal = {credit_principal}!')
    elif not args.periods:
        years, months = calc_periods_remaining(args.principal, args.payment, monthly_i)
        total_periods = 12 * years + months
        over_pmt = overpayment(args.principal, total_periods * args.payment)
        print(format_annuity(years, months))
print(f'Overpayment = {over_pmt}')
