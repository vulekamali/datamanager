
def sort_categories(revenue_data):
    """
    Need to sort the category data so that its matches what is
    showed in the national budget.
    """
    revenue = []
    duties_total = 0
    other_total = 0
    for r in revenue_data:
        if ('duties' in r['category_two']) or ('duty' in r['category_two']):
            duties_total += int(r['amount'])

        elif 'income tax' in r['category_two']:
            revenue.append(
                {
                    'category': r['category_two'],
                    'amount': r['amount']
                }
            )
        elif 'Value-added tax' in r['category_two']:
            revenue.append(
                {
                    'category': r['category_two'],
                    'amount': r['amount']
                }
            )
        elif 'General fuel levy' in r['category_two']:
            revenue.append(
                {
                    'category': r['category_two'],
                    'amount': r['amount']
                }
            )
        else:
            other_total += int(r['amount'])
    revenue.append(
        {
            'category': 'Customs and Excise Duties',
            'amount': duties_total
        }
    )
    revenue.append(
        {
            'category': 'Other',
            'amount': other_total
        }
    )
    return revenue
