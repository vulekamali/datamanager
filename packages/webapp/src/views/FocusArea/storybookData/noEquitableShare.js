const allComponents = value => ({
  name: 'Focus Area',
  id: value,
  national: {
    notices: ['This data will be available upon the release of the 2019-20 Provincial Budgets'],
    footnotes: [
      'source: random text footer for expenditure',
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
    notices: ['This is a string inside of an array of strings for notices'],
    footnotes: [
      'source: Some random text to test footer expenditure'
    ],
    provinces: {
      'Eastern Cape': {
        name: 'Eastern Cape',
        amount: 78433947071.99603,
        percentage: 13.257633039392502,
        children: [
          {
            amount: 983800097.958883,
            name: 'Cooperative Governance And Traditional Affairs',
            province: 'Eastern Cape',
            id: 'cooperative-governance-and-traditional-affairs',
            percentage: 0,
          },
          {
            amount: 1146006188,
            name: 'Economic Development, Environmental Affairs And Tourism',
            province: 'Eastern Cape',
            id: 'economic-development-environmental-affairs-and-tourism',
            percentage: 0,
          },
          {
            amount: 34772125813.66324,
            name: 'Education',
            province: 'Eastern Cape',
            id: 'education',
            percentage: 0,
          },
          {
            amount: 23699560300.5,
            name: 'Health',
            province: 'Eastern Cape',
            id: 'health',
            percentage: 0,
          },
          {
            amount: 2376749000,
            name: 'Human Settlements',
            province: 'Eastern Cape',
            id: 'human-settlements',
            percentage: 0,
          },
          {
            amount: 973396122,
            name: 'Office Of The Premier',
            province: 'Eastern Cape',
            id: 'office-of-the-premier',
            percentage: 0,
          },
          {
            amount: 525999443.3629,
            name: 'Provincial Legislature',
            province: 'Eastern Cape',
            id: 'provincial-legislature',
            percentage: 0,
          },
          {
            amount: 591487000,
            name: 'Provincial Treasury',
            province: 'Eastern Cape',
            id: 'provincial-treasury',
            percentage: 0,
          },
          {
            amount: 2344172000,
            name: 'Roads And Public Works',
            province: 'Eastern Cape',
            id: 'roads-and-public-works',
            percentage: 0,
          },
          {
            amount: 2328236322.4110003,
            name: 'Rural Development And Agrarian Reform',
            province: 'Eastern Cape',
            id: 'rural-development-and-agrarian-reform',
            percentage: 0,
          },
          {
            amount: 101490000,
            name: 'Safety And Liaison',
            province: 'Eastern Cape',
            id: 'safety-and-liaison',
            percentage: 0,
          },
          {
            amount: 2836581000,
            name: 'Social Development',
            province: 'Eastern Cape',
            id: 'social-development',
            percentage: 0,
          },
          {
            amount: 942759682.6,
            name: 'Sport, Recreation, Arts And Culture',
            province: 'Eastern Cape',
            id: 'sport-recreation-arts-and-culture',
            percentage: 0,
          },
          {
            amount: 4811584101.5,
            name: 'Transport',
            province: 'Eastern Cape',
            id: 'transport',
            percentage: 0,
          },
        ],
      },
      'Free State': {
        name: 'Free State',
        amount: 34877227030,
        percentage: 5.89527232348622,
        children: [
          {
            amount: 810479000,
            name: 'Agriculture And Rural Development',
            province: 'Free State',
            id: 'agriculture-and-rural-development',
            percentage: 0,
          },
          {
            amount: 443329000,
            name: 'Cooperative Governance And Traditional Affairs',
            province: 'Free State',
            id: 'cooperative-governance-and-traditional-affairs',
            percentage: 0,
          },
          {
            amount: 631931000,
            name:
              'Economic And Small Business Development, Tourism And Environmental Affairs',
            province: 'Free State',
            id:
              'economic-and-small-business-development-tourism-and-environmental-affairs',
            percentage: 0,
          },
          {
            amount: 13579224000,
            name: 'Education',
            province: 'Free State',
            id: 'education',
            percentage: 0,
          },
          {
            amount: 253118000,
            name: 'Free State Legislature',
            province: 'Free State',
            id: 'free-state-legislature',
            percentage: 0,
          },
          {
            amount: 10403313000,
            name: 'Health',
            province: 'Free State',
            id: 'health',
            percentage: 0,
          },
          {
            amount: 1391778000,
            name: 'Human Settlements',
            province: 'Free State',
            id: 'human-settlements',
            percentage: 0,
          },
          {
            amount: 2776609000,
            name: 'Police, Roads And Transport',
            province: 'Free State',
            id: 'police-roads-and-transport',
            percentage: 0,
          },
          {
            amount: 611279000,
            name: 'Premier',
            province: 'Free State',
            id: 'premier',
            percentage: 0,
          },
          {
            amount: 347832000,
            name: 'Provincial Treasury',
            province: 'Free State',
            id: 'provincial-treasury',
            percentage: 0,
          },
          {
            amount: 1635268000,
            name: 'Public Works And Infrastructure',
            province: 'Free State',
            id: 'public-works-and-infrastructure',
            percentage: 0,
          },
          {
            amount: 1266057000,
            name: 'Social Development',
            province: 'Free State',
            id: 'social-development',
            percentage: 0,
          },
          {
            amount: 727010030,
            name: 'Sport, Arts, Culture And Recreation',
            province: 'Free State',
            id: 'sport-arts-culture-and-recreation',
            percentage: 0,
          },
        ],
      },
    }  
  }
});

export default allComponents;
