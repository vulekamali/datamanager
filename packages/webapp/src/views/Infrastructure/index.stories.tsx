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
    }
  ]
}



const currentProps = {
    "dataset_url": "/datasets/infrastructure-projects/major-infrastructure-projects-by-national-departments",
    "description": "Infrastructure projects in South Africa for 2019-20",
    "projects": [
        {  
            "id": "/infrastructure-projects/water-and-sanitation-calitzdorp-and-ladismith-w",
            "coordinates": [
                {
                    "latitude": -33.913362,
                    "longitude": 18.419422
                }
            ],
            "dataset_url": "/datasets/infrastructure-projects/major-infrastructure-projects-by-national-departments",
            "department": {
                "budget_document": "https://data.vulekamali.gov.za/dataset/b48e70b5-ef57-4005-882d-882d3982e5b5/resource/7476dc34-0845-422d-ba0e-d3102ff274cf/download/vote-35-transport.pdf",
                "name": "Transport",
                "url": "/2019-20/national/departments/transport"
            },
            "description": "Bus rapid transport network in Cape Town",
            "detail": "/infrastructure-projects/transport-cape-towns-metro-southeast-myciti-phase-2a",
            "resources": [],
            "chartData": [
                {
                    "amount": 0,
                    "budget_phase": "Audited Outcome",
                    "year": 2015,
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
                    "amount": 0,
                    "budget_phase": "Audited Outcome",
                    "year": 2017,
                    "name": "2017",
          "Actual": 0,
          "Projected": null,
          "Connection": 0
                },
                {
                    "amount": 33000000,
                    "budget_phase": "Adjusted Appropriation",
                    "year": 2018,
                    "name": "2018",
          "Actual": null,
          "Projected": 0,
          "Connection": 0
                },
                {
                    "amount": 354000000,
                    "budget_phase": "MTEF",
                    "year": 2019,
                    "name": "2019",
          "Actual": null,
          "Projected": 15000000,
          "Connection": null
                },
                {
                    "amount": 1045000000,
                    "budget_phase": "MTEF",
                    "year": 2020,
                    "name": "2020",
          "Actual": null,
          "Projected": 30000000,
          "Connection": null
                },
                {
                    "amount": 1433000000,
                    "budget_phase": "MTEF",
                    "year": 2021,
                    "name": "2021",
          "Actual": null,
          "Projected": 30000000,
          "Connection": null
                }
            ],
            "infrastructure_type": "Public transport",
            "name": "Cape Town's metro Southeast (MyCiti phase 2A)",
            "nature_of_investment": "Upgrades and additions",
            "page_title": "Cape Town's metro Southeast (MyCiti phase 2A) - vulekamali",
            "projected_budget": 2832000000.0,
            "provinces": [
                "Western Cape"
            ],
            "slug": "/infrastructure-projects/transport-cape-towns-metro-southeast-myciti-phase-2a",
            "stage": "Construction",
            "total_budget": 7100000000
        }
    ],
    "selected_tab": "infrastructure-projects",
    "slug": "infrastructure-projects",
    "title": "Infrastructure Projects - vulekamali"
}



const detailsFalse = () => <Infrastructure {...props} />;
const detailsTrue = () => <Infrastructure {...props} details />;


storiesOf('views.Infrastructure', module)
  .add('Details False', detailsFalse)
  .add('Details True', detailsTrue);
