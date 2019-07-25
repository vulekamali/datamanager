import React from 'react';
import { storiesOf } from '@storybook/react';
import Infrastructure from './index';


const props = {
  datasetUrl: "123",
  projects: [
    {
      "id": "/infrastructure-projects/water-and-sanitation-calitzdorp-and-ladismith-w",
      "subheading": "Water and Sanitation",
      "heading": "Calitzdorp and Ladismith W",
      "points": [
        {
          "id": "0",
          "x": 21.599253,
          "y": -33.517731
        }
      ],
      "activeProvinces": [
        "Western Cape"
      ],
      "stage": "Feasibility",
      "totalBudget": 77459000,
      "projectedBudget": 75000000,
      "description": "Upgrading of wastewater treatment works",
      "link": "/infrastructure-projects/water-and-sanitation-calitzdorp-and-ladismith-w",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 0,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 0,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 0,
          "Projected": null,
          "Connection": 0
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 0,
          "Connection": 0
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 15000000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 30000000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 30000000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "Upgrading and additions",
        "infrastructure": "Waste Water Services",
        "department": {
          "budget_document": null,
          "name": "Water and Sanitation",
          "url": "/2019-20/national/departments/water-and-sanitation"
        }
      }
    },
    {
      "id": "/infrastructure-projects/transport-cape-towns-metro-southeast-myciti-phase-2a",
      "subheading": "Transport",
      "heading": "Cape Town's metro Southeast (MyCiti phase 2A)",
      "points": [
        {
          "id": "0",
          "x": 18.419422,
          "y": -33.913362
        }
      ],
      "activeProvinces": [
        "Western Cape"
      ],
      "stage": "Construction",
      "totalBudget": 7100000000,
      "projectedBudget": 2832000000,
      "description": "Bus rapid transport network in Cape Town",
      "link": "/infrastructure-projects/transport-cape-towns-metro-southeast-myciti-phase-2a",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 0,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 0,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 0,
          "Projected": null,
          "Connection": 0
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 33000000,
          "Connection": 33000000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 354000000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 1045000000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 1433000000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "Upgrades and additions",
        "infrastructure": "Public transport",
        "department": {
          "budget_document": null,
          "name": "Transport",
          "url": "/2019-20/national/departments/transport"
        }
      }
    },
    {
      "id": "/infrastructure-projects/justice-and-constitutional-development-durban-high-court",
      "subheading": "Justice and Constitutional Development",
      "heading": "Durban high court",
      "points": [
        {
          "id": "0",
          "x": 31.020099,
          "y": -29.861855
        }
      ],
      "activeProvinces": [
        "KwaZulu-Natal"
      ],
      "stage": "Design",
      "totalBudget": 902659000,
      "projectedBudget": 557228000,
      "description": "Expansion of accommodation",
      "link": "/infrastructure-projects/justice-and-constitutional-development-durban-high-court",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 2978000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 19608000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 27381000,
          "Projected": null,
          "Connection": 27381000
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 33935000,
          "Connection": 33935000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 175910000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 180002000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 201316000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "New infrastructure assets",
        "infrastructure": "High Court",
        "department": {
          "budget_document": null,
          "name": "Justice and Constitutional Development",
          "url": "/2019-20/national/departments/justice-and-constitutional-development"
        }
      }
    },
    {
      "id": "/infrastructure-projects/health-eastern-cape-bambisana-hospital",
      "subheading": "Health",
      "heading": "Eastern Cape: Bambisana hospital",
      "points": [
        {
          "id": "0",
          "x": 29.45397,
          "y": -31.45019
        }
      ],
      "activeProvinces": [
        "Eastern Cape"
      ],
      "stage": "Design",
      "totalBudget": 700113000,
      "projectedBudget": 172182000,
      "description": "Emergency repairs and revitalisation",
      "link": "/infrastructure-projects/health-eastern-cape-bambisana-hospital",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 155000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 14184000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 24708000,
          "Projected": null,
          "Connection": 24708000
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 0,
          "Connection": 0
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 71700000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 41819000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 58663000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "Maintenance and Upgrades",
        "infrastructure": "District Hospital",
        "department": {
          "budget_document": null,
          "name": "Health",
          "url": "/2019-20/national/departments/health"
        }
      }
    },
    {
      "id": "/infrastructure-projects/health-free-state-dihlabeng-hospital",
      "subheading": "Health",
      "heading": "Free State:  Dihlabeng hospital",
      "points": [
        {
          "id": "0",
          "x": 28.3197,
          "y": -28.23317
        }
      ],
      "activeProvinces": [
        "Free State"
      ],
      "stage": "Construction",
      "totalBudget": 312313000,
      "projectedBudget": 121000000,
      "description": "Upgrades and maintenance of hospital",
      "link": "/infrastructure-projects/health-free-state-dihlabeng-hospital",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 7431000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 25426000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 8270000,
          "Projected": null,
          "Connection": 8270000
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 18931000,
          "Connection": 18931000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 55000000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 40000000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 26000000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "Maintenance and Upgrades",
        "infrastructure": "District and regional hospitals",
        "department": {
          "budget_document": null,
          "name": "Health",
          "url": "/2019-20/national/departments/health"
        }
      }
    },
    {
      "id": "/infrastructure-projects/health-free-state-lusaka-community-health-centre",
      "subheading": "Health",
      "heading": "Free State: Lusaka community health centre",
      "points": [
        {
          "id": "0",
          "x": 26.69797,
          "y": -28.41668
        }
      ],
      "activeProvinces": [
        "Free State"
      ],
      "stage": "Design",
      "totalBudget": 250000000,
      "projectedBudget": 91098000,
      "description": "Replacement of community health centre",
      "link": "/infrastructure-projects/health-free-state-lusaka-community-health-centre",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 935000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 663000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 2434000,
          "Projected": null,
          "Connection": 2434000
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 1702000,
          "Connection": 1702000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 33784000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 34477000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 22837000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "New infrastructure assets",
        "infrastructure": "Community health Centre",
        "department": {
          "budget_document": null,
          "name": "Health",
          "url": "/2019-20/national/departments/health"
        }
      }
    },
    {
      "id": "/infrastructure-projects/water-and-sanitation-giyani-water-services-phase-2",
      "subheading": "Water and Sanitation",
      "heading": "Giyani water services phase 2",
      "points": [
        {
          "id": "0",
          "x": 30.726936,
          "y": -23.305826
        }
      ],
      "activeProvinces": [
        "Limpopo"
      ],
      "stage": "Construction",
      "totalBudget": 2754644000,
      "projectedBudget": 408285000,
      "description": "Construction of new bulk water scheme and upgrading of existing bulk water scheme",
      "link": "/infrastructure-projects/water-and-sanitation-giyani-water-services-phase-2",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 799829000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 912578000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 633952000,
          "Projected": null,
          "Connection": 633952000
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 214500000,
          "Connection": 214500000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 114027000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 150000000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 144258000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "Upgrading and additions",
        "infrastructure": "Bulk Water Supply",
        "department": {
          "budget_document": null,
          "name": "Water and Sanitation",
          "url": "/2019-20/national/departments/water-and-sanitation"
        }
      }
    },
    {
      "id": "/infrastructure-projects/water-and-sanitation-limpopo-region",
      "subheading": "Water and Sanitation",
      "heading": "Limpopo region",
      "points": [],
      "activeProvinces": [
        "Limpopo"
      ],
      "stage": "Construction",
      "totalBudget": 0,
      "projectedBudget": 950525000,
      "description": "Construction of water supply and sanitation backlog",
      "link": "/infrastructure-projects/water-and-sanitation-limpopo-region",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 178353000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 20263000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 5143000,
          "Projected": null,
          "Connection": 5143000
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 233002000,
          "Connection": 233002000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 170233000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 360600000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 419692000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "Upgrading and additions",
        "infrastructure": "Water supply and sanitation",
        "department": {
          "budget_document": null,
          "name": "Water and Sanitation",
          "url": "/2019-20/national/departments/water-and-sanitation"
        }
      }
    },
    {
      "id": "/infrastructure-projects/health-limpopo-academic-hospital",
      "subheading": "Health",
      "heading": "Limpopo:  Academic hospital",
      "points": [
        {
          "id": "0",
          "x": 29.479913,
          "y": -23.91781
        }
      ],
      "activeProvinces": [
        "Limpopo"
      ],
      "stage": "Feasibility",
      "totalBudget": 3963000000,
      "projectedBudget": 1398000000,
      "description": "Construction of new hospital",
      "link": "/infrastructure-projects/health-limpopo-academic-hospital",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 0,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 14941000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 7466000,
          "Projected": null,
          "Connection": 7466000
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 190059000,
          "Connection": 190059000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 247000000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 653000000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 498000000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "New infrastructure assets",
        "infrastructure": "Tertiary hospital",
        "department": {
          "budget_document": null,
          "name": "Health",
          "url": "/2019-20/national/departments/health"
        }
      }
    },
    {
      "id": "/infrastructure-projects/health-limpopo-chebeng-community-health-centre",
      "subheading": "Health",
      "heading": "Limpopo: Chebeng community health centre",
      "points": [
        {
          "id": "0",
          "x": 29.2702404,
          "y": -23.8157864
        }
      ],
      "activeProvinces": [
        "Limpopo"
      ],
      "stage": "Tender",
      "totalBudget": 219646000,
      "projectedBudget": 104082000,
      "description": "Replacement of community health centre",
      "link": "/infrastructure-projects/health-limpopo-chebeng-community-health-centre",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 959000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 642000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 3837000,
          "Projected": null,
          "Connection": 3837000
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 4000000,
          "Connection": 4000000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 9041000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 55041000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 40000000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "New infrastructure assets",
        "infrastructure": "Community health Centre",
        "department": {
          "budget_document": null,
          "name": "Health",
          "url": "/2019-20/national/departments/health"
        }
      }
    },
    {
      "id": "/infrastructure-projects/police-member-and-office-accommodation",
      "subheading": "Police",
      "heading": "Member and office accommodation",
      "points": [
        {
          "id": "0",
          "x": 27.1454,
          "y": -25.4007
        }
      ],
      "activeProvinces": [
        "North West"
      ],
      "stage": "Construction",
      "totalBudget": 756079000,
      "projectedBudget": 479891000,
      "description": "Construction of living quarters and offices",
      "link": "/infrastructure-projects/police-member-and-office-accommodation",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 69964000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 32905000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 42135000,
          "Projected": null,
          "Connection": 42135000
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 131184000,
          "Connection": 131184000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 142768000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 162469000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 174654000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "Upgrading and additions",
        "infrastructure": "Office accommodation and living quarters",
        "department": {
          "budget_document": null,
          "name": "Police",
          "url": "/2019-20/national/departments/police"
        }
      }
    },
    {
      "id": "/infrastructure-projects/water-and-sanitation-misgund-bulk-water-supply",
      "subheading": "Water and Sanitation",
      "heading": "Misgund bulk water supply",
      "points": [
        {
          "id": "0",
          "x": 23.445781,
          "y": -33.765182
        }
      ],
      "activeProvinces": [
        "Eastern Cape"
      ],
      "stage": "Feasibility",
      "totalBudget": 41674000,
      "projectedBudget": 35000000,
      "description": "Construction of new bulk water scheme and Upgrading of existing bulk water scheme",
      "link": "/infrastructure-projects/water-and-sanitation-misgund-bulk-water-supply",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 422000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 1557000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 695000,
          "Projected": null,
          "Connection": 695000
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 4000000,
          "Connection": 4000000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 0,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 5000000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 30000000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "New infrastructure assets",
        "infrastructure": "Bulk Water Supply",
        "department": {
          "budget_document": null,
          "name": "Water and Sanitation",
          "url": "/2019-20/national/departments/water-and-sanitation"
        }
      }
    },
    {
      "id": "/infrastructure-projects/water-and-sanitation-mogalakwena-bulk-water-supply-phase-1",
      "subheading": "Water and Sanitation",
      "heading": "Mogalakwena bulk water supply phase 1",
      "points": [
        {
          "id": "0",
          "x": 28.611827,
          "y": -23.745589
        }
      ],
      "activeProvinces": [
        "Limpopo"
      ],
      "stage": "Construction",
      "totalBudget": 1399590000,
      "projectedBudget": 733558000,
      "description": "Upgrading of boreholes and construction of new bulk water scheme",
      "link": "/infrastructure-projects/water-and-sanitation-mogalakwena-bulk-water-supply-phase-1",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 252788000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 161067000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 142177000,
          "Projected": null,
          "Connection": 142177000
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 110000000,
          "Connection": 110000000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 183558000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 250000000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 300000000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "Upgrading and additions",
        "infrastructure": "Bulk Water Supply",
        "department": {
          "budget_document": null,
          "name": "Water and Sanitation",
          "url": "/2019-20/national/departments/water-and-sanitation"
        }
      }
    },
    {
      "id": "/infrastructure-projects/health-mpumalanga-balfour-community-health-centre-24-hour-mini-hospital",
      "subheading": "Health",
      "heading": "Mpumalanga: Balfour community health centre (24-hour mini-hospital)",
      "points": [
        {
          "id": "0",
          "x": 28.6043845,
          "y": -26.6466909
        }
      ],
      "activeProvinces": [
        "Mpumalanga"
      ],
      "stage": "Design",
      "totalBudget": 299123000,
      "projectedBudget": 111000000,
      "description": "Replacement of community health centre",
      "link": "/infrastructure-projects/health-mpumalanga-balfour-community-health-centre-24-hour-mini-hospital",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 432000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 190000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 342000,
          "Projected": null,
          "Connection": 342000
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 1500000,
          "Connection": 1500000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 20000000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 31000000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 60000000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "New infrastructure assets",
        "infrastructure": "Community health Centre",
        "department": {
          "budget_document": null,
          "name": "Health",
          "url": "/2019-20/national/departments/health"
        }
      }
    },
    {
      "id": "/infrastructure-projects/health-non-capital-infrastructure-projects-including-maintenance-national-health-insurance-facilities",
      "subheading": "Health",
      "heading": "Non-capital infrastructure projects, including maintenance (national health insurance facilities)",
      "points": [],
      "activeProvinces": [],
      "stage": "Ongoing",
      "totalBudget": 684500000,
      "projectedBudget": 90000000,
      "description": "Maintenance, provision of provincial management support units and project management information systems, conditional assessments of facilities in national health insurance scheme pilot districts, in loco supervision, monitoring of 10-year health infrastructure",
      "link": "/infrastructure-projects/health-non-capital-infrastructure-projects-including-maintenance-national-health-insurance-facilities",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 205419000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 105376000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 81832000,
          "Projected": null,
          "Connection": 81832000
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 70000000,
          "Connection": 70000000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 50000000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 30000000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 10000000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "Maintenance and repair",
        "infrastructure": "Various",
        "department": {
          "budget_document": null,
          "name": "Health",
          "url": "/2019-20/national/departments/health"
        }
      }
    },
    {
      "id": "/infrastructure-projects/water-and-sanitation-north-west-region",
      "subheading": "Water and Sanitation",
      "heading": "North West region",
      "points": [],
      "activeProvinces": [
        "North West"
      ],
      "stage": "Construction",
      "totalBudget": 0,
      "projectedBudget": 507556000,
      "description": "Construction of water supply and sanitation backlog",
      "link": "/infrastructure-projects/water-and-sanitation-north-west-region",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 7186000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 1154000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 69120000,
          "Projected": null,
          "Connection": 69120000
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 502324000,
          "Connection": 502324000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 115000000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 212556000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 180000000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "Upgrading and additions",
        "infrastructure": "Water supply and sanitation",
        "department": {
          "budget_document": null,
          "name": "Water and Sanitation",
          "url": "/2019-20/national/departments/water-and-sanitation"
        }
      }
    },
    {
      "id": "/infrastructure-projects/police-police-stations",
      "subheading": "Police",
      "heading": "Police stations",
      "points": [
        {
          "id": "0",
          "x": 30.203,
          "y": -30.4759
        }
      ],
      "activeProvinces": [
        "KwaZulu-Natal"
      ],
      "stage": "Various",
      "totalBudget": 4315060000,
      "projectedBudget": 1965373000,
      "description": "Construction of new and re-established police stations",
      "link": "/infrastructure-projects/police-police-stations",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 516065000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 733288000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 494454000,
          "Projected": null,
          "Connection": 494454000
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 605880000,
          "Connection": 605880000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 627552000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 644733000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 693088000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "Upgrading and additions",
        "infrastructure": "Police stations",
        "department": {
          "budget_document": null,
          "name": "Police",
          "url": "/2019-20/national/departments/police"
        }
      }
    },
    {
      "id": "/infrastructure-projects/basic-education-school-infrastructure-backlogs-grant",
      "subheading": "Basic Education",
      "heading": "School infrastructure backlogs grant",
      "points": [],
      "activeProvinces": [],
      "stage": "Various",
      "totalBudget": 9045389000,
      "projectedBudget": 5688808000,
      "description": "Replace 510 schools that have inappropriate infrastructure, of which 395 are mud schools; provide water to 1 120 schools, sanitation to 741 schools and electricity to 916 schools",
      "link": "/infrastructure-projects/basic-education-school-infrastructure-backlogs-grant",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 1368285000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 1049535000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 1617716000,
          "Projected": null,
          "Connection": 1617716000
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 2121045000,
          "Connection": 2121045000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 1869482000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 1628591000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 2190735000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "New infrastructure assets",
        "infrastructure": "Eradication of inappropriate school infrastructure and provision of basic services to schools",
        "department": {
          "budget_document": null,
          "name": "Basic Education",
          "url": "/2019-20/national/departments/basic-education"
        }
      }
    },
    {
      "id": "/infrastructure-projects/water-and-sanitation-sebokeng-waste-treatment-works-phase-1-and-phase-2",
      "subheading": "Water and Sanitation",
      "heading": "Sebokeng waste treatment works phase 1 and phase 2",
      "points": [
        {
          "id": "0",
          "x": 27.853407,
          "y": -26.558511
        }
      ],
      "activeProvinces": [
        "Gauteng"
      ],
      "stage": "Construction",
      "totalBudget": 1123584000,
      "projectedBudget": 541684000,
      "description": "Upgrading of existing wastewater treatment works",
      "link": "/infrastructure-projects/water-and-sanitation-sebokeng-waste-treatment-works-phase-1-and-phase-2",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 99786000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 166263000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 117567000,
          "Projected": null,
          "Connection": 117567000
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 140700000,
          "Connection": 140700000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 128684000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 263000000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 150000000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "Upgrading and additions",
        "infrastructure": "Waste Water Services",
        "department": {
          "budget_document": null,
          "name": "Water and Sanitation",
          "url": "/2019-20/national/departments/water-and-sanitation"
        }
      }
    },
    {
      "id": "/infrastructure-projects/water-and-sanitation-sedibeng-bulk-regional-sewerage",
      "subheading": "Water and Sanitation",
      "heading": "Sedibeng bulk regional sewerage",
      "points": [
        {
          "id": "0",
          "x": 27.83102,
          "y": -26.692133
        }
      ],
      "activeProvinces": [
        "Gauteng"
      ],
      "stage": "Feasibility",
      "totalBudget": 3000000000,
      "projectedBudget": 448800000,
      "description": "Construction of new wastewater treatment works",
      "link": "/infrastructure-projects/water-and-sanitation-sedibeng-bulk-regional-sewerage",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 26911000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 44087000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 10078000,
          "Projected": null,
          "Connection": 10078000
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 62659000,
          "Connection": 62659000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 76800000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 152000000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 220000000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "New infrastructure assets",
        "infrastructure": "Waste Water Services",
        "department": {
          "budget_document": null,
          "name": "Water and Sanitation",
          "url": "/2019-20/national/departments/water-and-sanitation"
        }
      }
    },
    {
      "id": "/infrastructure-projects/science-and-technology-square-kilometre-array",
      "subheading": "Science and Technology",
      "heading": "Square Kilometre Array",
      "points": [
        {
          "id": "0",
          "x": 18.470737,
          "y": -33.932972
        }
      ],
      "activeProvinces": [
        "Western Cape"
      ],
      "stage": "Construction",
      "totalBudget": 10021173000,
      "projectedBudget": 2355920000,
      "description": "Construction of telescopes",
      "link": "/infrastructure-projects/science-and-technology-square-kilometre-array",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 687415000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 652756000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 693931000,
          "Projected": null,
          "Connection": 693931000
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 709412000,
          "Connection": 709412000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 686974000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 812139000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 856807000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "New other fixed structures",
        "infrastructure": "Radio Telescopes",
        "department": {
          "budget_document": null,
          "name": "Science and Technology",
          "url": "/2019-20/national/departments/science-and-technology"
        }
      }
    },
    {
      "id": "/infrastructure-projects/higher-education-and-training-student-housing-infrastructure-programme-nelson-mandela-university",
      "subheading": "Higher Education and Training",
      "heading": "Student Housing Infrastructure Programme: Nelson Mandela University",
      "points": [
        {
          "id": "0",
          "x": 25.671476,
          "y": -34.000976
        }
      ],
      "activeProvinces": [
        "Eastern Cape"
      ],
      "stage": "Design",
      "totalBudget": 67000000,
      "projectedBudget": 33500000,
      "description": "Student Housing Infrastructure programme",
      "link": "/infrastructure-projects/higher-education-and-training-student-housing-infrastructure-programme-nelson-mandela-university",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 0,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 0,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 0,
          "Projected": null,
          "Connection": 0
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 33500000,
          "Connection": 33500000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 33500000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 0,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 0,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "New infrastructure assets",
        "infrastructure": "Student accommodation",
        "department": {
          "budget_document": null,
          "name": "Higher Education and Training",
          "url": "/2019-20/national/departments/higher-education-and-training"
        }
      }
    },
    {
      "id": "/infrastructure-projects/higher-education-and-training-student-housing-infrastructure-programme-sefako-makgatho-health-sciences-university",
      "subheading": "Higher Education and Training",
      "heading": "Student Housing Infrastructure Programme: Sefako Makgatho Health Sciences University",
      "points": [
        {
          "id": "0",
          "x": 28.016895,
          "y": -25.621066
        }
      ],
      "activeProvinces": [
        "Gauteng"
      ],
      "stage": "Design",
      "totalBudget": 62450000,
      "projectedBudget": 31200000,
      "description": "Student Housing Infrastructure programme",
      "link": "/infrastructure-projects/higher-education-and-training-student-housing-infrastructure-programme-sefako-makgatho-health-sciences-university",
      "resources": [
        {
          heading: 'Example 3 B',
          size: '3.3MB',
          format: 'PDF',
          link:'123',
        },
        {
          heading: 'Example 4 B',
          size: '3.3MB',
          format: 'PDF',
          link:'345',
        },
        {
          heading: 'Example 1 C',
          size: '3.3MB',
          format: 'PDF',
          link:'678',
        },
        {
          heading: 'Example 2 C',
          size: '3.3MB',
          format: 'PDF',
          link:'910',
        },
      ],
      "chartData": [
        {
          "name": "2015",
          "Actual": 0,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 0,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 0,
          "Projected": null,
          "Connection": 0
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 31250000,
          "Connection": 31250000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 31200000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 0,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 0,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "New infrastructure assets",
        "infrastructure": "Student accommodation",
        "department": {
          "budget_document": null,
          "name": "Higher Education and Training",
          "url": "/2019-20/national/departments/higher-education-and-training"
        }
      }
    },
    {
      "id": "/infrastructure-projects/higher-education-and-training-student-housing-infrastructure-programme-vaal-university-of-technology",
      "subheading": "Higher Education and Training",
      "heading": "Student Housing Infrastructure Programme: Vaal University of Technology",
      "points": [
        {
          "id": "0",
          "x": 27.862468,
          "y": -26.710476
        }
      ],
      "activeProvinces": [
        "Gauteng"
      ],
      "stage": "Design",
      "totalBudget": 78980000,
      "projectedBudget": 40300000,
      "description": "Student Housing Infrastructure programme",
      "link": "/infrastructure-projects/higher-education-and-training-student-housing-infrastructure-programme-vaal-university-of-technology",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 0,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 0,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 0,
          "Projected": null,
          "Connection": 0
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 38680000,
          "Connection": 38680000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 40300000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 0,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 0,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "New infrastructure assets",
        "infrastructure": "Student accommodation",
        "department": {
          "budget_document": null,
          "name": "Higher Education and Training",
          "url": "/2019-20/national/departments/higher-education-and-training"
        }
      }
    },
    {
      "id": "/infrastructure-projects/water-and-sanitation-westonaria-randfontein-regional-bulk-wastewater-treatment-works-zuurbekom",
      "subheading": "Water and Sanitation",
      "heading": "Westonaria/Randfontein regional bulk wastewater treatment works (Zuurbekom)",
      "points": [
        {
          "id": "0",
          "x": 27.654933,
          "y": -26.378582
        }
      ],
      "activeProvinces": [
        "Gauteng"
      ],
      "stage": "Design",
      "totalBudget": 1570000000,
      "projectedBudget": 444214000,
      "description": "Construction of new wastewater treatment works",
      "link": "/infrastructure-projects/water-and-sanitation-westonaria-randfontein-regional-bulk-wastewater-treatment-works-zuurbekom",
      "resources": [],
      "chartData": [
        {
          "name": "2015",
          "Actual": 7104000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2016",
          "Actual": 1314000,
          "Projected": null,
          "Connection": null
        },
        {
          "name": "2017",
          "Actual": 1036000,
          "Projected": null,
          "Connection": 1036000
        },
        {
          "name": "2018",
          "Actual": null,
          "Projected": 55500000,
          "Connection": 55500000
        },
        {
          "name": "2019",
          "Actual": null,
          "Projected": 70000000,
          "Connection": null
        },
        {
          "name": "2020",
          "Actual": null,
          "Projected": 100000000,
          "Connection": null
        },
        {
          "name": "2021",
          "Actual": null,
          "Projected": 274214000,
          "Connection": null
        }
      ],
      "sideInfo": {
        "investment": "New infrastructure assets",
        "infrastructure": "Waste Water Services",
        "department": {
          "budget_document": null,
          "name": "Water and Sanitation",
          "url": "/2019-20/national/departments/water-and-sanitation"
        }
      }
    }
  ]
}


const detailsFalse = () => <Infrastructure {...props} />;
const detailsTrue = () => <Infrastructure {...props} details />;


storiesOf('views.Infrastructure', module)
  .add('Details False', detailsFalse)
  .add('Details True', detailsTrue);
