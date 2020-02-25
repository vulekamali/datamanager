const calcFineprint = year => {
  if (year === '2018-19') {
    return 'Budget data from 1 April 2018 - 31 March 2019'
  }

  if (year === '2019-20') {
    return 'Budget data from 1 April 2019 - 31 March 2020'
  }

  return '';
}

export default calcFineprint;