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

const detailsFalse = () => <Infrastructure {...props} />;
const detailsTrue = () => <Infrastructure {...props} details />;


storiesOf('views.Infrastructure', module)
  .add('Details False', detailsFalse)
  .add('Details True', detailsTrue);
