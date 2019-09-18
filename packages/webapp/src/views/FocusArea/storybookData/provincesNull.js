const provincesNull = value => ({
  name: 'Focus Area',
  id: value,
  national: {
    notices: ['This data will be available upon the release of the 2019-20 Provincial Budgets'],
    footnotes: [
      'sourceEquitable: Estimates for expenditure',
      'note: Other random text to test footer note for provincial equitable share'
    ],
    departments: [
    {
      name: 'Administration',
      amount: 695320000000,
      url: null
    },
    {
      name: 'Economic Statistics',
      amount: 493210000000,
      url: null
    },
    {
      name: 'Population & Social Statistics',
      amount: 202300000000,
      url: null
    },
    {
      name: 'Methodology, Standards & Reasearch',
      amount: 67400000000,
      url: null
    },
    {
      name: 'Statistical Support & Informatics',
      amount: 267100000000,
      url: null
    },
    {
      name: 'Statistical Collection & Outreach',
      amount: 608000000000,
      url: null
    },
    {
      name: 'Survey Operations',
      amount: 194740000000,
      url: null
    },
  ]},
  provincial: {
    notices: ['This is a notice that is showing because the provinces is null'],
    footnotes: [
      'source: Some random text to test footer for expenditure'
    ],
    provinces: null,
  }
});

export default provincesNull;
